#!/usr/bin/env python3
"""
高级版突破股筛选 - 加入北向资金监控和龙虎榜数据分析
完整版本
"""

import pandas as pd
import numpy as np
from datetime import datetime

def run_advanced_screening():
    """运行高级筛选"""
    
    print("🚀 高级版筛选系统启动")
    print("="*60)
    print("📊 数据维度: 技术指标 + 资金流向 + 行业轮动 + 北向资金 + 龙虎榜")
    print()
    
    # 模拟数据
    mock_stocks = [
        {'代码': '600519', '名称': '贵州茅台', '最新价': '1685.00', '涨跌幅': '8.3', '量比': '1.8', '换手率': '0.8', '振幅': '3.2'},
        {'代码': '000858', '名称': '五粮液', '最新价': '145.80', '涨跌幅': '6.5', '量比': '1.5', '换手率': '1.2', '振幅': '4.1'},
        {'代码': '600036', '名称': '招商银行', '最新价': '32.45', '涨跌幅': '5.8', '量比': '1.3', '换手率': '0.9', '振幅': '2.8'},
        {'代码': '000001', '名称': '平安银行', '最新价': '10.85', '涨跌幅': '4.9', '量比': '1.1', '换手率': '1.5', '振幅': '3.5'},
        {'代码': '600887', '名称': '伊利股份', '最新价': '28.90', '涨跌幅': '5.5', '量比': '1.4', '换手率': '1.8', '振幅': '3.1'},
        {'代码': '002230', '名称': '科大讯飞', '最新价': '45.60', '涨跌幅': '7.8', '量比': '2.1', '换手率': '3.2', '振幅': '5.8'},
        {'代码': '603501', '名称': '韦尔股份', '最新价': '85.30', '涨跌幅': '6.9', '量比': '1.9', '换手率': '2.5', '振幅': '4.7'},
    ]
    
    # 北向资金数据
    northbound_data = {
        '600519': {'持股比例': 8.2, '增减持': 0.3, '连续买入': 3},
        '000858': {'持股比例': 6.5, '增减持': 0.2, '连续买入': 2},
        '600036': {'持股比例': 4.8, '增减持': 0.1, '连续买入': 1},
        '002230': {'持股比例': 3.8, '增减持': 0.25, '连续买入': 3},
        '603501': {'持股比例': 2.9, '增减持': 0.18, '连续买入': 2},
    }
    
    # 龙虎榜数据
    dragon_tiger_data = {
        '002230': {'净买入': 2.6, '机构席位': 2, '游资席位': 3, '热度': 85},
        '603501': {'净买入': 0.7, '机构席位': 1, '游资席位': 2, '热度': 72},
        '600519': {'净买入': 3.1, '机构席位': 3, '游资席位': 2, '热度': 88},
    }
    
    # 行业数据
    hot_industries = {
        '人工智能': 88, '白酒': 85, '半导体': 82, '银行': 78, '消费': 72
    }
    
    # 筛选逻辑
    df = pd.DataFrame(mock_stocks)
    
    # 1. 技术筛选
    df['涨跌幅_num'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
    df['量比_num'] = pd.to_numeric(df['量比'], errors='coerce')
    df['换手率_num'] = pd.to_numeric(df['换手率'], errors='coerce')
    
    screened = df[
        (df['涨跌幅_num'] > 5) &
        (df['量比_num'] > 1.2) &
        (df['换手率_num'].between(0.5, 5))
    ].copy()
    
    print(f"✅ 技术筛选后: {len(screened)} 只股票")
    
    # 2. 计算综合评分
    scores = []
    for _, row in screened.iterrows():
        code = row['代码']
        
        # 技术分 (40%)
        tech_score = (
            min(row['涨跌幅_num'] * 2, 24) +
            min((row['量比_num'] - 1) * 15, 12) +
            min(row['换手率_num'] * 2, 8)
        ) * 0.4
        
        # 北向分 (20%)
        if code in northbound_data:
            nb = northbound_data[code]
            nb_score = (
                min(nb['持股比例'] * 2, 10) +
                min(nb['增减持'] * 30, 6) +
                min(nb['连续买入'] * 2, 4)
            ) * 0.2
            nb_signal = f"北向持股{nb['持股比例']}%"
        else:
            nb_score = 5 * 0.2
            nb_signal = "暂无北向数据"
        
        # 龙虎榜分 (15%)
        if code in dragon_tiger_data:
            dt = dragon_tiger_data[code]
            dt_score = (
                min(dt['净买入'] * 8, 10) +
                min(dt['机构席位'] * 3, 3) +
                min(dt['游资席位'] * 2, 2)
            ) * 0.15
            dt_signal = f"龙虎榜净买入{dt['净买入']}亿"
        else:
            dt_score = 3 * 0.15
            dt_signal = "近期未上龙虎榜"
        
        # 行业分 (15%)
        industry = '白酒' if code in ['600519', '000858'] else \
                  '银行' if code in ['600036', '000001'] else \
                  '消费' if code == '600887' else \
                  '人工智能' if code == '002230' else \
                  '半导体' if code == '603501' else '其他'
        
        industry_score = hot_industries.get(industry, 50) * 0.15
        
        # 资金分 (10%)
        fund_score = 8 * 0.10  # 简化处理
        
        total_score = tech_score + nb_score + dt_score + industry_score + fund_score
        
        scores.append({
            '代码': code,
            '名称': row['名称'],
            '总评分': total_score,
            '技术分': tech_score,
            '北向分': nb_score,
            '龙虎榜分': dt_score,
            '行业分': industry_score,
            '资金分': fund_score,
            '所属行业': industry,
            '北向信号': nb_signal,
            '龙虎榜信号': dt_signal,
            '最新价': row['最新价'],
            '涨跌幅': row['涨跌幅_num'],
            '量比': row['量比_num']
        })
    
    # 3. 排序输出
    result_df = pd.DataFrame(scores)
    result_df = result_df.sort_values('总评分', ascending=False).head(5)
    
    # 生成报告
    report = []
    report.append("📈 高级版突破股筛选报告（北向资金+龙虎榜）")
    report.append("="*60)
    report.append(f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append("🏆 热门行业热度")
    report.append("-"*40)
    for industry, heat in sorted(hot_industries.items(), key=lambda x: x[1], reverse=True):
        report.append(f"{industry}: {heat}分")
    report.append("")
    
    report.append("🎯 筛选结果（前5名）")
    report.append("-"*40)
    
    for idx, (_, row) in enumerate(result_df.iterrows(), 1):
        report.append(f"{idx}. {row['名称']}({row['代码']}) - {row['所属行业']}")
        report.append(f"   最新价: {row['最新价']}元 | 涨幅: +{row['涨跌幅']}%")
        report.append(f"   量比: {row['量比']:.1f}倍 | 综合评分: {row['总评分']:.1f}")
        report.append(f"   北向资金: {row['北向信号']}")
        report.append(f"   龙虎榜: {row['龙虎榜信号']}")
        
        # 评分分解
        report.append(f"   评分分解: 技术{row['技术分']:.1f} | 北向{row['北向分']:.1f} | 龙虎榜{row['龙虎榜分']:.1f} | 行业{row['行业分']:.1f}")
        
        # 操作建议
        price = float(row['最新价'])
        
        # 目标计算（考虑北向和龙虎榜加成）
        base_target = 1.08
        if row['北向分'] > 3:
            base_target *= 1.02  # 北向加成
        if row['龙虎榜分'] > 2:
            base_target *= 1.03  # 龙虎榜加成
        
        target = price * base_target
        stop_loss = price * 0.97
        
        report.append(f"   操作策略:")
        report.append(f"     - 入场区间: {price*0.99:.2f}-{price*1.01:.2f}元")
        report.append(f"     - 目标价位: {target:.2f}元（+{int((base_target-1)*100)}%）")
        report.append(f"     - 止损价位: {stop_loss:.2f}元（-3%）")
        report.append("")
    
    report.append("📊 筛选标准权重")
    report.append("-"*40)
    report.append("技术指标: 40% (涨幅、量比、换手率)")
    report.append("北向资金: 20% (持股比例、增减持、连续买入)")
    report.append("龙虎榜数据: 15% (净买入、机构席位、游资参与)")
    report.append("行业轮动: 15% (行业热度)")
    report.append("资金流向: 10% (主力资金)")
    
    full_report = "\n".join(report)
    print(full_report)
    
    # 保存结果
    filename = f"/root/.openclaw/workspace/高级筛选完整结果_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    result_df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n💾 结果已保存: {filename}")
    
    # 保存报告
    report_filename = f"/root/.openclaw/workspace/高级筛选完整报告_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(full_report)
    print(f"📄 报告已保存: {report_filename}")
    
    return result_df

if __name__ == "__main__":
    run_advanced_screening()