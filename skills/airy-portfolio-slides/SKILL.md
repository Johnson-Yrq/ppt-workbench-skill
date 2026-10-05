---
name: airy-portfolio-slides
description: 在用户选择留白衬线影集风格或续做该方向时，制作可编辑离线 HTML 演示稿，以近白纸色、黑色衬线字、宽阔留白与自然彩色摄影呈现作品，默认由用户自行导出和检查。
metadata:
  version: "1.0.0"
---

# 留白衬线影集演示稿

整稿 style ID 为 `airy-portfolio`，正式版本 **1.0.0**，状态 **ready**。用户已于 **2026-10-05** 明确回复「采用，并安装」，批准本方向的中文样稿、正式接入与安装；正常制作无需再次确认该设计方向。批准范围和历史转译见 [来源记录](assets/reference-design/source-notes.md#批准状态与交付位置)。

先读 [设计系统](references/design-system.md)，准备图片时读 [配图流程](references/image-workflow.md)。本包独立维护页头、页脚、封面、字体、字阶、边距与摄影策略；共享内容结构、编辑、保存、播放器及导出功能。参考来源和逐页转译见 [来源记录](assets/reference-design/source-notes.md)。

## 已批准样稿

已批准的十页中文样稿以虚构摄影工作室「拾光影像」为例，展示居中封面、纯文字主张、关于、右下理念，以及旅行、食物和聚会作品。正文与讲稿明确记录其示例性质；照片为新生成的原创素材，不冒充真实客户、团队或作品履历。

演讲型结构见 [deck.example.json](assets/deck.example.json)，阅读型内容示例见 [deck.reading.example.json](assets/deck.reading.example.json)。项目内中文样稿路径为 `examples/airy-portfolio/留白衬线影集-中文风格样稿.html`。正式项目使用共享构建器和 `deck.json`，按实际内容准备原创或用户提供的照片。开发和维护样例不启动真实演示稿的用途问卷。

本方向已满足共享 [新增独立风格包](../white-blue-slides/references/adding-styles.md#最小清单示例) 的样稿批准要求；历史草稿阶段不限制正常制作。将来另开独立方向时，才为新方向提供代表样稿并确认，不重复索取本方向的批准。

## 共享选版与正式制作

真实新稿沿用同级 [PPT 制作工作台](../ppt-workbench/SKILL.md) 已确认的风格和演讲／阅读用途，只询问缺少的选择。直接指定本 Skill 表达风格选择，续做保留当前项目选择；其用途规则见 [演示稿类型](../white-blue-slides/references/presentation-modes.md)。根对象记录 `style: "airy-portfolio"` 与 `presentation_mode: "speech" / "reading"`。

逐页按共享 [内容自主选版](../white-blue-slides/references/layout-selection.md) 判断关系、数量、素材和数据条件。使用 [数据结构](../white-blue-slides/references/deck-format.md)、[共享布局](../white-blue-slides/references/shared-layouts.md) 的真实字段，保留 `layout_intent / layout_selection`，理由沿用 `visual.rationale`，明确要求写入 `requirements`。当前共享构图为 20 种、可执行 profile 为 48 个；本方向复用并扩展 `type_poster / editorial_columns`，不维护私有版式渲染器，也不把来源编号当作 layout。

演讲型突出照片和核心判断，阅读型补齐机制、上下文、来源与边界，必要时拆页。用途不强制采用 `layout: reading`、等分图区或另一套字阶。图表遵循 [图表契约](../white-blue-slides/references/charts.md)，仅使用真实数据。文字与照片的数量来自内容，不要求每份稿复刻样稿的十页顺序。

有生图能力时主动准备适合内容的独立摄影素材。彩色旅行、食物和相聚摄影保持自然色彩；幕后人物可按叙事采用黑白，不给整稿施加灰阶。封面与文字主张页可以完全无图，标题、正文、图注、页码和品牌文字均保持可编辑。

以同级 `white-blue-slides` 为 `<shared>`，准备内容与必需素材后构建：

```sh
python3 <shared>/scripts/prepare_images.py <project>/deck.json --out <project>/image-handoff
python3 <shared>/scripts/build_deck.py <project>/deck.json --out <project>/演示稿.html
```

演示稿的 `--draft` 仅供缺图预排，缺图稿不能冒充成品；它不改变本风格的 ready 状态。

## 交付与维护

默认交付可编辑、离线单文件 HTML，由用户自行导出和检查；不自动执行整稿内容审查、批量截图、逐页验收或导出检查。用户明确要求 PPTX、PDF 或代查时，完成相应产物与检查，不将已要求的导出留作可选后续。修复构建失败与资源缺失仍属于制作工作，详见共享 [默认交付与职责](../white-blue-slides/references/export.md#默认交付与职责)。

风格主题与共享代码开发按 [开发验证](references/quality-check.md#风格开发与接入) 做与改动相称的验证，不将其作为普通成稿的自动验收流程。已完成的同范围批准不重复索取；将来另开独立方向时才建立新的方向批准。只修改文档时检查相关结构与链接即可。
