#!/usr/bin/env python3
"""
突破股筛选逻辑详解
"""

def explain_breakout_screening():
    """详细解释突破股筛选逻辑"""
    
    explanation = """
# 🎯 突破股筛选逻辑详解

## 1. 筛选目标
**纯主板突破股**，符合以下条件：
- 代码以60或00开头（上海/深圳主板）
- 排除：创业板(30)、中小板(002)、科创板(688)、ST股
- 持股周期：3-5天短线操作

## 2. 核心筛选指标

### 技术面指标
| 指标 | 要求 | 说明 |
|------|------|------|
| **5日涨幅** | >5% | 短期动量强劲 |
| **成交量** | 较5日均量放大>20% | 资金关注度高 |
| **价格位置** | 突破近期高点 | 技术突破确认 |
| **均线排列** | 5日>10日>20日 | 多头趋势 |
| **RSI** | 50-70区间 | 强势但不超买 |

### 基本面筛选（可选）
| 指标 | 要求 | 说明 |
|------|------|------|
| **市值** | >100亿元 | 流动性好 |
| **市盈率** | <行业平均 | 估值合理 |
| **机构持仓** | 近期增加 | 机构认可 |

## 3. 筛选流程

### 第一步：初筛（技术突破）
```python
# 获取A股实时数据
stocks = ak.stock_zh_a_spot_em()

# 筛选主板
main_board = stocks[stocks['代码'].str.startswith(('60', '00'))]

# 排除ST股
main_board = main_board[~main_board['名称'].str.contains('ST')]

# 筛选5日涨幅>5%
momentum_stocks = main_board[pd.to_numeric(main_board['涨跌幅']) > 5]
```

### 第二步：量价确认
```python
# 计算成交量比率
momentum_stocks['量比'] = pd.to_numeric(momentum_stocks['量比'])

# 筛选量比>1.2（成交量放大20%）
volume_confirmed = momentum_stocks[momentum_stocks['量比'] > 1.2]

# 筛选换手率适中（2%-10%）
turnover_filtered = volume_confirmed[
    (pd.to_numeric(volume_confirmed['换手率']) > 2) &
    (pd.to_numeric(volume_confirmed['换手率']) < 10)
]
```

### 第三步：趋势确认
```python
# 获取个股K线数据（需要历史数据）
for stock_code in selected_codes:
    # 获取20日K线
    kline = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                               start_date=start_date, end_date=end_date)
    
    # 检查是否突破20日高点
    recent_high = kline['最高'].max()
    current_price = get_current_price(stock_code)
    
    if current_price > recent_high * 0.98:  # 突破或接近高点
        breakout_stocks.append(stock_code)
```

### 第四步：风险过滤
```python
# 排除高波动股（振幅过大）
low_volatility = turnover_filtered[
    pd.to_numeric(turnover_filtered['振幅']) < 8  # 振幅小于8%
]

# 排除高价股（可选）
affordable = low_volatility[
    pd.to_numeric(low_volatility['最新价']) < 100  # 股价低于100元
]
```

## 4. 最终输出（3-5只）

### 排序标准
1. **综合评分** = 动量(40%) + 量能(30%) + 趋势(20%) + 基本面(10%)
2. **优先选择**：行业龙头、机构关注度高、技术形态清晰

### 示例输出
```
🎯 今日突破股筛选结果（2026-04-02）

1. 贵州茅台(600519) - 评分: 92
   ✓ 5日涨幅: +8.3%
   ✓ 量比: 1.8倍
   ✓ 突破: 1680元阻力位
   ✓ RSI: 62（健康）

2. 招商银行(600036) - 评分: 88
   ✓ 5日涨幅: +6.5%
   ✓ 量比: 1.5倍
   ✓ 突破: 32元平台
   ✓ 市盈率: 6.2倍

3. 中国平安(601318) - 评分: 85
   ✓ 5日涨幅: +5.8%
   ✓ 量比: 1.3倍
   ✓ 突破: 45元压力
   ✓ 北向资金: 连续3日净买入
```

## 5. 实际筛选代码示例

```python
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def screen_breakout_stocks():
    \"\"\"实际突破股筛选函数\"\"\"
    
    # 1. 获取实时数据
    df = ak.stock_zh_a_spot_em()
    
    # 2. 主板筛选
    df = df[df['代码'].str.startswith(('60', '00'))]
    df = df[~df['名称'].str.contains('ST')]
    
    # 3. 技术指标筛选
    df['涨跌幅_num'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
    df['量比_num'] = pd.to_numeric(df['量比'], errors='coerce')
    df['换手率_num'] = pd.to_numeric(df['换手率'], errors='coerce')
    
    # 筛选条件
    screened = df[
        (df['涨跌幅_num'] > 5) &           # 5日涨幅>5%
        (df['量比_num'] > 1.2) &           # 成交量放大20%
        (df['换手率_num'].between(2, 10)) & # 换手率2-10%
        (pd.to_numeric(df['最新价']) < 100) # 股价低于100元
    ]
    
    # 4. 排序取前5
    screened['综合分'] = (
        df['涨跌幅_num'] * 0.4 +
        df['量比_num'] * 0.3 +
        df['换手率_num'] * 0.3
    )
    
    top_5 = screened.nlargest(5, '综合分')
    
    return top_5[['代码', '名称', '最新价', '涨跌幅', '量比', '换手率', '综合分']]
```

## 6. 注意事项

### 数据时效性
- 使用收盘后数据筛选，避免盘中波动干扰
- 结合前一日收盘价和当日盘中数据

### 风险控制
- 每只股票设置明确止损位（3-5%）
- 分散投资，单只股票不超过总仓位20%
- 设置时间止损（3-5天无表现离场）

### 动态调整
- 根据市场环境调整筛选标准
- 牛市可适当放宽条件
- 熊市需更加严格

## 7. 明日优化计划

1. **增加基本面过滤**：市盈率、市净率、ROE
2. **加入资金流向**：北向资金、主力资金
3. **技术指标增强**：MACD、KDJ、布林带
4. **行业轮动分析**：优先选择热点行业

---
**总结**：突破股筛选是报告的核心，通过多重技术指标确保选股质量，
为短线交易提供明确的入场点和风险控制方案。
"""
    
    return explanation

if __name__ == "__main__":
    print(explain_breakout_screening())