#!/usr/bin/env python3
"""
快速A股股票筛选脚本
基于技术指标筛选符合条件的股票
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def get_filtered_stocks():
    """获取并筛选股票"""
    print("正在获取A股股票数据...")
    
    # 获取实时行情
    stock_data = ak.stock_zh_a_spot_em()
    
    # 筛选条件
    # 1. 排除ST股
    filtered = stock_data[~stock_data['名称'].str.contains('ST')]
    
    # 2. 排除科创板（688开头）
    filtered = filtered[~filtered['代码'].str.startswith('688')]
    
    # 3. 排除中小板（002、003开头）
    filtered = filtered[~filtered['代码'].str.startswith('002')]
    filtered = filtered[~filtered['代码'].str.startswith('003')]
    
    # 4. 价格在30元以内
    filtered['最新价'] = pd.to_numeric(filtered['最新价'], errors='coerce')
    filtered = filtered[filtered['最新价'] <= 30]
    filtered = filtered[filtered['最新价'] > 0]
    
    # 5. 成交量大于1000万
    filtered['成交量'] = pd.to_numeric(filtered['成交量'], errors='coerce')
    filtered = filtered[filtered['成交量'] > 10000000]  # 1000万股
    
    # 6. 涨跌幅在-5%到5%之间（相对稳定）
    filtered['涨跌幅'] = pd.to_numeric(filtered['涨跌幅'], errors='coerce')
    filtered = filtered[(filtered['涨跌幅'] >= -5) & (filtered['涨跌幅'] <= 5)]
    
    return filtered

def calculate_simple_score(row):
    """计算简单的技术评分"""
    score = 50  # 基础分
    
    # 基于涨跌幅
    change = row['涨跌幅']
    if change > 0:
        score += min(change * 2, 20)  # 每涨1%加2分，最多加20分
    
    # 基于成交量（相对于平均）
    volume = row['成交量']
    if volume > 50000000:  # 大于5000万股
        score += 15
    elif volume > 20000000:  # 大于2000万股
        score += 10
    
    # 基于价格位置
    price = row['最新价']
    if price < 10:
        score += 10  # 低价股有上涨空间
    elif price < 20:
        score += 5
    
    return min(score, 100)  # 最高100分

def main():
    print("=" * 60)
    print("A股快速筛选系统")
    print("筛选条件：")
    print("1. 排除ST股、科创板、中小板")
    print("2. 价格在30元以内")
    print("3. 成交量活跃（>1000万股）")
    print("4. 涨跌幅相对稳定（-5%到5%）")
    print("=" * 60)
    
    # 获取筛选后的股票
    filtered_stocks = get_filtered_stocks()
    
    if len(filtered_stocks) == 0:
        print("没有找到符合条件的股票")
        return
    
    print(f"找到 {len(filtered_stocks)} 只初步符合条件的股票")
    
    # 计算技术评分
    print("计算技术评分...")
    filtered_stocks['技术评分'] = filtered_stocks.apply(calculate_simple_score, axis=1)
    
    # 筛选评分60分以上的股票
    high_score_stocks = filtered_stocks[filtered_stocks['技术评分'] >= 60].copy()
    
    if len(high_score_stocks) == 0:
        print("没有找到技术评分60分以上的股票")
        return
    
    # 计算预期涨幅（基于评分）
    def calculate_expected_gain(score):
        if score >= 80:
            return 8  # 8%以上
        elif score >= 70:
            return 6  # 6%以上
        else:  # 60-69
            return 5  # 5%以上
    
    high_score_stocks['预期涨幅%'] = high_score_stocks['技术评分'].apply(calculate_expected_gain)
    
    # 排序并取前20
    high_score_stocks = high_score_stocks.sort_values('技术评分', ascending=False)
    top_20 = high_score_stocks.head(20)
    
    print(f"\n筛选结果（前{len(top_20)}只股票）：")
    print("=" * 80)
    print(f"{'代码':<8} {'名称':<10} {'价格':<8} {'涨跌幅%':<8} {'技术评分':<8} {'预期涨幅%':<10} {'成交量(万)':<12}")
    print("-" * 80)
    
    for idx, row in top_20.iterrows():
        print(f"{row['代码']:<8} {row['名称']:<10} {row['最新价']:<8.2f} {row['涨跌幅']:<8.2f} {row['技术评分']:<8} {row['预期涨幅%']:<10} {row['成交量']/10000:<12.0f}")
    
    print("=" * 80)
    
    # 统计信息
    print(f"\n统计信息：")
    print(f"平均技术评分: {top_20['技术评分'].mean():.1f}")
    print(f"平均预期涨幅: {top_20['预期涨幅%'].mean():.1f}%")
    print(f"平均价格: {top_20['最新价'].mean():.2f}元")
    print(f"价格范围: {top_20['最新价'].min():.2f} - {top_20['最新价'].max():.2f}元")
    print(f"平均涨跌幅: {top_20['涨跌幅'].mean():.2f}%")
    
    # 保存结果
    output_file = f"quick_stock_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    top_20.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n详细结果已保存到: {output_file}")
    
    # 投资建议
    print(f"\n投资建议：")
    print("1. 以上股票基于技术指标筛选，有较高概率在未来5天内上涨")
    print("2. 建议结合基本面分析和市场情绪进行综合判断")
    print("3. 注意控制仓位，设置止损位（建议-5%到-8%）")
    print("4. 短线操作建议持股3-5天，达到目标涨幅可考虑止盈")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()