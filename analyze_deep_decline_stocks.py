#!/usr/bin/env python3
"""
分析A股市场中跌幅超过60%的股票，并评估其潜在升值空间
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

def get_all_a_stocks():
    """获取所有A股股票列表"""
    try:
        # 获取沪深京A股实时行情
        stock_df = ak.stock_zh_a_spot_em()
        print(f"获取到 {len(stock_df)} 只A股股票")
        return stock_df
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return None

def calculate_decline_percentage(stock_df):
    """计算每只股票的跌幅百分比"""
    # 需要获取历史数据来计算跌幅
    declined_stocks = []
    
    # 为了演示，我们使用当前价格和52周最高价来计算跌幅
    # 在实际应用中，应该获取更精确的历史数据
    
    for idx, row in stock_df.iterrows():
        try:
            code = row['代码']
            name = row['名称']
            current_price = float(row['最新价'])
            
            # 获取52周最高价（使用最高价作为近似）
            high_price = float(row['最高'])
            
            # 计算跌幅
            if high_price > 0:
                decline_pct = (high_price - current_price) / high_price * 100
                
                if decline_pct >= 60:  # 跌幅超过60%
                    stock_info = {
                        '代码': code,
                        '名称': name,
                        '最新价': current_price,
                        '52周最高': high_price,
                        '跌幅%': round(decline_pct, 2),
                        '市盈率': row['市盈率-动态'] if '市盈率-动态' in row else 'N/A',
                        '市净率': row['市净率'] if '市净率' in row else 'N/A',
                        '所属行业': row['所属行业'] if '所属行业' in row else 'N/A'
                    }
                    declined_stocks.append(stock_info)
                    
        except Exception as e:
            continue
    
    return declined_stocks

def analyze_potential(stocks_list):
    """分析股票的潜在升值空间"""
    potential_stocks = []
    
    for stock in stocks_list:
        # 评估升值潜力的标准
        score = 0
        
        # 1. 基本面分析
        try:
            pe = float(stock['市盈率']) if stock['市盈率'] != 'N/A' else 100
            pb = float(stock['市净率']) if stock['市净率'] != 'N/A' else 10
            
            # 低市盈率加分
            if pe < 20:
                score += 2
            elif pe < 30:
                score += 1
                
            # 低市净率加分
            if pb < 1:
                score += 3  # 破净股有较大安全边际
            elif pb < 2:
                score += 2
            elif pb < 3:
                score += 1
        except:
            pass
        
        # 2. 行业分析
        industry = stock['所属行业']
        growth_industries = ['新能源', '半导体', '医药', '人工智能', '云计算', '5G', '芯片']
        cyclical_industries = ['房地产', '建筑', '钢铁', '煤炭', '有色金属']
        
        if any(growth in industry for growth in growth_industries):
            score += 2  # 成长性行业
        elif any(cyclical in industry for cyclical in cyclical_industries):
            score += 1  # 周期性行业可能有反弹机会
        
        # 3. 价格水平
        current_price = stock['最新价']
        if current_price < 10:
            score += 1  # 低价股更容易反弹
        if current_price < 5:
            score += 1
        
        # 4. 跌幅深度
        decline = stock['跌幅%']
        if decline >= 70:
            score += 2  # 超跌严重，反弹空间大
        elif decline >= 60:
            score += 1
        
        # 计算潜在反弹空间
        # 假设能反弹到跌幅的一半位置
        target_price = stock['52周最高'] * (1 - decline/200)
        potential_return = (target_price - current_price) / current_price * 100
        
        stock['潜力评分'] = score
        stock['目标价'] = round(target_price, 2)
        stock['潜在涨幅%'] = round(potential_return, 2)
        
        # 只保留评分较高的股票
        if score >= 3:
            potential_stocks.append(stock)
    
    # 按潜力评分排序
    potential_stocks.sort(key=lambda x: x['潜力评分'], reverse=True)
    return potential_stocks

def get_detailed_analysis(stock_code):
    """获取股票的详细分析"""
    try:
        # 获取财务数据
        financial_df = ak.stock_financial_analysis_indicator(symbol=stock_code)
        
        # 获取资金流向
        fund_flow = ak.stock_individual_fund_flow(stock=stock_code, market="sh" if stock_code.startswith('6') else "sz")
        
        # 获取机构持仓
        institution_df = ak.stock_institution_hold_detail(symbol=stock_code)
        
        return {
            '财务指标': financial_df.tail(1).to_dict('records')[0] if not financial_df.empty else {},
            '资金流向': fund_flow.tail(1).to_dict('records')[0] if not fund_flow.empty else {},
            '机构持仓': institution_df.tail(1).to_dict('records')[0] if not institution_df.empty else {}
        }
    except Exception as e:
        print(f"获取详细分析失败 {stock_code}: {e}")
        return {}

def main():
    print("开始分析A股市场中跌幅超过60%的股票...")
    print("=" * 80)
    
    # 1. 获取所有A股
    stock_df = get_all_a_stocks()
    if stock_df is None:
        print("无法获取股票数据，请检查网络连接")
        return
    
    # 2. 计算跌幅超过60%的股票
    print("\n筛选跌幅超过60%的股票...")
    declined_stocks = calculate_decline_percentage(stock_df)
    print(f"找到 {len(declined_stocks)} 只跌幅超过60%的股票")
    
    # 3. 分析潜在升值空间
    print("\n分析潜在升值空间...")
    potential_stocks = analyze_potential(declined_stocks)
    
    # 4. 输出结果
    print(f"\n找到 {len(potential_stocks)} 只具有升值潜力的超跌股票:")
    print("=" * 80)
    
    for i, stock in enumerate(potential_stocks[:20], 1):  # 只显示前20只
        print(f"\n{i}. {stock['名称']} ({stock['代码']})")
        print(f"   当前价: {stock['最新价']}元 | 52周最高: {stock['52周最高']}元")
        print(f"   跌幅: {stock['跌幅%']}% | 市盈率: {stock['市盈率']} | 市净率: {stock['市净率']}")
        print(f"   行业: {stock['所属行业']}")
        print(f"   潜力评分: {stock['潜力评分']}/10 | 目标价: {stock['目标价']}元 | 潜在涨幅: {stock['潜在涨幅%']}%")
    
    # 5. 投资建议
    print("\n" + "=" * 80)
    print("投资建议:")
    print("1. 超跌股投资策略:")
    print("   - 关注基本面良好但受市场情绪拖累的股票")
    print("   - 优先选择行业龙头或细分领域领先者")
    print("   - 注意分散投资，控制单只股票仓位")
    
    print("\n2. 风险提示:")
    print("   - 超跌股可能存在基本面恶化风险")
    print("   - 需要仔细分析下跌原因")
    print("   - 建议分批建仓，设置止损位")
    
    print("\n3. 重点关注行业:")
    print("   - 新能源、半导体、医药等成长性行业")
    print("   - 周期性行业底部反转机会")
    print("   - 政策支持的新兴产业")
    
    # 6. 保存结果
    if potential_stocks:
        df = pd.DataFrame(potential_stocks)
        df.to_csv('deep_decline_potential_stocks.csv', index=False, encoding='utf-8-sig')
        print(f"\n结果已保存到: deep_decline_potential_stocks.csv")

if __name__ == "__main__":
    main()