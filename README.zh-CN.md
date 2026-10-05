<a id="readme-top"></a>

<div align="center">

<h1>PPT-workbench-skill</h1>

<p><strong>把一份大纲，变成风格完整、可继续编辑的演示稿。</strong></p>
<p>九种视觉风格 · 演讲与阅读双模式 · 单文件 HTML 离线交付</p>

<p><a href="README.md">English</a> · <strong>简体中文</strong></p>

<p>
  <a href="#快速开始">快速开始</a> ·
  <a href="#视觉风格">视觉风格</a> ·
  <a href="#演讲型与阅读型">演讲型与阅读型</a> ·
  <a href="#版式库与自主选版">版式库</a> ·
  <a href="#命令行构建">命令行构建</a> ·
  <a href="#播放编辑与导出">播放与导出</a>
</p>

<p><code>Codex / Claude Code</code> &nbsp; <code>共享套件 v3.7.0</code> &nbsp; <a href="LICENSE">MIT 许可证</a></p>

</div>

---

把大纲交给 Agent，选好视觉风格和用途，就能拿到一份完整的演示稿：配图、图表和版式都按每页内容安排。入口是 [`ppt-workbench`](skills/ppt-workbench/SKILL.md)。每种风格独立维护主题、配图提示词和参考图，共用同一套版式、图表、编辑与导出工具。

| 整稿风格统一 | 信息贴合用途 | 打开即用 |
|---|---|---|
| 封面、字体、配图与尾页遵循同一套视觉规范。 | 演讲型服务现场讲解，阅读型让读者独自也能看懂。 | CSS、脚本、图片、图标和图表全部内嵌，自带编辑、打印与 PPTX 导出。 |

> **交付格式**：一个独立的 `.html` 文件。需要 PowerPoint 时，点播放器的“导出 PPTX”（或运行 `export_pptx.cjs`）得到可编辑的 `.pptx`，再在 PowerPoint 中过一遍。

## 视觉风格

下方预览三款插画风格，完整九种见后面的表格。点击图片查看原图；示例业务内容与图表数字仅作演示。

| 素白蓝调 | 海蓝玻璃 | 写实微缩 |
|:---:|:---:|:---:|
| <a href="skills/white-blue-slides/assets/reference-design/approved-open-icons.jpg"><img src="skills/white-blue-slides/assets/reference-design/approved-open-icons.jpg" alt="素白蓝调业务机制页：白色模型、蓝色语义图标与可编辑说明" width="290"></a> | <a href="docs/images/examples/speech-product.png"><img src="docs/images/examples/speech-product.png" alt="海蓝玻璃产品能力页：海军蓝标题、灰青强调与玻璃展陈场景" width="290"></a> | <a href="docs/images/examples/miniature-speech-cover.png"><img src="docs/images/examples/miniature-speech-cover.png" alt="写实微缩封面：暖灰纸底、石墨标题与细致的团队工作空间" width="290"></a> |
| 暖白纸底 · 明亮主蓝 · 哑光模型 | 海军蓝 · 玻璃材质 · 香槟金 | 暖灰纸底 · 真实材质 · 生动人物 |
| [`white-blue-slides`](skills/white-blue-slides/SKILL.md) | [`navy-glass-slides`](skills/navy-glass-slides/SKILL.md) | [`realistic-miniature-slides`](skills/realistic-miniature-slides/SKILL.md) |

九种风格都支持演讲型与阅读型。一份演示稿只用一种风格；配图画什么，由你的内容决定。

<details>
<summary><strong>全部九种风格、风格 ID 与更多示例</strong></summary>

| 风格 | `style` ID | 视觉特点 |
|---|---|---|
| **[素白蓝调](skills/white-blue-slides/SKILL.md)** | `scene-white` | 暖白纸底、明亮主蓝、白色哑光模型场景与微缩人物 |
| **[海蓝玻璃](skills/navy-glass-slides/SKILL.md)** | `saas-3d` | 暖白纸底、海军蓝文字与重点面、灰青及少量香槟金、精细的玻璃展陈 |
| **[写实微缩](skills/realistic-miniature-slides/SKILL.md)** | `real-miniature` | 暖灰、石墨、灰蓝、鼠尾草绿及少量赭黄；35–45° 微缩场景、写实材质、表情生动的人物，配图无字 |
| **[黑白编辑式](skills/monochrome-editorial-slides/SKILL.md)** | `monochrome-editorial` | 黑白页面、大标题、宽阔留白与冷调编辑摄影 |
| **[暖褐极简编辑式](skills/warm-minimal-editorial-slides/SKILL.md)** | `warm-minimal-editorial` | 暖米白、深褐、克制排版与自然暖调摄影 |
| **[原色建筑编辑式](skills/primary-architecture-slides/SKILL.md)** | `primary-architecture` | 白底黑字、窄高大标题、错位文字栏、建筑摄影与四色章节页 |
| **[留白衬线影集](skills/airy-portfolio-slides/SKILL.md)** | `airy-portfolio` | 近白纸色、黑色衬线字、宽阔留白与自然彩色作品摄影 |
| **[米白环线商务](skills/beige-ring-business-slides/SKILL.md)** | `beige-ring-business` | 温暖米白、黑色无衬线字、细线圆环与自然商务摄影 |
| **[黑白大理石商务](skills/monochrome-marble-slides/SKILL.md)** | `monochrome-marble` | 黑白反转、大号衬线标题、大理石纹理与自然彩色商务摄影 |

| 素白蓝调 · 分层架构 | 海蓝玻璃 · 演讲型封面 |
|:---:|:---:|
| <a href="skills/white-blue-slides/assets/reference-design/approved-architecture.jpg"><img src="skills/white-blue-slides/assets/reference-design/approved-architecture.jpg" alt="五层白色立体架构模型，模块直接标注，蓝色通道展示数据流向" width="440"></a> | <a href="docs/images/examples/speech-cover.png"><img src="docs/images/examples/speech-cover.png" alt="海蓝玻璃演讲型封面：左侧价值主张，右侧三维产品展陈" width="440"></a> |

| 写实微缩 · 阅读型页面 | 素白蓝调 · 页面参考 |
|:---:|:---:|
| <a href="docs/images/examples/miniature-reading-diagonal.png"><img src="docs/images/examples/miniature-reading-diagonal.png" alt="写实微缩阅读型对角布局：全景与协作近景搭配责任矩阵和环形图" width="440"></a> | <a href="skills/white-blue-slides/assets/reference-design/approved-overview.jpg"><img src="skills/white-blue-slides/assets/reference-design/approved-overview.jpg" alt="素白蓝调页面与场景参考，展示构图和视觉层级" width="440"></a> |

配图参考：[海蓝玻璃产品展陈](skills/navy-glass-slides/assets/reference-design/approved-product-overview.png) · [写实微缩团队工作空间](skills/realistic-miniature-slides/assets/reference-design/approved-workflow.png)。

参考图只用来确定材质、尺度与视觉层级，其中的业务内容不会被当作新项目的事实。

</details>

## 快速开始

### 1. 安装 Skill

装好 Node.js/npm 后，用 [Skills CLI](https://github.com/vercel-labs/skills#options) 直接从本仓库安装。

**Codex：**

```bash
npx skills@latest add Johnson-Yrq/ppt-workbench-skill --skill '*' -g -a codex
```

**Claude Code：**

```bash
npx skills@latest add Johnson-Yrq/ppt-workbench-skill --skill '*' -g -a claude-code
```

- `--skill '*'`：安装工作台与全部九种风格，共十个包；星号两侧的引号要保留。
- `-g`：全局安装，所有项目可用；去掉则只装到当前项目。
- `-a`：指定目标 Agent。

<details>
<summary><strong>查看可用 Skill 或手动安装</strong></summary>

只列出 Skill，不安装：

```bash
npx skills@latest add Johnson-Yrq/ppt-workbench-skill --list
```

或者克隆仓库后复制：

```bash
git clone https://github.com/Johnson-Yrq/ppt-workbench-skill.git
cd ppt-workbench-skill
```

**Codex：**

```bash
mkdir -p ~/.codex/skills
cp -R skills/* ~/.codex/skills/
```

**Claude Code：**

```bash
mkdir -p ~/.claude/skills
cp -R skills/* ~/.claude/skills/
```

十个目录须同级放置：`white-blue-slides` 带有其他风格依赖的共享套件，`ppt-workbench` 是统一入口。更新前先备份已有目录。只用素白蓝调时，可以单独安装 `white-blue-slides`。

</details>

### 2. 把大纲交给 Agent

让 Agent 先问风格和用途：

```text
用 $ppt-workbench，根据这份大纲制作演示稿，先让我选择风格和演讲型／阅读型。
```

已经想好时直接说明：

```text
用 $ppt-workbench，选择海蓝玻璃风格，做成阅读型。按内容需要安排配图、流程、矩阵和图表。
```

<details>
<summary><strong>直接调用指定风格</strong></summary>

```text
用 $white-blue-slides，把这份大纲做成素白蓝调风格的演讲型演示稿。
```

```text
用 $navy-glass-slides，把这份方案做成海蓝玻璃风格的阅读型演示稿。
```

```text
用 $realistic-miniature-slides，把这份团队协作方案做成写实微缩风格的阅读型演示稿，配图不要文字。
```

</details>

Agent 只问缺少的选项，项目里已确认的风格和用途直接沿用。说“你来选”，它会按目标挑选并说明理由。模板默认值不算你的选择，续做项目也不会因为换了主题而自动换风格。

### 3. 打开、演示与编辑

用浏览器打开交付的 HTML，即可离线演示，并直接修改文字和图表数据。改完点**另存 HTML**保存；浏览器里的修改不会回写 `deck.json`。

## 演讲型与阅读型

| | 演讲型 `speech` | 阅读型 `reading` |
|---|---|---|
| **读者** | 跟随讲解者理解 | 没有讲解，独自阅读 |
| **每页内容** | 一个结论和少量支撑，细节放讲稿 | 结论、机制、依据与边界都留在页面上 |
| **可视化** | 主场景、关键步骤、少量标注 | 增加真实的流程节点、比较维度、分层、职责与图表 |
| **内容超量时** | 拆成多页逐步讲 | 续到关联页面，不靠缩小字号 |

用途决定一页要自己讲清多少，不决定用哪种版式、配图比例或字号；所有版式两种用途都能用。阅读型的信息量来自更多有意义的关系和依据，而不是更小的字或更长的段落。没有可靠数字时，用流程、职责、比较或分层来表达，不编造指标。

两项选择记录在 `deck.json` 根对象（完整项目还需要标题和页面）：

```json
{
  "style": "saas-3d",
  "presentation_mode": "reading"
}
```

缺少这两个字段的旧稿按素白蓝调、演讲型构建；新稿应显式记录。详见 [用途与信息密度](skills/white-blue-slides/references/presentation-modes.md)。

### `reading` 复合版式

共享版式中的 `reading` 把配图和内容模块排成四种固定分区。它是可选版式，两种用途都能用；下面的比例只在选用它时生效，按页面主体计算，不含页头、页脚和全宽摘要。

| 分区 | `composition` | 配图 | 其余内容 |
|---|---|---|---|
| **1/2 左右** | `half_lr` | 左半区一张主图 | 图表加解释，或流程加责任矩阵 |
| **1/2 上下** | `half_tb` | 上半区 1–3 张图 | 两组互补内容，如流程加趋势 |
| **1/2 对角** | `half_diagonal` | 左上、右下各一张图 | 另外两个象限各一个内容模块 |
| **1/4 配图** | `quarter` | 左上四分之一一张图 | 其余三区放图表、表格、图标与文字 |

<details>
<summary><strong>查看四种分区</strong></summary>

| 1/2 左右 | 1/2 上下 |
|:---:|:---:|
| <a href="docs/images/examples/reading-half-lr.png"><img src="docs/images/examples/reading-half-lr.png" alt="阅读型左右各半：左侧产品场景，右侧条形图与工作说明" width="440"></a> | <a href="docs/images/examples/reading-half-tb.png"><img src="docs/images/examples/reading-half-tb.png" alt="阅读型上下各半：上方双场景，下方处理流程与趋势折线图" width="440"></a> |

| 1/2 对角 | 1/4 配图 |
|:---:|:---:|
| <a href="docs/images/examples/reading-half-diagonal.png"><img src="docs/images/examples/reading-half-diagonal.png" alt="阅读型对角双图：左上和右下配图，其余区域展示能力矩阵与环形图" width="440"></a> | <a href="docs/images/examples/reading-quarter.png"><img src="docs/images/examples/reading-quarter.png" alt="阅读型四分之一配图：其余三区展示数量比较、交付核对表和使用边界" width="440"></a> |

海蓝玻璃风格，1920 × 1080 实际页面；图表数字为示例。

</details>

同页有多张配图时，各自表现不同的对象、阶段或视角，色彩与材质保持一致。完整字段见 [阅读型示例](skills/navy-glass-slides/assets/deck.reading.example.json)。

### 离线可编辑图表

两种用途都可以使用图表：**横向条形图**比较类别，**折线图**看时间趋势，**环形图**或**饼图**看整体构成。每张图都要有单位和来源，在旁边写明结论与边界；示例数字要标明是示例。

要改数据，在播放器中点「编辑文字」，再展开图表右下角的「编辑图表数据」，修改类别、系列名和数值，图表即时刷新，「另存 HTML」后仍可继续编辑。改了数值，记得核对旁边的结论是否还成立。

图表以 SVG 离线渲染。每张图支持 2–8 个类别、1–3 组有限非负数；环形图和饼图只能有一组，且合计大于零。详见 [图表使用说明](skills/white-blue-slides/references/charts.md)。

### 页头、封面与尾页

素白蓝调、海蓝玻璃和写实微缩共用六种内容页页头，由 Agent 按每页内容自动选择，不额外询问；你指定某一种时照办。其余六种风格在各自主题中设计页头。

![六种页头样式](skills/white-blue-slides/assets/header-styles.png)

| `header` | 适合 |
|---|---|
| `standard` 标准 | 常规内容页（默认） |
| `compact` 紧凑 | 阅读型高密度页、表格、架构 |
| `rail` 侧栏编号 | 分章节推进、议程、分步讲解 |
| `band` 浅底横幅 | 章节开头、重点结论 |
| `aside` 标题副标题分栏 | 标题短、副标题较长的页 |
| `ghost` 水印页码 | 留白多的页、表格页 |

在 `deck.json` 根对象写 `"header": "band"` 作用于整稿，单页的 `header` 可以覆盖。

`cover` 封面版式有四种左右排布，`closing` 尾页有三种，由 Agent 按配图构图选择；想自己指定，在该页写 `variant`。

![封面与尾页排布](skills/white-blue-slides/assets/cover-variants.png)

| `variant` | 外观 |
|---|---|
| `standard` 标准 | 左文右图（默认，唯一支持右侧层级标注） |
| `mirror` 左图右文 | 图文左右对调 |
| `full` 出血大图 | 配图铺满右上角，左缘渐隐 |
| `panel` 色块分栏 | 文案落在左侧浅色块上，仅封面 |

## 版式库与自主选版

不必逐页指定版式。Agent 理解大纲后，逐页判断内容关系，再从共享版式库里挑选合适的结构。版式库共有 **48 个可执行 profile**，由 12 种基础版式、20 种共享构图和 8 个 `editorial` 变体组成，九种风格都能使用，外观仍由所选风格决定。

Agent 按以下顺序为每页选版：

1. **内容关系**：先判断这一页是步骤、对比、层级、数据还是并列要点。判断靠理解语义，不按关键词匹配。
2. **条目数量**：每种版式都有可容纳的主体数，例如 `snake_timeline` 需要 4–8 步，`metric_circles` 只放 2 个指标。
3. **图片与数据**：按实际图片数量筛选；图表版式要求真实数量、单位和来源，不为凑版式补造数据。
4. **文字容量**：估算本页文字量，超出容量的候选降分，并提示分区或拆页。
5. **整稿节奏**：相邻页尽量不重复同一构图，只在得分相近时起作用。

筛选和排序由 [`select_layout.py`](skills/white-blue-slides/scripts/select_layout.py) 离线完成，每个落选候选都附排除原因。构建后的审查若发现文字溢出，用 `--feedback` 排除当前版式再选一次。

| 内容关系 | 候选版式 |
|---|---|
| 封面、章节开场 `cover` | `cover`、`photo_banner`、`type_poster`、`editorial` |
| 解释一个观点 `explanation` | `split`、`scene`、`photo_pair`、`offset_pair`、`photo_divider`、`editorial_story`、`editorial_columns` |
| 并列要点 `parallel` | `split`、`domains`、`statement_tags`、`problem_columns`、`service_cards`、`hub_spoke` |
| 步骤流程 `sequence` | `journey`、`flow`、`snake_timeline`、`step_sidebar`、`step_row`、`reading` |
| 时间线 `timeline` | `journey`、`snake_timeline`、`step_sidebar`、`step_row` |
| 多维对比 `comparison` | `journey`、`table`、`metric_cards`、`metric_circles`、`reading` |
| 层级与架构 `hierarchy` | `architecture`、`hub_spoke`、`reading` |
| 关系网络与因果 `network` / `causality` | `relations`；关系网络也可用 `hub_spoke` |
| 数据图表 `data` | `chart_focus`、`editorial_columns`、`reading` |
| 关键指标 `statistics` | `metric_cards`、`metric_circles` |
| 目录 `agenda` | `domains`、`side_index`、`editorial` |
| 图集与团队 `gallery` / `team` | `photo_pair`、`photo_strip`、`photo_banner`、`editorial`、`editorial_columns` |

此外还有引言、联系方式、控制点、公式、表格、评价、复合模块和尾页等关系，共 22 种。完整规则见 [内容自主选版](skills/white-blue-slides/references/layout-selection.md)。

### 20 种共享构图

<a href="docs/images/layouts/shared-compositions.jpg"><img src="docs/images/layouts/shared-compositions.jpg" alt="20 种共享构图的实际页面缩略图，按编号排列" width="100%"></a>

以暖褐极简编辑式渲染，1920 × 1080；图片为原创生成意象，文字与数字均为示例。

| # | 构图 | 适合 | # | 构图 | 适合 |
|---|---|---|---|---|---|
| 01 | `photo_pair`<br>双图夹文 | 两个视角夹着一段论证 | 11 | `chart_focus`<br>结论与独立图表 | 一个结论配一张图表 |
| 02 | `offset_pair`<br>阶梯错位双图 | 从整体到细节的递进 | 12 | `photo_banner`<br>大标题与横幅图片 | 开场、引言、图片展示 |
| 03 | `statement_tags`<br>大字与标签群 | 一句主张加 2–6 个标签 | 13 | `photo_divider`<br>满幅图片与章节短句 | 章节过渡 |
| 04 | `checklist_photo`<br>半幅图片与分组清单 | 能力范围与使用边界 | 14 | `side_index`<br>侧向标题与目录 | 2–12 项目录 |
| 05 | `snake_timeline`<br>双行折返时间线 | 4–8 步的长流程 | 15 | `editorial_story`<br>双段正文与竖幅图片 | 叙事、评价、联系方式 |
| 06 | `metric_cards`<br>图片横幅与指标卡 | 2–4 个指标或对比维度 | 16 | `step_sidebar`<br>侧栏说明与竖排步骤 | 2–4 步方法 |
| 07 | `photo_strip`<br>多图条带与底部标题 | 2–5 张并列图片 | 17 | `type_poster`<br>纯文字海报与章节号 | 无图的开场、主张与结尾 |
| 08 | `problem_columns`<br>问题分栏与底部标题 | 2–3 个并列问题 | 18 | `editorial_columns`<br>自由宽度编辑分栏 | 图文、图组、人物、图表混排 |
| 09 | `service_cards`<br>不等尺寸服务块 | 主次分明的三项服务 | 19 | `hub_spoke`<br>中心关系与分支 | 中心对象与 4–8 个相关因素 |
| 10 | `metric_circles`<br>大小圆指标 | 两个指标的主次对比 | 20 | `step_row`<br>横向步骤与说明 | 2–6 步横向流程或阶段 |

`editorial` 另有封面、引言、目录、关于、服务、流程、作品集和尾页 8 个变体。各构图的字段与容量见 [共享构图合同](skills/white-blue-slides/references/shared-layouts.md)。

### 基础版式

基础版式大多围绕一张主配图排布，`table` 可以无图。

| 版式 | 用途 | 版式 | 用途 |
|---|---|---|---|
| `cover` | 封面 | `architecture` | 分层架构与直接标注 |
| `scene` | 大场景与两侧说明 | `flow` | 步骤与控制点 |
| `split` | 左右说明或三段控制 | `domains` | 多领域清单 |
| `journey` | 阶段、比较或路径 | `formula` | 因素及其组合关系 |
| `table` | 表格与边界对照 | `relations` | 实体与关联 |
| `closing` | 带配图的尾页 | `reading` | [四种复合分区](#reading-复合版式) |

## 制作流程与配图

**确认风格与用途 → 理解大纲 → 逐页选版 → 建立 `deck.json` → 准备配图 → 构建 → 交付 HTML**

Agent 根据每页的内容关系、条目数量、图片和数据自主选版（见 [版式库与自主选版](#版式库与自主选版)）。成稿默认由你自己查看，并自行导出 PPTX 或 PDF；需要 Agent 代为检查或导出时，直接告诉它。

| 配图条件 | 处理方式 |
|---|---|
| **已有图片** | 先复用，并核对每张图与所在页面是否对应。 |
| **有内置生图工具** | 为每个适合配图的页面按逐页简报生成，查看、调整后再构建。 |
| **没有内置工具，但有自己的生图 API** | Agent 引导你在自己的终端配置 provider、基址、模型和密钥，脚本按清单自动生成全部缺图；密钥不经过对话。 |
| **都没有** | 导出逐页完整提示词和供图清单，收到图片后继续制作，可以分批提供。 |

每张缺图都需要本页独有的 `image.brief`，写清对象与数量、动作、关系、层级、细节和构图。导出器会提示缺项和跨页重复的简报。标题、真实数据、业务说明和架构标注都放在可编辑内容里，不画进图片。

<details>
<summary><strong>在 Claude Code 等环境中用自己的生图 API 自动生成</strong></summary>

Claude Code、Cursor 等终端 Agent 没有内置生图工具。Agent 会先完成拆页、`deck.json` 和提示词导出，再询问是否使用你自己的生图 API。你同意后，它会给出一条配置命令，请在**自己的终端**执行。密钥以不回显的方式输入，保存在 `~/.config/ppt-workbench/image-api.json`（仅当前用户可读），不会出现在对话或项目文件中。

```bash
# OpenAI 官方或兼容服务（url 换成实际基址，model 换成实际模型名）
python3 skills/white-blue-slides/scripts/generate_images.py --setup --provider openai --url https://api.openai.com/v1 --model gpt-image-1
```

```bash
# Google Gemini
python3 skills/white-blue-slides/scripts/generate_images.py --setup --provider gemini --model gemini-2.5-flash-image
```

常见中转服务有预设，例如 Right Code：`--setup --preset rightapi --model gpt-image-2.5`（异步画图接口，脚本自动提交任务并轮询结果）。已设置 `OPENAI_API_KEY` 或 `GEMINI_API_KEY` 环境变量时，加 `--no-key`。

之后由 Agent 依次执行：`--check` 验证配置（免费）、`--dry-run` 预演（无需密钥）、`--pages 2` 先试一页，再生成其余缺图。结果按清单文件名保存，用页面纸色补边到目标比例，并记录在 `image-manifest.json`。每张图仍要逐一查看：不合格就改写简报，加 `--force` 重新生成，旧版本自动保留。

支持的 provider：`openai`（OpenAI Images API 及兼容代理，含 `gpt-image-1`、`dall-e-3`）和 `gemini`（`gemini-2.5-flash-image` 等）。字段、请求格式与限制见 [通过生图 API 自动生成配图](skills/white-blue-slides/references/image-api.md)。

</details>

<details>
<summary><strong>配图中的文字与需要保留的文件</strong></summary>

素白蓝调与写实微缩的配图默认无字；写实微缩只支持 `ui_text: "none"`，白板、屏幕、文件、日历和键帽上都不出现文字。海蓝玻璃默认 `ui_text: "demo"`，软件屏幕内只允许 Overview、Analytics、Activity、Demo 四个示意标签，也可选 `none`。配图里画的图表只是装饰，不代表真实数据。

最终交付物是一个独立的 `.html` 文件。`deck.json`、提示词和供图清单请保留，方便日后续改。缺图时的 `--draft` 构建只用于内部预排。

</details>

## 命令行构建

以下步骤通常由 Agent 代为执行。自己运行时，在仓库根目录执行，`project/` 为本次演示稿的工作目录：

```text
project/
├── 大纲.md
├── deck.json
├── images/          # 本项目配图
└── 演示稿.html      # 最终交付
```

### 从示例开始

| 示例 | 内容 |
|---|---|
| [素白蓝调](skills/white-blue-slides/assets/deck.example.json) | 封面、场景信息页和尾页 |
| [海蓝玻璃 · 演讲型](skills/navy-glass-slides/assets/deck.example.json) | 简洁的产品介绍与轻量强调 |
| [海蓝玻璃 · 阅读型](skills/navy-glass-slides/assets/deck.reading.example.json) | `reading` 四种分区、流程、矩阵与图表 |
| [写实微缩 · 演讲型](skills/realistic-miniature-slides/assets/deck.example.json) | 团队工作空间、协作交接与轻量强调 |
| [写实微缩 · 阅读型](skills/realistic-miniature-slides/assets/deck.reading.example.json) | `reading` 四种分区、职责流程与示例任务图表 |

其余六种风格也在各自的 `assets/` 目录提供 `deck.example.json` 与 `deck.reading.example.json`。示例附带配图简报，正式构建前需要准备好图片。图片路径相对 `deck.json` 所在目录，完整数据格式见 [内容数据与构建](skills/white-blue-slides/references/deck-format.md)。

### 准备配图并构建

```bash
# 导出逐页提示词与供图清单（不调用模型，不联网）
python3 skills/white-blue-slides/scripts/prepare_images.py project/deck.json \
  --out project/image-handoff

# 图片齐全后，构建单文件 HTML
python3 skills/white-blue-slides/scripts/build_deck.py project/deck.json \
  --out project/演示稿.html
```

结构错误或缺图时，构建器会停止并指出需要修改的字段。

<details>
<summary><strong>可选检查</strong></summary>

需要审查成稿或维护工具时运行：

```bash
# 检查设计决策与页面结构，不要求图片已存在
python3 skills/white-blue-slides/scripts/build_deck.py project/deck.json \
  --check-plan --out project/design-plan.json

# 逐页渲染、保存截图并报告问题
node skills/white-blue-slides/scripts/audit_deck.cjs project/演示稿.html \
  --out project/qa --browser chrome
```

审查会报告文字越界与重叠、缺图、外部依赖、图文分区和图表渲染问题。配图主体是否完整、是否与文字对应，仍需人工判断。

</details>

<details>
<summary><strong>构建选项</strong></summary>

| 工具或参数 | 用途 |
|---|---|
| `match_paper.py project/images/*.png --deck project/deck.json --dry-run` | 按当前主题检查配图底色与透明通道；去掉 `--dry-run` 后校正轻微偏差，并保留备份 |
| `--embed-format keep` | 保留原图格式，不转 WebP |
| `--embed-quality 85` | 设置图片压缩质量 |
| `--builder` | 加载项目自定义版式（基于共享组件） |
| `--allow-restyle` | 仅在用户要求时，允许超出所选主题修改封面、页头或页脚 |

旧稿无需迁移即可构建：`triad` 按图片在右的 3 项 `split` 渲染，残留的 `layout_selection`、`rationale` 字段会被忽略。流程行排布、架构引线、阶段时间标签、更多配图比例（`2:1 / 21:9 / 3:1`）以及 `image.background_mode: white-matte` 等细项，见 [`deck-format.md`](skills/white-blue-slides/references/deck-format.md)。

</details>

## 播放、编辑与导出

工具栏提供：**总览 · 全屏 · 讲稿 · 编辑文字 · 另存 HTML · 导出 PPTX · 导出 PDF / 打印**。页面画布为 1920 × 1080，在任何窗口或屏幕上等比缩放，不拉伸、不裁切；编辑时为工具栏留出空间。编辑后用「另存 HTML」保存，修改不会回写 `deck.json`。

| 按键 | 作用 | 按键 | 作用 |
|---|---|---|---|
| `→` / `PageDown` / `空格` | 下一页 | `O` | 总览 |
| `←` / `PageUp` | 上一页 | `F` | 全屏 |
| `Home` / `End` | 首页／末页 | `N` | 讲稿面板 |
| `Esc` | 退出总览、编辑或讲稿 | URL `#3` | 直接打开第 3 页 |

与 Cmd、Ctrl 或 Alt 组合的按键交给浏览器，Cmd+F、Ctrl+P 等快捷键照常可用。

### 导出 PowerPoint

**导出 PPTX** 生成可编辑的 PowerPoint 文件：标题与正文保留为文本框，字号、粗细、颜色与间距不变；信息块、标签与分隔线转为形状；配图与图标转为图片；图表转为 PowerPoint 原生图表并内嵌数据表（可用“编辑数据”）；讲稿写入备注。元素位置按实际渲染结果测量。全稿统一使用一种字体（默认微软雅黑，Windows 与 macOS 的 Office 都自带），英文和数字可能略宽。导出器内嵌在每份演示稿中，无需联网。命令行导出效果相同，还能处理加入该按钮之前构建的旧稿：

```bash
node skills/white-blue-slides/scripts/export_pptx.cjs project/演示稿.html \
  --out project/演示稿.pptx --browser chrome [--font "PingFang SC"]
```

### PDF 与打印

点“导出 PDF / 打印”会打开浏览器打印窗口，选择“另存为 PDF”，保持幻灯片尺寸，不要改成 A4 或 Letter。页面为 PowerPoint 宽屏尺寸 **960 × 540 pt（13⅓ × 7.5 英寸）**。打印前会先渲染所有图表，包括还没翻到的页面；全屏状态下打印同样一页一张。

需要稳定的页面尺寸和“适合页面”的打开方式时，使用导出脚本（除 Playwright 外还需要 `pdf-lib`）：

```bash
# 在浏览器中编辑过的话，用「另存 HTML」后的文件导出
node skills/white-blue-slides/scripts/export_pdf.cjs project/演示稿.html \
  --out project/演示稿.pdf --browser chrome
```

<details>
<summary><strong>PDF 阅读器提示与 PDF 转回演示版</strong></summary>

部分 PDF 阅读器会忽略“适合页面”的设置，此时手动选择即可。macOS 把**显示滚动条**设为**始终**时，Chrome 的 PDF 演示模式可能露出下一页顶部的细条；在我们的测试中，改为**系统设置 → 外观 → 显示滚动条 → 滚动时**，重新加载 PDF 再进入演示即可消除（该设置会影响全系统的滚动条）。修改 PDF 纸张尺寸解决不了这个问题。非 16:9 屏幕会保留上下或左右边带。要用 PDF 演示时，请在实际使用的阅读器里确认效果，HTML 演示正常不代表 PDF 阅读器也正常。

如果只剩 PDF，可以用随附转换器（Python + Poppler）生成离线 HTML 演示版：一次显示一页，矢量轮廓保持清晰。演示版的文字不可编辑、不可选择，请保留原 PDF 和可编辑源稿。

```bash
python3 skills/white-blue-slides/scripts/pdf_to_slides.py project/演示稿.pdf \
  --out project/全屏演示版.html
```

</details>

每个 HTML 文件内嵌构建时的播放器。想用上播放器的修复，从源项目重新构建即可；如果在浏览器里编辑过，先保留那份副本。

## 扩展与开发

每个风格包独立维护页面主题、配图基底、参考素材和验收规范。版式与播放器功能由共享脚本提供，不随风格复制。

查看已安装的风格：

```bash
python3 skills/white-blue-slides/scripts/style_packs.py --list
```

它会自动发现所有同级的有效风格包，返回名称、ID、说明和 Skill 入口。新增的包会自动出现，无需修改工作台。

<details>
<summary><strong>包结构与新增风格</strong></summary>

新包按视觉特点用小写英文加短横线命名，以 `-slides` 结尾，并与 Skill 名一致；中文显示名用于工作台中的选择。

```text
skills/
├── ppt-workbench/                 # 统一入口
├── white-blue-slides/             # 素白蓝调 + 共享制作套件
│   ├── scripts/                  # 构建、供图清单、风格发现与检查
│   ├── assets/                   # 组件、播放器、版式与图表
│   └── references/               # 数据格式、用途、图表与接入规范
├── navy-glass-slides/             # 独立风格包
├── …                              # 其他风格包
└── new-style-slides/              # 未来新增的风格
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/
    │   ├── style.json
    │   ├── theme.css
    │   ├── image-style.txt
    │   └── reference-design/
    └── references/
        ├── design-system.md
        ├── image-workflow.md
        └── quality-check.md
```

在 `assets/style.json` 中声明 `schema: "html-slide-style/v1"`、唯一 ID、风格资源和检查契约。样稿确认并验证通过后设为 `ready`，与其他包同级安装，工作台、构建器和配图导出器会自动识别。新风格同样支持两种用途和全部共享版式。

```bash
# 开发检查时连同 draft 包一起列出（不会因此启用草稿）
python3 skills/white-blue-slides/scripts/style_packs.py --list --include-drafts
```

字段、接入步骤与验证要求见 [新增独立风格包](skills/white-blue-slides/references/adding-styles.md)。

</details>

### 依赖与开发检查

| 用途 | 依赖 |
|---|---|
| 构建 HTML、导出提示词、列出风格、调用生图 API | Python 3.9+ 标准库 |
| WebP 压缩、API 配图按比例补边 | Pillow（可选；缺少时保留原图格式） |
| 配图底色校准 | NumPy + Pillow |
| 浏览器自动检查 | Node.js + Playwright + Chrome/Chromium |
| 命令行导出 PPTX | Playwright + Chrome/Chromium（工具栏按钮无需任何依赖） |
| 导出 PDF（核对页数与尺寸） | Playwright + pdf-lib + Chrome/Chromium |
| 已有 PDF 转演示版 | Python + Poppler（`pdfinfo`、`pdftocairo`） |
| 总览拼图 | Sharp（可选） |

ECharts 5.6.0 以精简构建随套件内置（条形、折线、饼图与 SVG 渲染器，约 550 KB），无需安装，也不依赖 CDN。要新增图表类型，在 [`echarts.entry.js`](skills/white-blue-slides/assets/vendor/echarts.entry.js) 中引入，并按文件内的命令重新构建。生图能力来自 Agent 环境或你自己的生图 API，不随 Skill 安装。

修改脚本或资源后运行自测：

```bash
python3 skills/white-blue-slides/scripts/selftest.py
```

自测覆盖共享组件、两种用途、风格隔离、风格发现、图表输入、缺图恢复和生图 API 脚本（使用离线假传输）。修改播放器、导出器或主题后，再用 `test_player.cjs` 对任一成稿运行播放器回归测试，覆盖翻页、快捷键、编辑、另存、PPTX 导出、全屏适配与打印。自测不能代替看真实页面：主题或版式改动后，请用真实配图构建并逐页查看。

## 许可证与素材

项目代码采用 [MIT](LICENSE) 许可证。第三方组件保留各自的许可证：

- Lucide 图标：[MIT 许可证](skills/white-blue-slides/assets/lucide-LICENSE.txt)。
- Apache ECharts：[Apache 2.0 许可证](skills/white-blue-slides/assets/vendor/ECHARTS-LICENSE.txt) 与 [NOTICE](skills/white-blue-slides/assets/vendor/ECHARTS-NOTICE.txt)，同时内嵌于含图表的成稿。

套件不包含任何 Logo 或公司名，页脚品牌信息由各项目自行提供。参考图用于展示风格，示例业务内容与数字不代表任何真实产品的能力或效果。

---

<p align="center"><a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="#readme-top">返回顶部 ↑</a></p>
