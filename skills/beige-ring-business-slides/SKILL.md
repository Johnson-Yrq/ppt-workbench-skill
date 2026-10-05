---
name: beige-ring-business-slides
description: 在用户选择米白环线商务风格或续做该方向时制作可编辑离线 HTML 演示稿，以温暖米白、黑色无衬线、细线圆环和自然商务摄影呈现营销与商业计划，默认由用户自行导出和检查。
metadata:
  version: "1.0.0"
---

# 米白环线商务演示稿

整稿 style ID 为 `beige-ring-business`，正式版本 **1.0.0**，状态 **ready**。用户已于 **2026-10-05** 回复「采用」，批准当前中文样稿方向、正式接入与安装；正常制作无需再次确认该设计方向。批准语境与范围见 [来源记录](assets/reference-design/source-notes.md#批准状态与交付位置)。

先读 [设计系统](references/design-system.md)，准备照片时读 [配图流程](references/image-workflow.md)。本包独立维护页头、封面、字体、字阶、边距、圆环和摄影策略；内容结构、可编辑组件、播放器、保存与导出复用共享层。参考来源与逐页转译见 [来源记录](assets/reference-design/source-notes.md)。

## 已批准样稿

已批准的十页样稿以虚构品牌「回环办公」为例，依次展示营销封面、目录、目标、用户画像、执行节奏、预算、团队、渠道、营销组合及 KPI。所有人物姓名、计划与数据均明确标为虚构示例；十张照片为内置 imagegen 新生成素材，不冒充真实团队、客户或经营成果，不复用来源模板照片。

演讲型结构见 [deck.example.json](assets/deck.example.json)，阅读型示例见 [deck.reading.example.json](assets/deck.reading.example.json)。源码项目内样稿位于 `examples/beige-ring-business/米白环线商务-中文风格样稿.html` 和 `examples/beige-ring-business/米白环线商务-阅读型样稿.html`。正式项目使用共享构建器和 `deck.json`，按实际内容准备原创或用户提供的素材；维护风格样例时不启动真实演示稿的用途问卷。

本方向已满足共享 [新增独立风格包](../white-blue-slides/references/adding-styles.md#最小清单示例) 的样稿批准要求，历史草稿阶段不限制正常制作。将来另开独立方向时，才为新方向提供代表样稿并确认，不重复索取本方向的批准。

## 共享选版与正式制作

真实新稿沿用同级 [PPT 制作工作台](../ppt-workbench/SKILL.md) 已确认的风格和用途，只询问缺少的核心选择。直接指定本 Skill 表达风格选择；续做保留当前项目选择。根对象记录 `style: "beige-ring-business"` 和 `presentation_mode: "speech" / "reading"`，用途规则见 [演示稿类型](../white-blue-slides/references/presentation-modes.md)。

逐页按 [内容自主选版](../white-blue-slides/references/layout-selection.md) 判断关系、数量、素材与数据条件；按 [数据结构](../white-blue-slides/references/deck-format.md) 和 [共享布局](../white-blue-slides/references/shared-layouts.md) 写真实字段，保留 `layout_intent / layout_selection`、`visual.rationale` 与明确的 `requirements`。本次共享层新增 `hub_spoke / step_row`，共享构图总数为 20、可执行 profile 为 48；原 100 条来源和编号保持不变。布局不限定风格或用途，也不要求每份稿复刻样例的十页顺序。

演讲型突出核心判断，阅读型补齐上下文、机制、来源与边界，内容过多时拆页；不因 reading 用途自动使用 `layout: reading`。关系图、箭头、表格和圆环由可编辑结构与 CSS 承载，不烘焙成信息图片。图表遵循 [图表契约](../white-blue-slides/references/charts.md)，真实稿只使用有来源的数据。KPI `progress` 的百分比和条长由当前值与目标值计算；不要在其他文本中再写一份会失同步的数值。

有生图能力时主动生成与当前内容相关的独立商务照片。自然肤色、石材、木材和柔和日光保留真实色彩，不施加整稿灰阶。封面、纯表格、关系图与时间线可无图；照片、标题、人物身份和业务信息保持分离。

以同级 `white-blue-slides` 为 `<shared>`，准备内容与必需素材后构建：

```sh
python3 <shared>/scripts/prepare_images.py <project>/deck.json --out <project>/image-handoff
python3 <shared>/scripts/build_deck.py <project>/deck.json --out <project>/演示稿.html
```

演示稿的 `--draft` 仅供缺图预排，缺图稿不能冒充成品；它不改变本风格的 ready 状态。

## 交付与维护

默认交付可编辑、离线单文件 HTML，由用户自行导出和检查，不自动执行整稿内容审查、批量截图、逐页验收或导出检查。用户明确要求 PPTX、PDF 或代查时，完成相应产物与验证，不将已要求的导出留作可选后续。构建失败、结构错误与缺失资源须修复，见 [默认交付与职责](../white-blue-slides/references/export.md#默认交付与职责)。

主题和共享代码开发按 [开发验证](references/quality-check.md#风格开发与接入) 完成与改动相称的检查。同方向的已满足批准不重复索取；未来独立新方向仍需取得其自己的样稿批准。
