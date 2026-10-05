---
name: warm-minimal-editorial-slides
description: 在用户选择暖褐极简编辑式风格或续做该风格项目时制作可编辑离线 HTML 演示稿；适用于品牌、作品集、生活方式、空间文旅、公司工作室及文化提案，以暖米白、深褐和丰富的暖调摄影组织内容。默认由用户自行导出和检查。
metadata:
  version: "1.1.0"
---

# 暖褐极简编辑式演示稿

整稿 style ID 为 `warm-minimal-editorial`，状态为 **ready**。用户已于 **2026-10-04** 明确批准中文风格样稿，并授权正式接入和安装；使用本风格无需再次确认设计方向。原独立样稿保留在仓库 `examples/warm-minimal-editorial/暖褐极简编辑式-中文风格样稿.html` 作为转译记录，正式项目使用共享构建器和 `deck.json`。

## 制作与交付

先读 [设计系统](references/design-system.md)，配图时读 [配图流程](references/image-workflow.md)。以暖色真实摄影、大块留白、少量文字和非对称构图为主；主动为多数适合配图的内容页准备独立主图、条带、细节或多图，不只给大纲点名配图的页面生成图片。标题、说明、图表和事实数据保留为可编辑内容。

普通新稿仍按同级 [PPT 制作工作台](../ppt-workbench/SKILL.md) 识别已确认的风格和演讲／阅读用途，只询问缺失选择。用户直接指定本包已表达风格选择；续做保留当前选择。开发本 Skill 或制作风格样稿时不启动真实演示稿的用途问卷。

共享套件是同级 `white-blue-slides`。复用其 [类型规则](../white-blue-slides/references/presentation-modes.md)、[数据结构](../white-blue-slides/references/deck-format.md)、[图表契约](../white-blue-slides/references/charts.md) 和播放器；不读取素白蓝调的视觉规范作为本包主题。根对象记录 `style: "warm-minimal-editorial"` 与 `presentation_mode: "speech" / "reading"`。

逐页按共享 [内容自主选版](../white-blue-slides/references/layout-selection.md) 判断关系、数量、素材与数据，用 `select_layout.py` 选择真实可执行候选并保留 `layout_intent / layout_selection`。100 条、19 类来源与 48 个执行策略分层维护；本包可使用全部共享结构，不只八个 `editorial` 变体。选版不增加用户批准或自动成稿审查步骤。

演讲型可从 [正式演讲示例](assets/deck.example.json) 起步，使用 `layout: "editorial"` 的封面、介绍、目录、关于、服务、流程、作品集和收束变体；准确字段见共享 [editorial 契约](../white-blue-slides/references/deck-format.md#editorial编辑式图文页面)。阅读型可从 [正式阅读示例](assets/deck.reading.example.json) 了解数据组织，再按内容自由选择共享布局，保留机制、依据与边界；示例中的 `reading` 四分区是可选结构，不限制所有阅读页。示例只演示结构，业务内容与图片须按实际大纲改写。页头、封面尾页、字阶和边距沿用本包独立设计，不继承六种预设；新增主体布局进入共享层供所有风格复用。

默认交付可编辑、离线单文件 HTML，用户通过播放器自行导出 PPTX／PDF 并检查。Agent 不自动核对整稿内容、不批量截图、不运行成稿审查或播放／编辑回归，也不自动导出或打开 PPTX；构建失败和缺失资源仍需修复。用户明确要求代为导出或检查时，仅执行所请求的部分，参考共享 [导出与分工](../white-blue-slides/references/export.md#默认交付与职责) 及本包 [检查边界](references/quality-check.md)。

## 构建命令

`<shared>` 为同级 `white-blue-slides`，`<project>` 为本次项目目录。普通制作准备数据与图片后直接构建，不预先运行计划或成稿审查：

```sh
# 导出本风格逐图简报与文件清单；不调用模型
python3 <shared>/scripts/prepare_images.py <project>/deck.json --out <project>/image-handoff

# 生成并保存所需图片后，构建独立离线 HTML
python3 <shared>/scripts/build_deck.py <project>/deck.json --out <project>/演示稿.html
```

## 维护与新方向

本风格的批准已经满足，不把初始 draft 阶段用作普通制作流程。维护主题、共享版式或播放器时按 [开发验证](references/quality-check.md#风格开发与接入) 执行与改动相称的测试；不改变旧风格视觉。将来另开独立设计方向时，才按共享 [新增风格包规范](../white-blue-slides/references/adding-styles.md) 提供代表样稿并取得该方向的批准。
