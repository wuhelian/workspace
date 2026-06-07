#!/bin/bash
# 零的每日通勤播报脚本 - 每天早上7:10被 cron 触发
# 获取天气并生成播报

# 获取 Open-Meteo 预报（今早7-8点）
WEATHER=$(curl -s "https://api.open-meteo.com/v1/forecast?latitude=22.35&longitude=113.45&hourly=temperature_2m,precipitation_probability,precipitation,weathercode&timezone=Asia/Shanghai&forecast_days=1")

# 解析数据
TEMP7=$(echo "$WEATHER" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['hourly']['temperature_2m'][7])" 2>/dev/null || echo "?")
TEMP8=$(echo "$WEATHER" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['hourly']['temperature_2m'][8])" 2>/dev/null || echo "?")
RAIN7=$(echo "$WEATHER" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['hourly']['precipitation_probability'][7])" 2>/dev/null || echo "?")
RAIN8=$(echo "$WEATHER" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['hourly']['precipitation_probability'][8])" 2>/dev/null || echo "?")

# 是否建议带伞
if [ "$RAIN7" != "?" ] && [ "$RAIN7" -gt 30 ]; then
  UMBRELLA="🌂 建议带伞，有$RAIN7%概率会下雨"
elif [ "$RAIN8" != "?" ] && [ "$RAIN8" -gt 30 ]; then
  UMBRELLA="🌂 建议带伞，8点后有$RAIN8%概率下雨"
else
  UMBRELLA="☀️ 不用带伞，今天降水概率低"
fi

# 当前温度取7点值
TEMP=$TEMP7

# 生成播报
cat << EOF
🌤 主人早上好！今日通勤播报：

🌡 气温 ${TEMP}°C ~ ${TEMP8}°C，${UMBRELLA}
🚗 三乡 → 珠海金鸡路 | 早高峰预估 45-60 分钟
💡 建议 7:20 前出发，避开最堵时段
🎯 今日数据：7点降水概率 ${RAIN7}%，8点 ${RAIN8}%

主人加油，今天也是元气满满的一天！🚗💨
EOF
