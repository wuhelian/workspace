# SQL 模板库

## 目录结构

```
sql-templates/
├── clickhouse/       # ClickHouse 专用模板
│   ├── aggregation.md
│   ├── window.md
│   ├── time-series.md
│   ├── materialized-view.md
│   └── optimization.md
├── spark/            # Spark SQL 专用模板
│   ├── aggregation.md
│   ├── window.md
│   ├── incremental.md
│   └── optimization.md
└── common/           # 通用模板
    ├── date-dim.md
    ├── pagination.md
    └── dedup.md
```

## 使用方式

1. 找到对应场景的模板文件
2. 替换 `{{变量名}}` 部分
3. 先在小数据量验证逻辑
4. 上全量跑

## 模板列表速查

| 场景 | ClickHouse | Spark SQL |
|------|-----------|-----------|
| 分组聚合统计 | ✅ | ✅ |
| 窗口函数(row_number/dense_rank) | ✅ | ✅ |
| 时间序列/滚动窗口 | ✅ | ✅ |
| 增量数据同步 | - | ✅ |
| 物化视图 | ✅ | - |
| 去重策略 | ✅ | ✅ |
| 分页查询 | ✅ | ✅ |
