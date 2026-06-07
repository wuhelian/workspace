#!/usr/bin/env python3
"""
低价股筛选系统 - 专注于8-15元价格区间的优质股票
"""

import pandas as pd
import numpy as np
from datetime import datetime

class LowPriceStockScreener:
    """低价股筛选器（8-15元区间）"""
    
    def __init__(self):
        self.price_range = (8, 15)  # 价格区间
        self.hot_industries = self.get_hot_industries()
        
    def get_hot_industries(self):
        """获取热门行业（低价股偏好行业）"""
        return {
            '银行': {'热度': 78, '特点': '低估值，高股息'},
            '公用事业': {'热度': 72, '特点': '防御性强，稳定'},
            '交通运输': {'热度': 68, '特点': '经济复苏受益'},
            '建筑装饰': {'热度': 65, '特点': '基建投资受益'},
            '化工': {'热度': 70, '特点': '周期反转'},
            '机械设备': {'热度': 73, '特点': '制造业升级'},
            '环保': {'热度': 66, '特点': '政策支持'},
            '纺织服装': {'热度': 62, '特点': '消费复苏'}
        }
    
    def get_low_price_stocks_pool(self):
        """获取低价股股票池（模拟数据）"""
        # 在实际环境中会从akshare获取所有A股，然后筛选价格区间
        low_price_stocks = [
            # 银行股（低估值，高股息）
            {'代码': '601288', '名称': '农业银行', '最新价': '3.65', '涨跌幅': '2.5', '量比': '1.3', '换手率': '0.8', '振幅': '2.1', '市盈率': '4.2', '市净率': '0.5', '股息率': '6.8'},
            {'代码': '601398', '名称': '工商银行', '最新价': '5.20', '涨跌幅': '1.8', '量比': '1.1', '换手率': '0.5', '振幅': '1.8', '市盈率': '4.8', '市净率': '0.6', '股息率': '6.2'},
            {'代码': '601939', '名称': '建设银行', '最新价': '6.85', '涨跌幅': '2.1', '量比': '1.2', '换手率': '0.6', '振幅': '2.0', '市盈率': '5.1', '市净率': '0.7', '股息率': '5.8'},
            
            # 8-15元区间优质股
            {'代码': '600016', '名称': '民生银行', '最新价': '8.45', '涨跌幅': '3.2', '量比': '1.5', '换手率': '1.2', '振幅': '3.5', '市盈率': '4.5', '市净率': '0.4', '股息率': '7.2'},
            {'代码': '600000', '名称': '浦发银行', '最新价': '9.20', '涨跌幅': '2.8', '量比': '1.4', '换手率': '1.0', '振幅': '3.2', '市盈率': '4.8', '市净率': '0.5', '股息率': '6.5'},
            {'代码': '600015', '名称': '华夏银行', '最新价': '10.85', '涨跌幅': '3.5', '量比': '1.6', '换手率': '1.5', '振幅': '3.8', '市盈率': '4.2', '市净率': '0.4', '股息率': '7.5'},
            
            # 公用事业股
            {'代码': '600011', '名称': '华能国际', '最新价': '8.90', '涨跌幅': '4.2', '量比': '1.8', '换手率': '2.1', '振幅': '4.5', '市盈率': '12.5', '市净率': '1.2', '股息率': '4.8'},
            {'代码': '600027', '名称': '华电国际', '最新价': '9.65', '涨跌幅': '3.8', '量比': '1.7', '换手率': '1.8', '振幅': '4.2', '市盈率': '10.8', '市净率': '1.1', '股息率': '5.2'},
            
            # 交通运输
            {'代码': '600029', '名称': '南方航空', '最新价': '11.20', '涨跌幅': '5.2', '量比': '2.1', '换手率': '2.5', '振幅': '5.8', '市盈率': '15.2', '市净率': '1.5', '股息率': '3.2'},
            {'代码': '600115', '名称': '东方航空', '最新价': '9.85', '涨跌幅': '4.8', '量比': '1.9', '换手率': '2.2', '振幅': '5.2', '市盈率': '14.8', '市净率': '1.4', '股息率': '3.5'},
            
            # 建筑装饰
            {'代码': '601668', '名称': '中国建筑', '最新价': '8.65', '涨跌幅': '3.2', '量比': '1.4', '换手率': '1.2', '振幅': '3.5', '市盈率': '4.2', '市净率': '0.6', '股息率': '5.8'},
            {'代码': '601186', '名称': '中国铁建', '最新价': '12.40', '涨跌幅': '2.9', '量比': '1.3', '换手率': '1.0', '振幅': '3.2', '市盈率': '5.1', '市净率': '0.7', '股息率': '4.5'},
            
            # 化工
            {'代码': '600309', '名称': '万华化学', '最新价': '85.60', '涨跌幅': '3.5', '量比': '1.6', '换手率': '1.8', '振幅': '4.2', '市盈率': '18.2', '市净率': '3.2', '股息率': '2.8'},
            {'代码': '600426', '名称': '华鲁恒升', '最新价': '14.85', '涨跌幅': '4.1', '量比': '1.7', '换手率': '2.1', '振幅': '4.8', '市盈率': '12.5', '市净率': '2.1', '股息率': '3.8'},
            
            # 机械设备
            {'代码': '000157', '名称': '中联重科', '最新价': '13.20', '涨跌幅': '5.8', '量比': '2.2', '换手率': '2.8', '振幅': '6.2', '市盈率': '14.2', '市净率': '1.8', '股息率': '4.2'},
            {'代码': '000425', '名称': '徐工机械', '最新价': '11.85', '涨跌幅': '4.5', '量比': '1.9', '换手率': '2.3', '振幅': '5.5', '市盈率': '13.8', '市净率': '1.6', '股息率': '4.5'},
            
            # 环保
            {'代码': '300070', '名称': '碧水源', '最新价': '9.20', '涨跌幅': '3.8', '量比': '1.6', '换手率': '1.9', '振幅': '4.5', '市盈率': '22.5', '市净率': '1.8', '股息率': '2.5'},
            
            # 纺织服装
            {'代码': '600398', '名称': '海澜之家', '最新价': '8.95', '涨跌幅': '3.2', '量比': '1.4', '换手率': '1.5', '振幅': '3.8', '市盈率': '11.2', '市净率': '1.5', '股息率': '5.2'},
            {'代码': '002029', '名称': '七匹狼', '最新价': '7.85', '涨跌幅': '2.8', '量比': '1.3', '换手率': '1.2', '振幅': '3.2', '市盈率': '13.5', '市净率': '1.2', '股息率': '4.8'},
        ]
        
        return low_price_stocks
    
    def get_stock_industry(self, stock_code, stock_name):
        """获取股票所属行业"""
        industry_map = {
            # 银行
            '601288': '银行', '601398': '银行', '601939': '银行',
            '600016': '银行', '600000': '银行', '600015': '银行',
            # 公用事业
            '600011': '公用事业', '600027': '公用事业',
            # 交通运输
            '600029': '交通运输', '600115': '交通运输',
            # 建筑装饰
            '601668': '建筑装饰', '601186': '建筑装饰',
            # 化工
            '600309': '化工', '600426': '化工',
            # 机械设备
            '000157': '机械设备', '000425': '机械设备',
            # 环保
            '300070': '环保',
            # 纺织服装
            '600398': '纺织服装', '002029': '纺织服装'
        }
        
        if stock_code in industry_map:
            return industry_map[stock_code]
        
        name_lower = stock_name.lower()
        if any(keyword in name_lower for keyword in ['银行', '农商', '招行']):
            return '银行'
        elif any(keyword in name_lower for keyword in ['电力', '能源', '发电']):
            return '公用事业'
        elif any(keyword in name_lower for keyword in ['航空', '机场', '物流']):
            return '交通运输'
        elif any(keyword in name_lower for keyword in ['建筑', '建设', '工程']):
            return '建筑装饰'
        elif any(keyword in name_lower for keyword in ['化工', '化学', '材料']):
            return '化工'
        elif any(keyword in name_lower for keyword in ['机械', '装备', '重工']):
            return '机械设备'
        elif any(keyword in name_lower for keyword in ['环保', '水务', '环境']):
            return '环保'
        elif any(keyword in name_lower for keyword in ['服装', '纺织', '服饰']):
            return '纺织服装'
        else:
            return '其他'
    
    def calculate_low_price_score(self, stock_data):
        """计算低价股综合评分"""
        
        price = float(stock_data['最新价'])
        
        # 价格优势评分（30%）：价格越低，优势越大
        if price < 10:
            price_score = 25
        elif price < 12:
            price_score = 20
        elif price < 15:
            price_score = 15
        else:
            price_score = 10
        
        # 技术指标评分（30%）
        tech_score = (
            min(stock_data['涨跌幅'] * 2, 20) +          # 涨幅，最高20分
            min((stock_data['量比'] - 1) * 15, 10)       # 量比，最高10分
        )
        
        # 估值指标评分（20%）
        pe = float(stock_data['市盈率'])
        pb = float(stock_data['市净率'])
        dividend = float(stock_data['股息率'])
        
        valuation_score = 0
        if pe < 8:
            valuation_score += 8  # 低市盈率
        elif pe < 15:
            valuation_score += 5
        
        if pb < 1:
            valuation_score += 7  # 破净股
        elif pb < 1.5:
            valuation_score += 4
        
        if dividend > 5:
            valuation_score += 5  # 高股息
        elif dividend > 3:
            valuation_score += 3
        
        # 行业轮动评分（20%）
        industry = self.get_stock_industry(stock_data['代码'], stock_data['名称'])
        if industry in self.hot_industries:
            industry_score = self.hot_industries[industry]['热度'] * 0.2
        else:
            industry_score = 50 * 0.2
        
        total_score = price_score * 0.3 + tech_score * 0.3 + valuation_score * 0.2 + industry_score
        
        return {
            '总评分': total_score,
            '价格分': price_score,
            '技术分': tech_score,
            '估值分': valuation_score,
            '行业分': industry_score,
            '所属行业': industry,
            '市盈率': pe,
            '市净率': pb,
            '股息率': dividend
        }
    
    def screen_low_price_stocks(self):
        """筛选低价股"""
        
        print(f"🎯 开始低价股筛选（价格区间: {self.price_range[0]}-{self.price_range[1]}元）")
        print("="*60)
        
        # 获取股票池
        stocks = self.get_low_price_stocks_pool()
        df = pd.DataFrame(stocks)
        
        print(f"📊 初始股票池: {len(df)} 只股票")
        
        # 1. 价格区间筛选
        df['最新价_num'] = pd.to_numeric(df['最新价'], errors='coerce')
        price_filtered = df[
            (df['最新价_num'] >= self.price_range[0]) &
            (df['最新价_num'] <= self.price_range[1])
        ].copy()
        
        print(f"✅ 价格区间筛选后: {len(price_filtered)} 只（{self.price_range[0]}-{self.price_range[1]}元）")
        
        if len(price_filtered) == 0:
            print("❌ 未找到符合价格区间的股票")
            return None
        
        # 2. 技术指标筛选
        price_filtered['涨跌幅_num'] = pd.to_numeric(price_filtered['涨跌幅'], errors='coerce')
        price_filtered['量比_num'] = pd.to_numeric(price_filtered['量比'], errors='coerce')
        price_filtered['换手率_num'] = pd.to_numeric(price_filtered['换手率'], errors='coerce')
        
        screened = price_filtered[
            (price_filtered['涨跌幅_num'] > 2) &           # 涨幅>2%
            (price_filtered['量比_num'] > 1.2) &           # 成交量放大20%
            (price_filtered['换手率_num'].between(0.5, 5))  # 换手率适中
        ].copy()
        
        print(f"✅ 技术指标筛选后: {len(screened)} 只")
        
        if len(screened) == 0:
            print("❌ 未筛选到符合条件的低价股")
            return None
        
        # 3. 计算综合评分
        scores = []
        for _, row in screened.iterrows():
            stock_data = {
                '代码': row['代码'],
                '名称': row['名称'],
                '最新价': row['最新价_num'],
                '涨跌幅': row['涨跌幅_num'],
                '量比': row['量比_num'],
                '市盈率': row['市盈率'],
                '市净率': row['市净率'],
                '股息率': row['股息率']
            }
            
            score_info = self.calculate_low_price_score(stock_data)
            scores.append(score_info)
        
        # 合并评分结果
        score_df = pd.DataFrame(scores)
        screened = pd.concat([screened.reset_index(drop=True), score_df], axis=1)
        
        # 4. 排序取前5
        screened = screened.sort_values('总评分', ascending=False)
        top_stocks = screened.head(5)
        
        return top_stocks
    
    def generate_low_price_report(self, top_stocks):
        """生成低价股报告"""
        
        report = []
        report.append(f"💰 低价股筛选报告（{self.price_range[0]}-{self.price_range[1]}元区间）")
        report.append("="*60)
        report.append(f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 热门行业分析
        report.append("🏆 低价股偏好行业")
        report.append("-"*40)
        for industry, info in sorted(self.hot_industries.items(), 
                                    key=lambda x: x[1]['热度'], reverse=True):
            report.append(f"{industry}: 热度{info['热度']}分 | {info['特点']}")
        report.append("")
        
        # 筛选结果
        report.append("🎯 优质低价股推荐（前5名）")
        report.append("-"*40)
        
        for idx, (_, row) in enumerate(top_stocks.iterrows(), 1):
            report.append(f"{idx}. {row['名称']}({row['代码']}) - {row['所属行业']}")
            report.append(f"   价格: {row['最新价']}元 | 涨幅: +{float(row['涨跌幅'])}%")
            report.append(f"   量比: {float(row['量比']):.1f}倍 | 换手率: {row['换手率']}%")
            report.append(f"   估值: PE={float(row['市盈率']):.1f} | PB={float(row['市净率']):.1f} | 股息率={row['股息率']}%")
            report.append(f"   综合评分: {row['总评分']:.1f}分")
            report.append(f"           价格分:{row['价格分']:.1f} | 技术分:{row['技术分']:.1f} | 估值分:{row['估值分']:.1f} | 行业分:{row['行业分']:.1f}")
            
            # 投资亮点
            highlights = []
            if float(row['最新价']) < 10:
                highlights.append("绝对低价")
            if float(row['市盈率']) < 8:
                highlights.append("低市盈率")
            if float(row['市净率']) < 1:
                highlights.append("破净股")
            if float(row['股息率']) > 5:
                highlights.append("高股息")
            if float(row['量比']) > 1.5:
                highlights.append("量能充沛")
            
            if highlights:
                report.append(f"   投资亮点: {' | '.join(highlights)}")
            
            # 操作建议（低价股通常有更高上涨空间）
            price = float(row['最新价'])
            
            # 低价股目标设定更积极
            if price < 10:
                target_multiplier = 1.15  # 15%目标
            elif price < 12:
                target_multiplier = 1.12  # 12%目标
            else:
                target_multiplier = 1.10  # 10%目标
            
            # 估值加成
            if float(row['市盈率']) < 8:
                target_multiplier *= 1.02  # 低PE加成
            if float(row['市净率']) < 1:
                target_multiplier *= 1.03  # 破净股加成
            
            entry_min = price * 0.99
            entry_max = price * 1.01
            target = price * target_multiplier
            stop_loss = price * 0.95  # 低价股止损放宽到5%
            
            report.append(f"   操作策略:")
            report.append(f"     - 入场区间: {entry_min:.2f}-{entry_max:.2f}元")
            report.append(f"     - 目标价位: {target:.2f}元（+{int((target_multiplier-1)*100)}%）")
            report.append(f"     - 止损价位: {stop_loss:.2f}元（-5%）")
            report.append(f"     - 建议仓位: 总资金15-20%（低价股可适当提高）")
            report.append("")
        
        # 低价股投资策略
        report.append("📈 低价股投资策略")
        report.append("-"*40)
        report.append("1. **价格优势**: 8-15元区间，上涨空间大")
        report.append("2. **估值安全**: 重点关注破净股、低市盈率股")
        report.append("3. **股息保护**: 高股息率提供下行保护")
        report.append("4. **流动性**: 适中换手率，进出方便")
        report.append("5. **风险控制**: 止损放宽至5%，给予更大波动空间")
        report.append("")
        
        report.append("⚠️ 风险提示")
        report.append("-"*40)
        report.append("1. 低价股波动性可能较大")
        report.append("2. 部分低价股基本面较弱")
        report.append("3. 需关注公司治理和财务健康")
        report.append("4. 避免过度追高，等待回调机会")
        
        return "\n".join(report)

def main():
    """主函数"""
    
    try:
        print("🚀 启动低价股筛选系统")
        print()
        
        # 创建筛选器
        screener = LowPriceStockScreener()
        
        # 筛选股票
        top_stocks = screener.screen_low_price_stocks()
        
        if top_stocks is not None:
            # 生成报告
            report = screener.generate_low_price_report(top_stocks)
            print(report)
            
            # 保存结果
            filename = f"/root/.openclaw/workspace/低价股筛选结果_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            top_stocks.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n💾 结果已保存: {filename}")
            
            # 保存报告
            report_filename = f"/root/.openclaw/workspace/低价股筛选报告_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 报告已保存: {report_filename}")
            
        else:
            print("❌ 未筛选到符合条件的低价股")
            
    except Exception as e:
        print(f"❌ 运行过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()