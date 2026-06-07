# 通用模板

## 1. 日期维度生成 (通用)

```sql
-- ClickHouse 版
SELECT
    toDate(date) AS date,
    toYear(date) AS year,
    toMonth(date) AS month,
    toDayOfMonth(date) AS day,
    toDayOfWeek(date) AS day_of_week,
    toQuarter(date) AS quarter,
    formatDateTime(date, '%W') AS weekday_name,
    CASE
        WHEN toDayOfWeek(date) IN (6, 7) THEN 1
        ELSE 0
    END AS is_weekend
FROM (
    SELECT arrayJoin(
        range(toUInt32(toDate('{{开始}}')), toUInt32(toDate('{{结束}}')) + 1)
    ) AS date
)
```

```sql
-- Spark SQL 版
SELECT
    date,
    YEAR(date) AS year,
    MONTH(date) AS month,
    DAY(date) AS day,
    DAYOFWEEK(date) AS day_of_week,
    QUARTER(date) AS quarter,
    DATE_FORMAT(date, 'EEEE') AS weekday_name,
    CASE WHEN DAYOFWEEK(date) IN (1, 7) THEN 1 ELSE 0 END AS is_weekend
FROM (
    SELECT sequence(
        DATE('{{开始}}'), DATE('{{结束}}'), INTERVAL 1 DAY
    ) AS date_range
)
LATERAL VIEW EXPLODE(date_range) AS date
```

## 2. 分页查询

```sql
-- CH 版 (利用排序键优化)
SELECT {{列}}
FROM {{表}}
WHERE {{排序键}} > {{上一页最后值}}
  AND {{分区条件}}
ORDER BY {{排序键}}
LIMIT {{page_size}}
-- 比 OFFSET 高效得多
```

```sql
-- Spark SQL 版
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY {{排序键}}) AS rn
    FROM {{表}}
    WHERE {{分区条件}}
)
WHERE rn BETWEEN {{offset + 1}} AND {{offset + page_size}}
```

## 3. 去重策略

### 按主键保留最新一条

```sql
SELECT *
FROM (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY {{主键}}
            ORDER BY {{更新时间}} DESC
        ) AS rn
    FROM {{表}}
)
WHERE rn = 1
```

### 去重统计 (近似)

```sql
-- CH: uniq 比 count(DISTINCT) 快且近似
SELECT uniq({{去重列}}) AS approx_uv FROM {{表}}

-- Spark: approx_count_distinct
SELECT approx_count_distinct({{去重列}}) AS approx_uv FROM {{表}}
```
