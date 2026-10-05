"""Finite editorial layouts in the shared editable slide library.

This module owns field validation and semantic defaults, not a renderer or a
style registry. Every style can use these structures with its own visual theme.
"""

EDITORIAL_VARIANTS = ('cover', 'intro', 'contents', 'about', 'services', 'process', 'portfolio', 'closing')
EDITORIAL_ROLES = {'cover': 'cover', 'intro': 'explanation', 'contents': 'briefing',
                   'about': 'explanation', 'services': 'capabilities', 'process': 'process',
                   'portfolio': 'explanation', 'closing': 'closing'}
EDITORIAL_RATIOS = {'cover': '3:4', 'intro': '21:9', 'contents': '2:1', 'about': '3:4',
                    'services': '16:9', 'process': '21:9', 'portfolio': '3:4', 'closing': '3:4'}

COMMON_FIELDS = {'id', 'layout', 'editorial_variant', 'title', 'chapter', 'header', 'surface', 'notes', 'visual',
                 'title_size', 'body_size', 'layout_intent', 'layout_selection', '_number'}
CONTENT_FIELDS = {
    'cover': {'image', 'kicker', 'subtitle'},
    'intro': {'image', 'copy'},
    'contents': {'image', 'items', 'copy'},
    'about': {'image', 'lead', 'columns'},
    'services': {'images', 'items'},
    'process': {'image', 'items'},
    'portfolio': {'images', 'copy'},
    'closing': {'image', 'subtitle', 'copy'},
}
IMAGE_FIELDS = {'src', 'alt', 'caption', 'ratio', 'brief', 'ui_text', 'zoom', 'offset_x',
                'offset_y', 'edge_fade', 'background_mode'}


def editorial_variant(slide):
    variant = slide.get('editorial_variant')
    if not isinstance(variant, str) or variant not in EDITORIAL_VARIANTS:
        raise ValueError('editorial_variant 可选 ' + ' / '.join(EDITORIAL_VARIANTS))
    return variant


def editorial_images(slide):
    """Use one image everywhere except the services strip and portfolio gallery.

    All eight editorial variants need illustrations; the existing image-free
    cover/closing layouts remain available independently of these variants.
    """
    variant = editorial_variant(slide)
    if 'image' in slide and 'images' in slide:
        raise ValueError('image 与 images 只能选一个')
    if variant in {'services', 'portfolio'}:
        low, high = (1, 3) if variant == 'services' else (2, 6)
        images = slide.get('images')
        if 'image' in slide or not isinstance(images, list) or not low <= len(images) <= high:
            raise ValueError(f'editorial.{variant} 使用 images 对象数组，需要 {low}–{high} 张配图')
        return images
    if 'images' in slide or 'image' not in slide:
        raise ValueError(f'editorial.{variant} 需要一个 image 对象，不使用 images')
    return [slide['image']]


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} 必须是非空字符串')


def validate_editorial_slide(slide, pack=None):
    """Reject fields that a finite variant would otherwise silently discard."""
    variant = editorial_variant(slide)
    extra = set(slide) - COMMON_FIELDS - CONTENT_FIELDS[variant]
    if extra:
        raise ValueError(f'editorial.{variant} 不支持字段：' + ' / '.join(sorted(extra)))
    _text(slide.get('title'), 'title')
    for field in ('subtitle', 'copy', 'kicker', 'lead'):
        if field in slide:
            _text(slide[field], field)
    if variant == 'intro':
        _text(slide.get('copy'), 'editorial.intro.copy')
    if variant == 'about':
        _text(slide.get('lead'), 'editorial.about.lead')
        columns = slide.get('columns')
        if not isinstance(columns, list) or len(columns) != 2:
            raise ValueError('editorial.about.columns 需要恰好 2 段正文字符串')
        for index, column in enumerate(columns, 1):
            _text(column, f'editorial.about.columns[{index}]')
    if variant in {'contents', 'services', 'process'}:
        low, high = {'contents': (2, 8), 'services': (1, 3), 'process': (2, 5)}[variant]
        values = slide.get('items')
        if not isinstance(values, list) or not low <= len(values) <= high:
            raise ValueError(f'editorial.{variant}.items 需要 {low}–{high} 项')
        fields = {'title', 'label'} if variant == 'contents' else {'title', 'text'}
        for index, item in enumerate(values, 1):
            if not isinstance(item, dict):
                raise ValueError(f'editorial.{variant}.items[{index}] 必须为对象')
            if set(item) - fields:
                raise ValueError(f'editorial.{variant}.items[{index}] 不支持字段：' + ' / '.join(sorted(set(item) - fields)))
            for field in fields:
                _text(item.get(field), f'editorial.{variant}.items[{index}].{field}')
    visual = slide.get('visual')
    if isinstance(visual, dict) and visual.get('treatment', 'open') not in {'open', 'none'}:
        raise ValueError('editorial 的 visual.treatment 使用 open / none；此版式以平面图文和细线组织信息')
    for index, image in enumerate(editorial_images(slide), 1):
        if not isinstance(image, dict):
            raise ValueError('editorial 配图须为对象（含 src、alt）')
        extra = set(image) - IMAGE_FIELDS
        if extra:
            raise ValueError(f'editorial 配图 {index} 不支持字段：' + ' / '.join(sorted(extra)))
        for field in ('src', 'alt'):
            _text(image.get(field), f'editorial 配图 {index}.{field}')
        if 'caption' in image:
            _text(image['caption'], f'editorial 配图 {index}.caption')
    return variant
