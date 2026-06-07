#!/usr/bin/env python3
"""
高级版突破股筛选 - 加入北向资金监控和龙虎榜数据分析
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AdvancedStockScreener:
    """高级版股票筛选器"""
    
    def __init__(self):
        self.hot_industries = self.get_hot_industries()
        self.northbound_data = self.get_northbound_data()
        self.dragon_tiger_data = self.get_dragon_tiger_data()
        
    def get_hot_industries(self):
        """获取热门行业"""
        return {
            '人工智能': {'热度': 88, '资金流入': 52.1, '趋势': '爆发'},
            '白酒': {'热度': 85, '资金流入': 42.5, '趋势': '上升'},
            '半导体': {'热度': 82, '资金流入': 45.3, '趋势': '强势'},
            '银行': {'热度': 78, '资金流入': 38.2, '趋势': '稳定'},
            '消费': {'热度': 72, '资金流入': 35.1, '趋势': '上升'},
            '医药': {'热度': 65, '资金流入': 28.4, '趋势': '反弹'},
            '新能源': {'热度': 68, '资金流入': 32.7, '趋势': '震荡'}
        }
    
    def get_northbound_data(self):
        """获取北向资金数据（模拟）"""
        # 在实际环境中会从akshare获取：ak.stock_hsgt_north_net_flow_in_em()
        return {
            '600519': {'持股比例': 8.2, '增减持': 0.3, '连续买入': 3},
            '000858': {'持股比例': 6.5, '增减持': 0.2, '连续买入': 2},
            '600036': {'持股比例': 4.8, '增减持': 0.1, '连续买入': 1},
            '000001': {'持股比例': 3.2, '增减持': 0.05, '连续买入': 1},
            '600887': {'持股比例': 5.1, '增减持': 0.15, '连续买入': 2},
            '000333': {'持股比例': 4.3, '增减持': 0.08, '连续买入': 1},
            '002230': {'持股比例': 3.8, '增减持': 0.25, '连续买入': 3},
            '603501': {'持股比例': 2.9, '增减持': 0.18, '连续买入': 2},
            '601318': {'持股比例': 5.6, '增减持': 0.12, '连续买入': 1},
            '600030': {'持股比例': 2.3, '增减持': 0.05, '连续买入': 0}
        }
    
    def get_dragon_tiger_data(self):
        """获取龙虎榜数据（模拟）"""
        # 在实际环境中会从akshare获取：ak.stock_lhb_detail_em()
        return {
            '002230': {
                '上榜日期': '2026-04-01',
                '上榜原因': '日涨幅偏离值达7%',
                '买入金额': 3.8,
                '卖出金额': 1.2,
                '净买入': 2.6,
                '机构席位': 2,
                '游资席位': 3,
                '热度': 85
            },
            '603501': {
                '上榜日期': '2026-04-01',
                '上榜原因': '日换手率达20%',
                '买入金额': 2.5,
                '卖出金额': 1.8,
                '净买入': 0.7,
                '机构席位': 1,
                '游资席位': 2,
                '热度': 72
            },
            '600519': {
                '上榜日期': '2026-03-31',
                '上榜原因': '连续三个交易日内涨幅偏离值累计20%',
                '买入金额': 5.2,
                '卖出金额': 2.1,
                '净买入': 3.1,
                '机构席位': 3,
                '游资席位': 2,
                '热度': 88
            },
            '000858': {
                '上榜日期': '2026-03-31',
                '上榜原因': '日振幅值达15%',
                '买入金额': 2.8,
                '卖出金额': 1.5,
                '净买入': 1.3,
                '机构席位': 2,
                '游资席位': 1,
                '热度': 78
            }
        }
    
    def analyze_northbound_signal(self, stock_code):
        """分析北向资金信号"""
        if stock_code in self.northbound_data:
            data = self.northbound_data[stock_code]
            
            # 评分逻辑
            score = 0
            signals = []
            
            # 持股比例评分
            if data['持股比例'] > 5:
                score += 25
                signals.append(f"北向重仓({data['持股比例']}%)")
            elif data['持股比例'] > 3:
                score += 15
                signals.append(f"北向中度持仓({data['持股比例']}%)")
            else:
                score += 5
                signals.append(f"北向轻仓({data['持股比例']}%)")
            
            # 增减持评分
            if data['增减持'] > 0.2:
                score += 20
                signals.append(f"北向大幅增持(+{data['增减持']}%)")
            elif data['增减持'] > 0.1:
                score += 15
                signals.append(f"北向增持(+{data['增减持']}%)")
            elif data['增减持'] > 0:
                score += 10
                signals.append(f"北向小幅增持(+{data['增减持']}%)")
            else:
                score += 5
                signals.append("北向持平或减持")
            
            # 连续买入评分
            if data['连续买入'] >= 3:
                score += 15
                signals.append(f"北向连续{data['连续买入']}日净买入")
            elif data['连续买入'] >= 2:
                score += 10
                signals.append(f"北向连续{data['连续买入']}日净买入")
            elif data['连续买入'] >= 1:
                score += 5
                signals.append("北向近期有买入")
            
            return {
                '北向评分': min(score, 50),  # 最高50分
                '北向信号': ' | '.join(signals),
                '持股比例': data['持股比例'],
                '增减持': data['增减持'],
                '连续买入': data['连续买入']
            }
        else:
            return {
                '北向评分': 10,
                '北向信号': '暂无北向数据',
                '持股比例': 0,
                '增减持': 0,
                '连续买入': 0
            }
    
    def analyze_dragon_tiger_signal(self, stock_code):
        """分析龙虎榜信号"""
        if stock_code in self.dragon_tiger_data:
            data = self.dragon_tiger_data[stock_code]
            
            # 评分逻辑
            score = 0
            signals = []
            
            # 净买入金额评分
            if data['净买入'] > 2:
                score += 25
                signals.append(f"龙虎榜大幅净买入{data['净买入']}亿")
            elif data['净买入'] > 1:
                score += 20
                signals.append(f"龙虎榜净买入{data['净买入']}亿")
            elif data['净买入'] > 0:
                score += 15
                signals.append(f"龙虎榜小幅净买入{data['净买入']}亿")
            else:
                score += 5
                signals.append("龙虎榜净卖出")
            
            # 机构席位评分
            if data['机构席位'] >= 3:
                score += 15
                signals.append(f"{data['机构席位']}家机构买入")
            elif data['机构席位'] >= 2:
                score += 12
                signals.append(f"{data['机构席位']}家机构买入")
            elif data['机构席位'] >= 1:
                score += 8
                signals.append(f"{data['机构席位']}家机构买入")
            
            # 游资席位评分
            if data['游资席位'] >= 3:
                score += 10
                signals.append(f"{data['游资席位']}路游资参与")
            elif data['游资席位'] >= 2:
                score += 7
                signals.append(f"{data['游资席位']}路游资参与")
            elif data['游资席位'] >= 1:
                score += 4
                signals.append(f"{data['游资席位']}路游资参与")
            
            # 上榜原因评分
            if '涨幅偏离' in data['上榜原因']:
                score += 10
                signals.append("涨幅异动上榜")
            elif '换手率' in data['上榜原因']:
                score += 8
                signals.append("高换手上榜")
            elif '振幅' in data['上榜原因']:
                score += 6
                signals.append("振幅异动上榜")
            
            return {
                '龙虎榜评分': min(score, 50),  # 最高50分
                '龙虎榜信号': ' | '.join(signals),
                '上榜日期': data['上榜日期'],
                '上榜原因': data['上榜原因'],
                '净买入': data['净买入'],
                '机构席位': data['机构席位'],
                '游资席位': data['游资席位'],
                '龙虎榜热度': data['热度']
            }
        else:
            return {
                '龙虎榜评分': 5,
                '龙虎榜信号': '近期未上龙虎榜',
                '上榜日期': '无',
                '上榜原因': '无',
                '净买入': 0,
                '机构席位': 0,
                '游资席位': 0,
                '龙虎榜热度': 0
            }
    
    def get_stock_industry(self, stock_code, stock_name):
        """获取股票所属行业"""
        industry_map = {
            '600519': '白酒', '000858': '白酒',
            '600036': '银行', '000001': '银行',
            '600887': '消费', '000333': '消费',
            '002230': '人工智能', '603501': '半导体',
            '601318': '保险', '600030': '证券',
            '600276': '医药', '000538': '医药',
            '300750': '新能源', '002594': '新能源'
        }
        
        if stock_code in industry_map:
            return industry_map[stock_code]
        
        name_lower = stock_name.lower()
        if any(keyword in name_lower for keyword in ['酒', '茅台', '五粮液']):
            return '白酒'
        elif any(keyword in name_lower for keyword in ['银行', '招行', '平安']):
            return '银行'
        elif any(keyword in name_lower for keyword in ['消费', '食品', '饮料', '伊利']):
            return '消费'
        elif any(keyword in name_lower for keyword in ['人工智能', 'AI', '智能', '讯飞']):
            return '人工智能'
        elif any(keyword in name_lower for keyword in ['半导体', '芯片', '韦尔']):
            return '半导体'
        elif any(keyword in name_lower for keyword in ['医药', '药', '生物', '医疗']):
            return '医药'
        elif any(keyword in name_lower for keyword in ['新能源', '电池', '光伏', '宁德']):
            return '新能源'
        else:
            return '其他'
    
    def get_fund_flow_data(self, stock_code):
        """获取资金流向数据"""
        flow_data = {
            '600519': {'主力净流入': 2.8, '超大单': 1.5},
            '000858': {'主力净流入': 1.5, '超大单': 0.8},
            '600036': {'主力净流入': 1.2, '超大单': 0.6},
            '000001': {'主力净流入': 0.8, '超大单': 0.4},
            '600887': {'主力净流入': 0.9, '超大单': 0.5},
            '000333': {'主力净流入': 0.7, '超大单': 0.3},
            '002230': {'主力净流入': 1.8, '超大单': 1.2},
            '603501': {'主力净流入': 1.3, '超大单': 0.8},
            '601318': {'主力净流入': 1.1, '超大单': 0.6},
            '600030': {'主力净流入': 0.6, '超大单': 0.3}
        }
        
        if stock_code in flow_data:
            return flow_data[stock_code]
        else:
            return {'主力净流入': 0.5, '超大单': 0.2}
    
    def calculate_comprehensive_score(self, stock_data):
        """计算综合评分（高级版）"""
        
        # 基础技术指标（40%）
        tech_score = (
            min(stock_data['涨跌幅'] * 2, 24) +          # 涨幅，最高24分
            min((stock_data['量比'] - 1) * 15, 12) +     # 量比，最高12分
            min(stock_data['换手率'] * 2, 8)             # 换手率，最高8分
        ) * 0.4  # 技术指标占40%
        
        # 资金流向指标（20%）
        flow_data = self.get_fund_flow_data(stock_data['代码'])
        flow_score = (
            min(flow_data['主力净流入'] * 8, 12) +       # 主力净流入，最高12分
            min(flow_data['超大单'] * 10, 8)             # 超大单，最高8分
        ) * 0.2  # 资金流向占20%
        
        # 行业轮动指标（15%）
        industry = self.get_stock_industry(stock_data['代码'], stock_data['名称'])
        if industry in self.hot_industries:
            industry_score = self.hot_industries[industry]['热度'] * 0.15  # 行业热度占15%
        else:
            industry_score = 50 * 0.15
        
        # 北向资金指标（15%）
        northbound = self.analyze_northbound_signal(stock_data['代码'])
        northbound_score = northbound['北向评分'] * 0.15
        
        # 龙虎榜指标（10%）
        dragon_tiger = self.analyze_dragon_tiger_signal(stock_data['代码'])
        dragon_tiger_score = dragon_tiger['龙虎榜评分'] * 0.10
        
        total_score = tech_score + flow_score + industry_score + northbound_score + dragon_tiger_score
        
        return {
            '总评分': total_score,
            '技术分': tech_score,
            '资金分': flow_score,
            '行业分': industry_score,
            '北向分': northbound_score,
            '龙虎榜分': dragon_tiger_score,
            '所属行业': industry,
            '北向信号': northbound['北向信号'],
            '龙虎榜信号': dragon_tiger['龙虎榜信号']
        }
    
    def screen_stocks(self, stock_list):
        """筛选股票"""
        
        print("🚀 开始高级版筛选（北向资金+龙虎榜数据）")
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
                '量比