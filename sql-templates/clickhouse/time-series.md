# ClickHouse 时间序列模板

## 1. 按任意粒度聚合

```sql
-- 场景：原始数据是秒级，想聚合成分钟/小时/天级别
SELECT
    toStartOfInterval(timestamp, INTERVAL {{N}} {{单位}}) AS bucket,  -- 例如 5 MINUTE / 1 HOUR / 1 DAY
    {{分组字段}},
    count(*) AS cnt,
    sum({{数值}}) AS total
FROM {{数据库}}.{{表名}}
WHERE timestamp BETWEEN '{{开始}}' AND '{{结束}}'
GROUP BY
    bucket,
    {{分组字段}}
ORDER BY bucket
```

## 2. 补全缺失时间点 (With FILL)

```sql
SELECT
    toStartOfDay(date) AS day,
    {{分组字段}},
    count(*) AS cnt
FROM {{数据库}}.{{表名}}
WHERE date BETWEEN '{{开始}}' AND '{{结束}}'
GROUP BY
    day,
    {{分组字段}}
ORDER BY day
WITH FILL
    STEP toIntervalDay(1)
    -- 缺失的 cnt 自动填 0
```

## 3. 滚动窗口聚合 (最近 N 天)

```sql
-- 针对每一天，统计该天往前 N 天的累计值
SELECT
    date,
    sum({{数值}}) OVER (
        ORDER BY date
        RANGE BETWEEN {{N}} PRECEDING AND CURRENT ROW
    ) AS rolling_total
FROM (
    SELECT
        toDate(timestamp) AS date,
        sum({{数值}}) AS {{数值}}
    FROM {{数据库}}.{{表名}}
    WHERE timestamp >= '{{开始}}'
    GROUP BY date
)
ORDER BY date
```
