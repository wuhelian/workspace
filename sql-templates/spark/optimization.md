# Spark SQL 优化 Checklist

## 配置层面

- [ ] **AQE 开了吗？** `spark.sql.adaptive.enabled=true` (Spark 3.0+) — 自动优化
- [ ] **动态分区裁剪开了吗？** `spark.sql.optimizer.dynamicPartitionPruning.enabled=true`
- [ ] **Shuffle 分区数合理吗？** `spark.sql.shuffle.partitions` — 数据量大设大(400-2000)，小数据别太大

## SQL 写法

### 1. 优先用 BROADCAST hint

```sql
-- 小表 (< 10MB) 强制广播，避免 shuffle
SELECT /*+ BROADCAST(小表) */ ...
```

### 2. 避免 COUNT DISTINCT 过多

```sql
-- ❌ 差：多次 COUNT DISTINCT 导致多次 Shuffle
SELECT
    COUNT(DISTINCT col1),
    COUNT(DISTINCT col2),
    COUNT(DISTINCT col3)
FROM t

-- ✅ 好：使用 approx_count_distinct 或拆成多次查询
SELECT
    approx_count_distinct(col1),
    approx_count_distinct(col2),
    approx_count_distinct(col3)
FROM t
```

### 3. 分区过滤加在最外层

```sql
-- Spark 不会下推子查询里的分区过滤
-- ✅ 在最终 SELECT 里加分区条件
```

### 4. 避免数据倾斜

```sql
-- 如果 GROUP BY 的键分布不均，用 salting
SELECT
    CONCAT({{倾斜键}}, '_', FLOOR(RAND() * {{N}})) AS salted_key,
    COUNT(*)
FROM t
GROUP BY salted_key
-- 然后再聚合一次去掉 salt
```

### 5. 列裁剪

```sql
-- ❌ 不需要的列别 SELECT
-- ✅ 只取需要的字段
```
