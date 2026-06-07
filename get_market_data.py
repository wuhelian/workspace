#!/usr/bin/env python3
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import sys

def get_market_overview():
    """获取市场概览"""
    print("=== 市场概览 ===")
    
    # 获取上证指数
    try:
        sz_index = ak.stock_zh_index_spot_em()
        sz_df = sz_index[sz_index['代码'] == 'sh000001']
        if not sz_df.empty:
            sz_close = float(sz_df.iloc[0]['最新价'])
            sz_change = float(sz_df.iloc[0]['涨跌幅'])
            print(f"上证指数: {sz_close:.2f} ({sz_change:+.2f}%)")
    except Exception as e:
        print(f"获取上证指数失败: {e}")
    
    # 获取深证成指
    try:
        sz_df = sz_index[sz_index['代码'] == 'sz399001']
        if not sz_df.empty:
            sz_close = float(sz_df.iloc[0]['最新价'])
            sz_change = float(sz_df.iloc[0]['涨跌幅'])
            print(f"深证成指: {sz_close:.2f} ({sz_change:+.2f}%)")
    except Exception as e:
        print(f"获取深证成指失败: {e}")
    
    # 获取创业板指
    try:
        sz_df = sz_index[sz_index['代码'] == 'sz399006']
        if not sz_df.empty:
            sz_close = float(sz_df.iloc[0]['最新价'])
            sz_change = float(sz_df.iloc[0]['涨跌幅'])
            print(f"创业板指: {sz_close:.2f} ({sz_change:+.2f}%)")
    except Exception as e:
        print(f"获取创业板指失败: {e}")

def get_hot_stocks():
    """获取热门股票"""
    print("\n=== 热门股票分析 ===")
    
    try:
        # 获取A股实时行情
        spot_data = ak.stock_zh_a_spot_em()
        
        # 筛选涨幅前20的股票
        spot_data['涨跌幅'] = pd.to_numeric(spot_data['涨跌幅'], errors='coerce')
        top_gainers = spot_data.nlargest(20, '涨跌幅')
        
        print("涨幅前20股票:")
        for idx, row in top_gainers.iterrows():
            if idx >= 10:  # 只显示前10
                break
            print(f"{row['代码']} {row['名称']}: {row['最新价']} ({row['涨跌幅']:+.2f}%) 成交量: {row['成交量']}")
            
    except Exception as e:
        print(f"获取热门股票失败: {e}")

def get_sector_performance():
    """获取板块表现"""
    print("\n=== 板块表现 ===")
    
    try:
        # 获取行业板块
        industry_data = ak.stock_board_industry_name_em()
        
        # 筛选涨幅前10的板块
        industry_data['涨跌幅'] = pd.to_numeric(industry_data['涨跌幅'], errors='coerce')
        top_industries = industry_data.nlargest(10, '涨跌幅')
        
        print("涨幅前10板块:")
        for idx, row in top_industries.iterrows():
            print(f"{row['板块名称']}: {row['涨跌幅']:+.2f}%")
            
    except Exception as e:
        print(f"获取板块数据失败: {e}")

def get_momentum_stocks():
    """获取动量股票"""
    print("\n=== 动量股票筛选 ===")
    
    try:
        # 获取A股实时行情
        spot_data = ak.stock_zh_a_spot_em()
        
        # 筛选条件：涨幅2-8%，成交量放大
        spot_data['涨跌幅'] = pd.to_numeric(spot_data['涨跌幅'], errors='coerce')
        spot_data['成交量'] = pd.to_numeric(spot_data['成交量'], errors='coerce')
        
        # 计算平均成交量
        avg_volume = spot_data['成交量'].mean()
        
        # 筛选动量股
        momentum_stocks = spot_data[
            (spot_data['涨跌幅'] >= 2.0) & 
            (spot_data['涨跌幅'] <= 8.0) &
            (spot_data['成交量'] > avg_volume * 1.5)
        ]
        
        # 按涨幅排序
        momentum_stocks = momentum_stocks.nlargest(15, '涨跌幅')
        
        print("动量股票候选（涨幅2-8%，成交量放大）:")
        for idx, row in momentum_stocks.iterrows():
            if idx >= 10:
                break
            volume_ratio = row['成交量'] / avg_volume
            print(f"{row['代码']} {row['名称']}: {row['最新价']} ({row['涨跌幅']:+.2f}%) 成交量倍数: {volume_ratio:.1f}x")
            
    except Exception as e:
        print(f"获取动量股票失败: {e}")

if __name__ == "__main__":
    try:
        get_market_overview()
        get_hot_stocks()
        get_sector_performance()
        get_momentum_stocks()
    except Exception as e:
        print(f"程序执行失败: {e}")
        sys.exit(1)