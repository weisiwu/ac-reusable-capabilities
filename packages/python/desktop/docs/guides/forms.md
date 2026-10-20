---
title: "表单与详情使用指南"
category: "工程能力"
tags: ["desktop", "forms", "type/usage-guide"]
summary: "表单与详情的场景选择、接入步骤、错误处理、资源所有权与验证入口。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 表单与详情

## 适用场景

从统一字段描述组合本地编辑对话框与只读详情。

## 接口与接入

FieldSpec 描述字段、类型、required、choices、validate 以及 custom 工厂/取值器；FormDialog 提交 dict；DetailView 只展示。

字段键必须非空且唯一；配置 text/multiline/integer/boolean/choice/custom。必填判断保留 False 和 0；初始文本数值 0 不再被清空。

## 失败与边界

正常校验失败显示字段错误并保持对话框；自定义取值或校验抛错时发 validation_failed(error)，保持窗口可操作；成功发 submitted(dict) 并接受。

没有持久化、权限或跨字段依赖引擎。服务器端和写入边界仍应校验。自定义 widget_factory 及构造错误属于调用方配置错误。

## 线程与资源

控件、信号接收方和读写 values 均在 Qt 线程；取消不写数据；独立创建的 dialog 在使用完毕后 close/deleteLater。

## 示例与验证

- [最小调用与公开契约](../contracts/forms.md)。每个模块的最小例子均由 `python examples/check_contract_examples.py` 执行；Qt 模块追加 `--qt`。
- [异常与恢复场景](../../examples/failure_scenarios.py)；[可交互桌面示例](../../examples/qt_showcase.py)。
- 验证入口：`tests/test_qt.py、tests/test_qt_contracts.py、tests/test_review_qt.py`。

校验回调只返回用户可读错误或 None；异常走 validation_failed 交给应用记录。
