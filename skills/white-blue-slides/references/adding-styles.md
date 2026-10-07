# 新增独立风格包

用于用户持续添加视觉方向时。风格包维护自己的视觉资产；数据结构、主体版式（包括 editorial）、演讲／阅读密度、图表、编辑、保存、离线与打印共用 `white-blue-slides` 制作套件。下文的接入验证用于工具开发；普通成稿仍默认由用户导出与检查。

## 目录与自动发现

在同一 skills 根目录新增文件夹，例如 `new-style-slides/`，不要把新方向写进已有风格的提示词或 CSS：

```text
new-style-slides/
├── SKILL.md                         # 独立入口、所选 style id、共享脚本路径
├── agents/openai.yaml               # 显示名称与包含 $技能名 的默认提示
├── assets/
│   ├── style.json                   # 自动发现与资源清单
│   ├── theme.css                    # 整稿视觉主题
│   ├── header.html                  # 独立风格自己的页头模板
│   ├── image-style.txt              # 配图材质、尺度、镜头与禁止项
│   ├── deck.example.json            # 已接入风格的演讲型结构示例
│   ├── deck.reading.example.json    # 已接入风格的阅读型结构示例
│   └── reference-design/            # 目标参考与已确认样例（有则保留）
└── references/
    ├── design-system.md            # 页面、字阶、强调与配图的设计规则
    ├── image-workflow.md           # 本风格提示词、复用图片与生图流程
    └── quality-check.md            # 本风格视觉检查 + 共享功能检查
```

构建器只发现同级 `*/assets/style.json` 中声明 `schema: "html-slide-style/v1"` 的包；无需改 Python 注册表、工作台菜单或已有风格。文件夹名用 Skill 名；`id` 是整稿选择值，两者可不同但必须稳定。`id` 在同级包中唯一，只用小写字母、数字和短横线，最长 64 字符。重名时拒绝选择，不按目录顺序覆盖。

文件夹按视觉特点使用直观的英文名称，格式为 `<visual-style>-slides`，例如 `white-blue-slides`、`navy-glass-slides`、`realistic-miniature-slides`。目录名、SKILL frontmatter 的 `name` 与默认调用提示保持一致；中文风格名留在显示名称中。仅调整目录名称时保留已发布的 `style` ID，更新同级引用与安装位置，并将旧包备份到 Skill 扫描目录之外，避免新旧包重复注册。

## 最小清单示例

下面是新包的结构示例，名称、描述和视觉参数须按新方向填写。现有风格包的清单也可作为字段参考，但不要继承不属于新方向的材质、配色或提示词禁令。

```json
{
  "schema": "html-slide-style/v1",
  "id": "new-style",
  "name": "新风格名称",
  "description": "用一句话说明视觉特点与适用内容。",
  "status": "draft",
  "css": "theme.css",
  "header_system": "style",
  "header_template": "header.html",
  "heading_icons": "optional",
  "cover_copy_policy": "style",
  "image_prompt": "image-style.txt",
  "ui_text_modes": ["none"],
  "default_ui_text": "none",
  "ui_text_prompts": {
    "none": "No text in the illustration. Keep labels and factual data as editable page content."
  },
  "layout_hints": {},
  "cover_labels_expected": false
}
```

- `status`：`draft` 供开发时检查，常规清单不列出且构建器拒绝使用；`ready` 表示可用于制作。现有已确认方向不用重新确认。新方向先生成代表性图片／页面样例供用户确认，再在项目源码中设为 ready，完成下面的构建与视觉验证后安装。`--draft` 是演示稿缺图预排，与风格包状态无关，不能绕过风格选择。
- `css / image_prompt / image_reference` 路径相对本包 `assets/`，不接受绝对路径或目录外资源。`image_prompt` 必填；`image_reference` 可选，填写后提示词导出器会随供图清单复制它。`css` 可为 null，但会沿用基础主题；独立新视觉应提供自己的主题。
- `image_background` 可选，只接受 `paper / scene`。默认 `paper` 沿用既有模型风格的提示词策略，要求图片使用本风格纸色的纯色背景；`scene` 用于真实摄影，保留现场的空间、材质与自然光背景，不要求背景匹配页面纸色。暖褐极简编辑式指定 `scene`。该字段只影响配图提示词，不改动照片像素，不自动抠图、换背景或映射纸色。
- `ui_text_modes / default_ui_text / ui_text_prompts` 定义配图内的文字策略，默认值须列于可用策略且每种策略有提示。页面标题、真实数据和业务说明始终由可编辑内容承载；图片上的示意界面不作为事实来源。
- `layout_hints` 可选：`above` 补充上图下文构图，`architecture` 补充分层结构要求。未提供时不注入其他风格的构图提示。
- `cover_labels_expected` 可选，默认 true：封面右图是否应带层级标注；为 true 而缺少时 `--check-plan` 给出警告。
- `surfaces` 可选，默认 `["light"]`，必须包含 `light` 且名称唯一。各名称最多 32 字符，仅含小写字母、数字和分隔用的短横线；不接受开头、结尾或连续短横线。除 `dark` 外可声明 `yellow / mustard / blue / red / lime` 等本包需要的名称，不是共享预设或任意 CSS。单页 `surface` 只能使用当前风格已声明的值，构建器输出对应 `data-surface`；同一稿仍只有一个 style。
- 主题须为每个表面提供完整、协调的颜色令牌，例如 `.slide[data-surface="mustard"]`；包含 `--diagram-panel` 等图表与阅读组件颜色，并把基础组件的固定浅底颜色改为读取令牌。`:root` 里用 `var()` 引用的令牌在根上已求值，不会随页面切换。新表面可以改变背景与对比，不改变内容关系、演讲／阅读用途或布局资格。
- `image_free_layouts` 可选，默认空；可列 `cover`、`closing`、`table`，这些页可以不写 `image`。只适合无图也完整的页面；table 可用于全宽数据表，由主题提供无图几何。未显式声明的风格保留原配图要求。无图页带 `no-image` 类；封面与尾页还带 `--title-chars`（最长标题行的字数，全角计 1、其他约 0.5），主题可据此让大字标题按长度适配，例如 `font-size:min(156px,calc(1120px / var(--title-chars)))`。
- 旧 `editorial_variants` 字段仅保留格式校验兼容，不再限制布局选择。editorial 的八种变体属于共享层，所有风格都可使用，数据字段见 [editorial 契约](deck-format.md#editorial编辑式图文页面)。其中需要配图的字段是布局结构，不规定照片或模型材质；具体外观由风格决定。

## 页头与视觉策略

- `header_system` 可选 `preset-six / style`，默认 `style`。只有最早的素白蓝调、海蓝玻璃与写实微缩显式采用 `preset-six`，在各自 Skill 中说明六种页头。新风格默认独立设计页头，不继承六种预设。
- `header_template` 是本包 `assets/` 内的 HTML 文件相对路径，不能在 deck 或 slide 覆写。新独立风格应提供它；旧第三方包未提供时使用共享中性页头后备结构，不套用六种预设。采用 `style` 的项目不填写根或单页 `header` 字段。
- `heading_icons` 可选 `required / optional`，默认 `optional`。最早三个风格保留 required；新风格按内容选图标，不把“有标题就必须有图标”作为共享规则。用户显式的 `visual.requirements` 无论哪个风格都需遵守。
- `cover_copy_policy` 可选 `legacy / style`，默认 `style`。最早三个风格保留 legacy 的封面单行预算；新风格自行规划封面和尾页标题行数、字阶、留白与布局，不套用旧封面字数限制。

页头模板仅有一个最外层 `<header>`，使用受控结构标签与 class／aria 等属性。可用插槽只有 `{{chapter}}`、`{{title}}`、`{{subtitle}}`、`{{page}}`、`{{company}}`、`{{year}}` 六个；插槽由构建器生成已转义的可编辑节点，空字段不生成空节点，不拼入原始用户 HTML。例如：

```html
<header class="style-header">
  <div class="style-heading">{{chapter}}{{title}}{{subtitle}}</div>
  <div class="style-meta">{{company}}{{year}}{{page}}</div>
</header>
```

模板定义结构，主题 CSS 定义标题位置、字阶、间距、页码和配色；必须与所用主体布局的可用空间协调。封面、editorial 及在主体中安排标题的共享布局不在页头重复标题；原 closing 仍使用页头中的标题位置。新增风格的页头自主设计不需要把项目切换到 `--allow-restyle`。

## 主题与共享边界

主题加载顺序为基础组件 → 当前所选共享布局的几何 → 所选风格 CSS → 用户已要求的项目颜色覆盖。`reading` 的几何只用于选择了该 layout 的页面，不随阅读型用途全局套用。新主题完整声明 `--paper / --blue / --ink / --muted / --line / --panel / --radius`，可用 `--diagram-accent` 指定流程和图表辅助色；颜色令牌使用六位十六进制。独立设计封面、页头、页码、图标、面板、表格、流程、图表与尾页的视觉，复用共享主体布局与组件；不继承其他风格的字号、边距或固定图文比例。不同风格 CSS 不会同时加载。

从英文或拉丁字体参考转译字阶时，按中文重新定字号：中文字面撑满方格，同样像素的中文标题视觉上约为英文的 1.5–2 倍。以常规字重为主，内容标题宜在 68–84px 一档、正文 24–26px，并以中文样稿实际截图确认简约感。标题缩小后单行可能伸到页码区，页头与在主体中放标题的布局都要为页码预留右侧空间。风格包宜附一份版式经验（本主题精调过哪些共享结构、哪些结构在本风格中易乱、每页字数预算），示例见 [黑白大理石版式选用](../../monochrome-marble-slides/references/layout-guide.md)。

图表基础三色依次读取 `--diagram-accent / --diagram-strong / --chart-tertiary`，网格读取 `--chart-grid`。可选 `--chart-quaternary / --chart-quinary` 在原三色后补充第 4、5 色；不声明便保留原三色，浏览器与原生 PPTX 导出一致。指标进度条可独立声明 `--progress-track / --progress-fill`。新风格按自己的配色提供令牌，既有主题不因此改变。

`SKILL.md` 写清本包对应的 `style`，引用共享的 [类型规则](presentation-modes.md)、[数据结构](deck-format.md)、[图表契约](charts.md) 和运行命令；不读取原风格的 SKILL 正文作为制作流程。使用动态工作台只确认缺少的选择，已确认的模式不再询问。每个包支持 speech 与 reading，差异放在信息组织而非固定排版或另建重复风格包。

若新风格需要超出现有布局契约的行为，先明确实际需要再扩展共享组件；不要用一个改名主题冒充尚不支持的版式。主题与 JS 保持本地内嵌，不引入 CDN、远程字体或外部图片。模型类配图需融入页面时使用本风格 `--paper`，校准时向 `match_paper.py` 显式传 `--paper '#RRGGBB'`；真实摄影保留自身背景，不应用模型纸色映射。

## 共享布局扩展

新增主体布局进入共享构建器、数据合同和组件层，所有风格都可选择。先判断是否已有等价结构；确需新增时定义语义字段、可编辑节点、默认几何与资源处理，随后补充共享文档和适用测试。不添加风格 ID 白名单，不把一套布局长期绑定某个 Skill 的专用渲染器。

布局描述内容关系与空间组织；照片、模型、字体、颜色、页头和具体字阶由风格决定。新布局不为套用某个风格强制摄影或装饰图；有结构性图片字段的版式按其合同使用，其余版式按内容选择图或文字。主题仅覆盖外观并适配必要空间，不复制共享业务代码。

既有项目的 `--builder` 自定义方式继续兼容，可用于探索结构；确定可复用的新增布局后接入共享层，不以每稿最多新增几种作为限制。开发时验证不同风格和两种用途下的代表内容，保持可编辑、离线、保存与导出能力；普通成稿仍不自动自检或导出。

## 接入验证与安装

1. 用 `python3 <shared>/scripts/style_packs.py --list --include-drafts` 检查清单、资源与重复 ID，修复相关错误。
2. 新方向样例已确认后设为 ready。分别以 speech 和 reading 编制代表性 `deck.json`，先 `build_deck.py ... --check-plan`，再 `prepare_images.py ...` 核对独立提示词、参考与逐图文字策略。
3. 复用或生成真实配图，构建并逐页查看；覆盖封面、信息页、尾页及本次受影响的共享布局；两种用途都验证信息密度，若改动 reading 布局才覆盖其分区组合，有图表时检查编辑、保存重开与离线。计划、成稿与供图清单必须记录新 ID；现有风格不能随之改变。
4. 运行共享 `scripts/selftest.py`。它会验证动态扩展风格在两种类型中可构建、已安装主题可使用全部共享版式、风格资源独立及缺失／重名／草稿等错误处理；实际新主题的视觉仍需第 3 步检查。
5. 将新包同级安装到实际 skills 目录；共享套件有改动时一并更新。运行安装位置的 `style_packs.py --list`，新包应出现在工作台清单。更新现有安装前备份相关目录，不覆盖无关技能。

暖褐极简编辑式的中文样稿已于 2026-10-04 获用户批准，并获正式接入与安装授权。该方向无需再次批准；其来源与批准记录保存在 `warm-minimal-editorial-slides/assets/reference-design/source-notes.md`。后续新设计方向仍按自己的批准状态接入。

原色建筑编辑式的中文样稿已于 2026-10-05 获用户明确采用，并获正式接入与安装授权；本包以 ready / 1.0.0 供正常制作。同一方向无需再次批准，详见 [来源与批准记录](../../primary-architecture-slides/assets/reference-design/source-notes.md#批准状态与交付位置)。这项记录不改变其他新方向的批准要求。

留白衬线影集的中文样稿已于 2026-10-05 获用户明确回复「采用，并安装」，批准当前方向、正式接入与安装；本包以 ready / 1.0.0 供正常制作。同一方向无需再次批准，详见 [来源与批准记录](../../airy-portfolio-slides/assets/reference-design/source-notes.md#批准状态与交付位置)。这项记录不改变其他新方向的批准要求。

米白环线商务 `beige-ring-business-slides` 的中文样稿已于 2026-10-05 获用户明确回复「采用」；该答复针对「采用这版，并正式安装吗？」的问句，批准当前方向、正式接入与安装。本包以 ready / 1.0.0 供正常制作，同一方向无需再次批准；详见 [来源与批准记录](../../beige-ring-business-slides/assets/reference-design/source-notes.md#批准状态与交付位置)。安装完成状态仍以安装位置的验证结果为准。这项记录不改变未来独立新方向的批准要求；中心关系图、横向步骤、可编辑比例指标及实心饼图继续作为所有风格可用的共享能力。

黑白大理石商务 `monochrome-marble-slides` 的十五页中文样稿已于 2026-10-05 获用户明确回复「采用，安装，并提交」，批准当前方向、正式接入、安装与 Git 提交。本包以 ready / 1.0.0 供正常制作，同一方向无需再次批准；详见 [来源与批准记录](../../monochrome-marble-slides/references/source-notes.md#批准状态与交付位置)。安装完成状态以安装位置的验证结果为准。十二项目录、标题独栏、无序图标分组与嵌套图表继续作为所有风格可用的共享能力；此批准不适用于未来新方向。

新增视觉风格维护自己的主题、页头模板与配图资产；新增主体布局维护共享层。现有项目按其 `style` 继续制作，新项目在工作台选择可用风格与类型。
