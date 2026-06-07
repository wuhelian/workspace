#!/usr/bin/env python3
"""
实际突破股筛选测试
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime

def test_screening_logic():
    """测试筛选逻辑（使用模拟数据）"""
    
    print("🧪 测试突破股筛选逻辑...")
    
    # 创建模拟数据（在实际环境中会从akshare获取）
    mock_stocks = [
        {
            '代码': '600519', '名称': '贵州茅台', '最新价': '1685.00', 
            '涨跌幅': '8.3', '量比': '1.8', '换手率': '0.8', '振幅': '3.2'
        },
        {
            '代码': '000858', '名称': '五粮液', '最新价': '145.80', 
            '涨跌幅': '6.5', '量比': '1.5', '换手率': '1.2', '振幅': '4.1'
        },
        {
            '代码': '600036', '名称': '招商银行', '最新价': '32.45', 
            '涨跌幅': '5.8', '量比': '1.3', '换手率': '0.9', '振幅': '2.8'
        },
        {
            '代码': '000001', '名称': '平安银行', '最新价': '10.85', 
            '涨跌幅': '4.9', '量比': '1.1', '换手率': '1.5', '振幅': '3.5'
        },
        {
            '代码': '300750', '名称': '宁德时代', '最新价': '185.60', 
            '涨跌幅': '7.2', '量比': '2.1', '换手率': '3.2', '振幅': '5.8'
        },
        {
            '代码': '002594', '名称': '比亚迪', '最新价': '245.30', 
            '涨跌幅': '6.8', '量比': '1.9', '换手率': '2.1', '振幅': '4.9'
        },
        {
            '代码': '600887', '名称': '伊利股份', '最新价': '28.90', 
            '涨跌幅': '5.5', '量比': '1.4', '换手率': '1.8', '振幅': '3.1'
        },
        {
            '代码': '601318', '名称': '中国平安', '最新价': '45.20', 
            '涨跌幅': '3.8', '量比': '1.2', '换手率': '0.7', '振幅': '2.5'
        },
        {
            '代码': '600030', '名称': '中信证券', '最新价': '22.80', 
            '涨跌幅': '4.2', '量比': '1.0', '换手率': '1.1', '振幅': '3.2'
        },
        {
            '代码': '000333', '名称': '美的集团', '最新价': '58.90', 
            '涨跌幅': '5.1', '量比': '1.3', '换手率': '0.9', '振幅': '2.9'
        }
    ]
    
    df = pd.DataFrame(mock_stocks)
    
    print(f"📊 初始股票池: {len(df)} 只股票")
    print(df[['代码', '名称', '涨跌幅', '量比']].to_string(index=False))
    
    # 筛选步骤
    print("\n" + "="*60)
    print("🔍 开始筛选...")
    print("="*60)
    
    # 1. 筛选主板（60/00开头）
    df = df[df['代码'].str.startswith(('60', '00'))]
    print(f"✅ 主板筛选后: {len(df)} 只")
    
    # 2. 排除创业板（虽然上一步已排除，这里再次确认）
    df = df[~df['代码'].str.startswith('30')]
    print(f"✅ 排除创业板后: {len(df)} 只")
    
    # 3. 转换数据类型
    df['涨跌幅_num'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
    df['量比_num'] = pd.to_numeric(df['量比'], errors='coerce')
    df['换手率_num'] = pd.to_numeric(df['换手率'], errors='coerce')
    df['最新价_num'] = pd.to_numeric(df['最新价'], errors='coerce')
    df['振幅_num'] = pd.to_numeric(df['振幅'], errors='coerce')
    
    # 4. 技术指标筛选
    screened = df[
        (df['涨跌幅_num'] > 5) &           # 5日涨幅>5%
        (df['量比_num'] > 1.2) &           # 成交量放大20%
        (df['换手率_num'].between(0.5, 5)) & # 换手率适中
        (df['最新价_num'] < 200) &         # 股价低于200元
        (df['振幅_num'] < 6)               # 振幅小于6%
    ]
    
    print(f"✅ 技术指标筛选后: {len(screened)} 只")
    
    if len(screened) > 0:
        # 5. 计算综合评分
        screened['综合分'] = (
            screened['涨跌幅_num'] * 0.4 +
            screened['量比_num'] * 0.3 +
            (screened['换手率_num'] * 10) * 0.3  # 换手率标准化
        )
        
        # 6. 排序取前5
        top_stocks = screened.nlargest(5, '综合分')
        
        print("\n" + "="*60)
        print("🎯 最终筛选结果（前5名）")
        print("="*60)
        
        result_df = top_stocks[['代码', '名称', '最新价', '涨跌幅', '量比', '换手率', '综合分']].copy()
        result_df['排名'] = range(1, len(result_df) + 1)
        result_df = result_df[['排名', '代码', '名称', '最新价', '涨跌幅', '量比', '换手率', '综合分']]
        
        print(result_df.to_string(index=False))
        
        # 7. 生成详细分析
        print("\n" + "="*60)
        print("📋 个股详细分析")
        print("="*60)
        
        for idx, row in result_df.iterrows():
            print(f"\n{row['排名']}. {row['名称']}({row['代码']})")
            print(f"   最新价: {row['最新价']}元")
            
            # 转换数据类型
            涨幅 = float(row['涨跌幅'])
            量比 = float(row['量比'])
            
            print(f"   5日涨幅: +{涨幅}%")
            print(f"   量比: {量比}倍（成交量放大{int((量比-1)*100)}%）")
            print(f"   换手率: {row['换手率']}%")
            print(f"   综合评分: {row['综合分']:.1f}")
            
            # 技术分析
            if 涨幅 > 7:
                momentum = "强势突破"
            elif 涨幅 > 5:
                momentum = "温和突破"
            else:
                momentum = "初步突破"
                
            if 量比 > 1.5:
                volume = "显著放量"
            elif 量比 > 1.2:
                volume = "温和放量"
            else:
                volume = "量能一般"
                
            print(f"   技术特征: {momentum} + {volume}")
            
            # 操作建议
            price = float(row['最新价'])
            entry_min = price * 0.99  # 回调1%入场
            entry_max = price * 1.01  # 突破1%入场
            target = price * 1.08     # 目标涨幅8%
            stop_loss = price * 0.97  # 止损3%
            
            print(f"   操作策略:")
            print(f"     - 入场区间: {entry_min:.2f}-{entry_max:.2f}元")
            print(f"     - 目标价位: {target:.2f}元（+8%）")
            print(f"     - 止损价位: {stop_loss:.2f}元（-3%）")
            print(f"     - 建议仓位: 总资金{min(15, 100//len(result_df))}%")
        
        return result_df
    else:
        print("❌ 未筛选到符合条件的突破股")
        return None

def main():
    try:
        print("🚀 突破股筛选测试开始")
        print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        result = test_screening_logic()
        
        if result is not None:
            print("\n" + "="*60)
            print("✅ 筛选测试完成")
            print("="*60)
            print(f"🎯 共筛选出 {len(result)} 只突破股")
            print("📊 筛选标准:")
            print("   - 主板股票（60/00开头）")
            print("   - 5日涨幅 > 5%")
            print("   - 量比 > 1.2（成交量放大20%）")
            print("   - 换手率 0.5-5%")
            print("   - 股价 < 200元")
            print("   - 振幅 < 6%")
            
            # 保存结果
            filename = f"/root/.openclaw/workspace/突破股筛选结果_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            result.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"💾 结果已保存: {filename}")
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()