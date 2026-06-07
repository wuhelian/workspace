#!/bin/bash
# 5日短线动量报告 - 数据采集脚本
# 使用新浪财经接口（东方财富接口IP被限流）

WORKDIR="/root/.openclaw/workspace"
REPORT_FILE="$WORKDIR/report-data.json"
TIMESTAMP=$(date +%s)

echo "=== 报告数据采集 $(date '+%Y-%m-%d %H:%M') ==="

# 1. 获取指数数据
echo ">>> 指数数据..."
INDEX_DATA=$(curl -s --connect-timeout 10 \
  -H "Referer: https://finance.sina.com.cn" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "http://hq.sinajs.cn/list=sh000001,sz399001,sz399006,sh000688,sh000016,sz399300" 2>&1)

echo "$INDEX_DATA" | iconv -f GBK -t UTF-8 2>/dev/null

# 2. 获取涨幅榜（构建批量查询）
echo ""
echo ">>> 获取全市场数据（分批）..."

# 新浪一次最多查1490只, 分多批获取
# 先拿一批主要股票
BATCH1=$(curl -s --connect-timeout 15 \
  -H "Referer: https://finance.sina.com.cn" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "http://hq.sinajs.cn/list=$(python3 -c "
codes = []
for pref in ['sh60','sz00']:
    for i in range(0, 1490):
        codes.append(f'{pref}{i:06d}')
print(','.join(codes[:1480]))
")" 2>&1)

echo "$BATCH1" | iconv -f GBK -t UTF-8 2>/dev/null > /tmp/batch1.txt 2>&1
echo "Batch1 $(wc -c < /tmp/batch1.txt) bytes"

# 3. 提取持仓股数据
echo ""
echo ">>> 持仓股: 五粮液 000858, 云南锗业 002428"
HOLDING_DATA=$(curl -s --connect-timeout 10 \
  -H "Referer: https://finance.sina.com.cn" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "http://hq.sinajs.cn/list=sz000858,sz002428" 2>&1)

echo "$HOLDING_DATA" | iconv -f GBK -t UTF-8 2>/dev/null

echo ""
echo "=== 数据采集完成 ==="
echo "Timestamp: $TIMESTAMP"
