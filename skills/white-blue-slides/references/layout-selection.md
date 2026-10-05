# 根据内容自主选版

此流程属于共享制作套件。沿用已确认的风格与演讲／阅读用途，常规逐页选版自行完成，不增加批准节点，也不替代已有的设计方向、发布或批次批准。用途决定内容密度与讲稿分工，不决定某个布局是否可用，也不强制图文等分、图片比例或统一字阶。

## 来源库与可执行策略

[layout-library.json](layout-library.json) 完整保留从 Canva 布局面板提取的 **100 条来源、19 个类别**。来源结构来自缩略图概括，不是精确坐标，示例人物、业务文案、数字和照片均不是用户事实。

当前有 **49 个可执行 profile**：原有 18 个内容选版策略、[原 16 种共享构图](shared-layouts.md#新增十六种构图)、8 个 `editorial` 变体，以及新增 `type_poster / editorial_columns` 对应的 [5 个选版策略](shared-layouts.md#文字海报与编辑分栏选版策略)，以及 `hub_spoke / step_row` 对应的 [2 个选版策略](shared-layouts.md#中心关系与横向步骤)。原 100 条来源仍有 81 条近似适配、19 条为 `reference_only`；本次独立模板放在 `additional_sources`，不覆盖原始记录、不改编号或虚增原库数量。来源编号不是 `layout`，100 条来源也不等于 100 个已经实现的模板。

- `adapted` 表示存在真实渲染路径，仍须满足该候选的关系、数量、字段、素材与数据条件；不是原图的像素复刻。
- `reference_only` 表示该来源尚未登记完整的可执行适配路径，不能直接选为成品布局。未支持的散点、漏斗、树图、复杂看板等不能换成另一种图后宣称已实现；新增共享能力也不自动重标旧来源。
- 原设备样机来源仍按一张已提供的完整设备与屏幕素材适配，旁侧文字可编辑。本次 `editorial_columns` 新增嵌套图片的 `frame: "monitor"`，由 CSS 绘制简化显示器框，属于独立新能力；不擅改旧来源映射，也不生成真实产品界面。
- 所有 profile 均可用于 `speech` 或 `reading`。`styles: ["*"]` 表示共享结构兼容动态发现的有效 `ready` 风格，外观仍由该风格的页头、字体、字阶、颜色和配图规范决定。
- `reading.half_lr / half_tb / half_diagonal / quarter` 是主动选择的四种旧复合构图，保留兼容，不是阅读用途的默认几何规则。

## 先理解关系

写布局字段前，先确定本页结论、真实内容关系和主体数量。同样三项内容，步骤用 `sequence`，三对象的多维对照用 `comparison`，三位成员用 `team`；不能按条目数统一套卡片。没有合格团队结构时，不把人物关系静默降为普通要点。

可选关系：`cover / closing / explanation / parallel / agenda / sequence / timeline / comparison / hierarchy / network / causality / formula / table / data / controls / mixed / team / testimonials / statistics / gallery / contact / quote`。

- `sequence` 强调先后；`timeline` 还需要与事件对应的真实时间；`causality` 需要可支持的因果方向。
- `comparison` 比较对象的共同维度，须声明维度数；`parallel` 是互相独立的内容。
- `hierarchy` 是层级或架构，需要场景空间对位时写 `spatial: true`；`controls` 要有真实控制分组；`formula` 只用于确有加和或乘积关系的因子。
- `data` 必须有可画的真实数量、单位和来源，目前图表支持 `bar / line / donut / pie`。`statistics` 同样不能补造数字或口径。
- `mixed` 用于真实的多关系模块组合，须提供 `block_types` 和内容；不能用它规避语义约束。

## 规划与筛选

在项目内建立轻量的 `layout-plan.json`，保留大纲及事实来源；每页给唯一 id、标题、实际待排文字和 `layout_intent`。这是供选择使用的过程文件，不是成品，也不是额外验收阶段。

```json
{
  "style": "scene-white",
  "presentation_mode": "speech",
  "slides": [{
    "id": "p02",
    "title": "从接收到完成的三个步骤",
    "content": ["接收：登记提交材料。", "核对：检查材料完整性。", "完成：记录处理结果。"],
    "layout_intent": {
      "relation": "sequence",
      "item_count": 3,
      "media": {"count": 1, "status": "planned"}
    }
  }]
}
```

`style` 和 `presentation_mode` 使用本项目已确认的值，不能从示例推断。

| 字段 | 含义 |
|---|---|
| `relation` | 模型判断的内容关系；脚本不按关键词代替语义分析 |
| `item_count` | 候选实际计数的主体数：步骤、条目、指标、标签、段落、图片或图表类别；具体见 profile 的 `count_field`。旧表格按数据行数，关系链按最长链节点数 |
| `dimension_count` | comparison 必填；多维矩阵还需一列对象名称 |
| `column_count` | table 的列数，包含行名称列；成稿可从 columns 读取 |
| `periods` | timeline 的真实时间数组，与事件对应；成稿写入 items[] 或 steps[] 的 period |
| `control_group_count` | 带控制说明的流程分组数；没有真实控制内容时省略 |
| `chain_count` | 关系链数量，默认 1 |
| `spatial` | 是否需要场景空间对位，可省略 |
| `media` | 规划图片数量及 provided/planned/unavailable 状态；成稿以实际图片字段为准，包含卡片内嵌图片。planned 不等于图片已经存在 |
| `block_types` | 使用旧 reading 复合结构时的模块列表；mixed 必填。它不适用于所有阅读用途的页面 |
| `exclude_profiles` | 本轮因实际问题排除的 profile.id；内容改变后可重新评估 |

单主题结构使用 `count_field: "single"`；其他结构按 `items / images / paragraphs / groups / steps / metrics / tags / columns / chart.categories` 的实际长度计数。`shared.editorial_people` 使用 `columns.people`，计所有 people 栏的实际成员总数；`shared.editorial_gallery` 使用 `columns.photos`，计所有 image 栏的单图与 gallery 栏图片总数，不计 people 栏头像。旧计数器 `columns.gallery` 保留兼容，仅计 gallery 栏图片。普通 `shared.editorial_columns` 按 2–6 个栏目计，people 按 1–24 个成员计，gallery 按 2–48 张图片计，图表对比使用 `shared.editorial_charts`，按 `columns.charts` 计 2–6 个真实图表栏，每栏必须有完整图表数据、单位与来源。这些计数不能混用。`shared.hub_spoke` 按 4–8 个 items 分支计，不把 center 加进主体数；`shared.step_row` 按 2–6 个 steps 计。不要为引用一个来源编号而改写来源原有项数，或虚增页面内容。

`type_poster` 的 statement、placement 与文字字段，以及 `editorial_columns` 的 show_title、单列 gallery 的 row_weights，均扩展现有共享结构；使用原 profile 并按 [字段合同](shared-layouts.md#文字海报与编辑分栏) 填值，不新增 profile，也不改变原 100 条来源记录。

规划图表放在页的 `chart` 对象，结构与 [图表契约](charts.md) 相同；旧复合布局的多图表用完整 `blocks`。每个图表都要有实际数据，不能只标记“有数据”。

```sh
# 按需读取能力与来源，不必把整个来源库装入上下文
python3 <shared>/scripts/select_layout.py --list
python3 <shared>/scripts/select_layout.py --catalog --relation comparison

# 输出候选、理由、容量估算和排除原因，不改写输入
python3 <shared>/scripts/select_layout.py <project>/layout-plan.json --out <project>/layout-report.json
```

筛选顺序是：实现能力、内容关系与素材数据条件 → 实际数量与文字密度 → 相近候选的页面节奏。重复版式的轻微扣分不能救活语义不匹配的布局。CJK 约按 1、ASCII 约按 0.55 单位估算文字，只作保守初筛；不保证无溢出，不据此强行改字号或开启自动成稿检查。

## 落到可渲染的 deck

从合格候选中选择最符合内容与素材形状的一项。首选通常可直接采用；不为多样性牺牲表达。

1. 使用候选的 `layout` 和 `settings`，按 [数据契约](deck-format.md) 或 [共享构图字段](shared-layouts.md) 完整组织内容；不能只换 layout 名。`editorial` 候选须应用 `editorial_variant`。`single_block_span: 2` 写入唯一的 `blocks[0].span`，不是页级字段。
2. 选版记录留在 `layout-report.json`，不写进 deck；需要日后按反馈重选的页可保留 `layout_intent`（构建时不读取）。大纲明确的视觉要求写入 `visual.requirements`。
3. 规划 `content` 不会渲染，转入真实字段后移除，原文与出处保留在大纲或 notes。
4. 准备必需图片与数据，直接构建独立 HTML；修复构建器报告的结构错误和缺失资源。旧稿里的 `layout_selection` 等记录会被忽略，无需迁移。

特殊组织要求：`journey.sequence` 使用 `connected: true`；`journey.compare` 使用 `connected: false`，仅作一维短比较；时间线保留每项真实 period；`flow.controls` 同时需要 steps 与真实控制 groups；`architecture.labels` 的主体数按 `kind=layer` 计；因果链须写 `directional: true`。允许零图的共享构图可完全无图；旧封面、尾页是否允许无图还由当前风格声明决定。

## 无合格候选与已报告问题

没有候选时，报告为 `needs_revision`。继续完成其他页面，本页按实际缺口补素材或数据、重组内容，或在页数约束内拆页；不能删掉必要事实、缩小字号或改变已确认风格来通过。只有无法同时满足的核心约束才需要用户决定。

默认由用户自行导出和检查成稿，不要求 Agent 运行 `--check-plan`、批量截图、逐页审查或导出回归。用户明确委托检查、提供问题反馈，或维护共享工具时，才在对应范围内使用诊断和重选能力：

```sh
python3 <shared>/scripts/select_layout.py <project>/deck.json --feedback <project>/qa/report.json --out <project>/layout-retry.json
```

反馈按页 id 匹配，按页面实际的 `layout` 与设置认出当前 profile，只排除出现容量或布局问题的那一个；重选需要该页的 `layout_intent`。缺图或主题错误不能靠换版掩盖。脚本不自动删字、改数据或改写 deck。修复已报告问题后停止，不把内部工作转为新的用户批准节点，也不反复启动全稿检查。

## 维护布局库

新增通用结构先实现共享渲染器、字段与数量契约，并完成与代码改动相称的开发验证，再登记 `ready`；不能用 `custom_css` 绕过主题保护。新风格使用自己的页头与视觉配置，正常接入共享结构无需增加风格白名单。扩展来源映射时，保留原始 id、名称、结构、容量与 limitations；只为真实可表达的关系和数量新增路径，仍不支持的结构继续保留为参考。
