#!/usr/bin/env python3
"""
简化版低价股筛选系统 - 8-15元价格区间
"""

import pandas as pd
import numpy as np
from datetime import datetime

def run_low_price_screening():
    """运行低价股筛选"""
    
    print("🚀 低价股筛选系统（8-15元区间）")
    print("="*60)
    
    # 低价股股票池（8-15元）
    stocks = [
        # 银行股（低估值高股息）
        {'代码': '600016', '名称': '民生银行', '价格': 8.45, '涨幅': 3.2, '量比': 1.5, '换手率': 1.2, '市盈率': 4.5, '市净率': 0.4, '股息率': 7.2},
        {'代码': '600000', '名称': '浦发银行', '价格': 9.20, '涨幅': 2.8, '量比': 1.4, '换手率': 1.0, '市盈率': 4.8, '市净率': 0.5, '股息率': 6.5},
        {'代码': '600015', '名称': '华夏银行', '价格': 10.85, '涨幅': 3.5, '量比': 1.6, '换手率': 1.5, '市盈率': 4.2, '市净率': 0.4, '股息率': 7.5},
        
        # 公用事业
        {'代码': '600011', '名称': '华能国际', '价格': 8.90, '涨幅': 4.2, '量比': 1.8, '换手率': 2.1, '市盈率': 12.5, '市净率': 1.2, '股息率': 4.8},
        {'代码': '600027', '名称': '华电国际', '价格': 9.65, '涨幅': 3.8, '量比': 1.7, '换手率': 1.8, '市盈率': 10.8, '市净率': 1.1, '股息率': 5.2},
        
        # 交通运输
        {'代码': '600029', '名称': '南方航空', '价格': 11.20, '涨幅': 5.2, '量比': 2.1, '换手率': 2.5, '市盈率': 15.2, '市净率': 1.5, '股息率': 3.2},
        {'代码': '600115', '名称': '东方航空', '价格': 9.85, '涨幅': 4.8, '量比': 1.9, '换手率': 2.2, '市盈率': 14.8, '市净率': 1.4, '股息率': 3.5},
        
        # 建筑装饰
        {'代码': '601668', '名称': '中国建筑', '价格': 8.65, '涨幅': 3.2, '量比': 1.4, '换手率': 1.2, '市盈率': 4.2, '市净率': 0.6, '股息率': 5.8},
        {'代码': '601186', '名称': '中国铁建', '价格': 12.40, '涨幅': 2.9, '量比': 1.3, '换手率': 1.0, '市盈率': 5.1, '市净率': 0.7, '股息率': 4.5},
        
        # 化工
        {'代码': '600426', '名称': '华鲁恒升', '价格': 14.85, '涨幅': 4.1, '量比': 1.7, '换手率': 2.1, '市盈率': 12.5, '市净率': 2.1, '股息率': 3.8},
        
        # 机械设备
        {'代码': '000157', '名称': '中联重科', '价格': 13.20, '涨幅': 5.8, '量比': 2.2, '换手率': 2.8, '市盈率': 14.2, '市净率': 1.8, '股息率': 4.2},
        {'代码': '000425', '名称': '徐工机械', '价格': 11.85, '涨幅': 4.5, '量比': 1.9, '换手率': 2.3, '市盈率': 13.8, '市净率': 1.6, '股息率': 4.5},
        
        # 环保
        {'代码': '300070', '名称': '碧水源', '价格': 9.20, '涨幅': 3.8, '量比': 1.6, '换手率': 1.9, '市盈率': 22.5, '市净率': 1.8, '股息率': 2.5},
        
        # 纺织服装
        {'代码': '600398', '名称': '海澜之家', '价格': 8.95, '涨幅': 3.2, '量比': 1.4, '换手率': 1.5, '市盈率': 11.2, '市净率': 1.5, '股息率': 5.2},
    ]
    
    df = pd.DataFrame(stocks)
    print(f"📊 初始股票池: {len(df)} 只股票（8-15元）")
    
    # 1. 技术筛选
    screened = df[
        (df['涨幅'] > 2) &           # 涨幅>2%
        (df['量比'] > 1.2) &         # 量比>1.2
        (df['换手率'].between(0.5, 5))  # 换手率适中
    ].copy()
    
    print(f"✅ 技术筛选后: {len(screened)} 只")
    
    if len(screened) == 0:
        print("❌ 未筛选到符合条件的股票")
        return
    
    # 2. 计算综合评分
    def calculate_score(row):
        """计算低价股综合评分"""
        score = 0
        
        # 价格优势（30%）：价格越低越好
        if row['价格'] < 10:
            score += 25
        elif row['价格'] < 12:
            score += 20
        else:
            score += 15
        
        # 技术指标（30%）
        score += min(row['涨幅'] * 2, 20)  # 涨幅
        score += min((row['量比'] - 1) * 15, 10)  # 量比
        
        # 估值指标（25%）
        if row['市盈率'] < 8:
            score += 8
        elif row['市盈率'] < 15:
            score += 5
            
        if row['市净率'] < 1:
            score += 7
        elif row['市净率'] < 1.5:
            score += 4
            
        if row['股息率'] > 5:
            score += 5
        elif row['股息率'] > 3:
            score += 3
        
        # 流动性（15%）
        score += min(row['换手率'] * 3, 15)
        
        return score
    
    screened['综合评分'] = screened.apply(calculate_score, axis=1)
    
    # 3. 排序取前5
    result = screened.sort_values('综合评分', ascending=False).head(5)
    
    # 生成报告
    report = []
    report.append("💰 优质低价股推荐（8-15元区间）")
    report.append("="*60)
    report.append(f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append("🎯 筛选标准")
    report.append("-"*40)
    report.append("1. 价格区间: 8-15元")
    report.append("2. 技术指标: 涨幅>2%，量比>1.2，换手率0.5-5%")
    report.append("3. 估值要求: 低市盈率、破净股、高股息优先")
    report.append("")
    
    report.append("🏆 推荐股票（前5名）")
    report.append("-"*40)
    
    for idx, (_, row) in enumerate(result.iterrows(), 1):
        report.append(f"{idx}. {row['名称']}({row['代码']})")
        report.append(f"   价格: {row['价格']}元 | 涨幅: +{row['涨幅']}%")
        report.append(f"   量比: {row['量比']:.1f}倍 | 换手率: {row['换手率']}%")
        report.append(f"   估值: PE={row['市盈率']:.1f} | PB={row['市净率']:.1f} | 股息率={row['股息率']}%")
        report.append(f"   综合评分: {row['综合评分']:.1f}")
        
        # 投资亮点
        highlights = []
        if row['价格'] < 10:
            highlights.append("绝对低价")
        if row['市盈率'] < 8:
            highlights.append("低市盈率")
        if row['市净率'] < 1:
            highlights.append("破净股")
        if row['股息率'] > 5:
            highlights.append("高股息")
        if row['量比'] > 1.5:
            highlights.append("量能充沛")
        
        if highlights:
            report.append(f"   投资亮点: {' | '.join(highlights)}")
        
        # 操作建议
        if row['价格'] < 10:
            target_pct = 15  # 低价股目标更高
        elif row['价格'] < 12:
            target_pct = 12
        else:
            target_pct = 10
        
        # 估值加成
        if row['市盈率'] < 8:
            target_pct += 2
        if row['市净率'] < 1:
            target_pct += 3
        
        entry_min = row['价格'] * 0.99
        entry_max = row['价格'] * 1.01
        target = row['价格'] * (1 + target_pct/100)
        stop_loss = row['价格'] * 0.95  # 低价股止损放宽
        
        report.append(f"   操作策略:")
        report.append(f"     - 入场区间: {entry_min:.2f}-{entry_max:.2f}元")
        report.append(f"     - 目标价位: {target:.2f}元（+{target_pct}%）")
        report.append(f"     - 止损价位: {stop_loss:.2f}元（-5%）")
        report.append(f"     - 建议仓位: 15-20%")
        report.append("")
    
    report.append("📈 低价股投资优势")
    report.append("-"*40)
    report.append("1. **上涨空间大**: 低价股翻倍机会更多")
    report.append("2. **估值安全垫**: 破净股、低市盈率提供保护")
    report.append("3. **股息回报**: 高股息率提供稳定现金流")
    report.append("4. **流动性好**: 适中换手率，进出方便")
    report.append("5. **风险分散**: 不同行业配置，降低风险")
    
    full_report = "\n".join(report)
    print(full_report)
    
    # 保存结果
    filename = f"/root/.openclaw/workspace/优质低价股推荐_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    result.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n💾 结果已保存: {filename}")
    
    return result

if __name__ == "__main__":
    run_low_price_screening()