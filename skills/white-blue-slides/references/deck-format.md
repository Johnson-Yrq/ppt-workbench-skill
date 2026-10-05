# 内容数据与构建

构建器负责稳定排版和内嵌素材；大纲理解、基于所给事实编写文字、场景设计与视觉取舍由制作方完成；成稿复核由用户自行完成。不会自动把 Markdown 按行变成幻灯片。

本文件是所有风格共用的数据与布局契约。页面色彩、字体、材质、页头页脚和配图规范，以当前所选 Skill 的设计文件为准；下文提到的“蓝色”“浅底”等外观描述为原风格示意，不要求其他风格沿用原色。布局的字段、可编辑标注、对象对应与检查要求共用。

普通制作只使用本文的数据与布局契约，不自动运行计划预检、成稿截图审查或导出检查。文中的检查器能力与看图建议供用户自行检查、明确委托检查及工具开发使用；默认分工见 [交付规则](export.md#默认交付与职责)。构建器自身的必需字段、资源路径和格式校验仍保留。

## 制作模式

动工前按 [用途确认规则](presentation-modes.md) 获取用户反馈，在根对象记录 `presentation_mode: "speech"`（演讲型）或 `"reading"`（阅读型），不要按模板默认值代替确认。模式独立于 `style`，不在单页覆写。旧稿省略时按 `speech` 兼容；计划输出 `mode_recorded` 区分是否已记录，字段本身不证明对话中的确认。

## 项目结构

```text
本次项目/
  大纲.md
  deck.json
  images/01.png …      PNG/JPEG/WebP 均可；构建时默认转成 WebP 内嵌
  layout.css          可选，本次版式微调
  builder.py          可选，扩展版式的 Builder 子类
  演示稿.html          最终唯一必需文件
  qa/                 可选：用户委托检查或工具开发时产生
```

Python 3.9+，标准库即可。安装了 Pillow 时构建器把配图转成 WebP 内嵌（一张 1.4MB 的 PNG 约变成 60KB，25 页成稿从几十 MB 降到 2MB 上下）；没有 Pillow 时保留原格式，并在输出 JSON 的 `embed.notes` 里提示。`--embed-format keep|jpeg|webp` 与 `--embed-quality` 可调。所有素材路径相对于 `deck.json` 所在目录，须在项目内；先把外部素材复制进来。接受实际 PNG、JPEG、WebP，不接受网址、SVG 或绝对路径。输出 HTML 内嵌素材，打开时不需要这些制作文件。命令见 SKILL.md「随附工具」。

## 根对象

```json
{
  "version": 1,
  "title": "本次演示稿名称",
  "style": "scene-white",
  "presentation_mode": "speech",
  "footer_label": "解决方案 · 简短名称",
  "slides": []
}
```

`version / title / slides` 是主要字段。`slides` 至少一页，顺序即页序。年份默认当前年；套件不含品牌，页脚默认只有年份与右侧标签。可选字段：`year`、`company`（公司名，留空则不显示）、项目内 `logo` 路径（未给则不显示 Logo）、`theme`（仅 `paper/blue/ink/muted/line/panel` 六位十六进制颜色）、`custom_css`（项目内 CSS 路径）。只有用户提供品牌资料时才填写 `company` 与 `logo`；`theme` 与 `custom_css` 仅在用户要求换风格时使用。

根字段 `style` 选择整稿视觉规范，值为 `python3 <shared>/scripts/style_packs.py --list` 返回的可用风格 ID。当前提供 `"scene-white"`（素白蓝调）、`"saas-3d"`（海蓝玻璃）、`"real-miniature"`（写实微缩）、`"warm-minimal-editorial"`（暖褐极简编辑式）和 `"monochrome-editorial"`（黑白编辑式）；未来符合 [风格包契约](adding-styles.md) 的同级目录自动加入。需要安装共享套件与所选风格包。未知值、缺资源、重名 ID、draft 状态和逐页设置 style 会报错，不静默回退或混搭。选择命名风格无需 `--allow-restyle`，也不会关闭品牌检查。`--check-plan`、构建结果、配图清单及 HTML 均记录当前风格。旧稿省略 style 仍兼容素白蓝调；新稿须先按用户选择显式写入 style 和 presentation_mode，不能以示例值或兼容默认代替选择。

### 风格独立的页头

页头体系由风格清单决定，不由主体 `layout` 或演讲／阅读用途决定。`assets/style.json` 的 `header_system` 可为 `preset-six` 或 `style`，默认 `style`。

- 素白蓝调、海蓝玻璃、写实微缩显式采用 `preset-six`。其根或单页 `header` 字段按各自 [素白蓝调页头](header-styles.md)、[海蓝玻璃页头](../../navy-glass-slides/references/header-styles.md)、[写实微缩页头](../../realistic-miniature-slides/references/header-styles.md) 使用；这组预设不向其他风格自动扩展。
- 独立风格采用 `style`，通过风格清单的 `header_template` 和主题 CSS 组织页头、标题、页码与可用空间；项目根对象或单页不再设置六种预设的 `header`。模板字段与受控插槽见 [页头与视觉策略](adding-styles.md#页头与视觉策略)。

页头模板属于风格资源，不能在 deck 或单页覆写。主体布局继续共享；页头和正文所占区域由当前风格协调。封面、editorial 及在正文安排大标题的共享布局不在页头重复输出标题；原 `closing` 布局的标题仍由页头位置承载，具体视觉由风格安排。

### 封面与尾页排布

封面和尾页用单页字段 `variant` 选择左右排布，默认 `standard`；只改变图文位置，字段、文案上限与配色不变。对比见 `assets/cover-variants.png`。

本节仅描述 `layout: cover / closing`；摄影编辑式页面使用独立的 `layout: editorial` 与 `editorial_variant`，不使用这里的 `variant`，见 [editorial 契约](#editorial编辑式图文页面)。

| `variant` | 外观 | 适合 |
|---|---|---|
| `standard` | 左文右图 | 默认；需要右侧层级标注 `labels` 时只能用它 |
| `mirror` | 左图右文 | 与上一份稿或封面形成呼应，配图主体偏左时 |
| `full` | 配图贴上、右两边出血，左缘渐隐 | 配图是完整大场景、想要更强冲击力时 |
| `panel` | 文案落在左侧浅色块上（仅封面） | 配图背景较杂、需要把文案区和图区分开时 |

由 Agent 按配图构图选择，不询问用户；用户指定时照办。尾页可与封面同一排布或选 `standard`。`labels` 只用于 `standard` 封面，其他布局不能使用本节的 variant 值；`type_poster` 有自己的 cover / chapter / statement 变体，见 [共享布局合同](shared-layouts.md#文字海报与编辑分栏)。

风格自己的页头模板与主题 CSS 可定义页头、封面尾页及字阶；以下保护针对单个项目覆盖，不限制风格开发。`custom_css` 只用于内容区布局，不接受 `@import`、`url()`、HTML 或 `!important`；选择器里出现 `header/footer/h1/.subtitle/.chapter/.page-number/.layout-cover/.layout-closing/.cover-*/.ending-*/.brand/.slide/body` 会被拒绝（用户明确要求在所选主题之外自定义这些区域时加 `--allow-restyle`）。按稳定 `id` 微调，例如 `#p03 .hero-scene{width:1180px}`；按页需要调整，不把临时样式写回 Skill。

新关系无法由现有版式清晰表达时，按 [共享布局扩展](adding-styles.md#共享布局扩展) 新增通用布局，供各风格复用。现有项目仍兼容 `builder.py` 和 `--builder builder.py` 的临时扩展路径，但正式新增布局不能停留为某个风格的私有渲染器：

```python
from build_deck import Builder as Base, items

class Builder(Base):
    LAYOUTS = Base.LAYOUTS | {'timeline'}        # 登记新版式名，deck.json 里 layout 即可写 timeline

    def timeline(self, s):                        # 只拼装共享组件，样式写在 custom_css
        points = ''.join(self.point(v) for v in items(s, 'items', 2, 6))
        return '<div class="timeline">' + self.image(s) + '<div class="points">' + points + '</div></div>' + self.bottom(s)
```

子类只能新增版式方法：覆盖 `icon/heading/point/image/bottom/footer/slide/render` 或任何内置版式名会被拒绝。保留可编辑节点和设计契约；不直接拼接裸 `h3` 跳过图标。正式共享布局按实际结构需要增加，不设每稿的固定新增数量；复用已有组件，避免重复实现同一种内容关系。自定义信息块标记 `data-component="panel"`，标签用 `tag`，状态用 `state`，架构用 `architecture-label`；步骤用 `data-step`，关系组用 `relation` 且包含关系连接。自定义版式的 `visual.role` 要显式写明。审查器独立核对实际外观，保留类名却删除背景也会失败。

## 每页通用字段

| 字段 | 说明 |
|---|---|
| `id` | 可选，默认 `p01` 等；唯一，只用英文、数字、短横线、下划线 |
| `layout` | 基础布局 `cover / scene / split / triad / journey / architecture / flow / domains / formula / table / relations / closing / reading / editorial`，以及下文的 20 种共享构图；现有项目仍兼容 `--builder` 自定义布局 |
| `title` | 必填，纯文字；用 `\n` 明确换行 |
| `chapter / subtitle` | 可选，纯文字 |
| `notes` | 原始大纲、本页口播、来源与事实状态；字符串，保留换行 |
| `title_size` | 可选显式覆盖参数，当前数值支持范围 36–110px；省略时用当前风格字阶，不是所有风格的推荐字号 |
| `body_size` | 可选显式覆盖参数，当前数值支持范围 21–30px，作用于支持它的布局；省略时用当前风格字阶，不是用途级字号下限 |
| `image` | 单图对象；是否需要及是否支持多图按所选布局合同。单图与顶层 `images` 互斥。风格清单 `image_free_layouts` 可豁免原 cover / closing / table 配图，不豁免带图 editorial 变体 |
| `surface` | 可选，默认 `light`；只能使用当前风格 `surfaces` 声明的名称，如 dark、mustard、blue。名称必须是最多 32 字符的小写字母／数字／短横线安全 slug，具体规则见风格包契约。页面颜色按内容节奏安排，不机械交替；不改变整稿 style 或布局 |
| `images` | 数量依布局：reading 1–3 张；editorial.services 1–3、portfolio 2–6；photo_pair / offset_pair 各 2 张，photo_strip 2–5 张。service_cards 的可选图片写在各条目的 image 中。各图有 src/alt，可选 caption、brief 等字段 |
| `editorial_variant` | 仅 `editorial`：cover / intro / contents / about / services / process / portfolio / closing；所有风格均可使用 |
| `composition` | 仅 `reading`：half_lr / half_tb / half_diagonal / quarter，按主体内容分区 |
| `visual` | 可选；大纲明确的视觉要求，及需要偏离布局默认值时的角色与分组处理，见下节 |
| `bottom / footnote` | 内容页可选；封面和尾页不使用 |

所有文案按纯文字处理，HTML 特殊符号会转义。不要输入 `<br>`；使用 JSON 换行 `\n`。正文都是可编辑节点，图标是内嵌 SVG，配图是 raster 图片。

```json
"image": {
  "src": "images/01.png",
  "alt": "团队沿集团层级核对业务凭证的场景",
  "ratio": "1:1",
  "zoom": 1,
  "offset_x": 0,
  "offset_y": 0,
  "brief": {
    "subject": "集团总部、下属企业、业务现场和底层凭证",
    "action": "各层团队核对对应业务，监管人员沿层级追溯凭证",
    "structure": "四层场景由一条淡蓝色纵向通道贯通，突出逐级穿透",
    "details": "从上到下依次是总部评审、企业办公室、仓储现场、合同与票据",
    "composition": "方形画幅，右前方等距视角，层次分明，主体完整"
  }
}
```

`src / alt` 必填。缺图时 `brief.subject/action/structure/details` 必填且每页各自成文（见 image-workflow 的字段表），用于输出完整提示词；模板句、跨页复制、subject 与 structure 相同都会被导出脚本拒绝。`ratio` 普通页默认 `4:3`，reading、journey 或显式 image_position: above 默认 `16:9`；可选 `1:1 / 4:3 / 3:2 / 16:9 / 3:4 / 2:1 / 21:9 / 3:1`。横向多阶段可选择全景比例；先看最长标题和必要说明的占幅，再确定图框与生图构图，默认 16:9 不是每页的推荐值。比例指导供图，不会拉伸已有图片。`zoom` 0.5–2.5，偏移单位为画布像素；先查看配图再调整，裁去空白时保留主要对象。`edge_fade` 默认 0.04，可在 0–0.12 内微调，仅用于轻微边缘融合；不能用大幅淡出掩盖底色错误，不全局使用 multiply。

`image.background_mode` 默认 `native`，保留素材。仅复用已有、已查看并确认均匀纯白底的素材时，可选 `white-matte`：构建器按当前主题纸色内嵌 sRGB 映射，保留原素材和透明通道，HTML、PDF 与 PPTX 图片导出使用相同映射。新生成／重绘图片直接使用当前纸色，不为使用此选项而先生成白底；换入同纸色新图后，将 background_mode 恢复为 native，避免二次映射。它会轻微调整主体颜色，须核对材质与阴影；不能用它消除灰色渐变或伪透明棋盘格。`prepare_images.py` 清单记录当前 `paper`；`match_paper.py 图片 --deck deck.json --dry-run` 可诊断轻微背景偏差和实际透明通道。

说明项常用 `{ "title": "…", "text": "…", "icon": "ShieldCheck", "presentation": "open" }`。图标是否默认必需由风格清单 `heading_icons` 决定：required 时选择图标或以 `icon_omit_reason` 说明真实不适用原因；optional 时按内容选择，无需为省略图标填写豁免。显式 `visual.requirements` 中的图标要求仍须遵守。

内置 Lucide 线性图标（键名区分大小写）：

`Activity ArrowRightLeft Award BadgeCheck BadgeDollarSign BarChart3 Bell BellRing Binoculars Blocks BookOpen Bot Boxes Brain BriefcaseBusiness Building Building2 Calculator CalendarDays ChartNoAxesCombined CircleAlert CircleCheck CircleHelp ClipboardCheck ClipboardList Clock Cloud Cog Coins Compass Cpu Database DatabaseZap Eye Factory FileCheck2 FileClock FileCog FileSignature FileText Filter Fingerprint Flag Folder Gauge GitBranch Globe2 GraduationCap Grid2x2 Hammer Handshake Heart HeartPulse History Hospital Info KeyRound Landmark Layers Layers3 LayoutDashboard Library Lightbulb Link ListChecks Lock Mail Map MapPin Merge MessageCircle MessageSquare Microscope Milestone Monitor Network Package Phone PieChart Pill Presentation Printer Puzzle Receipt RefreshCw Repeat Rocket Route Scale ScanSearch ScrollText Search Send Server Settings Shield ShieldCheck ShoppingCart SlidersHorizontal Smartphone Sparkles Split Star Stethoscope Store Table Target Timer TrendingUp TriangleAlert Truck Unplug UserRound UserRoundCheck Users Wallet Warehouse Workflow Wrench Zap`

需要别的图标时运行 `node <shared>/scripts/add_icons.cjs 名称…`，其中 `<shared>` 为 `white-blue-slides` 目录（需要本地 lucide 包，可用 `--lucide` 指定目录；`--list` 列出现有）。`presentation` 仅 `open` 或 `panel`；未指定时由本页 `visual.treatment` 决定（panels→panel，其它→open）；mixed 时每项必须明确选择。

### 配图风格与界面文字

`image.ui_text` 按所选风格取默认值：原风格为 `"none"` 且仅支持 none；海蓝玻璃风格默认为 `"demo"`，沿用已确认示例，只允许软件屏幕中使用 Overview、Analytics、Activity、Demo 四个短示意标签。用户要求纯无字配图时，SaaS 可显式设为 `"none"`，仍保留精细的软件界面结构。页面标题和真实数据始终由 HTML 呈现。该字段不改变整稿风格；不支持的值会在计划检查和导出时失败。`brief.action` 可以描述人物动作或软件处理；不强制每页添加人物。

配图导出器按根 style 选择对应基底，并添加本页比例、版式与 UI 文字策略。海蓝玻璃供图目录还会包含 `style-reference.png`；生图时同时附上它作为材质与尺度参考，业务对象仍遵循本页 brief。已有图片继续标记 provided，无须重生成。

## 每页设计契约

```json
"visual": {
  "role": "comparison",
  "treatment": "panels",
  "requirements": [
    {"feature":"icons", "min":5, "source":"大纲：五格等宽，每格一个图标"},
    {"feature":"panels", "min":5, "source":"大纲：横向五格"},
    {"feature":"manual", "text":"五列对应上方五个业务场景，图像主体充分展开", "source":"大纲横向五格与图片展示要求"}
  ]
}
```

`role` 可选 `cover/closing/explanation/capabilities/comparison/process/controls/architecture/entities/formula/table/domains/briefing`。`treatment` 可选 `open/panels/mixed/labels/none`。两者默认跟随布局，只在需要不同处理时填写；没有明确视觉要求时整个 `visual` 可省略。依据原始大纲填要求，不能从已生成 HTML 倒推一份恰好通过的契约。

可自动核对的 `feature`：`icons/panels/tags/states/architecture_labels/steps/relations/visual_blocks/tables/layers`。每项 `min` 默认 1，可附 `texts` 数组，检查指定短词确实出现在对应组件里；`source` 保留原句或用户确认要求。深浅分组、场景与对象对应、基线等用 `manual + text + source`，并逐页看图核对。`--check-plan` 按计划核对数量与短词；`manual` 项会列入审查报告的 `manualReview`，供用户看图确认，不触发 Agent 自动截图。

`journey` 自动启用上图下文面积检查；自定义相同结构时写 `visual.image_position: "above"`，并把文字行标记为 `data-captions`。阈值只定义在 `design_contract.py` 的 `IMAGE_BALANCE`（当前：图框高 ≥460px、占 main 高度 ≥60%、配图贴满图框的宽或高 ≥95%、下方文字行高 ≤220px），`--check-plan` 报告与审查器读取同一组数字，其他文档不另抄。图框宽高比随文字区变化；填满高度只说明图片元素足够大，不说明场景主体和整页占幅合理。阶段栏窄时审查器提供提示，仍须看整页确认场景、文字与留白的关系，不用裁掉主体换取铺满。

## 版式与容量

先定每页的结论和主体关系，再选版式；同样三项内容，步骤、三对象比较和三条独立要点用不同版式，不按条目数统一套卡片。

| 内容关系 | 版式 |
|---|---|
| 一个场景加少量说明 | `scene` |
| 两侧对照、要点加配图 | `split` |
| 三段控制或三个并列能力 | `triad` |
| 阶段、路径、多对象横向比较 | `journey` |
| 有先后的步骤与控制点 | `flow` |
| 分层结构，需在模型上直接标注 | `architecture` |
| 实体、字段与关系 | `relations` |
| 确有加和／乘积关系的因子 | `formula` |
| 指标、口径、边界 | `table` |
| 多领域清单 | `domains` |
| 可选多模块组合（流程、矩阵、分层、图表），两种用途均可用 | `reading` |
| 编辑式图文叙事，配图材质和页头由风格决定 | `editorial` |

图表只在有真实数量数据、单位和来源时使用；没有数据就保留定性说明。

### cover：封面内容结构

增加 `title_prefix`（可选标题第一行）、`promise`、`description`、最多 6 个短字符串 `benefits`、最多 2 个 `platforms`、`date`（默认当月，空字符串隐藏，固定在页脚上方）。章节标签留在页头原位；左栏从标题到平台标签是一个整体，构建器把它垂直居中在配图中线上；文案多少都不用手调位置。

下表的单行文案预算仅属于 `cover_copy_policy: "legacy"`（最早三个风格）。采用 `style` 策略的独立风格自行设计封面标题行数与字阶，不套用此预算；共享字段与可编辑能力不变。

| 字段 | 角色 | 上限 |
|---|---|---|
| `chapter` | 章节标签 | 12 字 |
| `title_prefix` / `title` | 标题两行：黑色前缀 + 蓝色主句 | 10 / 9 字 |
| `subtitle` | 对象与范围（面向谁、覆盖什么） | 24 字 |
| `promise` | 一句价值（做到什么） | 18 字 |
| `description` | 只在没有 promise 时使用 | 24 字 |
| `benefits` | 3 或 6 个短词 | 每个 4 字 |
| `platforms` | 0–2 个产品名 | 每个 10 字 |

保留必要信息并避免重复副标题。文案是否换行、主标题与说明如何分布，按所选风格和实际封面结构决定；上面的单行建议不扩展到 style 策略。

可选 `variant`（见 [封面与尾页排布](#封面与尾页排布)）。可选 `labels`（仅 standard）：`[{"title":"集团总部","text":"全局监管","y":272}]`。最多 5 项；`y` 为整张 1920×1080 页面的坐标，需看本页图调整。标签是右侧无底板的蓝色标题与灰色小字，不能照抄参考图坐标给所有配图。

封面还可使用 `credits: [{"title":"方案出品","text":"品牌团队"}]`，零至四项，每项只含必填的 `title / text`。这是可编辑的署名或汇报信息，可用于有图或风格允许的无图封面；位置由主题控制，不填写坐标，也不冒充配图的 `labels`。不使用时省略，不改变既有封面。`credits` 仅用于 `layout: cover`。

### scene：大场景与两侧说明

`left` 与 `right` 各 1–2 个说明项。用 `presentation` 按语义决定是否加框；混用是允许的。大图位于中间，可向说明区延伸，但不能遮住文字或动作。

```json
"left": [{"title":"明确对象", "text":"先对齐业务实体与责任边界", "icon":"Blocks", "presentation":"open"}],
"right": [{"title":"形成证据", "text":"把结论连接到可核查材料", "icon":"FileCheck2", "presentation":"panel"}]
```

### journey：横向比较、阶段或路径

`items` 2–7 项，每项含 `title/text`，可选 `icon/presentation/deliverable`。面板标题可设置 `header_fill: "blue"`，默认浅底。`connected: true` 仅用于真实时间或流程，并列能力默认不连箭头：无框项的箭头骑在顶部细线上并跨过列缝，信息块项的箭头对准头部色带中线。列缝默认 22px，需要更宽时在 `custom_css` 里写 `#p04 .journey-labels{--journey-gap:28px}`，不要另写箭头定位。每项可写 `state: "核查中"` 或 `states: ["…"]`，有状态时整行预留相同高度：无框项的状态标签在细线下方、标题上方；信息块项的状态标签悬在卡片上方，卡片从头部色带开始，没有状态的列不留空带。

上方图片优先，文字通常 1–2 行；6–7 列使用短标题和一句行动。状态不是普通正文，也不要统一挪到页底。下方说明过高时先缩减重复词；演讲型可把讲解细节放讲稿，阅读型的必要细节可改用更合适的共享布局或另起解释页；不靠缩小图片或字号解决。需要对应场景位置时调整列宽或图像位置，不能图中对象集中在中央、七列却铺满全页。

`content_width` 可设 900–1760（默认 1760）；`caption_width` 可设 900 到 content_width，默认相同。主体集中而文字拥挤时，优先重构为与列数相配的横向场景，或改用其他版式。只有图文都较少、收窄后仍清晰时才收窄内容区；不能靠一起缩小图文来通过面积检查。按真实对象调整列与场景对位，不强制所有阶段页使用全景或满宽。

阶段可用 `period` 表示时间，采用与状态同排的可编辑标签；原 `state/states` 保留。需要独立阅读时，用 `fields` 替代 `text/deliverable`，两套正文字段不能混用，以免静默丢失内容：

```json
{"title":"范围确认","icon":"Map","period":"M1—M2","fields":[
  {"label":"交付","text":"对象与责任清单"},
  {"label":"准入","text":"负责人确认范围"}
]}
```

`fields` 1–3 项；字段标签使用原始语义，准入条件、验收条件和完成条件不可混称。页底并行依赖可用 `bottom: {"type":"groups","items":[{"label":"数据线","text":"主数据映射、接口联调"},{"label":"规则线","text":"说明、回测、批准"}]}`，支持 1–4 组。避免把多条依赖拼成一整行粗体文字。

### split / triad：左右说明与三段控制

`split` 演讲型使用 `items` 1–3 项，阅读型支持 1–6 项，超过三项自动分成两列说明；`image_side` 可为 `left/right`，默认左图。`triad` 固定 3 项，默认右图；适合输入、判断、输出，角色为 controls、处理为 mixed 时逐项标明 presentation。根据实际分组边界与当前风格选择底板，强调方式遵循当前主题，不按项号强制第二项加框。共用图标标题与 point，不另写裸标题。

使用 `point` 的说明区（`scene / split / triad / domains`，以及 `formula / table / relations` 的说明项）可设布尔值 `emphasis`，默认 `false`。它不改变 `presentation` 或计为面板；当前海蓝玻璃主题对 `presentation: "open"` 的重点项将标题与图标放大约 10%，搭配标题字重、灰青色与短线，保持同级条目的左对齐、正文大小和间距。其他主题是否使用该标记由对应设计系统决定。

### formula：公式与平台解释

`formula: {"result":"精细化运营", "operator":"＋", "terms":[{"title":"数据说同一种话"},{"title":"每个异常有人负责"}]}`，operator 为 `＋/×`，terms 为 2–4 项，可设 `icon/presentation`。下方 `items` 可为 0–3 个说明项，与图片左右排列。有说明项时给说明标题图标；无说明项时公式项需图标或明确省略原因，避免重复装饰。

### table：指标与边界

`columns` 为 2–5 个表头字符串；`rows` 演讲型为 1–7 行、阅读型为 1–10 行字符串数组，每行数量等于表头数。某行确需图标时可用 `{"cells":["指标","口径","来源"],"icon":"ChartNoAxesCombined"}`，键名以图标库为准。默认表格左侧、相关图片右侧；风格清单显式将 `table` 列入 `image_free_layouts` 时可只写表格，由主题安排全宽几何；其他风格保留原配图要求。表头浅蓝、行间横线，默认不在每格塞图标。表格内容过密需重排列宽或简化正文，保留口径与来源。列宽、图文占比和字号依实际表格及当前主题安排，不因 reading 用途强制各占一半宽。列多或文字长时重排或拆页，保留口径与来源。

### relations：实体、字段与关系

`chains` 1–5 条，每条为 `{"nodes":["患者","治疗计划","收费单"],"directional":false,"relation":"围绕同一患者关联"}`；每条 2–5 个节点，节点也可为 `{"text":"患者","icon":"Users"}`。只有明确流向时 directional 才为 true。关系节点为 8px 标签，连接线由 HTML 生成；`items` 可补充 0–3 条共享说明项，图片位于右侧。

### architecture：与模型对齐的直接标注

坐标依据 `board`，与浏览器缩放无关；整个画板自动等比适配内容区。图像在板内的矩形可带负偏移以去除空白。标签不继承卡片风格，全部无背景、无边框。

复杂结构先查看所选风格的参考图：`scene-white` 使用 `white-blue-slides/assets/reference-design/approved-architecture.jpg`；其他风格使用自身的设计与配图规范以及已确认参考，不继承旧图材质。用完整分层模型承载全图，逐个映射模块、层板、数据来源和治理通道，再添加 HTML 文字；不可简化成图片旁边三段介绍。先定实际图像缩放，再定 label 坐标；调整 board.image 后重新核对全部标签。不要在本来无对象的位置加模块名，或拿底板遮住图中的错误层级。

```json
"board": {"width":1760,"height":740,"image":{"x":0,"y":0,"w":1760,"h":740}},
"labels": [
  {"text":"应用层","x":580,"y":180,"w":600,"h":32,"kind":"layer","font_size":26},
  {"text":"业务驾驶舱","x":500,"y":136,"w":160,"h":30,"kind":"module","font_size":23}
]
```

`labels` 至少一项，每项必填 `text/x/y/w/h`，整体必须在画板内。可选 `kind` 为 `layer/module/source/governance/flow`，`align` 为 `left/center/right`，`color` 为六位颜色，`font_size` 21–40。层级默认 28px，其余默认 24px。可选 `prefix`（如层级编号）、`detail`（次级说明）、`leader: "none/right/down"`（短引线）；流向类另支持 `direction: "none/up/down/left/right"`。这些文字各自可编辑，无需拆字符串或注入 HTML。

层级编号与名称形成第一层，模块名称为第二层，治理与方向说明形成独立语义层。强调使用字阶、字重、有限配色与细引线，保留无底板；按最终图片位置预留标注空间，引线不穿过无关模块。新增 prefix/detail 后重新分配标注框，不能保持原来的单行高度。此处坐标只是字段示例，不能作为架构图的预设标注位置。

### flow：步骤与控制点

演讲型 `steps` 3–5 项（阅读型 3–6 项），含 `title`，可选 `text/icon`，序号自动生成。`groups` 演讲型 2–3 项（阅读型 2–4 项），含 `title/icon/presentation` 和 `rows`；每组演讲型 1–3 行（阅读型 1–4 行）`{ "label":"规则闸门", "text":"先校验，再执行" }`。顶部步骤短而清楚；底部左侧大图、右侧少量控制分组。

并排分组中各行语义对应时，可在页面设 `align_control_rows: true`，按同排最长内容共享行高，此时 auto 使用标签在上的排列；需要同行可显式选 inline。不要给各行写死像素高度。

每组可选 `rows_layout: "auto/inline/stacked"`；默认 auto 在窄栏内将标签置于说明上方，宽栏保持同行，inline 保留原同行形式。长标签、较长条件或不同长度的说明优先 stacked。每行可选 `kind: "detail/check/exception"`：check 用分隔线归组，exception 用轻标签强调异常名称。先呈现校验要求，再呈现异常处置；同级内容对齐，避免固定行高造成空洞。

```json
{"title":"分析前控制","icon":"Filter","rows_layout":"stacked","rows":[
  {"kind":"check","label":"校验要求","text":"接入：来源与时间\n匹配：唯一标识\n分析：固定规则版本"},
  {"kind":"exception","label":"缺数据","text":"补证后重新校验。"}
]}
```

短标签被拆行、说明挤成多行时，先改行内结构或分配栏宽；必要事实继续留在页面。以上字段是可选表达能力，不要求所有控制页采用相同分组数量。

### domains：多领域清单

`items` 2–10 项，每项 `title/text`，可选 `icon`。自动均分左右；始终使用无框横线说明，忽略 `presentation`。最多 5 项一侧，正文尽量一行，主图保留足够面积。

### editorial：编辑式图文页面

适合品牌、作品集、介绍、流程和其他编辑式图文叙事。speech 与 reading 两种用途、所有风格均可使用八种变体；不再按风格清单做可用性限制。共享层提供默认几何结构，风格决定照片、模型等配图外观、页头、字阶、颜色与边距。需要其他内容关系时可选择任一共享布局，不限定使用下节 reading。

写 `layout: "editorial"`，并填写 `editorial_variant`。通用字段包括 `id / title / surface / notes / visual`，可用 `title_size`（36–110px）及 `body_size`（21–30px）。`visual` 仍需 `rationale` 与 `requirements`，`role` 默认按变体语义，`treatment` 默认 open，cover 与 closing 默认为 none；editorial 条目不强加图标字段。页面微字采用根对象已有的 `company / year`，页脚沿用 `footer_label`、品牌与页码，不写虚构品牌或年份。

| `editorial_variant` | 必需内容与配图 | 可选内容 |
|---|---|---|
| `cover` | `title`、`image` | `subtitle`、`kicker` |
| `intro` | `title`、非空字符串 `copy`、`image` | — |
| `contents` | `title`、`items` 2–8 项，每项非空 `title / label`；`image` | `copy` |
| `about` | `title`、非空字符串 `lead`、`columns` 恰好 2 段非空字符串；`image` | — |
| `services` | `title`、`items` 1–3 项，每项非空 `title / text`；`images` 1–3 张 | — |
| `process` | `title`、`items` 2–5 项，每项非空 `title / text`；`image` | — |
| `portfolio` | `title`、`images` 2–6 张 | `copy` |
| `closing` | `title`、`image` | `subtitle`、`copy` |

这八个带图变体都需配图，风格的 `image_free_layouts` 不作用于 editorial。只有 services 与 portfolio 使用 `images`，其他变体只使用单个 `image`；两者互斥。图片对象沿用共享 `src / alt / ratio / brief` 等字段，`src / alt` 必填，`caption` 可选且一旦填写必须非空，输出为可编辑文字。同页多图的路径规范化后也不可指向同一文件，不以重复图片凑数量。

`contents.items.label` 必须由实际内容给出，构建器不自动编造目录页码。按表格填写各变体适用字段；不接受顶层 `captions`、`mode`、`label`、`note`，也不接受用数组对代替条目对象。图片说明写在该图的 `caption`，讲稿与来源仍写 `notes`。

```json
{
  "id": "p02",
  "layout": "editorial",
  "editorial_variant": "intro",
  "title": "让日常，多一份从容。",
  "copy": "从实际使用出发，组织材料、光线与人与空间的关系。",
  "image": {
    "src": "images/intro.png",
    "alt": "自然光下的木材、亚麻与陶器形成一组日常物件",
    "caption": "概念摄影 · 用于说明视觉方向"
  }
}
```

这个片段说明结构，不是业务事实模板。正式示例见暖褐风格的 [演讲稿](../../warm-minimal-editorial-slides/assets/deck.example.json) 和 [阅读稿](../../warm-minimal-editorial-slides/assets/deck.reading.example.json)。需要新图时为每张图填写独立 `brief`，用 `prepare_images.py` 生成逐图清单；普通制作准备图片后直接构建，仍不自动执行内容自检或导出。

### reading：可选复合信息布局

这是保留兼容的可选复合布局，speech 与 reading 两种用途、所有风格均可使用。只有选择 `layout: "reading"` 时，才遵守本节的分区和模块结构；阅读型用途不要求选择此布局。`summary` 必填，用一两句话说明本页结论。`composition` 取 `half_lr / half_tb / half_diagonal / quarter`，其几何只作用于当前布局的主体区，不含页头、页脚和全宽摘要。页头与字号仍由风格决定。

| `composition` | 该布局的图片区 | 该布局的内容区 |
|---|---|---|
| `half_lr` | 左右各半，一张主图在左 | 右侧最多三个模块纵向排列 |
| `half_tb` | 上下各半，上方一至三张图 | 下方一行：两个模块，或一个 span: 2 模块 |
| `half_diagonal` | 左上与右下各一张图 | 右上与左下各一个模块 |
| `quarter` | 四宫格的左上一张图 | 其余三格各一个模块 |

`blocks` 为 1–4 个可编辑模块，上限随 `composition` 变化并由 `--check-plan` 核对：左右最多 3 个（在右半区纵向堆叠，span 无效）；上下只有一行，即 2 个并排模块或 1 个 `span: 2` 的整行模块；对角固定 2 个；四分之一固定 3 个。每块必填 `type/title`，标题图标按风格的 `heading_icons` 策略选择；可选 `note` 记录说明或来源。上下布局可用 `span: 2` 让流程占整行；对角和四分之一每块各占一格，不设置 span: 2。数组上限不是任意文字长度的容纳保证。

| `type` | 数据字段与容量 | 视觉表达 |
|---|---|---|
| `process` | `steps` 3–6 个 `{title, text, output?}` | 顺序、动作与产出；窄分区建议 3–4 步 |
| `matrix` | `columns` 2–5 列；`rows` 2–6 行，各行列数一致 | 对象在共同维度上的差异与对应 |
| `layers` | `layers` 2–4 个 `{title, items}`；每层 1–5 个短模块 | 层名与模块分组 |
| `facts` | `rows` 2–5 个 `{label, text}` | 前提、责任、边界与解释 |
| `chart` | `chart_type/categories/series/unit/source` | ECharts 比较、趋势与构成；见 [图表契约](charts.md) |

按本页需要选择模块，不要求每张阅读页都含流程、矩阵、层级或图表；文字说明本身足以表达时可选 facts。`visual.role: briefing`，`treatment: open`；`visual_blocks/tables/layers/steps/charts` 同时核对计划和实际可见内容。

`image` 与 `images` 必选其一。左右和四分之一需要一张图，对角需要两张，上下可用 1–3 张。各图可加短 `caption`，保持可编辑，字号依当前主题。缺图仍需各自的 `brief`；同页不能重复 src。窄而高的左右图片区可选 4:3；上下、对角和四分之一优先用横向场景，主体完整且适合实际图框。若比例不适合，调整构图或选择另一种内容布局，不强行拉伸。

```json
"composition": "half_diagonal",
"images": [
  {"src": "images/overview.png", "alt": "产品工作台与外围模块", "caption": "产品全景"},
  {"src": "images/workflow.png", "alt": "提交、校验与归档协作场景", "caption": "协作细节"}
]
```

上例还需两个 `blocks`。正式构建需要全部配图；草稿逐图记录缺图。用户可自行核对主体分区比例、位置、图区覆盖、字体、图表标签、文本碰撞以及离线编辑和保存；Agent 不自动启动浏览器验收。

完整示例见海蓝玻璃 Skill 的 `assets/deck.reading.example.json`。所有风格均可选用该布局并采用自己的外观；示例不限定阅读型用途必须采用同样的构图。

### closing：有配图的收束

`title` 例如“感谢聆听”，`chapter` 可为合作意向，`subtitle` 为一句愿景；可加两行 `message`；可选 `variant`：`standard / mirror / full`。`product` 默认根 `title`。每项都是本次大纲的内容，不自动制造联系信息。

是否补尾页在规划时决定。构建器严格按 `slides` 构建，不擅自加页，避免违反明确页数。

## 共享构图布局

下列 20 种布局与基础版式一起供所有风格及两种用途使用；结构与可编辑组件由共享 `composition_layouts.py` 实现。名称含 photo 只标识有图片区域，不要求摄影，图片可以是当前风格的模型、场景或其他合适素材。无图布局不因 style 强制添加图片。

| 布局 ID | 内容结构 | 布局 ID | 内容结构 |
|---|---|---|---|
| `photo_pair` | 双图夹文 | `offset_pair` | 阶梯错位双图 |
| `statement_tags` | 大字与标签群 | `checklist_photo` | 半幅图片与分组清单 |
| `snake_timeline` | 双行折返时间线 | `metric_cards` | 可选横幅与指标卡 |
| `photo_strip` | 多图条带与底部标题 | `problem_columns` | 问题分栏与底部标题 |
| `service_cards` | 不等尺寸服务块 | `metric_circles` | 大小圆指标 |
| `chart_focus` | 结论与独立图表 | `photo_banner` | 大标题与横幅图片 |
| `photo_divider` | 满幅图片与章节短句 | `side_index` | 侧向标题与目录 |
| `editorial_story` | 双段正文与竖幅图片 | `step_sidebar` | 侧栏说明与竖排步骤 |
| `type_poster` | 纯文字海报与章节号 | `editorial_columns` | 可变宽度的文字、图片、人物、分组与图表栏目 |
| `hub_spoke` | 中心概念与分支关系 | `step_row` | 横向步骤与说明 |

准确字段、图片数量、条目容量和示例见 [共享构图目录](shared-layouts.md)。这些布局不携带风格专属页头、颜色、字体或摄影要求；新结构也按同一共享机制添加，不另建风格白名单。

文字海报与编辑分栏的完整字段见 [文字海报与编辑分栏](shared-layouts.md#文字海报与编辑分栏)。`type_poster` 无图，支持 cover / chapter / statement；cover 与 statement 可通过 placement 选择左下、居中或右下，statement 可带 copy 与 bullets，章节变体保留可编辑 number 与必需 title。`editorial_columns` 为 2–6 栏，所有图片嵌套在栏目中，支持每栏 1–4 名独立 people 身份、gallery 图片、2–6 项无序 groups、chart 图表及 CSS 简化 monitor 框。groups 每项 title 必填、text/icon 可选；text 栏已有 heading 或实际承载显示的页标题时可省略 paragraphs。show_title 为 false 时仅隐藏展示态标题，单列 gallery 可用 row_weights 分配相对行高。

分栏按说明、联系信息、团队、图集或图表对比关系使用不同选版 profile：栏目数、成员数、image / gallery 栏图片总数与实际 chart 栏数各自计数，图集不包含团队头像。`shared.editorial_charts` 需要 2–6 个真实图表栏，每栏 chart 遵循完整数据合同，可加 copy 解释，自动进入离线编辑、保存与原生图表导出。`side_index.items` 支持 2–12 项。`hub_spoke / step_row` 字段及计数见 [中心关系与横向步骤](shared-layouts.md#中心关系与横向步骤)，当前合计 20 种共享构图、49 个 profile。`metric_cards` 还可使用 [单一数据源进度条](shared-layouts.md#指标卡进度条)，`chart_focus` 支持实心 `pie`，均复用已有布局。

## 页底结论、标签与因子

内容页可用下列一种 `bottom`，也可省略。优先一句清楚的结论；不要为装饰而强加标签。

```json
{"type":"text","text":"让每一步处理都有据可查","presentation":"open"}
{"type":"tags","label":"覆盖对象","items":["合同","供应商","付款"]}
{"type":"factors","label":"方案价值","items":["对象清晰","规则一致","证据完整"]}
```

`tags` 最多 12 项，`factors` 最多 5 项，适合短词。数组上限只是输入边界，不保证任意长度文字都放得下；最终版式由用户自行查看。

## 从最小示例开始

用途确认后复制当前所选 Skill 的演讲型示例 `assets/deck.example.json`，或参考 `deck.reading.example.json` 建立本次项目的 `deck.json`，根据实际大纲改写；这些是结构示例，不是内容生成模板。第一次缺图时直接运行提示词导出；不要把示例空路径当成用户应补充的额外资料。
