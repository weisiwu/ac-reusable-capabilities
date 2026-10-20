---
title: "desktop.crud 公开契约"
category: "工程能力"
tags: ["type/api-contract", "desktop", "crud"]
summary: "crud 模块的公开输入输出、边界与副作用。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# desktop.crud

导入路径：`ctf_desktop.crud`。标识一经收录保持稳定。下列契约包含适用边界；外部回调与业务事务由接入方管理。

## CrudRepository

稳定标识：`desktop.crud.CrudRepository`

Host-owned list/get/create/update/delete protocol; transaction and identity semantics belong to the host.

## CrudRepository.list_page

稳定标识：`desktop.crud.CrudRepository.list_page`

Return PageResult for PageRequest and filter mapping; host owns filtering and IO errors.

## CrudRepository.get

稳定标识：`desktop.crud.CrudRepository.get`

Return record mapping or None for identity; host owns IO errors.

## CrudRepository.create

稳定标识：`desktop.crud.CrudRepository.create`

Persist supplied mapping and return its identity; host owns transaction/errors.

## CrudRepository.update

稳定标识：`desktop.crud.CrudRepository.update`

Update identity using values and return None; host defines missing-row behavior.

## CrudRepository.delete

稳定标识：`desktop.crud.CrudRepository.delete`

Delete identity and return None; host defines missing-row behavior.

## CrudController

稳定标识：`desktop.crud.CrudController`

Require repository and explicit authorization callback; optional validation/change callbacks; no UI or persistence implementation.

## CrudController.list_page

稳定标识：`desktop.crud.CrudController.list_page`

Authorize list before repository access; None filters become empty mapping; return PageResult; errors propagate.

## CrudController.detail

稳定标识：`desktop.crud.CrudController.detail`

Authorize read on identity before repository get; return mapping or None; errors propagate.

## CrudController.create

稳定标识：`desktop.crud.CrudController.create`

Authorize create, validate, write then notify changed; return identity; errors propagate; notification failure cannot roll back host write.

## CrudController.update

稳定标识：`desktop.crud.CrudController.update`

Authorize update, validate, write then notify changed; return None; errors propagate, no implicit transaction.

## CrudController.delete

稳定标识：`desktop.crud.CrudController.delete`

Authorize delete before write then notify changed; return None; errors propagate, no implicit transaction.

## 最小调用示例

```python
from ctf_desktop.crud import CrudController
class Repository:
    def create(self, values): return values["name"]
controller = CrudController(Repository(), authorize=lambda action, resource: None)
assert controller.create({"name": "sample"}) == "sample"
```
