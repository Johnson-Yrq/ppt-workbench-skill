---
name: monochrome-editorial-slides
description: 在用户选择黑白编辑式风格或续做该风格项目时制作可编辑 HTML 演示稿；使用黑白页面、大标题、留白与丰富的冷调编辑摄影，交付前做基本排版 QA，默认由用户自行导出。未选风格时经 ppt-workbench 接入。
metadata:
  version: "0.3.0"
---

# 黑白编辑式演示稿

整稿 style ID 为 `monochrome-editorial`，清单状态为 **ready**。八页中文风格样稿的视觉方向已获确认，正式项目使用共享构建器与 `deck.json`；使用本风格无需重新确认设计方向。

先读 [设计系统](references/design-system.md)，写 `deck.json` 前读 [版式层次与文字页选版](references/layout-guide.md)，配图前读 [配图流程](references/image-workflow.md)。文字、胶囊、圆形指标与图表保持可编辑；有生图能力时主动生成多张内容相关照片，使摄影贯穿适合配图的页面，不限于大纲明确写“配图”的页面。纯文字、无图与固定构图要求优先。

## 默认交付

默认交付可编辑、离线单文件 HTML。交付前按共享 [基本排版 QA](../white-blue-slides/references/layout-qa.md) 运行 `audit_deck.cjs`，逐页看截图检查布局是否合理（碰撞、重心与留白、对齐、层次、断行、密度、图片裁切），修改并重建后再交付，交付时简述看过与改过的页。PPTX／PDF 由用户通过播放器自行导出；Agent 不自动导出、不做 PowerPoint 实看或播放／编辑回归。用户明确要求 PPTX、PDF 或更深入的检查时，完成所要求的部分。构建失败、结构错误与缺失资源须修复，见共享 [默认交付与职责](../white-blue-slides/references/export.md#默认交付与职责)。[检查参考](references/quality-check.md)补充本风格的看图要点。

## 共享选版与构建

先按共享 [制作大纲](../white-blue-slides/references/outline.md) 把用户内容转化为适合所选风格与用途的 `大纲.md`（逐页结论、关系与数量、上屏文字、版式、配图、讲稿与【待补】），再按大纲动手。

逐页按共享 [内容自主选版](../white-blue-slides/references/layout-selection.md) 判断关系、数量、素材与数据，用 `select_layout.py` 筛选候选。48 个执行策略都有真实渲染路径。本包使用共享布局，不把版式封存在专用渲染器。

从 [正式演讲示例](assets/deck.example.json) 或 [正式阅读示例](assets/deck.reading.example.json) 了解实际数据字段，再按大纲选择问题分栏、圆形指标、服务块、独立图表、照片转场或其他共享结构。演讲型多图与纯文字内页均按内容选用；不硬塞进 `reading`，也不为旧模板给无图页添加无关图片。历史独立样稿仅保留为视觉转译记录。

`<shared>` 为同级 `white-blue-slides`。准备真实文字、数据与必需素材后直接构建，修复构建失败并交付：

```sh
python3 <shared>/scripts/build_deck.py <project>/deck.json --out <project>/演示稿.html
```

单页 `surface: light / dark`、无图大字封面与尾页，以及本包独立的页头和字阶均由正式风格配置提供。新增通用结构继续进入共享层，供全部风格使用；将来另开独立设计方向时，才按共享 [接入规范](../white-blue-slides/references/adding-styles.md) 提供代表样稿并取得该方向的批准。

## 制作约定

- 已选择本风格时不重新询问方向；仅确认尚缺的演讲／阅读用途。根对象记录 style 与 presentation_mode。
- `light` 与 `dark` 是本风格内的页面表面，不是逐页更换 style。黑底页用于问题、能力或关键数据节点，按内容安排，不机械逐页切换。
- 大字封面、底部标题、多栏问题、矩形与圆形摄影、满版照片章节页、非对称能力、圆形指标、灰阶图表是主要视觉语法。根据内容选择，不要求每次凑齐。
- 演讲型保留一条结论与少量支撑；阅读型保留解释、来源与边界。用途不限制布局、图片比例或统一字号，按内容选共享结构。
- 页头、封面尾页、字阶与边距由本包独立设计，不继承最早三个风格的六种页头；共享的是主体布局与功能。
- 同级 `white-blue-slides` 为共享套件；复用其 [数据结构](../white-blue-slides/references/deck-format.md)、[类型规则](../white-blue-slides/references/presentation-modes.md)、[图表契约](../white-blue-slides/references/charts.md) 与 [导出规范](../white-blue-slides/references/export.md)，不读取它的视觉规范作为本包主题。
- 播放器保留“导出 PPTX”与“导出 PDF / 打印”按钮供用户使用，不把导出作为默认制作步骤；基本排版 QA 是默认步骤。
