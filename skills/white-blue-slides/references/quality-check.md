# 检查参考与工具维护

普通演示稿交付前由 Agent 完成 [基本排版 QA](layout-qa.md)（逐页截图、看布局并修改），见 [默认交付与职责](export.md#默认交付与职责)。导出后的 PowerPoint／PDF 实看由用户完成。本文补充用户自查要点、检查器说明和维护 Skill 时的开发检查。

## 用户自查要点

- 内容、页数、单位与数据来源是否对应大纲，概念图片是否被误认成真实客户、员工或产品截图。
- 标题、正文和图表标签是否清楚，是否出现遮挡、裁切或不合理换行；图与相邻说明是否对应，页面是否保持所选风格。
- 配图主体是否完整，场景、层级与素材来源是否适合本页；纯文字页和图表页是否有足够留白。
- HTML 的翻页、总览、讲稿、编辑、另存与离线打开是否符合使用需要。
- 自行导出后，在实际使用的 PowerPoint 或 PDF 阅读器中查看字体、图片、图表与页面比例；导出方法见 [用户自行导出](export.md)。

## 检查器

`audit_deck.cjs` 是基本排版 QA 的必跑步骤；`--check-plan` 计划诊断按需使用。`<shared>` 为 `white-blue-slides` 目录，`<project>` 为项目目录。

```sh
# 输入计划与结构诊断，不需要图片
python3 <shared>/scripts/build_deck.py <project>/deck.json --check-plan --out <project>/design-plan.json

# 成稿渲染诊断，需要 Node、Playwright 与浏览器
node <shared>/scripts/audit_deck.cjs <project>/演示稿.html --out <project>/qa --browser chrome
```

计划诊断提供设计字段、容量、坐标与资源信息。渲染审查器输出逐页截图及 `report.json`，可诊断越界、重叠、缺图、外部依赖、图表标签和所选 reading 布局的模块边界等问题，并提醒页标题超过两行与各页条目名字重不一致。`ok` 只表示自动诊断通过，不证明内容或美感；没有运行时不声称通过。遇到失败时先区分环境、输入与布局问题，不反复运行同一失败命令。

## 开发与维护检查

本节仅适用于修改 Skill 的脚本、播放器、导出器、图表、模板或主题，不因制作一份演示稿而启动（成稿只做基本排版 QA）。仅修改说明文档时，核对规则与引用并运行 Skill 元数据验证即可。

修改运行代码或主题资源后，运行 `python3 <shared>/scripts/selftest.py`，并以适合改动的代表稿验证受影响行为。改动播放器、导出器、图表、模板或主题 CSS 时，再运行相应播放器回归；其覆盖翻页、总览、讲稿、编辑、图表数据、另存重开、PPTX 导出、手机与全屏适配。涉及 PDF 时加 `--pdf`：

```sh
node <shared>/scripts/test_player.cjs <project>/演示稿.html --browser chrome [--pdf]
```

维护布局时使用控制区、架构与阶段页等受影响的代表案例，包含不同阶段数、长标题、高密度内容与错误输入；保留中文换行、可编辑字段、图文关系和其他风格的外观。需要视觉诊断时再运行审查器并查看受影响页面，不能仅以 DOM 无溢出证明布局正确，也不将特定页码或固定阶段数写成通用规则。

新增相关组件时可运行 `node <shared>/scripts/test_browser_refinements.cjs 验证稿.html`，覆盖共享行高、窄／宽栏切换、可编辑字段和纸色映射；使用并排 flow、带 prefix/detail 的 architecture、带 period/fields 的 journey 等相应案例。新风格接入与代表样稿批准继续遵循 [接入规范](adding-styles.md)，不因成稿只做基本排版 QA 而跳过。
