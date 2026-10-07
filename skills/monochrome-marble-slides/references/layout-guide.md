# 版式选用与内容预算

本页记录真实中文演讲稿（2026-10 医疗多智能体项目）在本风格中反复出现的排版问题与修法。写 `deck.json` 前先读，按内容关系从下表选结构，再按预算写字。共享合同仍以 [共享布局](../../white-blue-slides/references/shared-layouts.md) 为准。

## 优先使用本主题精调过的结构

本主题为下列结构单独设计了字阶、错位纹理、页码位置和留白，成稿最稳：

| 内容关系 | 首选结构 | 写法要点 |
|---|---|---|
| 封面 | `cover` | 合作方、单位写进 `subtitle` 第二行；不用 `credits`，它会与页脚相撞 |
| 介绍 / 解释 + 一张照片 | `editorial_columns` image / text 或 text / image | 图片 3:4 竖幅最稳 |
| 合作方 / 能力 + 照片 | `editorial_columns` image / groups，`title_column: 1` | 标题与条目在右栏，自动对着照片垂直居中 |
| 并列能力、架构、边界 | `editorial_columns` text / groups | groups 单列（不写 `group_columns`），3–5 项带图标；标题栏与条目栏都居中 |
| 角色分工、联系项 | `editorial_columns` groups / text，`title_column: 1` | 左侧条目可用 `group_columns: 2` 排 2×2，右侧短标题 |
| 前后对比、两张场景照 | `editorial_columns` gallery / text，`title_column: 1` | `grid_columns: 1` 上下叠放，图片 `ratio: "16:9"` |
| 问题 / 痛点 + 一张场景照 | `editorial_story`（常配 `dark`） | 2–3 项；页标题短，“问题一”等序号放 `eyebrow` |
| 规模指标 | `metric_cards`（`dark` + 大理石图） | 2 项竖排大数字；3–4 项自动排成带细线的 2×2 网格 |
| 判断 + 一张图表 | `chart_focus` | 需有真实数据与来源 |
| 章节声明 | `type_poster` statement（可配 `inset-dark`） | 一句判断加 2–3 行说明 |
| 目录 | `side_index`（`dark`） | 序号与标题保持独立文本 |
| 有序步骤 | `step_row` | 4–5 步；每步 `text` 一行；补充句写进 `note`，不写 `copy` |
| 中心关系 | `hub_spoke` | 标题两行以内；不写 `copy`，说明放讲稿 |
| 流程 + 一张图 | `flow` | `groups` 必填 2–3 组，每组一行 `rows` |

在本主题里容易显乱、应先换成上表结构的：

| 结构 | 现象 | 替代 |
|---|---|---|
| `photo_pair` | 小图、正文、大图三处分散 | gallery / text 编辑分栏 |
| `problem_columns` | 条目在顶、标题沉底、图片偏小，重心不稳 | `editorial_story` |
| `table`（两列短表） | 只占半幅，右侧大片空白 | groups / text 编辑分栏 |
| `snake_timeline` | 标题与页码、末行与页脚相撞 | `step_row`（≤6 步） |
| `editorial_columns` 三栏 image / text / groups | 图片压住条目 | 拆成两栏，或把说明并入 `subtitle` |

## 演讲型内容预算

- 每页一个判断：标题、一句说明、最多三项要点（架构类可到四项）；留白不少于版面一半。
- 条目 `title` 4–8 字，`text` 一行（中文约 10–18 字）；超出的细节逐页写进 `notes`，不删事实口径。
- 标题两行以内，每行约 5–12 字，在语义处手动 `\n` 断行；页头标题右侧为页码与短线预留了位置，过长也会被自动折行，但手动断行更自然。
- `editorial_story` 标题位于右下、窄于半幅：每行不超过约 8 字，避免压到照片。
- 标题独栏较窄时（左右分栏的标题栏），标题每行不超过约 6 字，否则逐字折行。
- 指标值保持短写法（如“约 3,000 份”），口径写进 `text` 或页级 `source`。

## 自查要点

用户要求代查或开发本主题时，截图看这几处即可：标题是否压到页码短线、条目或图片是否互相遮挡、内容是否全挤在上半部而下半页空白、页脚是否被正文或图片压住、四项指标是否溢出页底。
