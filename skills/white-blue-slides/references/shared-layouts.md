# 共享布局目录

布局定义内容怎样排列，风格定义页面怎样呈现。所有布局都可用于 `speech` 或 `reading`；用途只决定内容密度和讲稿分工，不再自动改变分区比例、图文位置或页头。按本页需要表达的关系选择，不要求一份稿集齐所有布局。

逐页使用 [根据内容自主选版](layout-selection.md)：共享 [布局库](layout-library.json) 登记 **48 个可执行策略**：17 个基础布局策略、原 16 种共享构图、8 个 `editorial` 变体、`type_poster / editorial_columns` 对应的 5 个 profile，以及 `hub_spoke / step_row` 对应的 2 个 profile。共享构图现在共 20 种。先判断关系、数量、素材和真实数据，再由 `select_layout.py` 筛选候选。

## 布局与风格的分工

- 共享层维护数据字段、图文位置、模块排列、图片内嵌、可编辑文字及图表。新增通用布局在共享层实现，不限制为某个风格专用。
- 风格包维护页头模板、页脚表现、字体、字阶、颜色、线条、面板和图片媒介。相同的双图布局可以放真实摄影，也可以放符合该风格的模型配图。
- 原六种页头只由素白蓝调、海蓝玻璃、写实微缩的清单启用。新增风格通过本包的 `header_template` 呈现自己的页头，不需要 `--allow-restyle`。
- 旧 `layout: reading` 和四种 `composition` 保留为可选布局与旧稿兼容能力。新稿不用因用途是阅读型而选择它；未选该布局时不施加其等分规则。
- 用户给定内容、真实来源、可读性与资源完整性仍须保留。普通制作不自动开展整稿自检或导出；相关脚本用于工具开发或用户明确委托的检查。

## 已有共享布局

`cover / scene / split / journey / architecture / flow / domains / formula / table / relations / closing / reading` 的字段仍见 [数据契约](deck-format.md)。

`editorial` 的八个变体 `cover / intro / contents / about / services / process / portfolio / closing` 已是共享能力，不再按风格名单限制。它们的图文几何加载自共享 `editorial.css`，视觉随当前主题；字段见 [editorial 契约](deck-format.md#editorial编辑式图文页面)。

## 新增十六种构图

下表中的字段直接放在单页对象，不另包 `composition`。每页都有 `id / layout / title`，可选 `chapter / subtitle / surface / notes / title_size / body_size / visual`。`header` 仅适用于启用六种预设的风格。图片使用共用的图片对象，`images` 是其数组；`caption` 始终是可编辑文字。未列字段会被拒绝，避免内容被静默丢弃。

| `layout` | 构图 | 必需内容 | 可选内容与数量 |
|---|---|---|---|
| `photo_pair` | 双图夹文 | `images` 恰好 2 张、`copy` | `eyebrow` |
| `offset_pair` | 阶梯错位双图 | `images` 恰好 2 张、`paragraphs` 2–3 段字符串 | 副标题保留在标题组中 |
| `statement_tags` | 大字与标签群 | `copy`、`tags` 2–6 个字符串 | `image` 0–1 张 |
| `checklist_photo` | 半幅图片与分组清单 | `image`、`groups` 2–3 组 | 每组含 `title / text / checks`；每组 2–6 个状态项 |
| `snake_timeline` | 双行折返时间线 | `steps` 4–8 步 | `image` 0–1 张、`note`；输入数组始终按时间顺序 |
| `metric_cards` | 图片横幅与指标卡 | `metrics` 2–4 项、`source` | `image` 0–1 张、`copy` |
| `photo_strip` | 多图条带与底部标题 | `images` 2–5 张 | `copy`；各图可配 `caption` |
| `problem_columns` | 问题分栏与底部标题 | `items` 2–3 项，每项 `title / text` | `image` 0–1 张 |
| `service_cards` | 不等尺寸服务块 | `items` 恰好 3 项，每项 `title / text` | 每项可有独立 `image`；`highlight` 为 0–2，默认 0；`aside` |
| `metric_circles` | 大小圆指标 | `metrics` 恰好 2 项、`source` | `image` 0–1 张、`copy`；圆面积不编码数值比例 |
| `chart_focus` | 左侧判断、右侧独立图表 | `copy`、`chart` | `stat: {value, label}`、`conclusion` |
| `photo_banner` | 大标题与横幅图片 | `image` | `copy / eyebrow`，`tags` 2–6 个字符串 |
| `photo_divider` | 满幅图片与章节短句 | `image` | `copy / eyebrow`；文字对比与图像遮罩由风格定义 |
| `side_index` | 侧向标题与目录 | `items` 2–12 项，每项 `title` | 每项 `label`，省略自动编号；`image` 0–1 张、`eyebrow` |
| `editorial_story` | 正文叙事与右侧竖图 | `image`、`items` 1–3 项，每项 `title / text` | `eyebrow` |
| `step_sidebar` | 左侧说明、右侧竖排步骤 | `copy`、`steps` 2–4 步 | `image` 0–1 张、`note` |

补充字段：

- `steps[]` 为 `{title, text, period?}`。折返时间线会安排第二行的视觉方向，但 DOM、编号和输入顺序始终保持先后关系，不让 Agent 反向重排原数据。
- `checks[]` 为 `{label, checked}`，`checked` 必须是布尔值。使用文字标记和可见符号表达状态，不只靠颜色区分。
- `metrics[]` 通常为 `{label, value?, text?}`。指标卡至少提供 `value / text / progress` 之一；只有指标卡支持下文的 `progress`，圆形指标必须提供 `value`。`source` 必填，演示数字须明确标注示例性质。
- `chart` 为 `{title, chart_type, categories, series, unit, source}`；`series[]` 为 `{name, values}`。图表使用共用 [图表契约](charts.md)，数值、单位与来源都保留在 HTML 中，可编辑并随保存持久化。
- 没有强制图片的布局可完全无图；不要为了通过旧模板检查而补无关图片。有多图时每张承担不同的信息，不在同一页复制同一文件凑数量。

## 文字海报与编辑分栏

以下两种共享布局连同前述十六种及后文的中心关系、横向步骤，合计二十种。它们使用相同的通用字段和资源处理，不绑定原色建筑或其他风格；`speech / reading` 均可选。标题由主体布局呈现，不在页头重复输出。`surface` 只能使用当前风格清单声明的名称，颜色与字阶仍由风格决定。

### type_poster：纯文字海报与章节号

此布局完全无图，页级 `image / images` 不可用。必须保留非空 `title`，可选通用 `subtitle` 等字段。

| 字段 | 类型与规则 |
|---|---|
| `variant` | `cover / chapter / statement`，默认 `cover` |
| `placement` | `bottom-left / center / bottom-right`；cover 默认 `bottom-left`，statement 默认 `center`；chapter 使用固定编号构图，不接受此字段 |
| `number` | 非空字符串；`chapter` 必填，`cover` 可选，statement 不接受。使用字符串保留 `01` 等格式，数字本身可编辑 |
| `show_title` | 布尔值，默认 `true`；只有 `chapter` 可为 `false`。展示时隐藏标题组（含副标题），语义内容仍保留，编辑态显示并可编辑；cover 与 statement 不能隐藏标题 |
| `eyebrow` | 可选非空字符串，作为独立可编辑眉题 |
| `copy / bullets` | 仅 statement 可用；copy 为非空字符串，bullets 为 1–8 个非空字符串；均可省略，保留纯文字短句页 |

纯文字封面使用大标题和留白；章节页可由当前风格提供单色表面与巨大数字；statement 用于短主张或带说明、要点的文字页。不要为仿照参考稿省略必需标题，或把数字烘焙为图片。新增变体与字段复用现有布局和 profile，不增加共享构图或选版策略数量。

### editorial_columns：自由宽度编辑分栏

页级必填 `columns`，为 **2–6 个栏目对象**；可选 `title_column` 为从 0 开始的有效栏索引，默认 0，标题和副标题在该栏中呈现。页级 `show_title` 为布尔值、默认 true；false 仅隐藏展示态的标题与副标题，必需 title 仍保留语义，编辑态显现并可编辑。图片全部嵌套在栏目中，不在页级写 `image / images`。

所有栏目共有：`type` 必填；`weight` 为 0.5–4 的有限数字、默认 1，用作相对栏宽；`align` 为 `start / end`、默认 `start`，决定栏内容的起始或末端对齐。数组顺序就是内容和阅读顺序，不按视觉错位重排原文。

| 栏目 `type` | 必需字段 | 可选字段与容量 |
|---|---|---|
| `text` | 正文栏使用 `paragraphs`，1–6 个非空字符串 | `heading` 非空字符串；已有 heading，或本栏是 title_column 且 show_title 为 true 时可省略 paragraphs。空数组不代表省略，仍会拒绝 |
| `image` | `image`，单个图片对象 | 图片对象可用下述 `frame` |
| `gallery` | `images`，2–8 个独立图片对象 | `grid_columns: 1 / 2`，默认 2；八图可形成两列四行。`row_weights` 仅用于 grid_columns 为 1，数组长度须与 images 相同，每项为 0.5–4 的有限数字，按图片顺序分配相对行高；省略时等高 |
| `people` | `items`，1–4 个成员对象，每项必须有 `image / name / role` | 姓名与角色为非空字符串并保持可编辑；不以说明段落替代独立身份字段 |
| `groups` | `items`，2–6 个对象，每项必须有非空 `title` | 每项可选非空 `text` 与有效 `icon` 名称，图标来自 assets/icons.json。`group_columns: 1 / 2`，默认 1；四组设为 2 列即可形成 2 × 2 文字区。条目为无序分组，不带步骤号或箭头 |
| `chart` | `chart`，完整 `{title, chart_type, categories, series, unit, source}` 图表对象 | 非空 `copy` 解释文字；图表在上，标题与解释在下，来源另行保留。沿用 [图表契约](charts.md)，不接受任意 ECharts 配置 |

图片对象沿用 `src / alt` 必填及 `caption / ratio / brief / ui_text / zoom / offset_x / offset_y / edge_fade / background_mode` 等共同字段。此布局的嵌套图片还可写 `frame: "none" / "monitor"`，默认 `none`。`monitor` 使用 CSS 绘制简化显示器框，屏幕图像仍是独立图片；不生成真实产品界面，不把框内照片宣称为可编辑模型。比例沿用受支持的 `ratio`，monitor 未指定时按 16:9 处理。

一页可以完全无图；有图时所有栏目合计最多 48 张，仍受每种栏目的数量上限约束。嵌套图片进入共同的路径、缺图、重复资源和离线内嵌处理，正式构建不能把尚未提供的图片视为已完成。没有列出的栏目或图片字段会被拒绝。

标题独占一栏时可写 `{"type":"text"}`，但该栏必须承载当前显示的页标题；隐藏页标题或把标题移到其他栏后，该栏需要自己的 heading 或正文。`groups` 可用带图标的标题条目表达能力或联系项，也可加 text 说明，不必填入占位正文。

各 chart 栏的图表数据、标题、解释和来源保持可编辑；嵌套图表进入共同脚本加载、功能计数、HTML 保存和原生 PPTX 图表导出。`visual.requirements` 中 charts 按图表栏数计，icons 按 groups 中实际提供的图标计。

### 文字海报与编辑分栏选版策略

| `profile` | 实际 `layout` | `layout_intent.item_count` |
|---|---|---|
| `shared.type_poster` | `type_poster` | 单主题，固定 1 |
| `shared.editorial_columns` | `editorial_columns` | 全部栏目数，2–6 |
| `shared.editorial_people` | `editorial_columns` | 所有 people 栏的成员总数，1–24；不是栏目数 |
| `shared.editorial_gallery` | `editorial_columns` | 计所有 image 栏与 gallery 栏的图片总数，2–48；不计 people 栏头像 |
| `shared.editorial_charts` | `editorial_columns` | 计真实 chart 栏数，2–6；每栏均须有完整图表数据，不以 categories 或全部栏目数代替 |

一个布局可按不同语义使用不同 profile。团队必须提供实际 people 成员，作品图集必须提供实际 image 或 gallery 栏图片，图表对比必须提供实际 chart 栏与来源，不能只用声明的项数或 chart_data_planned 绕过字段合同。联系信息沿用 shared.editorial_columns，以标题栏和无序 groups 栏组织。

## 中心关系与横向步骤

这两种布局均无图，使用通用 `title / subtitle / visual` 等字段，标题在主体中呈现。边框、圆形、字号、颜色与连接线的具体外观由所选风格定义，不绑定米白环线商务或其他风格。

| `layout / profile` | 必需字段 | 可选字段与计数 |
|---|---|---|
| `hub_spoke / shared.hub_spoke` | `center: {title, text?}`、`items` 4–8 个 `{title, text?}` | `copy` 为非空说明；按 items 分支数计，不含 center；无方向连接线表示关联，不能冒充因果或先后 |
| `step_row / shared.step_row` | `steps` 2–6 个 `{title, text, period?}` | `copy / note` 非空字符串；按 steps 数计。timeline 的 period 必须与真实阶段对应 |

中心关系图把分支数组的前半段放在上排、后半段放在下排，中心节点横跨两排；分支标题与可选正文保持原数组阅读顺序。横向步骤从左到右排列，序号与箭头由共享结构生成，不需要将月份或阶段名称画进图片。

```json
{
  "layout": "hub_spoke", "title": "用户与价值的关联",
  "center": {"title": "目标用户"},
  "items": [{"title": "需求"}, {"title": "场景"}, {"title": "体验"}, {"title": "反馈"}]
}
```

## 指标卡进度条

`metric_cards.metrics[]` 可用 `progress: {value, max}` 代替普通字符串 `value`。两个字段均为有限数值，`max > 0` 且 `0 ≤ value ≤ max`。同项不能同时设置 `progress` 和外层 `value`，避免百分比文字与条长来自不同数据。`label` 与页级 `source` 仍必填，解释写在 `text`；示例目标和示例结果须明确标注。

```json
{"label": "完成率", "progress": {"value": 77, "max": 100}, "text": "示例：已完成数 / 目标数"}
```

展示的百分比自动计算为 `value / max × 100`，最多一位小数；条形宽度与文字始终相同。编辑态展开“编辑进度数据”修改当前值和目标值；`compositions.js` 同步更新条长、百分比及辅助阅读属性。“另存 HTML”保存同一数据表，重开仍可编辑。无效值须修正后才能保存或导出；解释文字由用户按新口径自行调整。

进度条使用 HTML/CSS，不加载 ECharts；共享构建器只在实际使用 progress 时内嵌轻量脚本。导出 PPTX 时可见条形与百分比作为可编辑形状和文字，编辑用数据表不导出。若需要保留原生可编辑图表数据，应采用 [图表布局](charts.md)。进度条颜色读 `--progress-track / --progress-fill`，未声明时分别回退到 `--panel / --diagram-accent`。

## 示例与调用

[20 页共享布局示例](../assets/deck.layouts.example.json) 使用暖褐主题、五张既有原创图片及明确标注的示例数字。配图仅用于开发样例；实际项目应按主题准备相关素材。无需复制样稿的专用播放器或私有渲染器：

```sh
python3 <shared>/scripts/build_deck.py <shared>/assets/deck.layouts.example.json --out <project>/共享布局图册.html
```

把示例的 `style` 换为实际选择的风格即可复用结构；照片是否合适须由该风格的配图规范决定。由 `speech` 改为 `reading` 不会重新划分版面，需要在相同或其他共享布局中补齐读者独立理解所需的信息。

## 原型迁移记录

| 原型中的结构 | 共享位置 |
|---|---|
| 暖褐的半幅封面、通栏介绍、侧栏目录、关于、服务条带、流程、多图作品集、收束 | `editorial` 八变体 |
| 黑白横幅封面、底标题问题页、图文叙事、不等服务块、圆形指标、独立图表、摄影转场 | `photo_banner / problem_columns / editorial_story / service_cards / metric_circles / chart_focus / photo_divider` |
| 黑白及其他样稿的半图大字尾页 | `editorial.closing`、已有 `closing` 变体 |
| 墨蓝／朱红原型的封面、理念、计划 | `photo_banner / statement_tags / step_sidebar` |
| 墨蓝／朱红原型的侧向目录、双图夹文、错位双图、标签群、问题分栏 | `side_index / photo_pair / offset_pair / statement_tags / problem_columns` |
| 墨蓝／朱红原型的清单、横幅主张、图片条带、折返时间线、指标卡、半图尾页 | `checklist_photo / photo_banner / photo_strip / snake_timeline / metric_cards / editorial.closing` |
| 米白环线商务草稿的中心关系、单行阶段与比例指标 | `hub_spoke / step_row / metric_cards.progress`；其他页面复用已有布局 |

迁移的是布局能力，不会自动注册尚未批准的配色风格。历史样稿保留为来源记录，后续新稿使用共享构建器与所选风格。
