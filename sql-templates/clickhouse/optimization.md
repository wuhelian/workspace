# ClickHouse 性能优化 Checklist

## 查询前必检查

- [ ] **分区裁剪加了吗？** — `WHERE date = '...'` 或 `WHERE date >= '...'`，没有分区过滤等于全表扫描
- [ ] **排序键利用了吗？** — 条件里尽量带上 ORDER BY 的第一个字段
- [ ] **只取需要的列？** — 别 `SELECT *`，指定列名
- [ ] **数据量合适吗？** — 先 `SELECT count(*)` 摸清量级

## 常用优化技巧

### 1. PREWHERE 替代 WHERE（字符串过滤时）

```sql
-- CH 会自动优化，但手动指定更可控
SELECT {{列}}
FROM {{表}}
PREWHERE {{字符串列}} = '{{值}}'  -- 先过滤大字段
WHERE date = '{{分区}}'
```

### 2. 避免高基数 GROUP BY

```sql
-- ❌ 差：GROUP BY 用户ID（百万级）
-- ✅ 好：先粗粒度聚合，再细粒度
```

### 3. 大表 JOIN 优化

```sql
-- 右表如果能放进内存，用 JOIN 的 GLOBAL 模式
SELECT {{列}}
FROM {{大表}} AS a
GLOBAL JOIN {{小表}} AS b ON a.key = b.key
-- GLOBAL 会把右表广播到所有节点，避免分布式 join 的网络开销
```

### 4. 采样查询（非精确场景）

```sql
SELECT {{列}}
FROM {{表}} SAMPLE 0.1  -- 10% 采样，快速估算
WHERE {{条件}}
```

### 5. 不要用 subquery 做 JOIN 条件

```sql
-- ❌ 差
SELECT * FROM a WHERE a.id IN (SELECT id FROM b WHERE ...)

-- ✅ 好：用 JOIN 或者 GLOBAL IN
SELECT a.*
FROM a
INNER JOIN (SELECT DISTINCT id FROM b WHERE ...) AS b ON a.id = b.id

-- 或者用半连接
SELECT a.*
FROM a
SEMI LEFT JOIN b ON a.id = b.id
WHERE b.{{条件}}
```

### 6. Nullable 列处理

```sql
-- Nullable 列性能差，能用默认值就用
-- ❌ Nullable(String)
-- ✅ String DEFAULT ''
```

### 7. 利用 LIMIT 提前终止

```sql
-- 只需要 Top-N 时，CH 可以提前停止读取
SELECT {{列}} FROM {{表}} ORDER BY {{排序}} DESC LIMIT {{N}}
```
