---
title: "字节传输与串口使用指南"
category: "工程能力"
tags: ["desktop", "serial", "type/usage-guide"]
summary: "串口工厂注入、配置、短写处理、关闭失败重试与设备协议边界。"
created: 2026-10-20
updated: 2026-10-28
metadata_status: reviewed
home_area: theme
article_status: published
---

# 字节传输与串口


## 接入速查

| 接入项 | 要求 / 用法 |
| --- | --- |
| 环境与依赖 | 接口使用标准库；真实串口需要 `serial` extra |
| 核心入口 | `SerialConfig` / `SerialTransport` |
| 调用顺序 | 配置端口 → open → write/read → 协议层处理 → close |
| 关键边界 | 短写和驱动异常为 `TransportError`；不处理帧、CRC 或自动重连 |
| 方法 / 属性 | `open`, `write`, `read`, `close` |
| 版本与兼容 | [依赖说明](../架构与依赖.md) · [升级说明](../升级与兼容.md) |

## 接入流程

```mermaid
flowchart LR
    N0["配置端口"]
    N1["open"]
    N0 --> N1
    N2["write/read"]
    N1 --> N2
    N3["协议层处理"]
    N2 --> N3
    N4["close"]
    N3 --> N4
```


## 接入顺序

Transport 是字节 IO 协议，SerialTransport 是可选 pyserial 实现。先注入一个模拟工厂验证正常收发、短写和关闭路径，再接真实端口；上层自行处理帧提取、命令、应答、重试和心跳。

SerialConfig 要求非空白端口、正整数波特率、有限非负读写超时，bool 不当整数使用。默认 9600 波特率、读写各 1 秒；真实设备参数由应用明确配置。

## 错误与副作用

open 在已拥有句柄时幂等；read/write 在锁内串行化。write 必须完整写入后才 flush，短写和驱动错误转换为 TransportError，并保留底层 __cause__；不自动重试不确定的发送，避免重复触发设备操作。

close 失败保留句柄以便再次清理，成功才释放所有权。with SerialTransport(...) 会打开并在退出时关闭；如果驱动关闭失败，应用仍需记录并重试释放。它不代表 USB 断开后能无条件恢复同一物理连接。

## 资源与线程

一个对象拥有一个句柄；不要绕开该对象同时操作底层串口。读写超时只约束对应驱动调用，不能替代上层任务的取消策略。串口任务放入后台时由任务创建/关闭对象，不把 GUI 控件带进 worker。

[公开契约与最小例子](../contracts/transport.md) 展示工厂注入；[异常场景](../../examples/failure_scenarios.py) 展示短写不重试。测试入口为 tests/test_core.py、tests/test_contracts.py、tests/test_review_core.py、tests/test_extensions_core.py；真实端口与平台安装包仍由接入项目验收。
