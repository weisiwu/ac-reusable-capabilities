---
version: 1
slug: "site-index-html"
primary_target: "site/index.html"
related_targets: ["site/assets/app.mjs","site/assets/docs.css","site/assets/style.css","site/docs_build.py"]
---

# 能力目录与单项体验

Mode: Read（目录和文档）；Operate（单项演示）。用户确认分组索引列表与独立演示页。统一文档风格是绑定条件，本次直接执行已确认方案，不开启新的风格选择。

## Direction contract
THESIS: 一份可进入的能力索引。目录负责选择，体验页只操作当前能力，文档负责深入解释。
OWN-WORLD: 技术标准索引的清楚分组、基线与编号之外的秩序；冷白正文、淡灰蓝导航面、深蓝操作与位置提示，系统中文无衬线。避免卡片套卡片。
STORY: 首页找到功能，进入已有数据的演示，按需要进入同风格文档；返回保留搜索与筛选。
FIRST VIEWPORT: 64px共享页头，232px导航栏；目录标题下是搜索与三个分组索引，单项体验替换整个主区，文档采用760px阅读列与章节目录。
FORM: 技术标准索引（七个候选的第6项）；用户钉住的文档风格与分组列表优先。seed:feb30da80cb78c97。候选依次为开发手册、部件参考、课程索引、线路索引、图书分类、技术标准索引、藏品登记。浏览器前进后退与移动导航开合是签名交互；当前选择与展开状态即时反馈，reduced-motion禁用非必要动画。外来候选与用户绑定的文档任务不匹配；保留其精确对齐、密度控制、状态可辨与顺序纪律。
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
