---
name: white-blue-slides
description: 在用户选择素白蓝调风格或续做该风格项目时，根据PPT大纲制作可编辑、可离线单文件HTML演示稿，采用暖白纸底、明亮主蓝与白色哑光模型配图。与其他风格共用制作、排版与检查套件；未选择风格的通用请求先经 ppt-workbench 确认。明确要求PPTX时不能以HTML替代。
metadata:
  version: "3.5.0"
---

# 场景化 HTML 演示稿

把大纲变成一份**文字可编辑、图文对位、可独立离线打开的 HTML 演示稿**。不需要用户提供模板或版式参数；套件不含品牌，Logo 与公司名仅在用户提供时写入 deck，用户指定的品牌与内容优先。

本入口对应素白蓝调风格（`style: "scene-white"`，旧稿省略该字段亦相同）。直接指定本 Skill 视为选择该风格。尚未选择风格的通用请求，先按同级 [PPT 制作工作台](../ppt-workbench/SKILL.md) 确认；只有本目录时也可运行 `scripts/style_packs.py --list` 展示实际可用风格。续做项目保留已有选择。以下视觉规范只属于素白蓝调，共享脚本不要求其他风格继承。

## 动工前确认用途

按 [用途确认与信息密度](references/presentation-modes.md) 确认演讲型或阅读型；用户未明确时，在拆页、排版和生图前询问并等待；风格也未定时按 [PPT 制作工作台](../ppt-workbench/SKILL.md) 合并询问。确认后记录根字段 `style: "scene-white"` 与 `presentation_mode: speech / reading`；已确认或已授权自行选择的维度不重复询问。

## 运行路径

- **有可直接调用的内置生图工具**（例如 Codex 的 image_gen）：逐页生成场景图，保存到项目内，再完成 HTML。按当前工具文档调用；不索要 API Key，不静默改走付费 CLI。
- **没有内置生图工具但用户愿意配置生图 API**：按 [通过生图 API 自动生成配图](references/image-api.md) 引导。先问一次是否使用自己的 API；同意后把 `generate_images.py --setup` 交给用户在自己的终端执行（密钥不经过对话），再 `--check`、`--dry-run`、`--pages` 试一页，合格后生成其余缺图并逐张查看。
- **没有内置生图工具且不用 API**：交付逐页可复制的完整提示词和文件名清单，请用户回传图片；同时完成不依赖图片的内容与版式规划。
- 用户已给图时先检查并复用。以实际能力为依据，不声称调用了不可用的工具。

最终交付物是 **一个 `.html` 文件**。提示词、图片清单、`deck.json`、截图和 QA 报告都是过程文件；不把缺图草稿交付为成品。

## 默认设计

第一次制作时阅读 [设计与版式规则](references/design-system.md)（颜色、字号、固定不变的封面／尾页／页脚、六种页头与封面尾页排布），并查看 `assets/reference-design/` 下的参考图；它们只作质量与风格参照，不复制其中的业务内容。

- 配图是**白色哑光立体业务场景**：人物在做事，关系看得见，单图只表达一个主要关系；标题、标签与说明用 HTML，不烘焙进图片。每页都有关联配图，包括封面与尾页。
- 图要大、完整、与文字有联系。按实际可见的场景本体调整缩放与偏移；上图下文时文字过多先精简或改左右排布，不挤小图片、不裁掉主体。
- 有关联语义的分组标题默认配图标；不加时在 `icon_omit_reason` 写具体原因。
- 只在阶段、能力分组、字段或指标因子需要归组时加底板；普通说明用蓝色标题、横向细线和留白。架构文字直接标注在模型上，不套框、不加底板。
- 封面、尾页、页脚、纸色与主蓝是品牌，不是自由版式；页头按内容从六种 [`header`](references/deck-format.md#页头样式) 样式中选择，封面与尾页按配图从几种左右 [`variant`](references/deck-format.md#封面与尾页排布) 排布中选择，都不询问用户。`custom_css` 触碰这些部分会被构建器拒绝。大纲里的“版式规范”只提取结构要求（见 design-system）。

## 大纲到成稿

1. **规划每页。** 保留主线、必要信息和明确页数，一般每页一个结论。演讲型细节可放讲稿；阅读型把独立理解所需的机制、比较、来源与边界留在页面上。关键事实保留来源或待核验状态，不编造政策、业绩、联系人或产品截图。
2. **建立 `deck.json` 并先检设计。** 按 [数据结构与构建方法](references/deck-format.md) 选版式、写每页 `visual`，把大纲明确的视觉要求逐条转成 `requirements`，原始大纲与事实说明放 `notes`。运行 `--check-plan`，缺项先补齐再生图。
3. **准备场景图。** 按 [配图与人工供图流程](references/image-workflow.md) 为每页写**本页独有**的 `image.brief`：对象与数量、人物动作、关系机制、层级与构图。收到图片后逐张核对映射、层级、留白与乱码。
4. **构建并迭代。** 按实际渲染调整图文尺寸、间距、标注和密度；`custom_css` 只调内容区，确需新关系时按 deck-format 用 `--builder` 新增一两种版式。阅读型按[四类图文分区](references/presentation-modes.md#阅读型的四类图文分区)排版，放不下则拆页。数量数据用 [ECharts 图表](references/charts.md)。
5. **逐页验证后交付。** 按 [验收标准](references/quality-check.md) 跑审查器并逐页看截图；阅读型还要检查无口头补充时是否能理解。总览截图与“全部通过”不能代替逐页对照。

## 命令

`<skill>` 为本 Skill 文件夹，`<project>` 为本次工作目录，由当前环境解析路径。

```sh
# 检查设计决策与每页结构，不需要图片
python3 <skill>/scripts/build_deck.py <project>/deck.json --check-plan --out <project>/design-plan.json

# 导出提示词和供图清单，不调用模型或网络
python3 <skill>/scripts/prepare_images.py <project>/deck.json --out <project>/image-handoff

# 用户自己的生图 API：--setup 由用户在终端执行，之后 --check → --dry-run → --pages 2 → 生成其余缺图
python3 <skill>/scripts/generate_images.py <project>/deck.json --dry-run

# 收到图片后把背景贴平到纸色（原图备份到 images/original/）
python3 <skill>/scripts/match_paper.py <project>/images/*.png

# 构建唯一交付文件（默认 WebP 内嵌）
python3 <skill>/scripts/build_deck.py <project>/deck.json --out <project>/演示稿.html

# 渲染检查（需要 Node、Playwright 和 Chrome/Chromium）
node <skill>/scripts/audit_deck.cjs <project>/演示稿.html --out <project>/qa --browser chrome

# 修改本 Skill 后自测；改了播放器／导出器／主题再跑播放器回归测试
python3 <skill>/scripts/selftest.py
node <skill>/scripts/test_player.cjs <project>/演示稿.html --browser chrome
```

用户要 PDF 或 PPTX 时按 [导出](references/export.md) 执行，PPTX 须在 PowerPoint 中逐页核对。构建器与生图脚本只依赖 Python 标准库（Pillow 可选，用于压缩；底色校准需 numpy）；不能运行审查器时用可用浏览器逐页检查并说明范围。`--draft` 只供内部预排缺图，正式交付禁止。旧 HTML 内嵌旧播放器，从源项目重建；浏览器编辑过的旧稿先保留另存副本。新增风格按 [新增独立风格包](references/adding-styles.md) 接入。

## 续做与局部修改

- 继续修改本项目的 `deck.json`、图片与 CSS，不重做已确认部分。
- 旧项目用新版构建前，按原大纲补齐每页 visual；不为通过检查随意补卡片、填空泛豁免或删除大纲要求。
- “恢复原始样式”仅作用于指定范围；已选信息块与明确保留项不随之消失。
- 人工供图中途停止时保留清单与缺图状态，收齐后继续。
- 不主动追加 PPTX、PDF、视频或部署任务；用户明确要 PPTX 时用导出器生成，不以 HTML 替代。
