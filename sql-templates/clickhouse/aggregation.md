# ClickHouse 通用聚合模板

## 1. 多维度分组统计

```sql
SELECT
    {{维度列1}},
    {{维度列2}},
    count(DISTINCT {{去重列}}) AS uv,
    count(*) AS pv,
    sum({{数值列}}) AS total_amount,
    avg({{数值列}}) AS avg_amount,
    -- 百分位
    quantile(0.5)({{数值列}}) AS median_value,
    quantile(0.9)({{数值列}}) AS p90_value,
    quantile(0.99)({{数值列}}) AS p99_value
FROM {{数据库}}.{{表名}}
WHERE {{分区条件}}  -- 务必加分区过滤！
  AND {{过滤条件}}
GROUP BY
    {{维度列1}},
    {{维度列2}}
ORDER BY
    total_amount DESC
LIMIT {{N}}
```

## 2. 累加/累计聚合 (Running Total)

```sql
SELECT
    date,
    value,
    sum(value) OVER (ORDER BY date) AS running_total,
    round(avg(value) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS ma_7
FROM {{数据库}}.{{表名}}
WHERE date BETWEEN '{{开始日期}}' AND '{{结束日期}}'
ORDER BY date
```

## 3. 多表关联聚合

```sql
SELECT
    a.{{分组字段}},
    count(*) AS cnt,
    sum(b.{{数值}}) AS total
FROM {{数据库}}.{{左表}} AS a
INNER JOIN {{数据库}}.{{右表}} AS b
    ON a.{{关联键}} = b.{{关联键}}
    AND a.{{分区键}} = b.{{分区键}}  -- CH 中尽量带分区键提升性能
WHERE a.date = '{{目标日期}}'
GROUP BY a.{{分组字段}}
```

## 4. 环比/同比计算

```sql
WITH current AS (
    SELECT date, sum({{数值}}) AS value
    FROM {{数据库}}.{{表名}}
    WHERE date BETWEEN '{{当期开始}}' AND '{{当期结束}}'
    GROUP BY date
),
prev AS (
    SELECT
        date + INTERVAL '{{周期}}' AS anchor_date,  -- 例如 1 DAY / 1 MONTH
        sum({{数值}}) AS value
    FROM {{数据库}}.{{表名}}
    WHERE date BETWEEN '{{上期开始}}' AND '{{上期结束}}'
    GROUP BY date
)
SELECT
    c.date,
    c.value AS current_value,
    p.value AS prev_value,
    round((c.value - p.value) / p.value * 100, 2) AS growth_rate_pct
FROM current AS c
LEFT JOIN prev AS p ON c.date = p.anchor_date
ORDER BY c.date
```
