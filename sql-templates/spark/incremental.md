# Spark SQL 增量处理模板

## 1. 增量覆盖写 (Overwrite 分区)

```sql
-- 每次只处理增量数据，覆盖当天分区
INSERT OVERWRITE TABLE {{目标表}} PARTITION (dt = '{{日期}}')
SELECT
    {{列1}},
    {{列2}},
    current_timestamp() AS etl_time
FROM {{源表}}
WHERE dt = '{{日期}}'
```

## 2. 增量合并 (Merge Into, Spark 3.x)

```sql
-- 需要目标表支持 ACID（Delta Lake / Iceberg / Hudi）
MERGE INTO {{目标表}} AS target
USING {{增量表}} AS source
ON target.{{主键}} = source.{{主键}}
WHEN MATCHED THEN UPDATE SET
    target.{{字段1}} = source.{{字段1}},
    target.{{字段2}} = source.{{字段2}},
    target.update_time = current_timestamp()
WHEN NOT MATCHED THEN INSERT (
    {{字段1}}, {{字段2}}, create_time, update_time
) VALUES (
    source.{{字段1}}, source.{{字段2}},
    current_timestamp(), current_timestamp()
)
```

## 3. 增量追加 + 去重 (无 ACID 时)

```sql
-- 1) 先写入增量
INSERT INTO {{临时表}}
SELECT *, '{{日期}}' AS dt FROM {{源增量}};

-- 2) 全量拉取去重
INSERT OVERWRITE {{目标表}}
SELECT * FROM (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY {{主键}}
            ORDER BY update_time DESC
        ) AS rn
    FROM (
        SELECT * FROM {{目标表}} WHERE dt < '{{日期}}'
        UNION ALL
        SELECT * FROM {{临时表}}
    )
)
WHERE rn = 1
```

## 4. 增量标识常用方案

```sql
-- 方案A: 时间戳增量
WHERE update_time > '{{上次最大时间}}'

-- 方案B: 偏移量增量
WHERE id > {{上次最大ID}}

-- 方案C: 标志位
WHERE is_processed = 0
```
