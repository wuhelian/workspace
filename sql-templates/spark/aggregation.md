# Spark SQL 通用模板

## 1. 分组聚合

```sql
SELECT
    {{分组字段1}},
    {{分组字段2}},
    COUNT(DISTINCT {{去重列}}) AS uv,
    COUNT(*) AS pv,
    SUM({{数值列}}) AS total,
    AVG({{数值列}}) AS avg_val,
    -- 百分位（Spark 3.1+）
    PERCENTILE_APPROX({{数值列}}, 0.5) AS median,
    PERCENTILE_APPROX({{数值列}}, 0.9) AS p90
FROM {{数据库}}.{{表名}}
WHERE {{分区条件}}
  AND {{过滤条件}}
GROUP BY {{分组字段1}}, {{分组字段2}}
```

## 2. 窗口函数 — Top-N

```sql
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY {{分组字段}}
            ORDER BY {{排序字段}} DESC
        ) AS rn
    FROM {{数据库}}.{{表名}}
    WHERE {{分区条件}}
)
SELECT * FROM ranked WHERE rn <= {{N}}
```

## 3. 窗口函数 — 移动平均

```sql
SELECT
    date,
    {{数值}},
    AVG({{数值}}) OVER (
        PARTITION BY {{维度}}
        ORDER BY date
        ROWS BETWEEN {{N}} PRECEDING AND CURRENT ROW
    ) AS moving_avg,
    SUM({{数值}}) OVER (
        PARTITION BY {{维度}}
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_sum,
    LAG({{数值}}, 1) OVER (
        PARTITION BY {{维度}} ORDER BY date
    ) AS prev_value
FROM {{数据库}}.{{表名}}
WHERE date BETWEEN '{{开始}}' AND '{{结束}}'
```

## 4. 多表关联

```sql
-- Spark 3.x 支持 ANSI JOIN 和 hint 优化
SELECT /*+ BROADCAST({{小表}}) */
    a.{{字段}},
    b.{{字段}},
    a.{{数值}} * b.{{比例}} AS calculated
FROM {{数据库}}.{{大表}} AS a
INNER JOIN {{数据库}}.{{小表}} AS b
    ON a.{{关联键}} = b.{{关联键}}
WHERE a.dt = '{{分区日期}}'
```
