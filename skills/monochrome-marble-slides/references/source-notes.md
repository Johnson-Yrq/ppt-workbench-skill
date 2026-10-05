# 来源观察与中文转译

## 参考来源

- 用户于 2026-10-05 在 Chrome 中打开的 Canva 参考：**Black and White Simple Business Plan Presentation**。
- [本次 Canva 编辑入口](https://www.canva.com/design/DAHXG9MuIw8/pDRqfFpzqbimN32v2L3LvQ/edit?ui=eyJBIjp7fX0)。该地址用于追溯本次查看的设计，不推断原始模板作者或公开授权状态。
- 完整参考十五页；逐页截图保存在本包 `assets/reference-design/canva-01.png` 至 `canva-15.png`。截图仅用于设计观察，不作为新稿成品页或业务图片复用。
- 原作者与原字体无法从当前资料确认。Georgia、Songti SC 等为本地衬线近似选择；字号、边距与几何按可见结构转译，不宣称像素级复刻。

## 逐页提取

| 来源截图 | 可观察结构与共享映射 | 可借鉴之处与使用限制 |
|---|---|---|
| [01](../assets/reference-design/canva-01.png) | `cover`：左大标题、右侧大理石竖条 | 用大字和竖向纹理建立开场；标题与信息保持独立可编辑，不复用原整页 |
| [02](../assets/reference-design/canva-02.png) | `side_index`：十二项目录 | 清晰序号和条目节奏；实际目录须对应本稿内容，十二项是容量示例 |
| [03](../assets/reference-design/canva-03.png) | `type_poster`：左上标题、左下正文 | 以留白分开标题与叙述；不继承来源中的公司事实 |
| [04](../assets/reference-design/canva-04.png) | `editorial_columns`：左图、右标题正文 | 照片与纹理底衬形成层次；照片独立提供，纹理不烘焙进照片 |
| [05](../assets/reference-design/canva-05.png) | `editorial_columns`：左标题、右三人纵排，浅大理石 | 姓名、角色与人物照独立组织；不把原人物或生成人像视作真实成员 |
| [06](../assets/reference-design/canva-06.png) | `editorial_story`：深色底、左三项文字、右宽图与下置标题 | 用黑白反转改变页面节奏；正文数量由实际内容决定，不能靠缩字无限加项 |
| [07](../assets/reference-design/canva-07.png) | `editorial_columns`：三个图表并排，底部纹理带 | 图表、邻近标题和解释分开；来源曲线与数字仅作视觉参考，重新提供完整数据 |
| [08](../assets/reference-design/canva-08.png) | `editorial_columns`：左三个图标说明组、右大标题 | 图标帮助辨认并列信息；分组无序，不擅加流程箭头或步骤号 |
| [09](../assets/reference-design/canva-09.png) | `type_poster`：白边与内嵌黑色面板 | 明确的章节停顿和大字声明；使用 inset-dark，不把整页文字烘焙进图片 |
| [10](../assets/reference-design/canva-10.png) | `editorial_columns`：左文右图、浅大理石 | 文字与照片保持宽阔间距；图片保留自然色彩，纹理不降低正文对比 |
| [11](../assets/reference-design/canva-11.png) | `editorial_columns`：左标题、右五个图标标题，深色纹理 | 可用无正文的能力条目；title 必填，图标使用有效资源，不填无意义占位文字 |
| [12](../assets/reference-design/canva-12.png) | `editorial_columns`：左侧两图上下叠放、右文 | 两张独立照片形成叙事联系；不把多张场景拼成不可替换的单图 |
| [13](../assets/reference-design/canva-13.png) | `metric_cards`：深色页、左两个大数字、右大理石窄条 | 大数字突出结论；真实稿必须有单位、口径与来源，不沿用来源的示例指标 |
| [14](../assets/reference-design/canva-14.png) | `chart_focus`：左题文、右折线、左纹理边 | 解释与趋势相邻；只有有序时间或序列数据使用折线，不制造无依据趋势 |
| [15](../assets/reference-design/canva-15.png) | `editorial_columns`：深色联系页、左题文、右三组联系项及侧纹理 | 联系方式按独立条目编辑；不复制原地址、电话或身份，不将虚构资料投入真实联系 |

白 `#FFFFFF` 与近黑 `#0B0B0B` 构成本包基础色。天然黑白矿纹与自然彩色摄影分别承担材质和场景表达；参考没有要求把商务照片整体灰阶化。中文样稿按中文阅读习惯重写，保留结构特点而非来源文案。

## 共享实现边界

本方向维持 **20 种共享构图**，以既有布局承载十五页参考。`side_index` 扩到 2–12 项；`editorial_columns` 增加完整 chart 栏，groups 扩到 2–6 项且 text/icon 可选，并允许符合语义条件的标题独栏。增加 `shared.editorial_charts`，按实际 2–6 个图表栏计数；嵌套图表共享编辑、保存和原生导出标记。

所有扩展属于共享组件，可用于其他风格与 speech / reading。主题仅控制字体、颜色、留白、表面、纹理和照片的视觉。本方向不新增布局数量。

## 批准状态与交付位置

本包名 `monochrome-marble-slides`，style ID `monochrome-marble`，正式版本 **1.0.0**，状态 **ready**。用户于 **2026-10-05** 明确回复「采用，安装，并提交」，批准当前黑白大理石商务中文样稿方向、正式接入共享制作套件、安装到实际 Skill 目录，以及本次相关改动的版本提交。这项批准直接针对本方向，同一范围内无需重复索取，也不改变未来独立新方向的批准要求。

本方向最初以 draft / 0.1.0 制作代表样稿，获得上述确认后转为 ready / 1.0.0。历史草稿和开发记录用于追溯，不构成正常制作的待批准节点。安装与提交仍按已授权范围执行；具体安装完成状态以安装位置验证结果及主任务报告为准，本记录不代替实际执行结果。

- 中文样稿项目：源码 `examples/monochrome-marble/`，主题为虚构的「砚序咨询」2026 业务计划。
- 参考截图：本包 `assets/reference-design/` 的十五张逐页图片，见上表。
- 原创素材：本包 `assets/images/` 的九个 WebP 文件，含一张纹理、三张肖像与五张场景照；原始生成文件按出处清单保留。
- 提示词与出处：项目 `image-prompts.json` 和 `image-sources.json`，记录内置 imagegen 生成方式及本地路径。
- 结构样例：本包 `assets/deck.example.json` 与 `assets/deck.reading.example.json`，分别用于演讲与阅读用途。

人物、身份、业务计划和数字均为示意，不声称属于真实公司、团队或经营成果。默认交付可编辑离线 HTML，由用户自行导出与检查；Skill 开发验证仍由 Agent 完成，已明确要求的 PDF、PPTX 或代查不能留作可选后续。
