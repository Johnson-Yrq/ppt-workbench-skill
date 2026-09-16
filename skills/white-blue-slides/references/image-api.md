# 通过生图 API 自动生成配图

适用于当前环境**没有内置生图工具**（Claude Code、Cursor、终端 Agent 等）而用户愿意使用自己的生图 API 的情况。共享脚本 `scripts/generate_images.py` 读取 `prepare_images.py` 导出的 `image-manifest.json`，逐张调用 API、保存到清单指定的项目路径并写回状态。所有风格通用；提示词、纸色与参考图仍来自所选风格。

三条运行路径的优先级：内置生图工具 → 用户配置的生图 API → 人工供图。API 路径只在用户明确同意后启用；不因为环境缺工具就默认走付费接口。

## Agent 引导流程

1. **先完成不依赖图片的工作**：拆页、`deck.json`、`--check-plan`、逐页 `image.brief`，再运行 `prepare_images.py` 导出清单。任何路径都需要这一步。
2. **询问一次**：说明当前环境没有内置生图工具，给出两个选项：配置生图 API 自动生成，或按 `配图提示词.md` 人工供图。同时列出支持的 provider（`openai`：OpenAI Images API 及兼容代理；`gemini`：Google Gemini 图像模型）和大致费用来源。用户不选或选择人工供图时，按 [人工供图](image-workflow.md#人工供图) 继续。
3. **用户同意后，把配置命令交给用户在自己的终端执行**。密钥不经过对话：`--setup` 在交互终端里用不回显的方式读取，保存到仅当前用户可读的配置文件。

   ```sh
   # OpenAI 官方或兼容服务（把 url 换成实际基址，model 换成实际模型名）
   python3 <shared>/scripts/generate_images.py --setup --provider openai --url https://api.openai.com/v1 --model gpt-image-1

   # Google Gemini
   python3 <shared>/scripts/generate_images.py --setup --provider gemini --model gemini-2.5-flash-image
   ```

   中转服务（用自己的域名转发 OpenAI 格式接口，常见于国内）先看是否有预设：`--setup --preset rightapi --model <模型名>` 会一次写入基址、异步任务地址与参考图方式，不需要用户查文档。没有预设的中转服务把 `--url` 换成服务商给的基址（到 `/v1` 为止），需要异步任务或非标准字段时按下文“中转服务与异步任务”配置。

   ```sh
   # Right Code（rightapi.ai）中转：异步画图接口
   python3 <shared>/scripts/generate_images.py --setup --preset rightapi --model gpt-image-2.5
   ```

   用户已有 `OPENAI_API_KEY` / `GEMINI_API_KEY` 环境变量时，加 `--no-key` 即可，脚本会自动回退到这些变量；也可用 `--key-env 变量名` 指定其他变量。**Agent 不要求用户把密钥贴进对话，不代替用户输入密钥，也不把密钥写进任何项目文件**。用户若已在对话中贴出密钥，提醒其轮换，并仍按上面的方式配置。
4. **验证配置**（免费，不生图）：

   ```sh
   python3 <shared>/scripts/generate_images.py --check
   ```

   输出 provider、基址、模型、密钥掩码与来源。`fail` 说明缺密钥或鉴权失败；`warn` 通常是兼容服务没有模型列表接口，可先生成一页试试。
5. **先预演，再小批量生成**：

   ```sh
   python3 <shared>/scripts/generate_images.py <project>/deck.json --dry-run
   python3 <shared>/scripts/generate_images.py <project>/deck.json --pages 2
   ```

   `--dry-run` 列出每张图的比例、请求尺寸和提示词长度，不需要密钥。先生成一页，查看结果是否符合风格与简报；合格后再去掉 `--pages` 生成其余缺图。
6. **逐张查看后再构建**。生成不等于合格：核对对象数量、流程顺序、层级、主次尺度、纸色与残留文字，按所选风格的配图流程处理底色（`match_paper.py --dry-run`）。不合格的页面改写 `brief` 后用 `--pages N --force` 重生成，原图自动改名为 `-v1`、`-v2` 保留。
7. **报告结果**：说明生成了哪些文件、失败原因、仍缺哪些图；失败页面可回退为人工供图，不把缺图草稿称为成稿。

## 配置

配置文件默认在 `~/.config/ppt-workbench/image-api.json`，可用 `--config` 或环境变量 `SLIDES_IMAGE_API_CONFIG` 指定。仓库 `.gitignore` 已排除 `image-api.json`；不要把它放进项目目录再提交。

| 字段 | 说明 |
|---|---|
| `provider` | `openai` 或 `gemini` |
| `url` | API 基址。openai 默认 `https://api.openai.com/v1`，兼容服务填其 `/v1` 基址；gemini 默认 `https://generativelanguage.googleapis.com/v1beta`。粘贴完整端点也会自动截成基址 |
| `model` | 图像模型名。openai 默认 `gpt-image-1`，也支持 `dall-e-3` 及兼容服务的模型名；gemini 默认 `gemini-2.5-flash-image` |
| `api_key` / `api_key_env` | 密钥本身（`--setup` 写入）或密钥所在环境变量名。运行时优先级：`SLIDES_IMAGE_API_KEY` → `api_key` → `api_key_env` → `OPENAI_API_KEY` / `GEMINI_API_KEY` |
| `reference` | `auto`（默认）/ `on` / `off`。是否随提示词附上供图目录的 `style-reference.*`。auto 在 gemini 与 `gpt-image*` 模型上附图（分别走 generateContent 内联图片和 `/images/edits`），其他模型不附 |
| `fit` | `pad`（默认）/ `none`。API 只能输出固定尺寸；pad 用清单中的纸色把结果补边到清单比例，需要 Pillow |
| `sizes` | 覆盖请求尺寸，键为比例（`"4:3"`）或 `landscape / portrait / square`，值为 `WxH`。兼容服务支持其他尺寸时使用 |
| `quality` | 透传给 OpenAI 兼容接口的 `quality`（如 `high / medium / low`，DALL·E 用 `standard / hd`） |
| `timeout` | 单次请求超时秒数，默认 180 |
| `preset` | `--setup --preset` 写入的预设名，仅作记录 |
| `async` | `true` 时请求体带 `"async": true`，收到 `task_id` 后轮询 `tasks_url` 直到完成 |
| `tasks_url` | 任务查询地址模板，含 `{task_id}`；默认 `{url}/tasks/{task_id}` |
| `check_url` | `--check` 使用的模型列表地址；中转服务的列表接口常在站点级 `/v1/models` 而不在画图基址下 |
| `size_style` | `pixels`（默认，发送 `WxH`）或 `ratio`（发送 `16:9` 这类比例串，取 `ratios` 中最接近且同方向的一项） |
| `ratios` | `size_style: ratio` 时服务支持的比例列表，默认为套件全部比例 |
| `reference_transport` | `multipart`（默认，走 `/images/edits`）或 `data_url`（参考图以 data URL 数组放在 generations 请求体的 `image` 字段） |
| `image_size` | 透传 `imageSize`（如 `1K / 2K / 4K`），部分中转服务支持 |
| `poll_timeout` | 异步任务最长等待秒数，默认 600 |

环境变量 `SLIDES_IMAGE_PROVIDER / SLIDES_IMAGE_API_URL / SLIDES_IMAGE_MODEL / SLIDES_IMAGE_API_KEY` 覆盖配置文件；命令行 `--provider / --url / --model / --reference / --fit / --quality / --timeout` 覆盖两者。

## 中转服务与异步任务

内置预设：

| 预设 | 基址 | 特点 |
|---|---|---|
| `rightapi` | `https://www.rightapi.ai/draw/v1` | 请求体固定 `async: true`；轮询 `https://www.rightapi.ai/v1/tasks/{task_id}`（站点级，不带 `/draw`）；`size` 用比例串（`1:1 / 16:9 / 9:16 / 4:3`）；参考图为 data URL 数组；模型名按服务商列表，如 `gpt-image-2.5`、`nano-banana-fast` |

其他中转服务用 `--setup --provider openai --url <基址>` 后，在配置文件中按需补 `async / tasks_url / size_style / ratios / reference_transport / image_size` 字段。轮询把 `queued / processing / in_progress` 视为进行中，`completed`（或直接返回 `data`）视为完成，`failed` 读取 `error.message` 记入清单。

## 请求与结果

- openai：无参考图时 `POST {url}/images/generations`；附参考图时 `POST {url}/images/edits`（multipart，`gpt-image*` 用 `image[]` 字段），`reference_transport: data_url` 时改为 generations 请求体的 `image` 数组。结果 `url` 为 data URL 时直接解码。`gpt-image*` 不发送 `response_format`，其他模型请求 `b64_json`。尺寸默认横图 `1536x1024`、竖图 `1024x1536`、方图 `1024x1024`；`dall-e` 模型改为 `1792x1024 / 1024x1792 / 1024x1024`。
- gemini：`POST {url}/models/{model}:generateContent`，`responseModalities: ["TEXT","IMAGE"]`，`imageConfig.aspectRatio` 取与清单比例最接近的受支持比例（如 `2:1` → `16:9`，`3:1` → `21:9`），再按 `fit` 补边。
- 限流与 5xx 自动重试（默认 2 次，指数退避）；401/403 立即停止并提示检查密钥；单页失败记录到清单 `error`，继续下一页，最后退出码为 1。
- 结果按清单文件名保存（扩展名决定 PNG/JPEG/WebP），清单条目更新为 `status: generated`、`method: api:<provider>/<model>`、`request_size`、`pixels`、`generated_at`、`reference_used`，补边时附 `note`。已有文件不覆盖，除非 `--force`。

## 边界

- 脚本只依赖 Python 标准库；补边与格式转换需要 Pillow，缺少时保存原始输出并在清单记 `note`。
- 不做内容审核绕过、不并发轰炸接口；提示词按清单原样发送，DALL·E 3 等有长度上限的模型可能拒绝过长提示词，此时改用支持长提示词的模型或人工供图。
- `--check` 只调用模型列表接口，不产生生成费用；每次实际生成都会计费，先 `--dry-run` 再 `--pages` 试一页。
- 生成图片与内置工具、人工供图一样要经过逐张查看和风格验收；API 路径改变的只是取图方式，不改变质量标准。
