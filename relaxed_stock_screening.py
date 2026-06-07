#!/usr/bin/env python3
"""
宽松条件A股股票筛选
放宽成交量要求，找到更多潜在标的
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def get_relaxed_filtered_stocks():
    """获取并筛选股票（宽松条件）"""
    print("正在获取A股股票数据...")
    
    # 获取实时行情
    stock_data = ak.stock_zh_a_spot_em()
    
    # 筛选条件（宽松版）
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
    
    # 5. 成交量大于100万股（放宽要求）
    filtered['成交量'] = pd.to_numeric(filtered['成交量'], errors='coerce')
    filtered = filtered[filtered['成交量'] > 1000000]  # 100万股
    
    # 6. 涨跌幅在-8%到8%之间（放宽要求）
    filtered['涨跌幅'] = pd.to_numeric(filtered['涨跌幅'], errors='coerce')
    filtered = filtered[(filtered['涨跌幅'] >= -8) & (filtered['涨跌幅'] <= 8)]
    
    return filtered

def calculate_enhanced_score(row):
    """计算增强版技术评分"""
    score = 50  # 基础分
    
    # 基于涨跌幅
    change = row['涨跌幅']
    if change > 0:
        score += min(change * 3, 25)  # 每涨1%加3分，最多加25分
    elif change < 0:
        score += max(change, -10)  # 每跌1%减1分，最多减10分
    
    # 基于成交量（相对于平均）
    volume = row['成交量']
    if volume > 20000000:  # 大于2000万股
        score += 20
    elif volume > 10000000:  # 大于1000万股
        score += 15
    elif volume > 5000000:  # 大于500万股
        score += 10
    
    # 基于价格位置
    price = row['最新价']
    if price < 5:
        score += 15  # 超低价股有更大上涨空间
    elif price < 10:
        score += 10
    elif price < 20:
        score += 5
    
    # 基于换手率（如果有）
    if '换手率' in row:
        turnover = pd.to_numeric(row['换手率'], errors='coerce')
        if not pd.isna(turnover):
            if turnover > 5:
                score += 10
            elif turnover > 3:
                score += 5
    
    return min(max(score, 0), 100)  # 限制在0-100分

def main():
    print("=" * 60)
    print("A股宽松条件筛选系统")
    print("筛选条件：")
    print("1. 排除ST股、科创板、中小板")
    print("2. 价格在30元以内")
    print("3. 成交量活跃（>100万股）")
    print("4. 涨跌幅相对稳定（-8%到8%）")
    print("=" * 60)
    
    # 获取筛选后的股票
    filtered_stocks = get_relaxed_filtered_stocks()
    
    if len(filtered_stocks) == 0:
        print("没有找到符合条件的股票")
        return
    
    print(f"找到 {len(filtered_stocks)} 只初步符合条件的股票")
    
    # 计算技术评分
    print("计算技术评分...")
    filtered_stocks['技术评分'] = filtered_stocks.apply(calculate_enhanced_score, axis=1)
    
    # 筛选评分60分以上的股票
    high_score_stocks = filtered_stocks[filtered_stocks['技术评分'] >= 60].copy()
    
    if len(high_score_stocks) == 0:
        print("没有找到技术评分60分以上的股票")
        # 显示评分最高的20只股票
        top_stocks = filtered_stocks.sort_values('技术评分', ascending=False).head(20)
        high_score_stocks = top_stocks
    
    # 计算预期涨幅（基于评分）
    def calculate_expected_gain(score):
        if score >= 80:
            return 8  # 8%以上
        elif score >= 70:
            return 6  # 6%以上
        elif score >= 60:
            return 5  # 5%以上
        else:
            return 3  # 3%以上（对于评分较低的）
    
    high_score_stocks['预期涨幅%'] = high_score_stocks['技术评分'].apply(calculate_expected_gain)
    
    # 排序并取前20
    high_score_stocks = high_score_stocks.sort_values('技术评分', ascending=False)
    top_20 = high_score_stocks.head(20)
    
    print(f"\n筛选结果（前{len(top_20)}只股票）：")
    print("=" * 100)
    print(f"{'代码':<8} {'名称':<10} {'价格':<8} {'涨跌幅%':<8} {'技术评分':<8} {'预期涨幅%':<10} {'成交量(万)':<12} {'换手率%':<10}")
    print("-" * 100)
    
    for idx, row in top_20.iterrows():
        turnover = row.get('换手率', 'N/A')
        if isinstance(turnover, (int, float)):
            turnover_str = f"{turnover:.2f}"
        else:
            turnover_str = str(turnover)
        
        print(f"{row['代码']:<8} {row['名称']:<10} {row['最新价']:<8.2f} {row['涨跌幅']:<8.2f} {row['技术评分']:<8.0f} {row['预期涨幅%']:<10} {row['成交量']/10000:<12.0f} {turnover_str:<10}")
    
    print("=" * 100)
    
    # 统计信息
    print(f"\n统计信息：")
    print(f"平均技术评分: {top_20['技术评分'].mean():.1f}")
    print(f"平均预期涨幅: {top_20['预期涨幅%'].mean():.1f}%")
    print(f"平均价格: {top_20['最新价'].mean():.2f}元")
    print(f"价格范围: {top_20['最新价'].min():.2f} - {top_20['最新价'].max():.2f}元")
    print(f"平均涨跌幅: {top_20['涨跌幅'].mean():.2f}%")
    
    # 按价格区间分组
    print(f"\n按价格区间分布：")
    price_bins = [0, 5, 10, 20, 30]
    price_labels = ['5元以下', '5-10元', '10-20元', '20-30元']
    
    top_20['价格区间'] = pd.cut(top_20['最新价'], bins=price_bins, labels=price_labels)
    price_dist = top_20['价格区间'].value_counts().sort_index()
    
    for price_range, count in price_dist.items():
        print(f"{price_range}: {count}只股票")
    
    # 保存结果
    output_file = f"relaxed_stock_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    top_20.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n详细结果已保存到: {output_file}")
    
    # 投资建议
    print(f"\n投资建议：")
    print("1. 以上股票基于技术指标筛选，评分越高上涨概率越大")
    print("2. 重点关注技术评分70分以上的股票")
    print("3. 建议结合个股基本面、行业趋势和市场情绪进行综合判断")
    print("4. 短线操作建议：")
    print("   - 技术评分≥80：目标涨幅8%，止损-8%")
    print("   - 技术评分70-79：目标涨幅6%，止损-7%")
    print("   - 技术评分60-69：目标涨幅5%，止损-6%")
    print("5. 建议持股周期3-5个交易日，达到目标可分批止盈")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()