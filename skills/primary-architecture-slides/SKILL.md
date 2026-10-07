---
name: primary-architecture-slides
description: 在用户选择原色建筑编辑式风格或续做该方向时，制作可编辑离线 HTML 演示稿。白底黑字、窄高大字、错位文字栏、黑白建筑摄影与四色章节页；使用独立页头和共享布局，交付前做基本排版 QA，默认由用户自行导出。
metadata:
  version: "1.0.0"
---

# 原色建筑编辑式演示稿

整稿 style ID 为 `primary-architecture`，状态为 **ready**，正式版本 **1.0.0**。用户已于 **2026-10-05** 明确采用中文转译样稿，并批准正式接入与安装；正常制作无需再次确认该设计方向。状态、参考、批准与转译范围见 [来源记录](assets/reference-design/source-notes.md)。

先读 [设计系统](references/design-system.md)，准备图片时读 [配图流程](references/image-workflow.md)。本包独立设计页头、封面尾页、字阶、边距与配色；共享内容布局、可编辑文字、图表和播放器。原六种页头不属于本风格，阅读型也不强制采用等分图区或 `layout: reading`。

## 已批准样稿

已批准的中文转译采用十页虚构建筑工作室示例，展示纯文字封面、四色数字转场、错位栏、团队肖像、价值观分组、显示器画面与建筑拼贴。历史样稿位置为 `examples/primary-architecture/原色建筑编辑式-中文风格样稿.html`；示例品牌、人物身份、项目与文案均不冒充真实履历。正式项目使用共享构建器和 `deck.json`，根据实际内容生成原创照片，不复制 Canva 模板照片、占位文案或团队信息。

本方向的样稿确认已满足共享 [新增独立风格包](../white-blue-slides/references/adding-styles.md#最小清单示例) 的批准要求，不把历史 draft 阶段用于普通制作，也不重复索取同一方向的批准。将来另开独立方向时，才提供新代表样稿并按该规则确认；开发本 Skill 或制作维护样例不启动真实演示稿的用途问卷。

## 共享选版与正式制作

真实新稿沿用同级 [PPT 制作工作台](../ppt-workbench/SKILL.md) 已确认的风格和演讲／阅读用途，仅询问缺少的选择。直接指定本 Skill 已表达风格选择；续做项目保留当前选择。根对象记录 `style: "primary-architecture"` 与 `presentation_mode: "speech" / "reading"`。

先按共享 [制作大纲](../white-blue-slides/references/outline.md) 把用户内容转化为适合所选风格与用途的 `大纲.md`（逐页结论、关系与数量、上屏文字、版式、配图、讲稿与【待补】），再按大纲动手。

逐页按共享 [内容自主选版](../white-blue-slides/references/layout-selection.md) 判断关系、数量、素材与数据条件，用 `select_layout.py` 从真实可执行策略筛选；新增 `type_poster` 与 `editorial_columns` 同样进入共享层，所有风格可用；本包不维护私有渲染器。明确要求写入 `visual.requirements`。

按 [数据结构](../white-blue-slides/references/deck-format.md)、[共享布局](../white-blue-slides/references/shared-layouts.md) 组织真实字段。演讲型保留结论和少量支撑；阅读型保留机制、来源与边界，按实际内容选择栏目和图片数量，必要时拆页。不能为仿照拉丁文字的窄栏密度而把中文压得过小。

有生图能力时主动为适合配图的页面生成多张独立、相关的照片，让摄影贯穿内容页；纯文字封面、数字章节页及用户明确要求无图的页面保持无图。标题、姓名、角色、章节数字、图注与真实数据都由可编辑页面承载，不烘焙进照片。

正式项目使用同级 `white-blue-slides` 作为 `<shared>`，准备必需内容与素材后直接构建；`--draft` 仅供缺图预排，缺图草稿不能作为成品交付：

```sh
python3 <shared>/scripts/prepare_images.py <project>/deck.json --out <project>/image-handoff
python3 <shared>/scripts/build_deck.py <project>/deck.json --out <project>/演示稿.html
```

## 交付与维护

默认交付可编辑、离线单文件 HTML。交付前按共享 [基本排版 QA](../white-blue-slides/references/layout-qa.md) 运行 `audit_deck.cjs`，逐页看截图检查布局是否合理（碰撞、重心与留白、对齐、层次、断行、密度、图片裁切），修改并重建后再交付，交付时简述看过与改过的页。PPTX／PDF 由用户通过播放器自行导出；Agent 不自动导出、不做 PowerPoint 实看或播放／编辑回归。用户明确要求 PPTX、PDF 或更深入的检查时，完成所要求的部分。构建失败、结构错误与缺失资源须修复，见共享 [默认交付与职责](../white-blue-slides/references/export.md#默认交付与职责)。

开发本风格及其共享布局时，才按 [开发验证](references/quality-check.md#风格开发与接入) 完成与改动相称的结构、视觉与功能验证。已完成的批准不重复索取；将来另开独立方向时才建立新的方向批准。只修改说明文档不触发整稿检查或导出。
