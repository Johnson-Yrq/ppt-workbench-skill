---
name: warm-minimal-editorial-slides
description: 在用户选择暖褐极简编辑式风格或续做该风格项目时制作可编辑离线 HTML 演示稿；适用于品牌、作品集、生活方式、空间文旅、公司工作室及文化提案，以暖米白、深褐和丰富的暖调摄影组织内容。交付前做基本排版 QA，默认由用户自行导出。
metadata:
  version: "1.1.0"
---

# 暖褐极简编辑式演示稿

整稿 style ID 为 `warm-minimal-editorial`，状态为 **ready**。用户已于 **2026-10-04** 明确批准中文风格样稿，并授权正式接入和安装；使用本风格无需再次确认设计方向。原独立样稿保留在仓库 `examples/warm-minimal-editorial/暖褐极简编辑式-中文风格样稿.html` 作为转译记录，正式项目使用共享构建器和 `deck.json`。

## 制作与交付

先读 [设计系统](references/design-system.md)，配图时读 [配图流程](references/image-workflow.md)。以暖色真实摄影、大块留白、少量文字和非对称构图为主；主动为多数适合配图的内容页准备独立主图、条带、细节或多图，不只给大纲点名配图的页面生成图片。标题、说明、图表和事实数据保留为可编辑内容。

普通新稿仍按同级 [PPT 制作工作台](../ppt-workbench/SKILL.md) 识别已确认的风格和演讲／阅读用途，只询问缺失选择。用户直接指定本包已表达风格选择；续做保留当前选择。开发本 Skill 或制作风格样稿时不启动真实演示稿的用途问卷。

共享套件是同级 `white-blue-slides`。复用其 [类型规则](../white-blue-slides/references/presentation-modes.md)、[数据结构](../white-blue-slides/references/deck-format.md)、[图表契约](../white-blue-slides/references/charts.md) 和播放器；不读取素白蓝调的视觉规范作为本包主题。根对象记录 `style: "warm-minimal-editorial"` 与 `presentation_mode: "speech" / "reading"`。

先按共享 [制作大纲](../white-blue-slides/references/outline.md) 把用户内容转化为适合所选风格与用途的 `大纲.md`（逐页结论、关系与数量、上屏文字、版式、配图、讲稿与【待补】），再按大纲动手。

逐页按共享 [内容自主选版](../white-blue-slides/references/layout-selection.md) 判断关系、数量、素材与数据，用 `select_layout.py` 选择真实可执行候选。共 48 个执行策略；本包可使用全部共享结构，不只八个 `editorial` 变体。选版不增加用户批准步骤；交付前统一做基本排版 QA。

演讲型可从 [正式演讲示例](assets/deck.example.json) 起步，使用 `layout: "editorial"` 的封面、介绍、目录、关于、服务、流程、作品集和收束变体；准确字段见共享 [editorial 契约](../white-blue-slides/references/deck-format.md#editorial编辑式图文页面)。阅读型可从 [正式阅读示例](assets/deck.reading.example.json) 了解数据组织，再按内容自由选择共享布局，保留机制、依据与边界；示例中的 `reading` 四分区是可选结构，不限制所有阅读页。示例只演示结构，业务内容与图片须按实际大纲改写。页头、封面尾页、字阶和边距沿用本包独立设计，不继承六种预设；新增主体布局进入共享层供所有风格复用。

默认交付可编辑、离线单文件 HTML。交付前按共享 [基本排版 QA](../white-blue-slides/references/layout-qa.md) 运行 `audit_deck.cjs`，逐页看截图检查布局是否合理（碰撞、重心与留白、对齐、层次、断行、密度、图片裁切），修改并重建后再交付，交付时简述看过与改过的页。PPTX／PDF 由用户通过播放器自行导出；Agent 不自动导出、不做 PowerPoint 实看或播放／编辑回归。用户明确要求 PPTX、PDF 或更深入的检查时，完成所要求的部分。构建失败、结构错误与缺失资源须修复，见共享 [默认交付与职责](../white-blue-slides/references/export.md#默认交付与职责)。本包看图要点见 [检查边界](references/quality-check.md)。

## 构建命令

`<shared>` 为同级 `white-blue-slides`，`<project>` 为本次项目目录。普通制作准备数据与图片后直接构建，不预先运行计划诊断；构建后做基本排版 QA：

```sh
# 导出本风格逐图简报与文件清单；不调用模型
python3 <shared>/scripts/prepare_images.py <project>/deck.json --out <project>/image-handoff

# 生成并保存所需图片后，构建独立离线 HTML
python3 <shared>/scripts/build_deck.py <project>/deck.json --out <project>/演示稿.html
```

## 维护与新方向

本风格的批准已经满足，不把初始 draft 阶段用作普通制作流程。维护主题、共享版式或播放器时按 [开发验证](references/quality-check.md#风格开发与接入) 执行与改动相称的测试；不改变旧风格视觉。将来另开独立设计方向时，才按共享 [新增风格包规范](../white-blue-slides/references/adding-styles.md) 提供代表样稿并取得该方向的批准。
