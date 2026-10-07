# 留白衬线影集：来源与中文转译记录

## 来源

- Canva 模板：**Presentación Portafolio Estudio de Fotografía Simple Minimalista Blanco**。
- 作者：**Mica Crocce - Creare DG**。
- 预览入口：[Canva 模板预览](https://www.canva.com/s/templates?query=&adj=eyJFIjp7IkEiOiJ0QUV4UkxnODFSSSJ9fQ)。该地址是当时的模板预览入口，不是已确认的永久设计地址；不据此编造模板 ID。
- 页面显示 1920 × 1080 演示文稿，共 10 页。以下截图保留浏览器与 Canva 界面，仅用于视觉来源，不作为交付页面背景。

| 页 | 本地截图 | 来源结构与中文转译 |
|---|---|---|
| 01 | [canva-01.png](canva-01.png) | 居中衬线封面、眉题和副标题；译为「光阴有形」，使用 `type_poster.cover` 与 center |
| 02 | [canva-02.png](canva-02.png) | 大面积留白中的居中短句；译为观看与时间的主张，使用 `type_poster.statement` |
| 03 | [canva-03.png](canva-03.png) | 左侧黑白幕后照片、右下介绍；译为「关于拾光」，使用 image / text 分栏 |
| 04 | [canva-04.png](canva-04.png) | 右下理念标题、正文和三项列表；译为「我们的观看方式」，使用 statement 与 bottom-right |
| 05 | [canva-05.png](canva-05.png) | 左侧上下风景照片、右侧项目叙述；译为「沿途的光」，使用 gallery / text |
| 06 | [canva-06.png](canva-06.png) | 城市照片一大两小，无可见正文；译为「城市的另一面」，使用 image / gallery 并隐藏展示态标题 |
| 07 | [canva-07.png](canva-07.png) | 左侧食物近景、右侧项目叙述；译为「寻常滋味」，使用 image / text |
| 08 | [canva-08.png](canva-08.png) | 左侧不等高双图、右侧大幅食物照片；译为「餐桌上的细节」，使用单列 gallery 的 row_weights 与 image |
| 09 | [canva-09.png](canva-09.png) | 左下项目叙述、右侧聚会摄影；译为「相聚的理由」，使用 text / image |
| 10 | [canva-10.png](canva-10.png) | 三张等高竖幅聚会照片；译为「让此刻留下」，使用三个 image 栏并隐藏展示态标题 |

源第 9、10 页印刷页码仍为 7、8；本地样稿使用实际页序生成动态页码，修复重复。源模板未包含联系页，不将相似模板缩略图中的联系页计入本来源，也不编造联系信息。

## 提取与替代边界

保留近白纸色、黑色衬线文字、宽阔留白、直角图框、细横线页脚和居中页码／品牌。旅行、食物及聚会照片保留自然彩色，人物幕后图可用黑白；来源不支持整稿灰阶处理。

原字体名称未知。中文转译使用本地 Georgia、Times New Roman、Songti SC 及 serif 后备，不宣称识别出 Canva 原字体。纸色 `#FAFAFA` 为截图经过 ICC 转换到 sRGB 后的本地采样近似，不冒称原模板的精确设计令牌。

中文内容以虚构摄影工作室「拾光影像」为示例，品牌、项目叙述与人物场景均为虚构；每页 notes 明确记录，不代表真实客户、作品履历或事件。14 张图片由内置 imagegen 原创生成，素材位于 `assets/images/`；未复制来源照片、品牌或西班牙语占位文字。

## 批准状态与交付位置

本包名 `airy-portfolio-slides`，style ID `airy-portfolio`，正式版本 **1.0.0**，状态 **ready**。用户于 **2026-10-05** 对本方向的中文样稿明确回复「采用，并安装」，批准采用当前视觉、正式接入共享制作套件及安装。该批准直接针对留白衬线影集，无需借用此前其他风格的批准，也不改变其他新方向的批准要求。

本方向最初以 draft / 0.1.0 开发并展示十页中文样稿，在获得上述确认后升级为 ready / 1.0.0。历史草稿样例和开发记录仅用于追溯，不是正常制作的待确认节点。

- 演讲型结构：[deck.example.json](../deck.example.json)。
- 阅读型内容示例：[deck.reading.example.json](../deck.reading.example.json)。
- 项目内中文样稿：`examples/airy-portfolio/留白衬线影集-中文风格样稿.html`。
- 提示词与素材记录：`examples/airy-portfolio/image-prompts.json`、`examples/airy-portfolio/image-sources.json`。

本方向的样稿批准已经满足；正式制作不再次索取同一方向批准。安装与更新遵循共享接入验证流程，具体完成状态以安装验证结果为准，本记录不代替验证。普通成稿默认交付 HTML，交付前做基本排版 QA，由用户自行导出，明确要求的 PPTX／PDF 仍需完成。
