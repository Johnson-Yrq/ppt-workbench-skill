---
name: monochrome-marble-slides
description: 在用户选择黑白大理石商务风格或续做该方向时，制作可编辑离线 HTML 演示稿，以黑白反转、大衬线字、天然大理石纹理与自然彩色商务摄影呈现商业计划和公司介绍，交付前做基本排版 QA，默认由用户自行导出。
metadata:
  version: "1.0.0"
---

# 黑白大理石商务演示稿

整稿 style ID 为 `monochrome-marble`，正式版本 **1.0.0**，状态 **ready**。用户已于 **2026-10-05** 明确回复「采用，安装，并提交」，批准当前中文样稿方向、正式接入、安装及本次相关改动提交；同方向制作无需再次确认视觉。批准范围与交付位置见 [来源说明](references/source-notes.md#批准状态与交付位置)，安装完成状态以实际安装位置验证及主任务报告为准。

先读 [设计系统](references/design-system.md)；写 `deck.json` 前读 [版式选用与内容预算](references/layout-guide.md)，优先使用本主题精调过的结构并控制每页字数；准备图片时读 [配图流程](references/image-workflow.md)。本包独立维护页头、封面、字体、字阶、留白、黑白表面和大理石纹理；内容字段、共享构图、播放器、编辑、保存与导出复用共享层。原参考与逐页转译见 [来源说明](references/source-notes.md)。

## 已批准样稿

中文样稿以虚构的「砚序咨询」2026 业务计划为例，覆盖封面、目录、公司叙事、团队、行业、市场、能力、指标及联系信息。人物姓名、职能、计划与数字均为示意；生成照片不代表真实员工、客户或项目成果。参考截图只作为设计依据，不复用其中的照片、业务文案、人物身份或数据。

样稿项目位于源码中的 `examples/monochrome-marble/`，提示词与素材出处保存在该目录的 `image-prompts.json` 和 `image-sources.json`。本包的结构示例分别使用 `assets/deck.example.json` 与 `assets/deck.reading.example.json`；维护风格样例时不启动真实演示稿的用途问卷。实际验证结果单独记录，历史草稿仅用于追溯，不构成正常制作的待批准节点。

本方向已满足 [新增独立风格包](../white-blue-slides/references/adding-styles.md#最小清单示例) 的样稿批准要求，并具备安装和相关改动提交授权；继续完成接入、验证和安装时不重复索取同一批准。未来另开独立视觉方向，仍需为新方向提供可审阅样稿并取得其自身的批准。

## 内容制作与共享选版

真实新稿沿用同级 [PPT 制作工作台](../ppt-workbench/SKILL.md) 已确认的风格与用途，只询问缺少的核心信息。直接指定本 Skill 表达风格选择，续做保留已有选择。根对象记录 `style: "monochrome-marble"` 与 `presentation_mode: "speech" / "reading"`，用途规则见 [演示稿类型](../white-blue-slides/references/presentation-modes.md)。

先按共享 [制作大纲](../white-blue-slides/references/outline.md) 把用户内容转化为适合所选风格与用途的 `大纲.md`（逐页结论、关系与数量、上屏文字、版式、配图、讲稿与【待补】），再按大纲动手。

逐页按 [内容自主选版](../white-blue-slides/references/layout-selection.md) 判断关系、数量、素材与数据条件，再按 [数据结构](../white-blue-slides/references/deck-format.md) 和 [共享布局](../white-blue-slides/references/shared-layouts.md) 写字段，明确要求写入 `visual.requirements`。共享库维持 **20 种构图、48 个 profile**；本方向复用既有布局，只扩展目录和编辑分栏的通用容量与组件，不把十五页参考当作十五种新布局。

`editorial_columns` 可组合文字、照片、人物、无序图标分组与完整图表；标题独栏只有在该栏承载可见页标题，或具有自己的 heading 时才能省略正文。`shared.editorial_charts` 按实际图表栏数计 2–6 项，每栏必须有真实数据、单位和来源。详细合同见 [图表契约](../white-blue-slides/references/charts.md)。演讲型突出主要判断，阅读型补齐上下文、机制、来源和边界；阅读用途不自动等同 `layout: reading`，内容过多时拆页。

采用独立页头，不填写六种预设的 `header` 字段。可用表面仅为 `light / dark / marble-light / marble-dark / inset-dark`，由页面内容和节奏选择。图标按语义选用，页码、短线、标题、表格、图表和业务数字全部保留可编辑内容，不放进背景图。

有生图能力时主动生成当前内容需要的原创照片。保留自然肤色与场景色；大理石使用独立黑白纹理，页面负责纹理的尺度、位置和透明度。封面、纯表格、图表或纯文字页可以无业务照片，不为填充模板空位索取无关素材。

以同级 `white-blue-slides` 为 `<shared>`，准备内容和必需素材再构建：

```sh
python3 <shared>/scripts/prepare_images.py <project>/deck.json --out <project>/image-handoff
python3 <shared>/scripts/build_deck.py <project>/deck.json --out <project>/演示稿.html
```

演示稿 `--draft` 仅供缺图预排，缺图稿不能冒充成品；它不改变本风格的 ready 状态。

## 交付与维护

默认交付可编辑、离线单文件 HTML。交付前按共享 [基本排版 QA](../white-blue-slides/references/layout-qa.md) 运行 `audit_deck.cjs`，逐页看截图检查布局是否合理（碰撞、重心与留白、对齐、层次、断行、密度、图片裁切），修改并重建后再交付，交付时简述看过与改过的页。PPTX／PDF 由用户通过播放器自行导出；Agent 不自动导出、不做 PowerPoint 实看或播放／编辑回归。用户明确要求 PPTX、PDF 或更深入的检查时，完成所要求的部分。构建失败、结构错误与缺失资源须修复，见共享 [默认交付与职责](../white-blue-slides/references/export.md#默认交付与职责)。

主题和共享代码开发必须按 [开发验证](references/quality-check.md#风格开发与接入) 完成与改动相称的 QA，由 Agent 检查并修复，不将内部验收转交用户。本方向已满足的批准不重复索取；未来独立新方向的采用与安装确认仍在可审阅样稿之后按原定范围执行。
