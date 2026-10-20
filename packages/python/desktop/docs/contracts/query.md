---
title: "desktop.query 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "query"]
summary: "query 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.query

导入路径：`ctf_desktop.query`。标识一经收录保持稳定。下列契约包含适用边界；外部回调与业务事务由接入方管理。

## PageRequest

稳定标识：`desktop.query.PageRequest`

Immutable number=1 and size=20; require positive integers (bool rejected), else ValueError; no IO.

## PageRequest.offset

稳定标识：`desktop.query.PageRequest.offset`

Return zero-based (number-1)*size without changing state.

## PageResult

稳定标识：`desktop.query.PageResult`

Immutable items tuple, nonnegative integer total and PageRequest; reject negative/noninteger totals; no IO.

## PageResult.pages

稳定标识：`desktop.query.PageResult.pages`

Return ceiling(total/size), at least one page even for an empty result.

## SqlWhere

稳定标识：`desktop.query.SqlWhere`

Copy a caller-trusted column whitelist; accumulate SQLite ? predicates and bound values; never execute SQL.

## SqlWhere.equal

稳定标识：`desktop.query.SqlWhere.equal`

Skip None/empty text; otherwise whitelist field or raise ValueError, append equality and return self.

## SqlWhere.contains

稳定标识：`desktop.query.SqlWhere.contains`

Skip empty text; whitelist field, escape literal percent/underscore/backslash, append LIKE and return self.

## SqlWhere.range

稳定标识：`desktop.query.SqlWhere.range`

Whitelist field even for empty bounds; append inclusive start and exclusive end when not None; return self.

## SqlWhere.build

稳定标识：`desktop.query.SqlWhere.build`

Return detached (WHERE text, bound-value tuple); empty builder returns empty text and tuple; repeatable without mutation.

## 最小调用示例

```python
from ctf_desktop.query import PageRequest, PageResult, SqlWhere
request = PageRequest(2, 10)
assert request.offset == 10
assert PageResult((), 0, request).pages == 1
assert SqlWhere({"name": "name"}).equal("name", "example").build() == ("WHERE name = ?", ("example",))
```
