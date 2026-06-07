# ClickHouse 物化视图模板

## 1. 创建聚合物化视图

```sql
-- 目标：将明细层聚合到汇总层，查询时直接查物化视图
CREATE MATERIALIZED VIEW {{数据库}}.{{视图名}}
ENGINE = {{引擎}}  -- SummingMergeTree / AggregatingMergeTree 等
PARTITION BY toYYYYMMDD({{分区字段}})
ORDER BY ({{排序键}})
AS SELECT
    toStartOfHour(timestamp) AS hour,
    {{分组字段1}},
    {{分组字段2}},
    countState() AS cnt,
    sumState({{数值}}) AS total
FROM {{数据库}}.{{源表}}
GROUP BY
    hour,
    {{分组字段1}},
    {{分组字段2}}
```

## 2. 查询物化视图

```sql
-- 使用聚合函数的 merge 语法查询
SELECT
    hour,
    {{分组字段1}},
    countMerge(cnt) AS cnt,
    sumMerge(total) AS total
FROM {{数据库}}.{{视图名}}
WHERE hour >= now() - INTERVAL {{N}} DAY
GROUP BY
    hour,
    {{分组字段1}}
ORDER BY hour
```

## 3. 替换物化视图 (需要先删重建)

```sql
DROP TABLE IF EXISTS {{数据库}}.{{视图名}};
-- 等待 DROP 完成后再执行 CREATE
```
