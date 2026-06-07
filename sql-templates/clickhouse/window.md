# ClickHouse 窗口函数模板

## 1. 分组 Top-N

```sql
SELECT *
FROM (
    SELECT
        {{分组字段}},
        {{排序字段}},
        {{其他字段}},
        row_number() OVER (
            PARTITION BY {{分组字段}}
            ORDER BY {{排序字段}} DESC
        ) AS rn
    FROM {{数据库}}.{{表名}}
    WHERE {{分区条件}}
)
WHERE rn <= {{N}}
```

## 2. 分组内排名 (允许并列)

```sql
SELECT
    {{分组字段}},
    {{数值字段}},
    dense_rank() OVER (
        PARTITION BY {{分组字段}}
        ORDER BY {{数值字段}} DESC
    ) AS rank
FROM {{数据库}}.{{表名}}
```

## 3. 移动平均 / 滑动窗口

```sql
SELECT
    date,
    {{维度}},
    {{数值}},
    avg({{数值}}) OVER (
        PARTITION BY {{维度}}
        ORDER BY date
        ROWS BETWEEN {{N}} PRECEDING AND CURRENT ROW
    ) AS moving_avg,
    sum({{数值}}) OVER (
        PARTITION BY {{维度}}
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_sum
FROM {{数据库}}.{{表名}}
WHERE date BETWEEN '{{开始}}' AND '{{结束}}'
```

## 4. 前后行对比 (LAG/LEAD)

```sql
SELECT
    date,
    {{数值}},
    lag({{数值}}, 1) OVER (PARTITION BY {{维度}} ORDER BY date) AS prev_day,
    lead({{数值}}, 1) OVER (PARTITION BY {{维度}} ORDER BY date) AS next_day,
    {{数值}} - lag({{数值}}, 1) OVER (PARTITION BY {{维度}} ORDER BY date) AS diff
FROM {{数据库}}.{{表名}}
```
