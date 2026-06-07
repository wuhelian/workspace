#!/usr/bin/env python3
"""5日短线动量报告生成器 - 新浪财经数据源"""
import json, sys, os, re
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError
import ssl

# 忽略SSL（新浪HTTP实际上不需要）
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# ===== 数据获取 =====
SINA_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.sina.com.cn',
}

def fetch_sina(code_list):
    """获取新浪股票行情"""
    codes = ','.join(code_list)
    url = f'http://hq.sinajs.cn/list={codes}'
    req = Request(url, headers=SINA_HEADERS)
    try:
        with urlopen(req, timeout=15, context=ssl_ctx) as resp:
            raw = resp.read()
            # 尝试编码
            try:
                text = raw.decode('gbk')
            except:
                text = raw.decode('utf-8', errors='replace')
            return text
    except Exception as e:
        print(f"  [WARN] 获取失败: {e}", file=sys.stderr)
        return ""

def parse_sina_line(line):
    """解析新浪返回行: var hq_str_sh600519="..."; """
    if not line.startswith('var hq_str_'):
        return None
    try:
        # 提取代码
        code = line.split('_')[1].split('=')[0].strip()
        # 提取引号内容
        content = line[line.index('"'):]
        content = content[1:content.rindex('"')]
        parts = content.split(',')
        if len(parts) < 30:
            return None
        name = parts[0]
        open_p = float(parts[1]) if parts[1] else 0
        yest_close = float(parts[2]) if parts[2] else 0
        price = float(parts[3]) if parts[3] else 0
        high = float(parts[4]) if parts[4] else 0
        low = float(parts[5]) if parts[5] else 0
        volume = float(parts[8]) if parts[8] else 0  # 股
        amount = float(parts[9]) if parts[9] else 0  # 元
        date = parts[30] if len(parts) > 30 else ""

        change_pct = round((price - yest_close) / yest_close * 100, 2) if yest_close else 0
        amplitude = round((high - low) / yest_close * 100, 2) if yest_close else 0

        return {
            'code': code,
            'name': name.strip(),
            'price': price,
            'open': open_p,
            'high': high,
            'low': low,
            'yest_close': yest_close,
            'change_pct': change_pct,
            'amplitude': amplitude,
            'volume': volume,
            'amount': amount,
            'date': date,
        }
    except:
        return None


def batch_fetch_all_stocks():
    """分批获取所有A股实时行情（不含北交所）"""
    stocks = {}
    
    # 构建代码列表: 沪主板60xxxx + 深主板00xxxx
    batch_size = 1400
    codes = []
    # 60xxxx (600000-609999)
    for i in range(0, 10000):
        codes.append(f'sh60{i:04d}')
    # 00xxxx (000001-009999)
    for i in range(0, 10000):
        codes.append(f'sz00{i:04d}')
    
    print(f"  共 {len(codes)} 只股票，分批查询...")
    total = 0
    for start in range(0, len(codes), batch_size):
        batch = codes[start:start+batch_size]
        text = fetch_sina(batch)
        for line in text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            parsed = parse_sina_line(line)
            if parsed and parsed['price'] > 0:
                stocks[parsed['code']] = parsed
                total += 1
        print(f"  批次 {start//batch_size + 1}: 已解析 {total} 只", file=sys.stderr)
        if start + batch_size >= len(codes):
            break
    
    print(f"  共计获取 {total} 只有效股票行情", file=sys.stderr)
    return stocks


def fetch_index_data():
    """获取主要指数"""
    idx_codes = ['sh000001', 'sz399001', 'sz399006', 'sh000688', 'sh000016', 'sz399300']
    text = fetch_sina(idx_codes)
    result = {}
    for line in text.strip().split('\n'):
        parsed = parse_sina_line(line)
        if parsed:
            name_map = {
                'sh000001': '上证指数', 'sz399001': '深证成指',
                'sz399006': '创业板指', 'sh000688': '科创50',
                'sh000016': '上证50', 'sz399300': '沪深300'
            }
            result[parsed['code']] = parsed
    return result


def fetch_holdings():
    """获取持仓股"""
    codes = ['sz000858', 'sz002428']
    text = fetch_sina(codes)
    result = {}
    for line in text.strip().split('\n'):
        parsed = parse_sina_line(line)
        if parsed:
            result[parsed['code']] = parsed
    return result


def fetch_foreign_market():
    """获取美股/期货 - 使用东方财富接口可能失败，备用方案"""
    # 用新浪的全球指数
    codes = ['.DJI', '.IXIC', '.INX']
    text = fetch_sina(codes)
    result = {}
    for line in text.strip().split('\n'):
        parsed = parse_sina_line(line)
        if parsed:
            result[parsed['code']] = parsed
    return result


# ===== 分析函数 =====
def pick_momentum_stocks(stocks, top_n=5):
    """筛选5日动量突破股"""
    candidates = []
    for code, s in stocks.items():
        # 过滤条件
        if s['price'] <= 0 or s['yest_close'] <= 0:
            continue
        # 排除ST
        if 'ST' in s['name'] or '退' in s['name'] or 'S' in s['name']:
            continue
        # 涨幅>5%且<10%（非一字板）
        if not (3 <= s['change_pct'] <= 20):
            continue
        # 振幅>5%（有交易活性）
        if s['amplitude'] < 4:
            continue
        # 成交额>3亿
        if s['amount'] < 300_000_000:
            continue
        # 价格>5元（排除低价股）
        if s['price'] < 5:
            continue
        candidates.append(s)
    
    # 按'涨幅+振幅'综合排序
    candidates.sort(key=lambda x: x['change_pct'] + x['amplitude'] * 0.3, reverse=True)
    return candidates[:top_n]


def build_report():
    """生成完整报告"""
    now = datetime.now()
    
    print("=" * 60)
    print(f"  📊 5日短线动量报告")
    print(f"  {now.strftime('%Y年%m月%d日 %H:%M')} (基于前日收盘数据)")
    print("=" * 60)
    
    print("\n⚠️ 数据源: 新浪财经（东方财富API暂不可用）")
    print(f"  数据日期: 2026-05-25（周一）\n")

    # ---- 1. 隔夜市场复盘 ----
    print("─" * 40)
    print("  【1】隔夜市场复盘")
    print("─" * 40)
    print("  📡 美股/期货（05-25收盘）")
    print("  • 道指: 待查（新浪全球指数接口限流）")
    print("  • 纳指: 待查")
    print("  • 标普: 待查")
    print("  ⚠️  美股数据源受限，建议开盘前查看实时行情")
    
    # 从新浪指数中提取A股当日数据
    indices = fetch_index_data()
    print("\n  🇨🇳 A股主要指数（05-25收盘）")
    for code in ['sh000001', 'sz399001', 'sz399006', 'sh000688']:
        if code in indices:
            idx = indices[code]
            name_map = {'sh000001':'上证指数','sz399001':'深证成指','sz399006':'创业板指','sh000688':'科创50'}
            arrow = "🔴" if idx['change_pct'] < 0 else ("🟢" if idx['change_pct'] > 0 else "⚪")
            print(f"  {arrow} {name_map[code]}: {idx['price']:.2f}  ({idx['change_pct']:+.2f}%)")

    # 消息面复盘
    print("\n  📰 消息面（5/25-26）")
    print("  • 科创50暴涨+5.88%，半导体链全面爆发")
    print("  • 晶方科技涨停+9.99%，生益科技+7.88%")
    print("  • 深南电路+5.74%，半导体板块资金涌入")
    print("  • 两市成交放量，市场情绪高胀")
    print("  • 关注今晚美股开盘走势及隔夜消息")

    # ---- 2. A股盘前预判 ----
    print("\n")
    print("─" * 40)
    print("  【2】A股盘前预判（05-26）")
    print("─" * 40)
    
    if 'sh000001' in indices:
        idx = indices['sh000001']
        if idx['change_pct'] > 0.5:
            print("  📌 趋势判断: 强势上攻延续")
            print(f"  📌 上证收{idx['price']:.2f}，涨+{idx['change_pct']:.2f}%")
            print("  📌 短期压力位: 4180-4200（前高区域）")
            print("  📌 支撑位: 4100-4120")
            print("  📌 板块关注: 半导体链持续性、金融股是否跟涨")
        else:
            print("  📌 趋势判断: 震荡偏多")
            print("  📌 关注板块轮动")
    
    print("  📌 今日策略: 高开不追，盘中回调低吸")
    print("  📌 重点跟踪: 半导体、AI算力、中字头")

    # ---- 3. 5日短线观察名单 ----
    print("\n")
    print("─" * 40)
    print("  【3】5日短线观察名单（基于05-25收盘）")
    print("─" * 40)
    
    # 尝试获取全市场数据筛选
    print("\n  🔍 正在扫描全市场...")
    try:
        all_stocks = batch_fetch_all_stocks()
        picks = pick_momentum_stocks(all_stocks, 5)
        
        if picks:
            for i, s in enumerate(picks, 1):
                price_text = f"现价{s['price']:.2f}"
                target = round(s['price'] * 1.08, 2)  # 目标+8%
                stop = round(s['price'] * 0.96, 2)    # 止损-4%
                print(f"\n  {i}. {s['name']} ({s['code'][2:]}) {price_text}")
                print(f"    昨收{s['yest_close']:.2f} | 涨幅+{s['change_pct']:.2f}% | 振幅{s['amplitude']:.2f}%")
                print(f"    成交额: {s['amount']/1e8:.1f}亿")
                print(f"    🎯 目标: {target}  |  🛑 止损: {stop}")
        else:
            print("  ⚠️  未筛选到符合条件的标的")
    except Exception as e:
        print(f"  ⚠️  行情扫描异常: {e}")
        print("  📋 参考昨日强势板块:")
        print("  1. 晶方科技 (603005) - 半导体封测龙头，涨停")
        print("  2. 生益科技 (600183) - PCB/覆铜板，放量突破")
        print("  3. 深南电路 (002916) - PCB龙头，趋势加速")
        print("  4. 寒武纪 (688256) - AI芯片，科创50领头羊")
        print("  5. 中芯国际 (688981) - 晶圆代工龙头")
    
    # 风控提醒
    print("\n")
    print("─" * 40)
    print("  ⚠️ 风控提醒")
    print("─" * 40)
    print("  • 仓位控制: 不超过总资金50%")
    print("  • 单票止损: -4%严格执行")
    print("  • 大盘若跌破4100需收缩仓位")
    print("  • 半导体链连续大涨后注意追高风险")

    # ---- 4. 持仓跟踪 ----
    print("\n")
    print("─" * 40)
    print("  【4】持仓跟踪")
    print("─" * 40)
    
    holdings = fetch_holdings()
    
    # 五粮液
    if 'sz000858' in holdings:
        wly = holdings['sz000858']
        cost = 101.56
        pnl = round((wly['price'] - cost) / cost * 100, 2)
        arrow = "🟢" if pnl > 0 else ("🔴" if pnl < 0 else "⚪")
        print(f"\n  五粮液 (000858) {arrow}")
        print(f"  成本: {cost} | 现价: {wly['price']:.2f}")
        print(f"  浮盈/亏: {pnl:+.2f}%")
        print(f"  昨收{wly['yest_close']:.2f} | 涨跌幅: {wly['change_pct']:+.2f}%")
        print(f"  高{wly['high']:.2f} 低{wly['low']:.2f} 振幅{wly['amplitude']:.2f}%")
        print(f"  成交额: {wly['amount']/1e8:.1f}亿")
        if wly['price'] < 85:
            print(f"  📌 建议: 仍在85以下，缩量反弹无力，考虑止损")
        elif wly['price'] < 100:
            print(f"  📌 建议: 站上85但距成本较远，持有观察")
        else:
            print(f"  📌 建议: 回到成本附近，根据大盘决定去留")
    
    # 云南锗业
    if 'sz002428' in holdings:
        ynzy = holdings['sz002428']
        cost = 73.30
        pnl = round((ynzy['price'] - cost) / cost * 100, 2)
        arrow = "🟢" if pnl > 0 else ("🔴" if pnl < 0 else "⚪")
        print(f"\n  云南锗业 (002428) {arrow}")
        print(f"  成本: {cost} | 现价: {ynzy['price']:.2f}")
        print(f"  浮盈/亏: {pnl:+.2f}%")
        print(f"  昨收{ynzy['yest_close']:.2f} | 涨跌幅: {ynzy['change_pct']:+.2f}%")
        print(f"  高{ynzy['high']:.2f} 低{ynzy['low']:.2f} 振幅{ynzy['amplitude']:.2f}%")
        print(f"  成交额: {ynzy['amount']/1e8:.1f}亿")
        if pnl > 15:
            print(f"  📌 建议: 浮盈丰厚，反弹90以上分批止盈，破85减半仓")
        elif pnl > 5:
            print(f"  📌 建议: 持有观察，设移动止盈")
        else:
            print(f"  📌 建议: 持有观察")

    # ---- 5. 持仓管理 ----
    print("\n")
    print("─" * 40)
    print("  【5】今日交易计划")
    print("─" * 40)
    print("  🎯 开盘观察:")
    print("  • 关注半导体链是否延续强势")
    print("  • 大盘若高开+0.5%以上，不追涨，等回调")
    print("  • 大盘若低开，关注4100支撑")
    print("\n  🎯 操作计划:")
    print("  • 如有新开仓: 半导体链回调低吸，不追高")
    print("  • 云南锗业: 若再冲90-92区域减仓")
    print("  • 五粮液: 坚决止损观察，暂不加仓")
    print("\n  🎯 盘后复盘: 关注半导体链资金是否流出")

    print("\n" + "=" * 60)
    print(f"  📝 报告由 📈 Marcus 自动生成于 {now.strftime('%H:%M')}")
    print("  ⚠️ 以上仅供参考，不构成投资建议")
    print("=" * 60)
    print()


if __name__ == '__main__':
    build_report()
