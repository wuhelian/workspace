#!/usr/bin/env python3
"""Fetch A-share market data with retry logic"""
import akshare as ak
import pandas as pd
import time
import json

results = {}

# 1. Try index data first (smaller dataset)
print("1. 获取指数行情...")
for attempt in range(3):
    try:
        df_index = ak.stock_zh_index_spot_em()
        print(f"  成功！共{len(df_index)}条")
        key_indices = ['上证指数', '深证成指', '创业板指', '科创50']
        for name in key_indices:
            row = df_index[df_index['名称'] == name]
            if not row.empty:
                r = row.iloc[0]
                print(f"  {name}: {r['最新价']} | 涨跌幅: {r['涨跌幅']:.2f}%")
        results['indices'] = df_index
        break
    except Exception as e:
        print(f"  尝试{attempt+1}失败: {e}")
        time.sleep(3)
else:
    print("  全部失败")

# 2. Individual stock data for our holdings
print("\n2. 个股数据...")
for code, name in [('000858', '五粮液'), ('002428', '云南锗业')]:
    for attempt in range(3):
        try:
            df = ak.stock_individual_spot_xq(symbol=f"SZ{code}" if code.startswith('00') else f"SH{code}")
            print(f"  {name}({code}): {df}")
            results[f'stock_{code}'] = df
            break
        except Exception as e:
            print(f"  {name} 尝试{attempt+1}失败: {e}")
            time.sleep(2)
    else:
        print(f"  {name} 全部失败")

# 3. Historical daily data for holdings for technical analysis
print("\n3. 获取历史K线数据...")
end_date = "20260430"
for code, name in [('000858', '五粮液'), ('002428', '云南锗业')]:
    for attempt in range(3):
        try:
            df_h = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                      start_date="20260401", end_date=end_date, adjust="qfq")
            print(f"  {name}({code}) K线: {len(df_h)}条")
            print(f"  {df_h.tail(3)[['日期', '开盘', '收盘', '最高', '最低', '成交量', '涨跌幅']].to_string(index=False)}")
            results[f'hist_{code}'] = df_h
            break
        except Exception as e:
            print(f"  {name}K线 尝试{attempt+1}失败: {e}")
            time.sleep(2)
    else:
        print(f"  {name}K线 全部失败")

# 4. Try spot data with alternative function
print("\n4. 获取全市场实时行情(alternative)...")
for attempt in range(3):
    try:
        df_spot = ak.stock_zh_a_spot_em()
        print(f"  成功！共{len(df_spot)}条")
        # Filter main board
        mask = (
            df_spot['代码'].str.match(r'^(60\d{4}|00\d{4})$') &
            ~df_spot['代码'].str.match(r'^(002|003|300|688)')
        )
        df_main = df_spot[mask].copy()
        df_main = df_main[~df_main['名称'].str.contains('ST|退', na=False)]
        print(f"  主板(60/00开头,非ST): {len(df_main)}只")
        
        # Top gainers
        df_top = df_main.nlargest(30, '涨跌幅')
        print(f"\n  主板涨幅TOP30:")
        print(df_top[['代码','名称','最新价','涨跌幅','成交额','换手率']].head(30).to_string(index=False))
        results['spot'] = df_spot
        results['main_board'] = df_main
        results['top_gainers'] = df_top
        
        # Breakout candidates
        df_breakout = df_main[
            (df_main['涨跌幅'] > 3.0) &
            (df_main['涨跌幅'] < 10.0) &
            (df_main['最新价'] > 5.0) &
            (df_main['换手率'] > 2.0) &
            (df_main['换手率'] < 30.0) &
            (df_main['成交额'] > 2.0e8)
        ].nlargest(15, '涨跌幅')
        print(f"\n  突破候选({len(df_breakout)}只):")
        if not df_breakout.empty:
            print(df_breakout[['代码','名称','最新价','涨跌幅','成交额','换手率','市盈率-动态']].to_string(index=False))
            df_breakout.to_csv('/tmp/breakout_v2.csv', index=False)
        else:
            # Relax criteria
            df_breakout = df_main[
                (df_main['涨跌幅'] > 2.0) &
                (df_main['最新价'] > 5.0) &
                (df_main['换手率'] > 1.5) &
                (df_main['成交额'] > 1.0e8)
            ].nlargest(15, '涨跌幅')
            print(f"  (放宽条件后{len(df_breakout)}只):")
            print(df_breakout[['代码','名称','最新价','涨跌幅','成交额','换手率']].to_string(index=False))
        results['breakout'] = df_breakout
        break
    except Exception as e:
        print(f"  尝试{attempt+1}失败: {e}")
        time.sleep(3)
else:
    print("  全市场行情全部失败")

# 5. Board data
print("\n5. 板块行情...")
for attempt in range(3):
    try:
        df_board = ak.stock_board_industry_name_em()
        print(f"  成功！共{len(df_board)}个板块")
        top_boards = df_board.sort_values('涨跌幅', ascending=False).head(15)
        print(f"  涨幅TOP15板块:")
        print(top_boards[['板块名称','涨跌幅','上涨家数','下跌家数','领涨股']].to_string(index=False))
        results['boards'] = df_board
        results['top_boards'] = top_boards
        break
    except Exception as e:
        print(f"  尝试{attempt+1}失败: {e}")
        time.sleep(3)
else:
    print("  板块数据全部失败")

# Save all results
print("\n✅ 数据采集完成")
for k, v in results.items():
    if isinstance(v, pd.DataFrame):
        print(f"  {k}: {len(v)} rows")

# Save key dataframes to csv for later use in report
if 'breakout' in results and not results['breakout'].empty:
    results['breakout'].to_csv('/tmp/report_breakout.csv', index=False)
if 'main_board' in results:
    results['main_board'].to_csv('/tmp/report_main_board.csv', index=False)
if 'top_boards' in results:
    results['top_boards'].to_csv('/tmp/report_top_boards.csv', index=False)
