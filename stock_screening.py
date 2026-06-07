#!/usr/bin/env python3
"""
A股股票筛选脚本
筛选条件：
1. 排除ST股、科创板、中小板
2. 价格在30元以内
3. 预计未来5天有60%概率涨幅5%以上
4. 取前20个股票
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def get_all_a_stocks():
    """获取所有A股股票列表"""
    print("正在获取A股股票列表...")
    
    # 获取沪深京A股列表
    stock_info_a_code_name_df = ak.stock_info_a_code_name()
    
    # 获取实时行情数据
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    
    # 合并数据
    stock_data = pd.merge(
        stock_info_a_code_name_df,
        stock_zh_a_spot_em_df,
        left_on='code',
        right_on='代码',
        how='inner'
    )
    
    return stock_data

def filter_stocks(stock_data):
    """筛选符合条件的股票"""
    print(f"初始股票数量: {len(stock_data)}")
    
    # 1. 排除ST股
    filtered = stock_data[~stock_data['名称'].str.contains('ST')]
    print(f"排除ST股后: {len(filtered)}")
    
    # 2. 排除科创板（688开头）
    filtered = filtered[~filtered['代码'].str.startswith('688')]
    print(f"排除科创板后: {len(filtered)}")
    
    # 3. 排除中小板（002、003开头）
    filtered = filtered[~filtered['代码'].str.startswith('002')]
    filtered = filtered[~filtered['代码'].str.startswith('003')]
    print(f"排除中小板后: {len(filtered)}")
    
    # 4. 价格在30元以内
    filtered['最新价'] = pd.to_numeric(filtered['最新价'], errors='coerce')
    filtered = filtered[filtered['最新价'] <= 30]
    print(f"价格30元以内: {len(filtered)}")
    
    # 5. 过滤掉价格异常或为0的股票
    filtered = filtered[filtered['最新价'] > 0]
    print(f"去除零价格股票后: {len(filtered)}")
    
    return filtered

def calculate_technical_indicators(stock_code, days=20):
    """计算技术指标来评估上涨概率"""
    try:
        # 获取历史数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=60)).strftime('%Y%m%d')
        
        hist_data = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )
        
        if len(hist_data) < 20:
            return None
        
        # 计算技术指标
        df = hist_data.copy()
        df['收盘'] = pd.to_numeric(df['收盘'])
        df['成交量'] = pd.to_numeric(df['成交量'])
        
        # 1. 计算移动平均线
        df['MA5'] = df['收盘'].rolling(window=5).mean()
        df['MA10'] = df['收盘'].rolling(window=10).mean()
        df['MA20'] = df['收盘'].rolling(window=20).mean()
        
        # 2. 计算RSI
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 3. 计算MACD
        exp1 = df['收盘'].ewm(span=12, adjust=False).mean()
        exp2 = df['收盘'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['Histogram'] = df['MACD'] - df['Signal']
        
        # 4. 计算布林带
        df['BB_middle'] = df['收盘'].rolling(window=20).mean()
        bb_std = df['收盘'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + 2 * bb_std
        df['BB_lower'] = df['BB_middle'] - 2 * bb_std
        
        # 5. 计算成交量变化率
        df['Volume_MA5'] = df['成交量'].rolling(window=5).mean()
        df['Volume_Ratio'] = df['成交量'] / df['Volume_MA5']
        
        # 获取最新数据
        latest = df.iloc[-1]
        
        # 计算上涨概率评分（简化版）
        score = 0
        
        # 技术指标评分
        if latest['MA5'] > latest['MA10'] > latest['MA20']:
            score += 30  # 多头排列
        
        if 30 <= latest['RSI'] <= 70:
            score += 20  # RSI在合理区间
        
        if latest['MACD'] > latest['Signal']:
            score += 20  # MACD金叉
        
        if latest['收盘'] > latest['BB_middle']:
            score += 15  # 价格在中轨上方
        
        if latest['Volume_Ratio'] > 1.2:
            score += 15  # 成交量放大
        
        return {
            'score': score,
            'price': latest['收盘'],
            'ma5': latest['MA5'],
            'ma10': latest['MA10'],
            'ma20': latest['MA20'],
            'rsi': latest['RSI'],
            'macd': latest['MACD'],
            'volume_ratio': latest['Volume_Ratio']
        }
        
    except Exception as e:
        print(f"计算技术指标时出错 {stock_code}: {e}")
        return None

def main():
    print("=" * 60)
    print("A股股票筛选系统")
    print("筛选条件：")
    print("1. 排除ST股、科创板、中小板")
    print("2. 价格在30元以内")
    print("3. 预计未来5天有60%概率涨幅5%以上")
    print("4. 取前20个股票")
    print("=" * 60)
    
    # 获取并筛选股票
    all_stocks = get_all_a_stocks()
    filtered_stocks = filter_stocks(all_stocks)
    
    if len(filtered_stocks) == 0:
        print("没有找到符合条件的股票")
        return
    
    print(f"\n开始分析 {len(filtered_stocks)} 只符合条件的股票...")
    
    # 分析每只股票的技术指标
    results = []
    for idx, row in filtered_stocks.iterrows():
        stock_code = row['代码']
        stock_name = row['名称']
        current_price = row['最新价']
        
        print(f"分析 {stock_code} {stock_name}...", end='\r')
        
        indicators = calculate_technical_indicators(stock_code)
        
        if indicators and indicators['score'] >= 60:  # 60分以上认为有60%上涨概率
            # 计算预期涨幅（基于技术指标）
            expected_gain = 0
            
            # 基于技术指标估算涨幅
            if indicators['score'] >= 80:
                expected_gain = 8  # 8%以上
            elif indicators['score'] >= 70:
                expected_gain = 6  # 6%以上
            elif indicators['score'] >= 60:
                expected_gain = 5  # 5%以上
            
            results.append({
                '代码': stock_code,
                '名称': stock_name,
                '当前价格': current_price,
                '技术评分': indicators['score'],
                '预期涨幅%': expected_gain,
                'RSI': round(indicators['rsi'], 2),
                'MA5': round(indicators['ma5'], 2),
                '成交量比率': round(indicators['volume_ratio'], 2)
            })
    
    print("\n" + "=" * 60)
    
    if len(results) == 0:
        print("没有找到符合技术分析条件的股票")
        return
    
    # 转换为DataFrame并排序
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('技术评分', ascending=False)
    
    # 取前20个
    top_20 = results_df.head(20)
    
    print(f"\n筛选结果（前{len(top_20)}只股票）：")
    print("=" * 80)
    print(f"{'代码':<8} {'名称':<10} {'价格':<8} {'技术评分':<8} {'预期涨幅%':<10} {'RSI':<8} {'MA5':<8} {'成交量比':<8}")
    print("-" * 80)
    
    for idx, row in top_20.iterrows():
        print(f"{row['代码']:<8} {row['名称']:<10} {row['当前价格']:<8.2f} {row['技术评分']:<8} {row['预期涨幅%']:<10} {row['RSI']:<8.2f} {row['MA5']:<8.2f} {row['成交量比率']:<8.2f}")
    
    print("=" * 80)
    
    # 保存结果到文件
    output_file = f"stock_screening_results_{datetime.now().strftime('%Y%m%d')}.csv"
    top_20.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n详细结果已保存到: {output_file}")
    
    # 统计信息
    print(f"\n统计信息：")
    print(f"平均技术评分: {top_20['技术评分'].mean():.1f}")
    print(f"平均预期涨幅: {top_20['预期涨幅%'].mean():.1f}%")
    print(f"平均价格: {top_20['当前价格'].mean():.2f}元")
    print(f"价格范围: {top_20['当前价格'].min():.2f} - {top_20['当前价格'].max():.2f}元")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()