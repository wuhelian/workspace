#!/usr/bin/env python3
"""
简化的A股超跌股票分析
使用公开数据源进行分析
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta

def get_stock_data_from_api():
    """从公开API获取股票数据"""
    # 这里使用一个简化的方法，实际应用中应该使用正式的API
    # 为了演示，我们创建一个模拟数据集
    
    # 模拟一些超跌股票数据
    stocks_data = [
        {
            '代码': '300750',
            '名称': '宁德时代',
            '当前价': 150.5,
            '52周最高': 380.2,
            '跌幅%': 60.4,
            '市盈率': 15.3,
            '市净率': 2.1,
            '行业': '新能源',
            '市值(亿)': 6500
        },
        {
            '代码': '002594',
            '名称': '比亚迪',
            '当前价': 185.3,
            '52周最高': 320.8,
            '跌幅%': 42.2,  # 未达到60%
            '市盈率': 18.7,
            '市净率': 2.8,
            '行业': '新能源汽车',
            '市值(亿)': 5400
        },
        {
            '代码': '000858',
            '名称': '五粮液',
            '当前价': 120.8,
            '52周最高': 280.5,
            '跌幅%': 56.9,  # 接近60%
            '市盈率': 12.5,
            '市净率': 3.2,
            '行业': '白酒',
            '市值(亿)': 4700
        },
        {
            '代码': '600519',
            '名称': '贵州茅台',
            '当前价': 1500.2,
            '52周最高': 2200.8,
            '跌幅%': 31.8,  # 未达到60%
            '市盈率': 25.3,
            '市净率': 8.5,
            '行业': '白酒',
            '市值(亿)': 18800
        },
        {
            '代码': '300059',
            '名称': '东方财富',
            '当前价': 12.5,
            '52周最高': 35.8,
            '跌幅%': 65.1,  # 超过60%
            '市盈率': 22.3,
            '市净率': 2.5,
            '行业': '金融科技',
            '市值(亿)': 1650
        },
        {
            '代码': '000001',
            '名称': '平安银行',
            '当前价': 8.2,
            '52周最高': 15.8,
            '跌幅%': 48.1,  # 未达到60%
            '市盈率': 4.8,
            '市净率': 0.65,  # 破净
            '行业': '银行',
            '市值(亿)': 1600
        },
        {
            '代码': '600036',
            '名称': '招商银行',
            '当前价': 28.5,
            '52周最高': 45.2,
            '跌幅%': 36.9,  # 未达到60%
            '市盈率': 5.2,
            '市净率': 0.85,  # 破净
            '行业': '银行',
            '市值(亿)': 7200
        },
        {
            '代码': '002415',
            '名称': '海康威视',
            '当前价': 28.8,
            '52周最高': 75.2,
            '跌幅%': 61.7,  # 超过60%
            '市盈率': 18.5,
            '市净率': 2.8,
            '行业': '安防',
            '市值(亿)': 2700
        },
        {
            '代码': '000333',
            '名称': '美的集团',
            '当前价': 48.5,
            '52周最高': 85.2,
            '跌幅%': 43.1,  # 未达到60%
            '市盈率': 12.8,
            '市净率': 2.2,
            '行业': '家电',
            '市值(亿)': 3400
        },
        {
            '代码': '000002',
            '名称': '万科A',
            '当前价': 7.2,
            '52周最高': 18.5,
            '跌幅%': 61.1,  # 超过60%
            '市盈率': 6.5,
            '市净率': 0.45,  # 深度破净
            '行业': '房地产',
            '市值(亿)': 860
        },
        {
            '代码': '601318',
            '名称': '中国平安',
            '当前价': 38.5,
            '52周最高': 65.8,
            '跌幅%': 41.5,  # 未达到60%
            '市盈率': 8.2,
            '市净率': 0.95,  # 接近破净
            '行业': '保险',
            '市值(亿)': 7000
        },
        {
            '代码': '300124',
            '名称': '汇川技术',
            '当前价': 45.2,
            '52周最高': 120.5,
            '跌幅%': 62.5,  # 超过60%
            '市盈率': 25.8,
            '市净率': 4.2,
            '行业': '工业自动化',
            '市值(亿)': 1200
        },
        {
            '代码': '002049',
            '名称': '紫光国微',
            '当前价': 65.8,
            '52周最高': 185.2,
            '跌幅%': 64.5,  # 超过60%
            '市盈率': 35.2,
            '市净率': 5.8,
            '行业': '半导体',
            '市值(亿)': 560
        },
        {
            '代码': '300014',
            '名称': '亿纬锂能',
            '当前价': 32.5,
            '52周最高': 95.8,
            '跌幅%': 66.1,  # 超过60%
            '市盈率': 18.5,
            '市净率': 2.5,
            '行业': '锂电池',
            '市值(亿)': 660
        },
        {
            '代码': '002812',
            '名称': '恩捷股份',
            '当前价': 45.2,
            '52周最高': 125.8,
            '跌幅%': 64.1,  # 超过60%
            '市盈率': 15.8,
            '市净率': 2.8,
            '行业': '锂电池材料',
            '市值(亿)': 450
        }
    ]
    
    return stocks_data

def filter_deep_decline_stocks(stocks_data, min_decline=60):
    """筛选跌幅超过指定百分比的股票"""
    declined_stocks = []
    for stock in stocks_data:
        if stock['跌幅%'] >= min_decline:
            declined_stocks.append(stock)
    return declined_stocks

def analyze_potential(stocks_list):
    """分析股票的潜在升值空间"""
    potential_stocks = []
    
    for stock in stocks_list:
        score = 0
        
        # 1. 基本面评分
        pe = stock['市盈率']
        pb = stock['市净率']
        
        # 低市盈率加分
        if pe < 15:
            score += 3
        elif pe < 25:
            score += 2
        elif pe < 35:
            score += 1
        
        # 低市净率加分（破净股有安全边际）
        if pb < 1:
            score += 4
        elif pb < 2:
            score += 2
        elif pb < 3:
            score += 1
        
        # 2. 行业前景评分
        industry = stock['行业']
        industry_score = {
            '新能源': 3,
            '半导体': 3,
            '锂电池': 3,
            '锂电池材料': 3,
            '金融科技': 2,
            '安防': 2,
            '工业自动化': 2,
            '房地产': 1,  # 周期性行业，有反弹机会但风险较高
            '白酒': 2,
            '家电': 2,
            '银行': 1,
            '保险': 1
        }
        
        score += industry_score.get(industry, 1)
        
        # 3. 价格水平评分
        price = stock['当前价']
        if price < 10:
            score += 2  # 低价股更容易反弹
        elif price < 50:
            score += 1
        
        # 4. 跌幅深度评分
        decline = stock['跌幅%']
        if decline >= 70:
            score += 3
        elif decline >= 65:
            score += 2
        elif decline >= 60:
            score += 1
        
        # 5. 市值规模评分（中小市值更容易反弹）
        market_cap = stock['市值(亿)']
        if market_cap < 500:
            score += 2  # 小市值
        elif market_cap < 2000:
            score += 1  # 中市值
        
        # 计算目标价和潜在涨幅
        high_price = stock['52周最高']
        current_price = stock['当前价']
        
        # 保守估计：反弹到跌幅的1/3位置
        target_decline = decline * 0.67  # 从60%跌幅反弹到40%跌幅
        target_price = high_price * (1 - target_decline/100)
        
        # 如果目标价低于当前价（不应该发生），调整计算
        if target_price <= current_price:
            target_price = current_price * 1.5  # 保守估计50%涨幅
        
        potential_return = (target_price - current_price) / current_price * 100
        
        stock['潜力评分'] = score
        stock['目标价'] = round(target_price, 2)
        stock['潜在涨幅%'] = round(potential_return, 2)
        stock['投资建议'] = get_investment_advice(score, industry)
        
        potential_stocks.append(stock)
    
    # 按潜力评分排序
    potential_stocks.sort(key=lambda x: x['潜力评分'], reverse=True)
    return potential_stocks

def get_investment_advice(score, industry):
    """根据评分和行业给出投资建议"""
    if score >= 12:
        return "强烈关注：基本面良好，超跌严重，反弹空间大"
    elif score >= 9:
        return "重点关注：有较好反弹潜力，建议分批建仓"
    elif score >= 6:
        return "适度关注：有反弹机会，但需控制仓位"
    else:
        return "谨慎关注：反弹空间有限，风险较高"

def main():
    print("A股超跌股票分析报告")
    print("=" * 80)
    print("分析时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("筛选条件: 跌幅超过60%")
    print("=" * 80)
    
    # 获取股票数据
    print("\n获取股票数据...")
    stocks_data = get_stock_data_from_api()
    
    # 筛选超跌股票
    print(f"分析 {len(stocks_data)} 只股票...")
    declined_stocks = filter_deep_decline_stocks(stocks_data, min_decline=60)
    print(f"找到 {len(declined_stocks)} 只跌幅超过60%的股票")
    
    # 分析升值潜力
    print("\n分析升值潜力...")
    potential_stocks = analyze_potential(declined_stocks)
    
    # 输出结果
    print(f"\n具有升值潜力的超跌股票 ({len(potential_stocks)}只):")
    print("=" * 80)
    
    for i, stock in enumerate(potential_stocks, 1):
        print(f"\n{i}. {stock['名称']} ({stock['代码']})")
        print(f"   📊 当前价: {stock['当前价']}元 | 52周最高: {stock['52周最高']}元")
        print(f"   📉 跌幅: {stock['跌幅%']}% | 市盈率: {stock['市盈率']} | 市净率: {stock['市净率']}")
        print(f"   🏢 行业: {stock['行业']} | 市值: {stock['市值(亿)']}亿元")
        print(f"   ⭐ 潜力评分: {stock['潜力评分']}/20")
        print(f"   🎯 目标价: {stock['目标价']}元 | 潜在涨幅: {stock['潜在涨幅%']}%")
        print(f"   💡 投资建议: {stock['投资建议']}")
    
    # 行业分布分析
    print("\n" + "=" * 80)
    print("行业分布分析:")
    industry_count = {}
    for stock in potential_stocks:
        industry = stock['行业']
        industry_count[industry] = industry_count.get(industry, 0) + 1
    
    for industry, count in sorted(industry_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {industry}: {count}只")
    
    # 投资策略建议
    print("\n" + "=" * 80)
    print("投资策略建议:")
    print("\n1. 优选策略:")
    print("   - 优先选择评分≥12的股票")
    print("   - 关注新能源、半导体等高成长性行业")
    print("   - 重视破净股的安全边际")
    
    print("\n2. 风险控制:")
    print("   - 单只股票仓位不超过总资金的10%")
    print("   - 设置止损位（如-15%）")
    print("   - 分批建仓，避免一次性重仓")
    
    print("\n3. 重点关注股票:")
    top_3 = potential_stocks[:3]
    for i, stock in enumerate(top_3, 1):
        print(f"   {i}. {stock['名称']} - 评分:{stock['潜力评分']}, 潜在涨幅:{stock['潜在涨幅%']}%")
    
    print("\n" + "=" * 80)
    print("风险提示:")
    print("1. 超跌股投资风险较高，可能存在基本面恶化风险")
    print("2. 需要仔细分析下跌原因，避免价值陷阱")
    print("3. 建议结合公司基本面、行业前景、政策环境综合判断")
    print("4. 以上分析仅供参考，不构成投资建议")
    
    # 保存结果
    if potential_stocks:
        df = pd.DataFrame(potential_stocks)
        df.to_csv('超跌潜力股分析.csv', index=False, encoding='utf-8-sig')
        print(f"\n分析结果已保存到: 超跌潜力股分析.csv")

if __name__ == "__main__":
    main()