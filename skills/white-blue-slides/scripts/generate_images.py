#!/usr/bin/env python3
"""Generate the missing illustrations of a deck through a user-configured image API.

Used only when the agent environment has no built-in image tool and the user has
explicitly agreed to use their own image API. The API key never passes through the
conversation: the user runs `--setup` in their own terminal (the key is read with
getpass) or exports an environment variable. Standard library only; Pillow is optional
for padding the result to the exact aspect ratio with the page paper colour.

  python3 generate_images.py --setup --provider openai --url https://api.openai.com/v1 --model gpt-image-1
  python3 generate_images.py --setup --preset rightapi --model gpt-image-2.5
  python3 generate_images.py --check
  python3 generate_images.py <project>/deck.json --dry-run
  python3 generate_images.py <project>/deck.json [--pages 3,5] [--force]
"""
import argparse
import base64
import getpass
import io
import json
import math
import os
import re
import stat
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import IMAGE_RATIOS, image_size, pillow, read_raster  # noqa: E402

CONFIG_ENV = 'SLIDES_IMAGE_API_CONFIG'
DEFAULT_CONFIG = Path.home() / '.config' / 'ppt-workbench' / 'image-api.json'
ENV = {'api_key': 'SLIDES_IMAGE_API_KEY', 'url': 'SLIDES_IMAGE_API_URL', 'model': 'SLIDES_IMAGE_MODEL', 'provider': 'SLIDES_IMAGE_PROVIDER'}
PROVIDERS = {
    'openai': {'label': 'OpenAI Images API 及兼容服务', 'url': 'https://api.openai.com/v1', 'model': 'gpt-image-1', 'key_env': 'OPENAI_API_KEY'},
    'gemini': {'label': 'Google Gemini 图像模型', 'url': 'https://generativelanguage.googleapis.com/v1beta', 'model': 'gemini-2.5-flash-image', 'key_env': 'GEMINI_API_KEY'},
}
REFERENCE_MODES = ('auto', 'on', 'off')
FIT_MODES = ('pad', 'none')
SIZE_STYLES = ('pixels', 'ratio')
REFERENCE_TRANSPORTS = ('multipart', 'data_url')
TASK_PENDING = {'queued', 'pending', 'processing', 'in_progress', 'running', 'submitted'}
# Relay services that wrap the Images API with their own conventions. `--setup --preset NAME` copies these fields into the config.
PRESETS = {
    'rightapi': {'provider': 'openai', 'url': 'https://www.rightapi.ai/draw/v1', 'model': 'gpt-image-2.5', 'async': True,
                 'tasks_url': 'https://www.rightapi.ai/v1/tasks/{task_id}', 'check_url': 'https://www.rightapi.ai/v1/models',
                 'size_style': 'ratio', 'ratios': ['1:1', '16:9', '9:16', '4:3'], 'reference_transport': 'data_url',
                 'label': 'Right Code 中转（异步画图接口）'},
}
GEMINI_RATIOS = ['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9']
RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}
USER_AGENT = 'ppt-workbench-generate-images/1.0'


# ---------------------------------------------------------------- configuration

def config_path(explicit=None):
    return Path(explicit or os.environ.get(CONFIG_ENV) or DEFAULT_CONFIG).expanduser()


def read_config(path):
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except ValueError as exc:
        raise ValueError(f'配置文件不是有效 JSON：{path}（{exc}）')
    if not isinstance(data, dict):
        raise ValueError(f'配置文件需要一个 JSON 对象：{path}')
    return data


def write_config(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def normalize_url(provider, url):
    url = (url or '').strip().rstrip('/')
    if not url:
        return PROVIDERS[provider]['url']
    if not re.match(r'https?://', url):
        raise ValueError(f'url 需要以 http(s):// 开头：{url}')
    # Accept a pasted full endpoint and keep only the base.
    for tail in ('/images/generations', '/images/edits'):
        if url.endswith(tail):
            url = url[:-len(tail)]
    url = re.sub(r'/models/[^/]+:generateContent$', '', url)
    return url


def resolve_settings(args, environ=None):
    """CLI flags > environment > config file > provider defaults. Never prints the key."""
    environ = os.environ if environ is None else environ
    path = config_path(args.config)
    stored = read_config(path)
    settings = dict(stored)
    for key, name in ENV.items():
        if environ.get(name):
            settings[key] = environ[name]
    for key in ('provider', 'url', 'model', 'reference', 'fit', 'quality', 'timeout', 'image_size'):
        value = getattr(args, key, None)
        if value is not None:
            settings[key] = value
    provider = settings.get('provider')
    if provider not in PROVIDERS:
        raise ValueError('尚未配置生图 API。请用户在自己的终端运行 --setup（provider 可选 ' + ' / '.join(PROVIDERS) + f'），或设置环境变量 {ENV["provider"]}。')
    settings['provider'] = provider
    settings['url'] = normalize_url(provider, settings.get('url'))
    settings['model'] = (settings.get('model') or PROVIDERS[provider]['model']).strip()
    settings['reference'] = settings.get('reference', 'auto')
    if settings['reference'] not in REFERENCE_MODES:
        raise ValueError('reference 可选 ' + ' / '.join(REFERENCE_MODES))
    settings['fit'] = settings.get('fit', 'pad')
    if settings['fit'] not in FIT_MODES:
        raise ValueError('fit 可选 ' + ' / '.join(FIT_MODES))
    timeout = settings.get('timeout', 180)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 10 <= timeout <= 900:
        raise ValueError('timeout 需要 10–900 秒')
    settings['timeout'] = timeout
    sizes = settings.get('sizes', {})
    if not isinstance(sizes, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in sizes.items()):
        raise ValueError('sizes 需要 {"比例或 landscape/portrait/square": "WxH"} 映射')
    settings['sizes'] = sizes
    settings['async'] = bool(settings.get('async', False))
    tasks_url = settings.get('tasks_url') or settings['url'] + '/tasks/{task_id}'
    if not isinstance(tasks_url, str) or '{task_id}' not in tasks_url:
        raise ValueError('tasks_url 需要包含 {task_id} 占位符，例如 https://host/v1/tasks/{task_id}')
    settings['tasks_url'] = tasks_url
    settings['size_style'] = settings.get('size_style', 'pixels')
    if settings['size_style'] not in SIZE_STYLES:
        raise ValueError('size_style 可选 ' + ' / '.join(SIZE_STYLES))
    ratios = settings.get('ratios') or sorted(IMAGE_RATIOS)
    if not isinstance(ratios, list) or any(not isinstance(r, str) or not re.fullmatch(r'\d+:\d+', r) for r in ratios):
        raise ValueError('ratios 需要形如 "16:9" 的比例数组')
    settings['ratios'] = ratios
    settings['reference_transport'] = settings.get('reference_transport', 'multipart')
    if settings['reference_transport'] not in REFERENCE_TRANSPORTS:
        raise ValueError('reference_transport 可选 ' + ' / '.join(REFERENCE_TRANSPORTS))
    if settings.get('image_size') is not None and not isinstance(settings['image_size'], str):
        raise ValueError('image_size 需要字符串，例如 1K / 2K / 4K')
    poll = settings.get('poll_timeout', 600)
    if isinstance(poll, bool) or not isinstance(poll, (int, float)) or not 30 <= poll <= 3600:
        raise ValueError('poll_timeout 需要 30–3600 秒')
    settings['poll_timeout'] = poll
    key = environ.get(ENV['api_key']) or settings.get('api_key')
    if not key:
        for name in (settings.get('api_key_env'), PROVIDERS[provider]['key_env']):
            if name and environ.get(name):
                key = environ[name]
                settings['api_key_source'] = f'环境变量 {name}'
                break
    elif environ.get(ENV['api_key']):
        settings['api_key_source'] = f'环境变量 {ENV["api_key"]}'
    else:
        settings['api_key_source'] = f'配置文件 {path}'
    settings['api_key'] = key or ''
    settings['config_path'] = str(path)
    return settings


def masked(key):
    if not key:
        return '（未设置）'
    return key[:3] + '…' + key[-4:] if len(key) > 10 else '…' + key[-2:]


def setup(args):
    """Write provider settings; read the key from the user's own terminal, never from arguments."""
    path = config_path(args.config)
    data = read_config(path)
    if args.preset:
        if args.preset not in PRESETS:
            raise ValueError('--preset 可选 ' + ' / '.join(f'{k}（{v["label"]}）' for k, v in PRESETS.items()))
        for key, value in PRESETS[args.preset].items():
            if key != 'label':
                data[key] = value
        data['preset'] = args.preset
    provider = args.provider or data.get('provider')
    if provider not in PROVIDERS:
        raise ValueError('--setup 需要 --provider，可选 ' + ' / '.join(f'{k}（{v["label"]}）' for k, v in PROVIDERS.items()) + '；或 --preset ' + ' / '.join(PRESETS))
    data['provider'] = provider
    data['url'] = normalize_url(provider, args.url if args.url is not None else data.get('url'))
    data['model'] = (args.model or data.get('model') or PROVIDERS[provider]['model']).strip()
    for key in ('reference', 'fit', 'quality', 'timeout', 'image_size'):
        value = getattr(args, key, None)
        if value is not None:
            data[key] = value
    if args.key_env:
        data['api_key_env'] = args.key_env
        data.pop('api_key', None)
        key_note = f'密钥将从环境变量 {args.key_env} 读取'
    elif args.no_key:
        data.pop('api_key', None)
        key_note = f'未保存密钥；运行前设置环境变量 {ENV["api_key"]} 或 {PROVIDERS[provider]["key_env"]}'
    elif sys.stdin.isatty():
        entered = getpass.getpass(f'请输入 {PROVIDERS[provider]["label"]} 的 API Key（输入不回显，直接回车保留现有设置）：').strip()
        if entered and (re.match(r'https?://', entered) or ' ' in entered or len(entered) < 8):
            raise ValueError('输入的不像 API Key（密钥通常是一串以 sk- 等开头、不含空格的长字符串，不是网址）。请到服务商的 API Key 页面复制密钥后重新运行 --setup。')
        if entered:
            data['api_key'] = entered
            key_note = '密钥已保存到配置文件（仅当前用户可读）'
        else:
            key_note = '保留现有密钥设置' if data.get('api_key') or data.get('api_key_env') else f'未保存密钥；运行前设置环境变量 {ENV["api_key"]} 或 {PROVIDERS[provider]["key_env"]}'
    else:
        data.pop('api_key', None)
        key_note = f'当前不是交互终端，未读取密钥；请在自己的终端重新运行 --setup，或设置环境变量 {ENV["api_key"]}'
    write_config(path, data)
    print(json.dumps({'config': str(path), 'provider': provider, 'preset': data.get('preset'), 'url': data['url'], 'model': data['model'],
                      'async': bool(data.get('async')), 'api_key': key_note}, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- HTTP

def http_request(method, url, headers, body=None, timeout=180):
    """Single HTTP exchange. Tests replace this function; nothing else touches the network."""
    request = urllib.request.Request(url, data=body, method=method, headers=dict(headers, **{'User-Agent': USER_AGENT}))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read()
    except urllib.error.URLError as exc:
        raise ConnectionError(f'无法连接 {url}：{exc.reason}')


def api_error(status, payload):
    text = payload.decode('utf-8', 'replace') if isinstance(payload, bytes) else str(payload)
    try:
        data = json.loads(text)
        err = data.get('error', data)
        if isinstance(err, dict):
            text = err.get('message') or json.dumps(err, ensure_ascii=False)
        elif isinstance(err, str):
            text = err
    except ValueError:
        pass
    text = ' '.join(text.split())
    return f'HTTP {status}: {text[:600]}'


def call_with_retry(method, url, headers, body, timeout, retries, describe):
    delay = 3
    for attempt in range(retries + 1):
        status, resp_headers, payload = http_request(method, url, headers, body, timeout)
        if status < 300:
            return payload
        if status in RETRY_STATUS and attempt < retries:
            print(f'  {describe}：{api_error(status, payload)}；{delay}s 后重试（{attempt + 1}/{retries}）', file=sys.stderr)
            time.sleep(delay)
            delay = min(delay * 2, 30)
            continue
        if status in (401, 403):
            raise PermissionError(f'{describe}：{api_error(status, payload)}。请检查 API Key 是否正确、是否对该模型有权限。')
        raise RuntimeError(f'{describe}：{api_error(status, payload)}')
    raise RuntimeError(f'{describe}：重试后仍失败')


def multipart(fields, files):
    boundary = 'ppt-workbench-' + uuid.uuid4().hex
    out = io.BytesIO()
    for name, value in fields:
        out.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode('utf-8'))
    for name, filename, mime, data in files:
        out.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\nContent-Type: {mime}\r\n\r\n'.encode('utf-8'))
        out.write(data)
        out.write(b'\r\n')
    out.write(f'--{boundary}--\r\n'.encode('utf-8'))
    return f'multipart/form-data; boundary={boundary}', out.getvalue()


# ---------------------------------------------------------------- sizes

def ratio_value(ratio):
    w, h = ratio.split(':')
    return int(w) / int(h)


def orientation(ratio):
    value = ratio_value(ratio)
    return 'square' if abs(value - 1) < 1e-6 else 'landscape' if value > 1 else 'portrait'


def openai_size(settings, ratio):
    sizes = settings['sizes']
    if ratio in sizes:
        return sizes[ratio]
    kind = orientation(ratio)
    if kind in sizes:
        return sizes[kind]
    if settings['model'].lower().startswith('dall-e'):
        return {'square': '1024x1024', 'landscape': '1792x1024', 'portrait': '1024x1792'}[kind]
    return {'square': '1024x1024', 'landscape': '1536x1024', 'portrait': '1024x1536'}[kind]


def nearest_ratio(ratio, choices):
    """Closest supported ratio; a landscape request never falls back to a portrait size (and vice versa) when the orientation exists."""
    target = math.log(ratio_value(ratio))
    same = [r for r in choices if orientation(r) == orientation(ratio)]
    return min(same or choices, key=lambda r: abs(math.log(ratio_value(r)) - target))


def gemini_ratio(ratio):
    return nearest_ratio(ratio, GEMINI_RATIOS)


def request_size(settings, ratio):
    if settings['provider'] == 'gemini':
        return gemini_ratio(ratio)
    if settings['size_style'] == 'ratio':
        return settings['sizes'].get(ratio) or nearest_ratio(ratio, settings['ratios'])
    return openai_size(settings, ratio)


def uses_reference(settings, reference_file):
    mode = settings['reference']
    if mode == 'off' or not reference_file or not reference_file.is_file():
        return False
    if mode == 'on':
        return True
    if settings['provider'] == 'gemini' or settings['reference_transport'] == 'data_url':
        return True
    return settings['model'].lower().startswith('gpt-image')


# ---------------------------------------------------------------- providers

def _openai_headers(settings):
    return {'Authorization': f'Bearer {settings["api_key"]}'}


def _decode_image_field(item):
    if isinstance(item.get('b64_json'), str):
        return base64.b64decode(item['b64_json'])
    if isinstance(item.get('url'), str):
        if item['url'].startswith('data:'):
            return base64.b64decode(item['url'].split(',', 1)[1])
        status, _, payload = http_request('GET', item['url'], {}, None, 120)
        if status >= 300:
            raise RuntimeError(f'下载生成图片失败：{api_error(status, payload)}')
        return payload
    raise RuntimeError('响应中没有 b64_json 或 url 图片字段')


def poll_task(settings, task_id, describe):
    """Async relays return a task id; poll until the task completes and hand back the final payload."""
    url = settings['tasks_url'].replace('{task_id}', task_id)
    headers = _openai_headers(settings)
    deadline = time.time() + settings['poll_timeout']
    interval = 4
    while True:
        status, _, payload = http_request('GET', url, headers, None, settings['timeout'])
        if status >= 300 and status not in RETRY_STATUS:
            raise RuntimeError(f'{describe}：查询任务失败 {api_error(status, payload)}')
        data = None
        if status < 300:
            try:
                data = json.loads(payload.decode('utf-8'))
            except ValueError:
                raise RuntimeError(f'{describe}：任务查询响应不是 JSON')
        if isinstance(data, dict):
            state = str(data.get('status') or '').lower()
            if state == 'failed' or (isinstance(data.get('error'), dict) and state not in TASK_PENDING):
                err = data.get('error') or {}
                raise RuntimeError(f'{describe}：任务失败 ' + (err.get('message') if isinstance(err, dict) else str(err)))
            if state == 'completed' or data.get('data') or data.get('candidates'):
                return payload
            if state and state not in TASK_PENDING:
                raise RuntimeError(f'{describe}：任务状态未知 {state}')
            progress = data.get('progress')
            print(f'  任务 {task_id[:18]}… {state or "处理中"}' + (f' {progress}%' if isinstance(progress, (int, float)) else ''), file=sys.stderr)
        if time.time() >= deadline:
            raise RuntimeError(f'{describe}：任务 {task_id} 在 {settings["poll_timeout"]} 秒内未完成；稍后可用 --pages 重试')
        time.sleep(interval)
        interval = min(interval + 2, 15)


def generate_openai(settings, entry, reference, retries):
    size = request_size(settings, entry['ratio'])
    model = settings['model']
    describe = f'第 {entry["page"]} 页 {entry["file"]}'
    if reference and settings['reference_transport'] == 'data_url':
        mime, data = read_raster(reference)
        body = {'model': model, 'prompt': entry['prompt'], 'n': 1, 'size': size, 'image': [f'data:{mime};base64,' + base64.b64encode(data).decode('ascii')]}
        if settings.get('quality'):
            body['quality'] = settings['quality']
        if settings.get('image_size'):
            body['imageSize'] = settings['image_size']
        if settings['async']:
            body['async'] = True
        headers = dict(_openai_headers(settings), **{'Content-Type': 'application/json'})
        payload = call_with_retry('POST', settings['url'] + '/images/generations', headers, json.dumps(body).encode('utf-8'), settings['timeout'], retries, describe)
    elif reference:
        fields = [('model', model), ('prompt', entry['prompt']), ('n', '1'), ('size', size)]
        if settings.get('quality'):
            fields.append(('quality', settings['quality']))
        mime, data = read_raster(reference)
        field = 'image[]' if model.lower().startswith('gpt-image') else 'image'
        content_type, body = multipart(fields, [(field, reference.name, mime, data)])
        headers = dict(_openai_headers(settings), **{'Content-Type': content_type})
        payload = call_with_retry('POST', settings['url'] + '/images/edits', headers, body, settings['timeout'], retries, describe)
    else:
        body = {'model': model, 'prompt': entry['prompt'], 'n': 1, 'size': size}
        if settings.get('quality'):
            body['quality'] = settings['quality']
        if settings.get('image_size'):
            body['imageSize'] = settings['image_size']
        if settings['async']:
            body['async'] = True
        elif not model.lower().startswith('gpt-image'):
            body['response_format'] = 'b64_json'
        headers = dict(_openai_headers(settings), **{'Content-Type': 'application/json'})
        payload = call_with_retry('POST', settings['url'] + '/images/generations', headers, json.dumps(body).encode('utf-8'), settings['timeout'], retries, describe)
    try:
        data = json.loads(payload.decode('utf-8'))
    except ValueError:
        raise RuntimeError(f'{describe}：响应不是 JSON')
    if settings['async'] and isinstance(data, dict) and data.get('task_id') and not data.get('data'):
        print(f'  已提交任务 {data["task_id"]}，等待完成…', file=sys.stderr)
        payload = poll_task(settings, str(data['task_id']), describe)
        data = json.loads(payload.decode('utf-8'))
    try:
        items = data['data']
    except (ValueError, KeyError, TypeError):
        raise RuntimeError(f'{describe}：响应不是 Images API 格式（缺少 data 数组）')
    if not items:
        raise RuntimeError(f'{describe}：响应 data 为空')
    return _decode_image_field(items[0]), size


def generate_gemini(settings, entry, reference, retries):
    aspect = gemini_ratio(entry['ratio'])
    parts = [{'text': entry['prompt']}]
    if reference:
        mime, data = read_raster(reference)
        parts.insert(0, {'inlineData': {'mimeType': mime, 'data': base64.b64encode(data).decode('ascii')}})
        parts[1]['text'] = 'Use the attached image only as a reference for materials, scale, lighting and visual hierarchy. Do not copy its objects, brand or business content.\n\n' + entry['prompt']
    body = {'contents': [{'role': 'user', 'parts': parts}],
            'generationConfig': {'responseModalities': ['TEXT', 'IMAGE'], 'imageConfig': {'aspectRatio': aspect}}}
    headers = {'x-goog-api-key': settings['api_key'], 'Content-Type': 'application/json'}
    describe = f'第 {entry["page"]} 页 {entry["file"]}'
    url = f'{settings["url"]}/models/{settings["model"]}:generateContent'
    payload = call_with_retry('POST', url, headers, json.dumps(body).encode('utf-8'), settings['timeout'], retries, describe)
    try:
        data = json.loads(payload.decode('utf-8'))
        candidates = data.get('candidates') or []
        for candidate in candidates:
            for part in (candidate.get('content') or {}).get('parts') or []:
                inline = part.get('inlineData') or part.get('inline_data')
                if inline and isinstance(inline.get('data'), str):
                    return base64.b64decode(inline['data']), aspect
        reason = (candidates[0].get('finishReason') if candidates else None) or (data.get('promptFeedback') or {}).get('blockReason')
    except (ValueError, AttributeError, TypeError):
        raise RuntimeError(f'{describe}：响应不是 generateContent 格式')
    raise RuntimeError(f'{describe}：响应中没有图片' + (f'（finishReason: {reason}）' if reason else '') + '；模型可能不支持出图或提示词被拦截')


GENERATORS = {'openai': generate_openai, 'gemini': generate_gemini}


def check_connection(settings):
    """A free, read-only request that validates the key and base URL without generating."""
    if settings['provider'] == 'gemini':
        status, _, payload = http_request('GET', settings['url'] + '/models?pageSize=1', {'x-goog-api-key': settings['api_key']}, None, 30)
    else:
        status, _, payload = http_request('GET', settings.get('check_url') or settings['url'] + '/models', _openai_headers(settings), None, 30)
    if status in (401, 403):
        return 'fail', f'鉴权失败：{api_error(status, payload)}'
    if status == 404 or status == 405:
        return 'warn', f'该服务不提供模型列表接口（HTTP {status}），无法在此验证密钥；可先用 --pages 生成一张试试'
    if status >= 300:
        return 'warn', f'模型列表接口返回 {api_error(status, payload)}'
    try:
        data = json.loads(payload.decode('utf-8'))
        names = [m.get('id') or m.get('name', '') for m in (data.get('data') or data.get('models') or []) if isinstance(m, dict)]
    except (ValueError, AttributeError):
        return 'warn', f'{settings.get("check_url") or settings["url"] + "/models"} 返回的不是模型列表 JSON；请确认基址正确，再用 --pages 生成一页验证'
    model = settings['model']
    if names and not any(n.endswith(model) or n == model for n in names):
        return 'warn', f'连接正常，但模型列表中没有 {model}（列表可能不完整，共 {len(names)} 项）'
    return 'ok', '连接正常' + (f'，模型 {model} 可用' if names else '')


# ---------------------------------------------------------------- output

def paper_rgb(paper):
    return tuple(int(paper[i:i + 2], 16) for i in (1, 3, 5))


def fit_to_ratio(data, ratio, paper, mode, target_suffix):
    """Pad with the page paper colour so the saved file has exactly the manifest ratio. Returns (bytes, note)."""
    mime, _ = read_raster_bytes(data)
    Image = pillow()
    if Image is None:
        return data, '未安装 Pillow，保存原始输出，未按比例补边或转换格式'
    im = Image.open(io.BytesIO(data))
    if im.mode not in ('RGB', 'RGBA'):
        im = im.convert('RGBA' if 'A' in im.mode or im.mode == 'P' else 'RGB')
    note = None
    if mode == 'pad':
        target = ratio_value(ratio)
        w, h = im.size
        if abs(w / h - target) / target > 0.01:
            nw, nh = (w, round(w / target)) if w / h > target else (round(h * target), h)
            canvas = Image.new('RGB', (nw, nh), paper_rgb(paper))
            base = im.convert('RGBA')
            canvas.paste(base, ((nw - w) // 2, (nh - h) // 2), base.getchannel('A'))
            im = canvas
            note = f'已用纸色 {paper} 补边至 {ratio}（{w}×{h} → {nw}×{nh}）'
    fmt = {'.png': 'PNG', '.jpg': 'JPEG', '.jpeg': 'JPEG', '.webp': 'WEBP'}.get(target_suffix.lower(), 'PNG')
    if fmt == 'JPEG' and im.mode == 'RGBA':
        flat = Image.new('RGB', im.size, paper_rgb(paper))
        flat.paste(im, mask=im.getchannel('A'))
        im = flat
    buf = io.BytesIO()
    im.save(buf, fmt, **({'quality': 92} if fmt in ('JPEG', 'WEBP') else {}))
    return buf.getvalue(), note


def read_raster_bytes(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png', data
    if data.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg', data
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'image/webp', data
    raise ValueError('生成结果不是 PNG/JPEG/WebP 图片')


def next_version(path):
    n = 1
    while True:
        candidate = path.with_name(f'{path.stem}-v{n}{path.suffix}')
        if not candidate.exists():
            return candidate
        n += 1


def load_manifest(deck_path, handoff):
    manifest_path = handoff / 'image-manifest.json'
    if not manifest_path.is_file():
        from prepare_images import prepare
        print(f'未找到 {manifest_path}，先导出提示词清单…', file=sys.stderr)
        prepare(str(deck_path), str(handoff))
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    if manifest.get('version') != 1 or not isinstance(manifest.get('images'), list):
        raise ValueError(f'清单格式不符：{manifest_path}')
    return manifest, manifest_path


def select_entries(manifest, root, pages, force):
    chosen = []
    for entry in manifest['images']:
        if pages and entry['page'] not in pages:
            continue
        file = root / entry['file']
        if file.is_file() and not force:
            entry['status'] = entry.get('status') if entry.get('status') in ('generated', 'provided') else 'provided'
            continue
        if not entry.get('prompt'):
            entry['status'] = 'missing'
            entry['error'] = '缺少 brief，未生成提示词'
            continue
        chosen.append(entry)
    return chosen


def generate(args):
    deck_path = Path(args.deck).resolve()
    if not deck_path.is_file():
        raise ValueError(f'找不到 deck：{deck_path}')
    root = deck_path.parent
    handoff = Path(args.handoff).resolve() if args.handoff else root / 'image-handoff'
    manifest, manifest_path = load_manifest(deck_path, handoff)
    pages = set()
    if args.pages:
        try:
            pages = {int(p) for p in re.split(r'[,\s]+', args.pages.strip()) if p}
        except ValueError:
            raise ValueError('--pages 需要逗号分隔的页码，例如 2,5,7')
    entries = select_entries(manifest, root, pages, args.force)
    settings = resolve_settings(args)
    reference = handoff / manifest['style_reference'] if manifest.get('style_reference') else None
    with_reference = uses_reference(settings, reference)
    plan = {'provider': settings['provider'], 'preset': settings.get('preset'), 'model': settings['model'], 'url': settings['url'], 'async': settings['async'], 'reference': with_reference,
            'fit': settings['fit'], 'api_key': masked(settings['api_key']), 'to_generate': [e['file'] for e in entries]}
    if args.dry_run:
        for e in entries:
            plan.setdefault('requests', []).append({'page': e['page'], 'file': e['file'], 'ratio': e['ratio'],
                                                    'size': request_size(settings, e['ratio']),
                                                    'prompt_chars': len(e['prompt'])})
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    if not entries:
        print(json.dumps(dict(plan, generated=[], failed=[], message='没有需要生成的图片；已有图片保持不变，用 --force 重生成'), ensure_ascii=False, indent=2))
        return 0
    if not settings['api_key']:
        raise PermissionError(f'缺少 API Key。请用户在自己的终端运行 --setup 输入，或设置环境变量 {ENV["api_key"]} / {PROVIDERS[settings["provider"]]["key_env"]}；不要把密钥贴到对话中。')
    generator = GENERATORS[settings['provider']]
    generated, failed = [], []
    for entry in entries:
        target = root / entry['file']
        print(f'生成第 {entry["page"]} 页 · {entry["title"]} → {entry["file"]}（{entry["ratio"]}）', file=sys.stderr)
        try:
            data, size = generator(settings, entry, reference if with_reference else None, args.retries)
            data, note = fit_to_ratio(data, entry['ratio'], entry.get('paper', manifest.get('paper', '#F7F6F2')), settings['fit'], target.suffix)
            mime, _ = read_raster_bytes(data)
            width, height = image_size(mime, data)
        except PermissionError:
            raise
        except (RuntimeError, ValueError, ConnectionError) as exc:
            failed.append({'page': entry['page'], 'file': entry['file'], 'error': str(exc)})
            entry['status'] = 'missing'
            entry['error'] = str(exc)
            print(f'  失败：{exc}', file=sys.stderr)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_file():
            previous = next_version(target)
            target.rename(previous)
            entry['previous_file'] = str(previous.relative_to(root))
        target.write_bytes(data)
        entry.update(status='generated', method=f'api:{settings["provider"]}/{settings["model"]}', request_size=size,
                     pixels=f'{width}x{height}', generated_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                     reference_used=with_reference)
        entry.pop('error', None)
        if note:
            entry['note'] = note
        generated.append({'page': entry['page'], 'file': entry['file'], 'pixels': f'{width}x{height}', 'note': note})
        print(f'  已保存 {entry["file"]}（{width}×{height}）' + (f'；{note}' if note else ''), file=sys.stderr)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    remaining = [e['file'] for e in manifest['images'] if not (root / e['file']).is_file()]
    print(json.dumps(dict(plan, generated=generated, failed=failed, remaining_missing=remaining, manifest=str(manifest_path),
                          next='逐张查看生成结果，核对对象数量、层级与纸色；必要时 match_paper.py --dry-run，再构建。'), ensure_ascii=False, indent=2))
    return 1 if failed else 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('deck', nargs='?', help='项目 deck.json；生成其清单中的缺图')
    p.add_argument('--handoff', help='prepare_images.py 的输出目录（默认 deck 同级 image-handoff）')
    p.add_argument('--pages', help='只生成这些页码，逗号分隔')
    p.add_argument('--force', action='store_true', help='重生成已有图片；原图改名为 -vN 保留')
    p.add_argument('--dry-run', action='store_true', help='只列出将要发起的请求，不调用 API、不需要密钥')
    p.add_argument('--retries', type=int, default=2, help='限流或服务错误时的重试次数（默认 2）')
    p.add_argument('--config', help=f'配置文件路径（默认 {DEFAULT_CONFIG}，或环境变量 {CONFIG_ENV}）')
    p.add_argument('--setup', action='store_true', help='写入 provider/url/model，并在交互终端中读取 API Key')
    p.add_argument('--check', action='store_true', help='验证配置与连通性，不生图')
    p.add_argument('--provider', choices=sorted(PROVIDERS))
    p.add_argument('--preset', choices=sorted(PRESETS), help='--setup 时套用中转服务预设（基址、异步任务、参考图方式），再用 --model 指定模型')
    p.add_argument('--url', help='API 基址，例如 https://api.openai.com/v1')
    p.add_argument('--model', help='图像模型名，例如 gpt-image-1 或 gemini-2.5-flash-image')
    p.add_argument('--reference', choices=REFERENCE_MODES, help='是否随提示词附上风格参考图（默认 auto）')
    p.add_argument('--fit', choices=FIT_MODES, help='结果不符合清单比例时用纸色补边（pad，默认）或保留原样（none）')
    p.add_argument('--quality', help='OpenAI 兼容接口的 quality 参数，例如 high / medium / low / standard / hd')
    p.add_argument('--image-size', dest='image_size', help='部分中转服务的 imageSize 参数，例如 1K / 2K / 4K')
    p.add_argument('--timeout', type=float, help='单次请求超时秒数（默认 180）')
    p.add_argument('--key-env', help='--setup 时记录密钥所在环境变量名，而不保存密钥本身')
    p.add_argument('--no-key', action='store_true', help='--setup 时不读取密钥')
    args = p.parse_args(argv)
    try:
        if args.setup:
            setup(args)
            return 0
        if args.check:
            settings = resolve_settings(args)
            state, message = ('fail', f'缺少 API Key；请用户在终端运行 --setup 或设置 {ENV["api_key"]}') if not settings['api_key'] else check_connection(settings)
            print(json.dumps({'status': state, 'message': message, 'provider': settings['provider'], 'url': settings['url'], 'model': settings['model'],
                              'api_key': masked(settings['api_key']), 'api_key_source': settings.get('api_key_source'), 'config': settings['config_path']}, ensure_ascii=False, indent=2))
            return 0 if state != 'fail' else 1
        if not args.deck:
            p.error('需要 deck.json 路径，或使用 --setup / --check')
        return generate(args)
    except (ValueError, OSError, PermissionError, ConnectionError, RuntimeError) as exc:
        print(f'生图失败：{exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
