#!/usr/bin/env python3
"""Fetch A-share market data for weekend report - 2026-05-03 (based on Apr 30 close)"""
import akshare as ak
import pandas as pd
import json
from datetime import datetime, timedelta

print("=" * 60)
print("1. 获取A股实时行情 (stock_zh_a_spot_em)")
print("=" * 60)
try:
    df_spot = ak.stock_zh_a_spot_em()
    print(f"Total stocks: {len(df_spot)}")
    print(f"Columns: {list(df_spot.columns)}")
    # Filter for main board only (60xxxx, 00xxxx), exclude 300/002/003/688
    mask = (
        df_spot['代码'].str.match(r'^(60\d{4}|00\d{4})$') &
        ~df_spot['代码'].str.match(r'^(002|003|300|688)')
    )
    df_main = df_spot[mask].copy()
    # Also exclude ST stocks
    df_main = df_main[~df_main['名称'].str.contains('ST|退', na=False)]
    print(f"Main board (60/00, non-ST): {len(df_main)}")
    
    # Sort by change pct descending, get top gainers
    df_top = df_main.nlargest(50, '涨跌幅')
    print(f"\nTop 50 gainers on main board:")
    print(df_top[['代码', '名称', '最新价', '涨跌幅', '成交量', '成交额', '换手率']].to_string(index=False))
    
    # Also look for breakout candidates: >3% gain, decent volume, not too cheap (<3 yuan)
    df_breakout = df_main[
        (df_main['涨跌幅'] > 3.0) &
        (df_main['涨跌幅'] < 10.0) &  # Exclude limit-up (hard to buy)
        (df_main['最新价'] > 5.0) &
        (df_main['换手率'] > 2.0) &
        (df_main['换手率'] < 30.0) &  # Not excessively speculative
        (df_main['成交额'] > 2.0e8)  # >200M turnover
    ].nlargest(20, '涨跌幅')
    
    print(f"\n\nBreakout candidates (涨跌幅>3%, turnover>2%, amount>200M, price>5):")
    print(f"Count: {len(df_breakout)}")
    if not df_breakout.empty:
        print(df_breakout[['代码', '名称', '最新价', '涨跌幅', '成交量', '成交额', '换手率', '市盈率-动态']].to_string(index=False))
        df_breakout.to_csv('/tmp/breakout_candidates.csv', index=False)
    else:
        print("No candidates found with strict criteria, relaxing...")
        df_breakout = df_main[
            (df_main['涨跌幅'] > 2.0) &
            (df_main['最新价'] > 5.0) &
            (df_main['换手率'] > 1.5) &
            (df_main['成交额'] > 1.0e8)
        ].nlargest(20, '涨跌幅')
        print(f"Relaxed candidates: {len(df_breakout)}")
        if not df_breakout.empty:
            print(df_breakout[['代码', '名称', '最新价', '涨跌幅', '成交量', '成交额', '换手率', '市盈率-动态']].to_string(index=False))
            df_breakout.to_csv('/tmp/breakout_candidates.csv', index=False)

except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("2. 获取板块行情 (stock_board_industry_name_em)")
print("=" * 60)
try:
    df_board = ak.stock_board_industry_name_em()
    print(f"Total boards: {len(df_board)}")
    print(f"Columns: {list(df_board.columns)}")
    df_board_sorted = df_board.sort_values('涨跌幅', ascending=False).head(20)
    print("\nTop 20 industries by change %:")
    print(df_board_sorted[['板块名称', '涨跌幅', '上涨家数', '下跌家数', '领涨股']].to_string(index=False))
    df_board_sorted.to_csv('/tmp/top_boards.csv', index=False)
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("3. 获取指数行情")
print("=" * 60)
try:
    df_index = ak.stock_zh_index_spot_em()
    key_indices = ['上证指数', '深证成指', '创业板指', '科创50']
    print(f"Available indices: {list(df_index['名称'].unique()[:20])}")
    for name in key_indices:
        row = df_index[df_index['名称'] == name]
        if not row.empty:
            print(f"{name}: {row.iloc[0]['最新价']} | 涨跌幅: {row.iloc[0]['涨跌幅']:.2f}%")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("4. 持仓分析 - 五粮液(000858)")
print("=" * 60)
try:
    row = df_spot[df_spot['代码'] == '000858']
    if not row.empty:
        r = row.iloc[0]
        cost = 101.56
        current = r['最新价']
        print(f"五粮液(000858): 现价={current}, 成本={cost}, 盈亏={((current-cost)/cost)*100:.2f}%")
        print(f"涨跌幅={r['涨跌幅']:.2f}%, 成交量={r['成交量']}, 换手率={r['换手率']}%")
except Exception as e:
    print(f"Error 五粮液: {e}")

print("\n" + "=" * 60)
print("5. 持仓分析 - 云南锗业(002428)")
print("=" * 60)
try:
    row = df_spot[df_spot['代码'] == '002428']
    if not row.empty:
        r = row.iloc[0]
        cost = 73.30
        current = r['最新价']
        print(f"云南锗业(002428): 现价={current}, 成本={cost}, 盈亏={((current-cost)/cost)*100:.2f}%")
        print(f"涨跌幅={r['涨跌幅']:.2f}%, 成交量={r['成交量']}, 换手率={r['换手率']}%")
    else:
        print("云南锗业数据未找到")
except Exception as e:
    print(f"Error 云南锗业: {e}")

print("\n✅ 数据采集完成")
