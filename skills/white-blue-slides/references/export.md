# 导出 PDF 与 PPTX

成稿是单文件 HTML。用户要 PDF 或 PPTX 时才导出；浏览器里编辑过的稿，先“另存 HTML”，用另存的文件作为输入。

```sh
# 16:9 宽屏、单页适配的 PDF（另需 pdf-lib；导出时核对页数与纸张尺寸）
node <skill>/scripts/export_pdf.cjs <project>/演示稿.html --out <project>/演示稿.pdf --browser chrome

# 可编辑 PPTX（文字、面板、图片、原生图表、讲稿；与播放器“导出 PPTX”按钮相同）
node <skill>/scripts/export_pptx.cjs <project>/演示稿.html --out <project>/演示稿.pptx --browser chrome [--font "PingFang SC"]

# 只有 PDF 且需要浏览器全屏演示时，生成单页显示的离线副本（需要 Poppler）
python3 <skill>/scripts/pdf_to_slides.py <project>/演示稿.pdf --out <project>/全屏演示版.html
```

## 画布与 PDF

画布保持 1920 × 1080。全屏按实际可用区域完整等比适配；编辑模式为工具栏留出空间。PDF 使用 PowerPoint 宽屏纸张 960 × 540 pt（13⅓ × 7.5 英寸），所有页保持与单页观看相同的纵向布局。播放器“导出 PDF / 打印”打开浏览器打印窗口；需要稳定纸张尺寸与单页适配偏好时用 `export_pdf.cjs`。阅读器可能忽略 PDF 观看偏好，此时选择“适合页面”；非 16:9 屏幕保留边带。旧 HTML 内嵌旧播放器，不会随 Skill 更新自动变化；从源项目重建，浏览器编辑过的旧稿须先保留另存副本，避免覆盖修改。

## PPTX

播放器“导出 PPTX”与 `export_pptx.cjs` 生成同一种可编辑 PowerPoint 文件：按实际渲染测量每个元素的位置，文字保留为文本框（字号、粗细、颜色、字距、行距不变），信息块、标签与横线转为形状，场景图与图标转为图片，ECharts 转为原生图表并内嵌数据表，讲稿写入备注。全稿统一使用一种通用字体（默认微软雅黑，`--font` 可改），因此英文与数字略宽，单行文字不折行、多行文字留有余量；毛玻璃、阴影等效果按 PowerPoint 能表达的程度近似。导出器随每份 HTML 内嵌、不联网；旧稿没有该按钮时用命令行导出。交付 PPTX 前在 PowerPoint 中逐页查看，不以 HTML 通过代替。

## PDF 全屏副本

用户接受 HTML 演示副本且只有 PDF 时，可用 `pdf_to_slides.py` 生成单文件副本。它依赖 Poppler 的 `pdfinfo` / `pdftocairo`，将每页转换为内嵌 SVG 图像，一次仅显示当前页，支持全屏、方向键、页码跳转和触控翻页。文字保留矢量轮廓但不可编辑或选择，不替代可编辑源稿或用户明确要求的 PDF；逐页查看转换结果，并检查实际浏览器全屏的四边和翻页。

## PDF 阅读器全屏白条

Chrome PDF 全屏出现下一页白条时，先区分 PDF 页面留白与阅读器露出相邻页。在 macOS 上，检查“系统设置 → 外观 → 显示滚动条”是否为“始终”；已复现案例中，经用户同意改为“滚动时”，退出演示并重新加载 PDF 后再进入演示，白条消失。该项影响系统内其他应用，不静默更改用户偏好。验证必须使用同一份 PDF，并检查翻页后的底部；不能用 HTML 演示通过来声称 PDF 已修复。不要以改变纸张尺寸、裁切内容或补黑边掩盖阅读器问题。
