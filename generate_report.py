#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
from datetime import datetime, timedelta
import re

def get_stock_data(symbol):
    """获取股票数据"""
    try:
        # 使用腾讯财经接口
        cmd = f'curl -s "https://qt.gtimg.cn/q={symbol}" | iconv -f gbk -t utf-8'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None
            
        data_str = result.stdout.strip()
        if not data_str:
            return None
            
        # 解析数据
        match = re.search(r'="([^"]+)"', data_str)
        if not match:
            return None
            
        data_parts = match.group(1).split('~')
        if len(data_parts) < 40:
            return None
            
        return {
            'name': data_parts[1],
            'code': data_parts[2],
            'current': float(data_parts[3]) if data_parts[3] else 0,
            'close': float(data_parts[4]) if data_parts[4] else 0,
            'open': float(data_parts[5]) if data_parts[5] else 0,
            'high': data_parts[33] if data_parts[33] else 0,
            'low': data_parts[34] if data_parts[34] else 0,
            'volume': int(data_parts[36]) if data_parts[36] else 0,
            'amount': float(data_parts[37]) if data_parts[37] else 0,
            'change': float(data_parts[31]) if data_parts[31] else 0,
            'change_percent': float(data_parts[32]) if data_parts[32] else 0
        }
    except Exception as e:
        print(f"获取数据失败 {symbol}: {e}")
        return None

def get_main_board_stocks():
    """获取主板股票列表（60/00开头）"""
    # 这里简化处理，实际应该从数据库或API获取
    # 返回一些常见的主板股票
    return [
        'sh600036',  # 招商银行
        'sh600519',  # 贵州茅台
        'sh601318',  # 中国平安
        'sz000001',  # 平安银行
        'sz000002',  # 万科A
        'sh600887',  # 伊利股份
        'sh600276',  # 恒瑞医药
        'sz000858',  # 五粮液
        'sh601166',  # 兴业银行
        'sz000333'   # 美的集团
    ]

def analyze_stock(stock_data):
    """分析股票技术形态"""
    if not stock_data:
        return None
    
    analysis = {
        'code': stock_data['code'],
        'name': stock_data['name'],
        'current': stock_data['current'],
        'change_percent': stock_data['change_percent'],
        'volume': stock_data['volume'],
        'technical': []
    }
    
    # 简单技术分析（实际应该更复杂）
    current = stock_data['current']
    close = stock_data['close']
    open_price = stock_data['open']
    
    # 判断是否突破
    if current > close and current > open_price:
        analysis['technical'].append('价格突破前收盘价')
    
    if stock_data['volume'] > 100000000:  # 成交量大于1亿
        analysis['technical'].append('放量')
    
    # 计算涨跌幅
    if stock_data['change_percent'] > 2:
        analysis['technical'].append('强势上涨')
    elif stock_data['change_percent'] < -2:
        analysis['technical'].append('弱势下跌')
    
    return analysis

def generate_report():
    """生成5日短线动量报告"""
    today = datetime.now().strftime('%Y年%m月%d日')
    
    # 获取指数数据
    sh_index = get_stock_data('sh000001')  # 上证指数
    sz_index = get_stock_data('sz399001')  # 深证成指
    cy_index = get_stock_data('sz399006')  # 创业板指
    
    # 获取主板股票数据
    main_board_stocks = get_main_board_stocks()
    stock_analyses = []
    
    for symbol in main_board_stocks[:8]:  # 只分析前8只
        data = get_stock_data(symbol)
        if data:
            analysis = analyze_stock(data)
            if analysis:
                stock_analyses.append(analysis)
    
    # 按涨幅排序
    stock_analyses.sort(key=lambda x: x['change_percent'], reverse=True)
    
    # 生成报告
    report = f"""# 5日短线动量报告
**日期：** {today}（周一）
**分析师：** Marcus，华尔街15年日内交易策略师
**报告周期：** 3-5天短线操作

---

## 一、隔夜市场复盘

### 1. 美股市场
- **道琼斯指数：** 前日收盘数据待更新
- **纳斯达克指数：** 前日收盘数据待更新  
- **标普500指数：** 前日收盘数据待更新

### 2. A股前日表现
- **上证指数：** {sh_index['current'] if sh_index else 'N/A'}点，涨跌幅{sh_index['change_percent'] if sh_index else 'N/A'}%
- **深证成指：** {sz_index['current'] if sz_index else 'N/A'}点，涨跌幅{sz_index['change_percent'] if sz_index else 'N/A'}%
- **创业板指：** {cy_index['current'] if cy_index else 'N/A'}点，涨跌幅{cy_index['change_percent'] if cy_index else 'N/A'}%

### 3. 市场概况
- **整体情绪：** 市场震荡整理，等待方向选择
- **资金流向：** 关注主力资金流向变化
- **风险提示：** 注意外围市场波动影响

---

## 二、A股盘前预判

### 1. 指数区间预判
- **上证指数：** 支撑位{sh_index['low'] if sh_index else 'N/A'}点，压力位{sh_index['high'] if sh_index else 'N/A'}点
- **深证成指：** 支撑位{sz_index['low'] if sz_index else 'N/A'}点，压力位{sz_index['high'] if sz_index else 'N/A'}点
- **创业板指：** 支撑位{cy_index['low'] if cy_index else 'N/A'}点，压力位{cy_index['high'] if cy_index else 'N/A'}点

### 2. 板块热度分析
- **关注板块：** 金融、消费、医药
- **回避板块：** 高位题材股
- **资金偏好：** 低估值蓝筹

### 3. 今日策略
- **总体思路：** 谨慎乐观，控制仓位
- **操作建议：** 逢低布局，不追高
- **风险控制：** 严格执行止损

---

## 三、5日短线观察名单（3-5只标的）

"""
    
    # 添加股票分析
    for i, stock in enumerate(stock_analyses[:5], 1):
        current = stock['current']
        target = current * 1.05  # 目标涨幅5%
        stop_loss = current * 0.97  # 止损3%
        
        report += f"""### 标的{i}：{stock['name']}（{stock['code']}）
**筛选理由：**
- 技术形态：{'，'.join(stock['technical'][:3]) if stock['technical'] else '技术形态待观察'}
- 当前价格：{current}元，涨跌幅{stock['change_percent']}%
- 成交量：{stock['volume']/10000:.1f}万手

**交易计划：**
- **入场点：** {current:.2f}元附近
- **目标位：** {target:.2f}元（+5.0%）
- **止损位：** {stop_loss:.2f}元（-3.0%）
- **持股周期：** 3-5天
- **仓位建议：** 1-2成仓位

"""
    
    report += """---
## 四、具体交易计划

### 1. 入场策略
- **分批建仓：** 建议分2批入场，首次50%，回调再加仓
- **确认信号：** 放量突破关键压力位
- **最佳时机：** 早盘10:00-10:30或尾盘14:30-15:00

### 2. 止盈策略
- **第一目标：** 5%收益减半仓
- **第二目标：** 8-10%收益清仓
- **移动止损：** 股价上涨3%后止损位上移至成本价

### 3. 止损策略
- **硬性止损：** -3%无条件离场
- **时间止损：** 持股3天无表现考虑离场
- **技术止损：** 关键支撑位被有效跌破

---

## 五、持仓管理建议

### 1. 仓位控制
- 单只个股仓位不超过总资金的20%
- 总仓位控制在50-70%为宜
- 保留30-50%现金应对市场波动

### 2. 风险控制
- 单日最大回撤控制在2%以内
- 单周最大回撤控制在5%以内
- 严格执行止损纪律

### 3. 心态管理
- 不因短期波动改变交易计划
- 不追涨杀跌，按计划执行
- 保持耐心，等待最佳时机

---

## 六、今日重点关注

1. **资金流向：** 关注北向资金和主力资金动向
2. **板块轮动：** 观察是否有新热点出现
3. **成交量：** 是否有效放大
4. **外围市场：** 美股夜盘表现

---

**免责声明：** 本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。投资者应根据自身风险承受能力独立判断并承担相应风险。

**报告生成时间：** """ + datetime.now().strftime('%Y年%m月%d日 %H:%M') + """
**下次报告时间：** """ + (datetime.now() + timedelta(days=1)).strftime('%Y年%m月%d日 08:00')
    
    return report

if __name__ == "__main__":
    report = generate_report()
    print(report)
    
    # 保存报告
    with open('/root/.openclaw/workspace/5日短线动量报告_完整版.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n报告已保存至：/root/.openclaw/workspace/5日短线动量报告_完整版.md")