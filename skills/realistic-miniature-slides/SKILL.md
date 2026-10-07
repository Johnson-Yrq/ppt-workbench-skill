---
name: realistic-miniature-slides
description: 在用户选择写实微缩风格或续做该风格项目时制作可编辑离线 HTML 演示稿，采用暖灰、石墨、灰蓝与鼠尾草绿，主动生成无文字的 35–45° 写实微缩配图。交付前做基本排版 QA，默认由用户自行导出；未选风格时经 ppt-workbench 接入。
metadata:
  version: "1.3.0"
---

# 写实微缩演示稿

将大纲制作成可编辑、可独立离线打开的单文件 HTML。整稿使用暖灰纸底、石墨文字、灰蓝重点、鼠尾草绿辅助色与少量赭黄；配图以真实材质的微缩场景呈现人物、物件与工作关系。适合软件产品、生产力系统、团队协作和解决方案，具体场景由实际内容决定。

## 选择与共享边界

- 直接调用本 Skill 即选择写实微缩；`deck.json` 根字段设为 `"style": "real-miniature"`。通用请求由 [PPT 制作工作台](../ppt-workbench/SKILL.md) 确认缺少的选择，不能仅凭“软件”“办公”等主题擅自选风格。续做保留当前项目已选方向。
- **真实演示稿动工前确认演讲型或阅读型**，按 [用途与信息密度](../white-blue-slides/references/presentation-modes.md) 执行。已在任务／项目中确认或已授权自行选择时直接采用；根字段 `presentation_mode` 记录 `speech / reading`；页头样式不询问，按内容为每页选择 [`header`](references/header-styles.md)，封面尾页按配图选择 [`variant`](../white-blue-slides/references/deck-format.md#封面与尾页排布)。工具开发和两种模式的验证示例不重复触发用途问卷。
- 本包与 `white-blue-slides` 同级安装。`<style>` 为本包，`<shared>` 为同级 `white-blue-slides`，`<project>` 为当前制作目录。共用脚本、主体版式、播放器与图标组件；套件不含品牌，Logo 与公司名仅在用户提供时写入 deck。本包只维护自己的主题、提示词、参考与规范，不复制脚本，也不加载其他风格的 SKILL 或视觉规则。
- 首次制作阅读 [设计系统](references/design-system.md)，查看 `assets/reference-design/approved-workflow.png`。这是已确认的无文字风格参考，`review-scene.png` 是同方向的协作近景样例。参考中的四区、人数、植物、箭头、顶部图形并非每页必备元素；品牌和场景内容不作为产品事实。

用途明确后，从 [演讲型示例](assets/deck.example.json) 或 [阅读型示例](assets/deck.reading.example.json) 建立项目。示例文案与数字仅用于展示排版，按实际大纲替换，不视作用户的选择或产品承诺。

默认交付可编辑、离线单文件 HTML。交付前按共享 [基本排版 QA](../white-blue-slides/references/layout-qa.md) 运行 `audit_deck.cjs`，逐页看截图检查布局是否合理（碰撞、重心与留白、对齐、层次、断行、密度、图片裁切），修改并重建后再交付，交付时简述看过与改过的页。PPTX／PDF 由用户通过播放器自行导出；Agent 不自动导出、不做 PowerPoint 实看或播放／编辑回归。用户明确要求 PPTX、PDF 或更深入的检查时，完成所要求的部分。构建失败、结构错误与缺失资源须修复，见共享 [默认交付与职责](../white-blue-slides/references/export.md#默认交付与职责)。

## 从内容到成稿

1. **按用途拆页。** 先按共享 [制作大纲](../white-blue-slides/references/outline.md) 把用户内容转化为适合所选风格与用途的 `大纲.md`（逐页结论、关系与数量、上屏文字、版式、配图、讲稿与【待补】），再按大纲动手。保留用户的主线、事实、页数与格式要求。演讲型一页一个结论，细节可放 `notes`；阅读型在页面补足机制、责任、依据、条件与边界，信息密度来自可视化关系而非小字。已有尾页或页数限制时不额外加页。
2. **选共享版式并建立计划。** 按共享 [内容自主选版](../white-blue-slides/references/layout-selection.md) 判断关系、数量、素材与数据，用 `select_layout.py` 从 48 个执行策略筛选。按 [数据结构与构建方法](../white-blue-slides/references/deck-format.md) 写真实字段；新增布局进入共享层，不限定本风格专用。大纲明确的视觉要求写入 `visual.requirements`，直接用于配图与构建，不另启内容预检。标题默认配语义图标，不适用时写具体 `icon_omit_reason`。
3. **按页准备配图。** 阅读 [配图流程](references/image-workflow.md)。逐图简报描述对象、动作、结构、材质细节与构图；保持 35–45° 镜头和 PBR 材质，人物在场时有细致五官、自然手势与衣物褶皱。数量和关系以本页内容为准，可用无人设备场景，不把每页套成四个办公分区。默认 `ui_text: "none"`，标题、说明、数字均由 HTML 承载。
4. **组织可编辑内容。** 阅读型按内容关系安排图片、流程、矩阵、解释和 [ECharts](../white-blue-slides/references/charts.md)，不规定固定图文比例或分区数量；多图分别解释不同阶段或视角。旧 `reading` 四分区仍是可选布局，其结构合同仅在选用时适用。数量图表标明单位与来源，示例标明示例，不补造产品效果。控制区长文字、阶段字段和架构分层标注使用共享构建器的结构化字段，先匹配列宽与配图比例，再调整细节。普通条目保持无框、相同缩进；重点标题和图标可放大约 10%，不突然增加一张卡片。
5. **构建并交付。** 使用共享构建器加载本包主题，完成必需内容与配图并修复构建失败。做基本排版 QA 后交付独立 `.html`，导出由用户自行完成；JSON 与提示词是过程文件。[检查参考](references/quality-check.md)补充本风格的看图要点。

## 命令

解析实际安装位置，不使用开发机器的固定路径：

```sh
python3 <shared>/scripts/prepare_images.py <project>/deck.json --out <project>/image-handoff
# 无内置生图工具且用户同意使用自己的 API：用户在终端 --setup 后，--check → --dry-run → --pages 试一页 → 生成其余缺图
python3 <shared>/scripts/generate_images.py <project>/deck.json --dry-run
python3 <shared>/scripts/build_deck.py <project>/deck.json --out <project>/演示稿.html
```

CSS、脚本、图表、图标、Logo 与配图全部内嵌。构建用 Python 标准库，Pillow 可压缩配图；使用环境已有运行时。`--draft` 仅供缺图预排，不是成品。

已有素材先查看后复用。有内置生图工具时直接生成并用于排版；不可用时导出完整供图清单，询问用户是否用自己的生图 API 按共享 [image-api](../white-blue-slides/references/image-api.md) 自动生成，否则人工供图；继续独立的文字与布局工作，如实列出尚缺素材，不静默改走付费 API。维护本包运行代码、主题或共享脚本时，按共享 [开发检查](../white-blue-slides/references/quality-check.md#开发与维护检查)执行适用测试；仅修改说明文档不触发成稿检查或导出。未来增加方向按 [新增独立风格包](../white-blue-slides/references/adding-styles.md) 创建同级包。
