#!/usr/bin/env python3
"""Prepare a fictional fifteen-page specimen; generated assets are already local."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACK = ROOT.parents[1] / 'skills/monochrome-marble-slides'
ASSETS = PACK / 'assets'


def image(key, alt, ratio='4:3'):
    return {'src': 'images/' + key + '.webp', 'alt': alt + '，原创生成示例', 'ratio': ratio,
            'brief': {'subject': alt, 'action': '自然商务场景、独立人物或天然石材纹理',
                      'structure': '单幅摄影，不含文字、标识或信息图',
                      'details': '自然肤色、真实日光与克制的中性色环境',
                      'composition': '按实际图框安全裁切，保留人物与物件完整轮廓'}}


def chart(title, values, unit='项', name='阶段目标'):
    return {'title': title, 'chart_type': 'line', 'categories': ['一月', '二月', '三月', '四月', '五月'],
            'series': [{'name': name, 'values': values}], 'unit': unit,
            'source': '来源：虚构业务计划假设，非真实经营数据。'}


slides = [
    {'layout': 'cover', 'title': '2026 年度\n业务计划',
     'subtitle': '砚序咨询 · 让每一步增长，都有清晰依据', 'date': ''},
    {'layout': 'side_index', 'title': '计划目录', 'surface': 'dark', 'items': [
        {'label': f'{i:02}', 'title': t} for i, t in enumerate([
            '执行摘要', '公司介绍', '核心团队', '行业观察', '阶段目标', '协作机制',
            '发展愿景', '产品服务', '服务能力', '市场策略', '资金规划', '财务目标'], 1)]},
    {'layout': 'type_poster', 'variant': 'statement', 'placement': 'bottom-left',
     'title': '以清晰判断，\n推动稳健增长',
     'copy': '砚序咨询是一家虚构的策略与设计顾问机构。\n本计划展示我们如何理解需求、建立方向并推动落地。\n从一次有依据的判断开始，让行动形成持续积累。'},
    {'layout': 'editorial_columns', 'title': '关于\n砚序咨询', 'title_column': 1, 'columns': [
        {'type': 'image', 'image': image('company', '顾问在明亮办公室使用笔记本电脑梳理计划', '3:4')},
        {'type': 'text', 'paragraphs': [
            '我们围绕品牌、产品与组织协作，为成长中的团队提供清晰的思考框架。',
            '将研究带进决策，将策略带进行动。每个项目都从真实问题出发，以可执行的成果收束。']} ]},
    {'layout': 'editorial_columns', 'title': '一起，\n把方向落实', 'surface': 'marble-light', 'columns': [
        {'type': 'text'},
        {'type': 'people', 'items': [
            {'image': image(key, name + '的虚构团队肖像', '1:1'), 'name': name, 'role': role}
            for key, name, role in [('portrait-lin', '林予安', '策略与研究'),
                                    ('portrait-zhou', '周明远', '品牌与设计'),
                                    ('portrait-shen', '沈知夏', '交付与协作')]]}]},
    {'layout': 'editorial_story', 'title': '变化之中，\n看见机会', 'surface': 'dark',
     'image': image('industry', '明亮玻璃办公室中的多人业务讨论', '16:9'), 'items': [
        {'title': '需求更加具体', 'text': '客户期待从抽象愿景走向明确任务，理解每项工作如何支持当前决策。'},
        {'title': '协作更加紧密', 'text': '研究、策略与执行需要共享语境，减少信息断层，让团队沿同一方向前进。'},
        {'title': '成果持续积累', 'text': '将项目中的经验整理为工具和方法，让一次合作留下可以继续使用的能力。'}]},
    {'layout': 'editorial_columns', 'title': '循序推进，建立增长基础', 'title_size': 94, 'columns': [
        {'type': 'chart', 'chart': chart('建立有效连接', [8, 12, 16, 22, 28], '次', '月度访谈'),
         'copy': '通过持续访谈理解客户情境，让新的服务方向有事实依据。'},
        {'type': 'chart', 'chart': chart('形成项目积累', [2, 3, 5, 6, 8], '个', '阶段项目'),
         'copy': '逐步扩展适合团队能力的项目类型，稳定交付节奏。'},
        {'type': 'chart', 'chart': chart('沉淀可用方法', [1, 2, 3, 5, 6], '套', '方法工具'),
         'copy': '把过程经验整理为可复用工具，支持下一次协作。'}]},
    {'layout': 'editorial_columns', 'title': '让协作\n形成合力', 'title_column': 1, 'columns': [
        {'type': 'groups', 'items': [
            {'icon': 'Search', 'title': '共同理解问题', 'text': '先确认背景、需求与限制，形成可以共享的问题定义。'},
            {'icon': 'Compass', 'title': '共同选择方向', 'text': '把判断依据讲清楚，让每个参与者理解取舍与优先级。'},
            {'icon': 'Handshake', 'title': '共同推进成果', 'text': '以清晰分工和阶段反馈，让策略逐步进入真实工作。'}]},
        {'type': 'text'}]},
    {'layout': 'type_poster', 'variant': 'statement', 'placement': 'center', 'surface': 'inset-dark',
     'title': '让复杂变得清晰，\n让行动更有方向。',
     'copy': '我们希望成为成长团队长期信赖的思考伙伴。\n以真诚的理解、独立的判断和持续的协作，\n帮助每一个值得推进的想法，稳步走向现实。'},
    {'layout': 'editorial_columns', 'title': '从研究出发，\n走向可用成果', 'surface': 'marble-light', 'title_size': 100, 'columns': [
        {'type': 'text', 'paragraphs': [
            '围绕关键业务问题，连接用户研究、品牌策略与服务设计。',
            '每项服务都以明确的问题定义开始，以团队能够使用的方案、工具与行动路径结束。']},
        {'type': 'image', 'image': image('service', '顾问在自然光下专注于研究工作', '3:4')}]},
    {'layout': 'editorial_columns', 'title': '五项能力，\n支撑完整服务', 'surface': 'marble-dark', 'title_size': 102, 'columns': [
        {'type': 'text'}, {'type': 'groups', 'items': [
            {'icon': icon, 'title': title} for icon, title in [
                ('Search', '用户与市场研究'), ('Compass', '品牌与业务策略'), ('Layers', '产品与服务设计'),
                ('Users', '团队共创与协作'), ('TrendingUp', '复盘与持续优化')]]}]},
    {'layout': 'editorial_columns', 'title': '用真实交流，\n建立长期连接', 'title_column': 1, 'title_size': 100, 'columns': [
        {'type': 'gallery', 'grid_columns': 1, 'images': [
            image('market-work', '顾问在落地窗前的工作桌开展资料研究', '16:9'),
            image('market-meet', '自然光下顾问与合作伙伴面对面交流', '16:9')]},
        {'type': 'text', 'paragraphs': [
            '以有价值的内容、开放的交流和可信赖的交付，建立客户对我们的理解。',
            '记录问题与方法，分享过程中的观察；通过小型共创活动认识伙伴，让联系在真实需求中持续。']}]},
    {'layout': 'metric_cards', 'title': '为长期建设，保留充足空间', 'surface': 'dark',
     'image': image('marble', '原创黑白天然大理石纹理', '3:4'),
     'metrics': [{'value': '300 万元', 'label': '资金规划示例', 'text': '支持团队建设、研究投入与服务发展。'},
                 {'value': '18 个月', 'label': '规划周期示例', 'text': '按阶段复盘投入与成果，保持调整空间。'}],
     'source': '来源：虚构计划假设，非融资承诺或真实财务数据。'},
    {'layout': 'chart_focus', 'title': '以稳健节奏，\n积累经营成果', 'title_size': 94,
     'copy': '按阶段观察收入与成本，\n以可持续的交付能力支持增长。\n所有数字仅用于展示图表样式。',
     'chart': {'title': '收入与成本假设', 'chart_type': 'line', 'categories': ['一季度', '二季度', '三季度', '四季度'],
               'series': [{'name': '收入', 'values': [40, 65, 85, 110]},
                          {'name': '成本', 'values': [45, 50, 58, 65]}], 'unit': '万元',
               'source': '来源：虚构年度计划假设，非真实财务数据。'}},
    {'layout': 'editorial_columns', 'title': '期待一起，\n开启新篇', 'surface': 'dark', 'columns': [
        {'type': 'text'}, {'type': 'groups', 'items': [
            {'title': '合作方向', 'text': '策略研究 · 品牌设计 · 团队共创'},
            {'title': '示例邮箱', 'text': 'hello@example.com'},
            {'title': '本次资料', 'text': '砚序咨询 · 2026 年度业务计划'}]}]}
]

metadata = [
    ('cover.fixed', 'cover', 1, 'cover'), ('shared.side_index', 'agenda', 12, 'briefing'),
    ('shared.type_poster', 'explanation', 1, 'briefing'), ('shared.editorial_columns', 'explanation', 2, 'explanation'),
    ('shared.editorial_people', 'team', 3, 'explanation'), ('shared.editorial_story', 'explanation', 3, 'explanation'),
    ('shared.editorial_charts', 'data', 3, 'comparison'), ('shared.editorial_columns', 'parallel', 2, 'explanation'),
    ('shared.type_poster', 'explanation', 1, 'briefing'), ('shared.editorial_columns', 'explanation', 2, 'capabilities'),
    ('shared.editorial_columns', 'parallel', 2, 'capabilities'), ('shared.editorial_gallery', 'gallery', 2, 'explanation'),
    ('shared.metric_cards', 'statistics', 2, 'briefing'), ('shared.chart_focus', 'data', 4, 'briefing'),
    ('shared.editorial_columns', 'contact', 2, 'closing')
]


def images_in(value):
    if isinstance(value, dict):
        if 'src' in value and 'alt' in value: return [value]
        return [i for v in value.values() for i in images_in(v)]
    return [i for v in value for i in images_in(v)] if isinstance(value, list) else []


for i, (slide, meta) in enumerate(zip(slides, metadata), 1):
    profile, relation, count, role = meta
    nimages = len(images_in(slide))
    slide.update(id=f'p{i:02}', notes='风格开发样稿。砚序咨询、人物姓名、业务计划及数字均为虚构示例。照片由内置 imagegen 原创生成，不代表真实客户、团队或经营成果。',
                 visual={'role': role, 'treatment': 'none' if i == 1 else 'open',
                         'rationale': '以黑白反转、大衬线字和自然摄影组织本页内容，使用共享可编辑结构承载信息。', 'requirements': []},
                 layout_intent={'relation': relation, 'item_count': count, 'media': {'count': nimages, 'status': 'provided' if nimages else 'unavailable'}},
                 layout_selection={'version': 1, 'profile': profile, 'source_ids': []})

deck = {'title': '黑白大理石商务 · 中文风格样稿', 'style': 'monochrome-marble', 'presentation_mode': 'speech',
        'company': '砚序咨询', 'year': '2026', 'footer_label': '虚构风格样稿', 'slides': slides}
(ASSETS / 'deck.example.json').write_text(json.dumps(deck, ensure_ascii=False, indent=2) + '\n')
reading = copy.deepcopy(deck)
reading['presentation_mode'] = 'reading'
reading['title'] = '黑白大理石商务 · 阅读型样稿'
for group, extra in zip(reading['slides'][7]['columns'][0]['items'], [
        '通过访谈与资料整理识别分歧，避免从未经验证的假设直接进入方案。',
        '以阶段讨论明确关键目标、需要验证的假设和下一步行动。',
        '在每次反馈后更新任务与责任人，确保项目成果可交接、可继续使用。']):
    group['text'] += extra
reading['slides'][11]['columns'][1]['paragraphs'].append('将有效的交流记录为后续行动，在适当的时间回应具体需求，逐步形成稳定的合作关系。')
(ASSETS / 'deck.reading.example.json').write_text(json.dumps(reading, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'slides': len(slides), 'image_placements': sum(len(images_in(s)) for s in slides),
                  'unique_images': len({im['src'] for s in slides for im in images_in(s)})}, ensure_ascii=False))
