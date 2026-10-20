---
title: "常见问题"
category: "工程能力"
tags: ["type/handbook", "能力复用"]
summary: "按安装、运行、显示器和生命周期定位 demo 与接入问题。"
created: 2026-10-20
updated: 2026-10-20
metadata_status: reviewed
home_area: theme
article_status: published
---

# 常见问题

| 现象 | 检查与处理 |
| --- | --- |
| `No module named ctf_desktop` | 用运行 demo 的同一解释器执行 `python -m pip install './packages/python/desktop'`；不要在仓库根直接 `pip install .` |
| 缺 PyQt5 | 安装 `./packages/python/desktop[qt]`；基础 demo 无需 Qt |
| UI 无法连接显示器 | 交互模式需要图形会话；自动验证使用 offscreen 与 `--smoke`，不要在 offscreen 下等待交互窗口 |
| `--smoke` 参数被拒绝 | 只有 desktop-ui 和 desktop-search 接受；其他入口自动结束 |
| 不清楚命令是否会自动退出 | 查 `python demo/run.py --list` 与 [清单](../demo/README.md)；UI 交互模式手动关闭窗口 |
| 示例成功但设备无响应 | 示例不连接真实设备；接入应用另行验证端口、协议与打印提交 |
| 搜索关闭等待较久 | 检查操作是否观察取消 Event，以及每次外部 IO 是否有有限超时；不能安全强杀 Python 线程 |
| 恢复失败或备份目标已存在 | 不覆盖现有快照，先读 [存储指南](../packages/python/desktop/docs/guides/storage.md)，检查停写、连接与文件系统硬链接支持 |
| 克隆后能力与安装来源不同 | `python -m pip show common-tech-framework-desktop` 核对安装位置；换来源后在隔离环境重新安装 |

检查工具报错时先按报错路径核对文件，不以手改成功状态绕过失败。进一步定位参考 [Desktop 排障](../packages/python/desktop/docs/常见问题与排障.md) 与 [验证命令](../docs/验证与维护.md)。
