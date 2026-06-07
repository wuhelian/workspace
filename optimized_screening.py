#!/usr/bin/env python3
"""
优化版突破股筛选 - 加入行业轮动和资金流向
"""

import pandas as pd
import numpy as np
from datetime import datetime

class OptimizedStockScreener:
    """优化版股票筛选器"""
    
    def __init__(self):
        self.hot_industries = self.get_hot_industries()
        self.industry_weights = self.calculate_industry_weights()
        
    def get_hot_industries(self):
        """获取热门行业（模拟数据）"""
        # 在实际环境中会从akshare获取行业板块数据
        return {
            '白酒': {'热度': 85, '资金流入': 42.5, '趋势': '上升'},
            '银行': {'热度': 78, '资金流入': 38.2, '趋势': '稳定'},
            '消费': {'热度': 72, '资金流入': 35.1, '趋势': '上升'},
            '医药': {'热度': 65, '资金流入': 28.4, '趋势': '反弹'},
            '半导体': {'热度': 82, '资金流入': 45.3, '趋势': '强势'},
            '新能源': {'热度': 68, '资金流入': 32.7, '趋势': '震荡'},
            '人工智能': {'热度': 88, '资金流入': 52.1, '趋势': '爆发'}
        }
    
    def calculate_industry_weights(self):
        """计算行业权重"""
        total_heat = sum(info['热度'] for info in self.hot_industries.values())
        weights = {}
        for industry, info in self.hot_industries.items():
            weights[industry] = info['热度'] / total_heat
        return weights
    
    def get_stock_industry(self, stock_code, stock_name):
        """获取股票所属行业（模拟）"""
        # 在实际环境中会从数据库或API获取
        industry_map = {
            '600519': '白酒', '000858': '白酒', '600809': '白酒',
            '600036': '银行', '000001': '银行', '601398': '银行',
            '600887': '消费', '000333': '消费', '000651': '消费',
            '600276': '医药', '000538': '医药', '600196': '医药',
            '603501': '半导体', '688981': '半导体', '002371': '半导体',
            '300750': '新能源', '002594': '新能源', '601012': '新能源',
            '002230': '人工智能', '300496': '人工智能', '603019': '人工智能'
        }
        
        # 尝试通过代码匹配
        if stock_code in industry_map:
            return industry_map[stock_code]
        
        # 尝试通过名称关键词匹配
        name_lower = stock_name.lower()
        if any(keyword in name_lower for keyword in ['酒', '茅台', '五粮液', '泸州']):
            return '白酒'
        elif any(keyword in name_lower for keyword in ['银行', '农商', '招行', '平安']):
            return '银行'
        elif any(keyword in name_lower for keyword in ['消费', '食品', '饮料', '伊利']):
            return '消费'
        elif any(keyword in name_lower for keyword in ['医药', '药', '生物', '医疗']):
            return '医药'
        elif any(keyword in name_lower for keyword in ['半导体', '芯片', '集成电路']):
            return '半导体'
        elif any(keyword in name_lower for keyword in ['新能源', '电池', '光伏', '风电']):
            return '新能源'
        elif any(keyword in name_lower for keyword in ['人工智能', 'AI', '智能', '科技']):
            return '人工智能'
        else:
            return '其他'
    
    def get_fund_flow_data(self, stock_code):
        """获取资金流向数据（模拟）"""
        # 在实际环境中会从akshare获取资金流向数据
        flow_data = {
            '600519': {'主力净流入': 2.8, '超大单': 1.5, '大单': 0.8, '中单': 0.3, '小单': -0.2},
            '000858': {'主力净流入': 1.5, '超大单': 0.8, '大单': 0.4, '中单': 0.2, '小单': -0.1},
            '600036': {'主力净流入': 1.2, '超大单': 0.6, '大单': 0.3, '中单': 0.2, '小单': -0.1},
            '000001': {'主力净流入': 0.8, '超大单': 0.4, '大单': 0.2, '中单': 0.1, '小单': -0.1},
            '600887': {'主力净流入': 0.9, '超大单': 0.5, '大单': 0.2, '中单': 0.1, '小单': -0.1},
            '000333': {'主力净流入': 0.7, '超大单': 0.3, '大单': 0.2, '中单': 0.1, '小单': -0.1},
            '601318': {'主力净流入': 1.1, '超大单': 0.6, '大单': 0.3, '中单': 0.1, '小单': -0.1},
            '600030': {'主力净流入': 0.6, '超大单': 0.3, '大单': 0.1, '中单': 0.1, '小单': -0.1}
        }
        
        if stock_code in flow_data:
            return flow_data[stock_code]
        else:
            # 默认值
            return {'主力净流入': 0.5, '超大单': 0.2, '大单': 0.1, '中单': 0.1, '小单': -0.1}
    
    def calculate_comprehensive_score(self, stock_data):
        """计算综合评分（优化版）"""
        
        # 基础技术指标（50%）
        tech_score = (
            min(stock_data['涨跌幅'] * 2, 30) +          # 涨幅，最高30分
            min((stock_data['量比'] - 1) * 20, 20) +     # 量比，最高20分
            min(stock_data['换手率'] * 2, 10)            # 换手率，最高10分
        ) * 0.5  # 技术指标占50%
        
        # 资金流向指标（30%）
        flow_data = self.get_fund_flow_data(stock_data['代码'])
        flow_score = (
            min(flow_data['主力净流入'] * 10, 20) +      # 主力净流入，最高20分
            min(flow_data['超大单'] * 15, 10)            # 超大单，最高10分
        ) * 0.3  # 资金流向占30%
        
        # 行业轮动指标（20%）
        industry = self.get_stock_industry(stock_data['代码'], stock_data['名称'])
        if industry in self.hot_industries:
            industry_score = self.hot_industries[industry]['热度'] * 0.2  # 行业热度占20%
        else:
            industry_score = 50 * 0.2  # 默认50分
        
        total_score = tech_score + flow_score + industry_score
        
        return {
            '总评分': total_score,
            '技术分': tech_score,
            '资金分': flow_score,
            '行业分': industry_score,
            '所属行业': industry
        }
    
    def screen_stocks(self, stock_list):
        """筛选股票"""
        
        print("🎯 开始优化版筛选（加入行业轮动和资金流向）")
        print("="*60)
        
        # 转换为DataFrame
        df = pd.DataFrame(stock_list)
        
        print(f"📊 初始股票池: {len(df)} 只股票")
        
        # 1. 主板筛选
        df = df[df['代码'].str.startswith(('60', '00'))]
        print(f"✅ 主板筛选后: {len(df)} 只")
        
        # 2. 技术指标筛选
        df['涨跌幅_num'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
        df['量比_num'] = pd.to_numeric(df['量比'], errors='coerce')
        df['换手率_num'] = pd.to_numeric(df['换手率'], errors='coerce')
        df['最新价_num'] = pd.to_numeric(df['最新价'], errors='coerce')
        df['振幅_num'] = pd.to_numeric(df['振幅'], errors='coerce')
        
        screened = df[
            (df['涨跌幅_num'] > 5) &           # 5日涨幅>5%
            (df['量比_num'] > 1.2) &           # 成交量放大20%
            (df['换手率_num'].between(0.5, 5)) & # 换手率适中
            (df['最新价_num'] < 200) &         # 股价低于200元
            (df['振幅_num'] < 6)               # 振幅小于6%
        ].copy()
        
        print(f"✅ 技术指标筛选后: {len(screened)} 只")
        
        if len(screened) == 0:
            print("❌ 未筛选到符合条件的股票")
            return None
        
        # 3. 计算综合评分
        scores = []
        for _, row in screened.iterrows():
            stock_data = {
                '代码': row['代码'],
                '名称': row['名称'],
                '涨跌幅': row['涨跌幅_num'],
                '量比': row['量比_num'],
                '换手率': row['换手率_num']
            }
            
            score_info = self.calculate_comprehensive_score(stock_data)
            scores.append(score_info)
        
        # 合并评分结果
        score_df = pd.DataFrame(scores)
        screened = pd.concat([screened.reset_index(drop=True), score_df], axis=1)
        
        # 4. 排序取前5
        screened = screened.sort_values('总评分', ascending=False)
        top_stocks = screened.head(5)
        
        return top_stocks
    
    def generate_analysis_report(self, top_stocks):
        """生成分析报告"""
        
        report = []
        report.append("📈 优化版突破股筛选报告")
        report.append("="*60)
        report.append(f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 热门行业分析
        report.append("🏆 当前热门行业分析")
        report.append("-"*40)
        for industry, info in sorted(self.hot_industries.items(), 
                                    key=lambda x: x[1]['热度'], reverse=True)[:5]:
            report.append(f"{industry}: 热度{info['热度']}分 | 资金流入{info['资金流入']}亿 | 趋势:{info['趋势']}")
        report.append("")
        
        # 筛选结果
        report.append("🎯 优化筛选结果（前5名）")
        report.append("-"*40)
        
        for idx, (_, row) in enumerate(top_stocks.iterrows(), 1):
            report.append(f"{idx}. {row['名称']}({row['代码']}) - {row['所属行业']}")
            report.append(f"   最新价: {row['最新价']}元 | 5日涨幅: +{float(row['涨跌幅'])}%")
            report.append(f"   量比: {float(row['量比']):.1f}倍 | 换手率: {row['换手率']}%")
            
            # 资金流向分析
            flow_data = self.get_fund_flow_data(row['代码'])
            report.append(f"   资金流向: 主力净流入{flow_data['主力净流入']}亿")
            report.append(f"           超大单:{flow_data['超大单']}亿 | 大单:{flow_data['大单']}亿")
            
            # 评分分析
            report.append(f"   综合评分: {row['总评分']:.1f}分")
            report.append(f"           技术:{row['技术分']:.1f} | 资金:{row['资金分']:.1f} | 行业:{row['行业分']:.1f}")
            
            # 操作建议
            price = float(row['最新价'])
            industry_info = self.hot_industries.get(row['所属行业'], {'热度': 50, '趋势': '中性'})
            
            if industry_info['热度'] > 80:
                target_multiplier = 1.10  # 热门行业目标更高
            elif industry_info['热度'] > 70:
                target_multiplier = 1.08
            else:
                target_multiplier = 1.06
            
            entry_min = price * 0.99
            entry_max = price * 1.01
            target = price * target_multiplier
            stop_loss = price * 0.97
            
            report.append(f"   操作策略:")
            report.append(f"     - 入场区间: {entry_min:.2f}-{entry_max:.2f}元")
            report.append(f"     - 目标价位: {target:.2f}元（+{int((target_multiplier-1)*100)}%）")
            report.append(f"     - 止损价位: {stop_loss:.2f}元（-3%）")
            
            # 行业轮动建议
            if industry_info['趋势'] == '上升' or industry_info['趋势'] == '强势':
                industry_advice = "行业处于上升趋势，可适当提高仓位"
            elif industry_info['趋势'] == '爆发':
                industry_advice = "行业处于爆发期，重点关注"
            else:
                industry_advice = "行业趋势中性，按正常仓位操作"
            
            report.append(f"     - 行业建议: {industry_advice}")
            report.append("")
        
        # 资金流向总结
        report.append("💰 资金流向特征分析")
        report.append("-"*40)
        
        total_main_flow = sum(self.get_fund_flow_data(row['代码'])['主力净流入'] 
                            for _, row in top_stocks.iterrows())
        avg_main_flow = total_main_flow / len(top_stocks)
        
        report.append(f"平均主力净流入: {avg_main_flow:.2f}亿元")
        
        if avg_main_flow > 1.0:
            report.append("资金面: 非常强势，大资金积极介入")
        elif avg_main_flow > 0.5:
            report.append("资金面: 较为强势，资金关注度较高")
        else:
            report.append("资金面: 一般，需关注后续资金变化")
        
        report.append("")
        
        # 行业分布
        report.append("🏭 行业分布情况")
        report.append("-"*40)
        
        industry_counts = top_stocks['所属行业'].value_counts()
        for industry, count in industry_counts.items():
            industry_info = self.hot_industries.get(industry, {'热度': 50})
            report.append(f"{industry}: {count}只股票 | 行业热度: {industry_info['热度']}分")
        
        report.append("")
        report.append("📊 筛选标准总结")
        report.append("-"*40)
        report.append("1. 技术指标（50%）：涨幅>5%，量比>1.2，换手率0.5-5%")
        report.append("2. 资金流向（30%）：主力净流入，超大单占比")
        report.append("3. 行业轮动（20%）：行业热度，趋势判断")
        report.append("4. 风险控制：股价<200元，振幅<6%，明确止损")
        
        return "\n".join(report)

def main():
    """主函数"""
    
    # 模拟股票数据
    mock_stocks = [
        {'代码': '600519', '名称': '贵州茅台', '最新价': '1685.00', '涨跌幅': '8.3', '量比': '1.8', '换手率': '0.8', '振幅': '3.2'},
        {'代码': '000858', '名称': '五粮液', '最新价': '145.80', '涨跌幅': '6.5', '量比': '1.5', '换手率': '1.2', '振幅': '4.1'},
        {'代码': '600036', '名称': '招商银行', '最新价': '32.45', '涨跌幅': '5.8', '量比': '1.3', '换手率': '0.9', '振幅': '2.8'},
        {'代码': '000001', '名称': '平安银行', '最新价': '10.85', '涨跌幅': '4.9', '量比': '1.1', '换手率': '1.5', '振幅': '3.5'},
        {'代码': '600887', '名称': '伊利股份', '最新价': '28.90', '涨跌幅': '5.5', '量比': '1.4', '换手率': '1.8', '振幅': '3.1'},
        {'代码': '601318', '名称': '中国平安', '最新价': '45.20', '涨跌幅': '3.8', '量比': '1.2', '换手率': '0.7', '振幅': '2.5'},
        {'代码': '600030', '名称': '中信证券', '最新价': '22.80', '涨跌幅': '4.2', '量比': '1.0', '换手率': '1.1', '振幅': '3.2'},
        {'代码': '000333', '名称': '美的集团', '最新价': '58.90', '涨跌幅': '5.1', '量比': '1.3', '换手率': '0.9', '振幅': '2.9'},
        {'代码': '002230', '名称': '科大讯飞', '最新价': '45.60', '涨跌幅': '7.8', '量比': '2.1', '换手率': '3.2', '振幅': '5.8'},
        {'代码': '603501', '名称': '韦尔股份', '最新价': '85.30', '涨跌幅': '6.9', '量比': '1.9', '换手率': '2.5', '振幅': '4.7'},
        {'代码': '300750', '名称': '宁德时代', '最新价': '185.60', '涨跌幅': '7.2', '量比': '2.1', '换手率': '3.2', '振幅': '5.8'},
        {'代码': '002594', '名称': '比亚迪', '最新价': '245.30', '涨跌幅': '6.8', '量比': '1.9', '换手率': '2.1', '振幅': '4.9'},
        {'代码': '600276', '名称': '恒瑞医药', '最新价': '38.90', '涨跌幅': '4.5', '量比': '1.2', '换手率': '1.3', '振幅': '3.2'},
        {'代码': '000538', '名称': '云南白药', '最新价': '52.40', '涨跌幅': '3.9', '量比': '1.1', '换手率': '0.9', '振幅': '2.8'}
    ]
    
    try:
        print("🚀 开始优化版筛选测试")
        print()
        
        # 创建筛选器
        screener = OptimizedStockScreener()
        
        # 筛选股票
        top_stocks = screener.screen_stocks(mock_stocks)
        
        if top_stocks is not None:
            # 生成报告
            report = screener.generate_analysis_report(top_stocks)
            print(report)
            
            # 保存结果
            filename = f"/root/.openclaw/workspace/优化筛选结果_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            top_stocks.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n💾 结果已保存: {filename}")
            
            # 保存报告
            report_filename = f"/root/.openclaw/workspace/优化筛选报告_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 报告已保存: {report_filename}")
            
        else:
            print("❌ 未筛选到符合条件的股票")
            
    except Exception as e:
        print(f"❌ 运行过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()