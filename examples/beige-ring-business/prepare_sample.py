#!/usr/bin/env python3
"""Prepare original assets and a fictional ten-page style-development example."""
import argparse
import copy
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PACK = REPO / 'skills/beige-ring-business-slides'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--generated-dir', type=Path, help='Optional original-image directory; otherwise reuse packaged WebP assets')
GENERATED = parser.parse_args().generated_dir
FILES = {
    'workspace': 'exec-5d90f301-2d0b-4539-a4f6-cdd7deff2d7d.png',
    'architecture': 'exec-47c98873-6cd0-456b-901f-59bed61fca2d.png',
    'portrait-lin': 'exec-af1716b1-413a-4c8e-ae59-27901f99ab37.png',
    'portrait-zhou': 'exec-dd95036b-6ed0-49eb-9ba1-31c75fef2b21.png',
    'portrait-xu': 'exec-376db1de-3303-47b8-81a9-6f273856fc87.png',
    'portrait-chen': 'exec-62574346-6b93-416f-8a96-22f8289eaa65.png',
    'portrait-wu': 'exec-56e1e0d4-ebe6-499e-8043-a9925255dcfd.png',
    'channel-space': 'exec-42f206b4-dfb5-4a20-b4f3-b0ccdc64fda6.png',
    'channel-content': 'exec-0d108ed5-b98a-401a-b976-b2f6071e3cf6.png',
    'channel-community': 'exec-fe776029-80d1-4572-a1f4-9b1f17870b77.png',
}
ASSETS = PACK / 'assets'
(ASSETS / 'images').mkdir(parents=True, exist_ok=True)
manifest = []
for key, filename in FILES.items():
    source = GENERATED / filename if GENERATED else None
    target = ASSETS / 'images' / (key + '.webp')
    if source is not None:
        with Image.open(source) as im:
            im.convert('RGB').save(target, 'WEBP', quality=88, method=6)
    elif not target.is_file():
        raise FileNotFoundError(f'Missing {target}; provide --generated-dir for original images')
    manifest.append({'id': key, 'generator': 'built-in image_gen', 'original': filename,
                     'asset': str(target.relative_to(REPO)), 'rights_note': 'Original generated fictional scene or person; no Canva photograph reused.'})
(ROOT / 'image-sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

def image(key, alt, ratio='1:1'):
    return {'src': 'images/' + key + '.webp', 'alt': alt + '，原创生成示例', 'ratio': ratio,
            'brief': {'subject': alt, 'action': '自然商务场景或独立人物肖像',
                      'structure': '单幅完整摄影，不含文字、标识或信息图',
                      'details': '米色石材、浅橡木、柔和日光与自然肤色',
                      'composition': '方形安全裁切' if ratio == '1:1' else '横幅主体与真实环境'}}

slides = [
    {'layout': 'cover', 'title': '2026 年度\n营销计划', 'subtitle': '让灵活办公，成为团队的日常选择',
     'description': '虚构品牌与数据示例', 'date': '', 'credits': [
         {'title': '方案出品', 'text': '回环办公 · 品牌团队'},
         {'title': '汇报对象', 'text': '运营与渠道伙伴'}]},
    {'layout': 'side_index', 'title': '计划目录', 'items': [
        {'label': f'{n:02}', 'title': title} for n, title in enumerate([
            '营销目标', '用户画像', '执行节奏', '预算分配', '核心团队', '传播渠道', '营销组合', '衡量成效'], 3)]},
    {'layout': 'reading', 'composition': 'half_diagonal', 'title': '让体验带动增长',
     'summary': '从真实办公需求出发，连接空间体验与长期关系。',
     'images': [image('workspace', '主理人在自然采光的办公空间审阅材料', '4:3'),
                image('architecture', '石材与玻璃构成的现代办公建筑')],
     'blocks': [
         {'type': 'facts', 'title': '品牌主张', 'rows': [
             {'label': '目标人群', 'text': '重视协作的成长型小团队'},
             {'label': '核心价值', 'text': '自在办公，灵活共创'}]},
         {'type': 'facts', 'title': '三项行动目标', 'rows': [
             {'label': '看见品牌', 'text': '用真实场景建立清晰认知'},
             {'label': '走进空间', 'text': '将线上兴趣转为线下体验'},
             {'label': '持续连接', 'text': '让成员成为社区的一部分'}]}]},
    {'layout': 'hub_spoke', 'title': '我们服务谁', 'subtitle': '从工作方式理解需求，形成一致的品牌体验',
     'center': {'title': '成长型\n小团队', 'text': '用户画像示例'},
     'items': [{'title': title, 'text': text} for title, text in [
         ('团队阶段', '初创与稳步成长'), ('工作习惯', '混合办公与协作'), ('价值偏好', '品质与灵活并重'), ('关注渠道', '内容与同行推荐'),
         ('空间需求', '专注与交流共存'), ('体验期待', '轻松进入工作状态'), ('决策考量', '成本清楚易调整'), ('关系诉求', '可信赖的社区')]]},
    {'layout': 'step_row', 'title': '四个月，循序推进',
     'steps': [{'title': title, 'period': period, 'text': text} for title, period, text in [
         ('准备期', '一月', '完成用户访谈与素材准备，统一品牌表达。'),
         ('预热期', '二月', '发布空间故事，邀请种子用户预约参访。'),
         ('体验期', '三月', '开展开放日与主题共创，收集体验反馈。'),
         ('优化期', '四月', '复盘渠道表现，沉淀有效内容与社区机制。')]],
     'note': '时间为风格样稿的虚构计划，不代表真实项目排期。'},
    {'layout': 'chart_focus', 'title': '把预算投入\n有效体验',
     'copy': '先让用户理解，再让体验发生。\n围绕内容、触达与社区投入。\n按月复盘，保留调整空间。',
     'stat': {'value': '60 万元', 'label': '计划预算 · 假设示例'},
     'chart': {'title': '预算分配示例', 'chart_type': 'pie',
               'categories': ['内容制作', '渠道推广', '空间活动', '社区运营', '研究复盘'],
               'series': [{'name': '预算', 'values': [18, 15, 12, 9, 6]}], 'unit': '万元',
               'source': '来源：虚构营销计划假设；合计 60 万元，非真实经营数据。'},
     'conclusion': '内容与触达占 55%，其余用于体验、社区与复盘。'},
    {'layout': 'editorial_columns', 'title': '一起，把计划落地', 'columns': [
        {'type': 'people', 'items': [{'name': name, 'role': role, 'image': image(key, name + '的虚构团队肖像')}]} for key, name, role in [
            ('portrait-lin', '林予安', '品牌统筹'), ('portrait-zhou', '周明远', '策略研究'),
            ('portrait-xu', '许一宁', '内容传播'), ('portrait-chen', '陈以恒', '空间体验'),
            ('portrait-wu', '吴知夏', '社区运营')]]},
    {'layout': 'service_cards', 'title': '三条路径，连接用户', 'highlight': 0,
     'items': [
         {'title': '空间体验', 'text': '以开放日和预约参访，让用户亲自感受空间的光线、动线与协作氛围。',
          'image': image('channel-space', '自然日光下的办公空间与木质工作桌', '4:3')},
         {'title': '内容传播', 'text': '记录工作日常与空间细节，把品牌价值变成可感知、可分享的故事。',
          'image': image('channel-content', '团队共同查看材质样本的工作细节', '4:3')},
         {'title': '社区连接', 'text': '通过主题交流与小型共创，帮助成员认识彼此，并建立持续关系。',
          'image': image('channel-community', '三位成员在材料工作桌旁自然交流', '4:3')}]},
    {'layout': 'table', 'title': '营销组合', 'columns': ['产品体验', '价格策略', '渠道触达', '品牌传播'],
     'rows': [['灵活工位', '清晰分级', '品牌官网', '空间故事'],
              ['协作空间', '月度选择', '内容平台', '成员访谈'],
              ['开放活动', '体验入口', '合作社群', '主题开放日'],
              ['社区服务', '团队方案', '用户推荐', '共创与分享']]},
    {'layout': 'metric_cards', 'title': '用三个信号，衡量成效',
     'metrics': [{'label': label, 'progress': {'value': value, 'max': maximum}, 'text': text} for label, value, maximum, text in [
         ('有效触达', 7700, 10000, '观察内容是否到达目标人群，识别持续增长的内容线索。'),
         ('预约体验', 54, 100, '关注从兴趣到行动的转化，持续优化预约与参访体验。'),
         ('社区参与', 24, 100, '持续追踪体验后的参与意愿，建立稳定而有温度的连接。')]],
     'source': '来源：虚构阶段性示例；百分比为当前值 ÷ 目标值。'}
]
metadata = [
    ('cover.fixed', 'cover', 1, 0, 'cover', 'none'),
    ('shared.side_index', 'agenda', 8, 0, 'briefing', 'open'),
    ('reading.half_diagonal', 'mixed', 2, 2, 'briefing', 'open'),
    ('shared.hub_spoke', 'network', 8, 0, 'explanation', 'open'),
    ('shared.step_row', 'timeline', 4, 0, 'process', 'open'),
    ('shared.chart_focus', 'data', 5, 0, 'briefing', 'open'),
    ('shared.editorial_people', 'team', 5, 5, 'explanation', 'open'),
    ('shared.service_cards', 'parallel', 3, 3, 'capabilities', 'open'),
    ('table.matrix', 'table', 4, 0, 'comparison', 'open'),
    ('shared.metric_cards', 'statistics', 3, 0, 'comparison', 'open')
]
for i, (s, data) in enumerate(zip(slides, metadata), 1):
    profile, relation, count, nimages, role, treatment = data
    s.update(id=f'p{i:02}', notes='风格开发样稿。回环办公、所有人物姓名、项目计划及数字均为虚构示例。照片由内置 imagegen 原创生成，不代表真实客户、团队或经营成果。',
             visual={'role': role, 'treatment': treatment, 'rationale': '按本页内容关系采用可编辑共享结构，米白纸面与细线圆环组织清晰的商务信息。', 'requirements': []},
             layout_intent={'relation': relation, 'item_count': count, 'media': {'count': nimages, 'status': 'provided' if nimages else 'unavailable'}},
             layout_selection={'version': 1, 'profile': profile, 'source_ids': []})
    if relation == 'mixed': s['layout_intent']['block_types'] = ['facts', 'facts']
    if relation == 'table': s['layout_intent']['column_count'] = len(s['columns'])
    if relation == 'timeline': s['layout_intent']['periods'] = [step['period'] for step in s['steps']]
deck = {'title': '米白环线商务 · 中文风格样稿', 'style': 'beige-ring-business', 'presentation_mode': 'speech',
        'company': '回环办公', 'year': '2026', 'footer_label': '虚构风格样稿', 'slides': slides}
(ASSETS / 'deck.example.json').write_text(json.dumps(deck, ensure_ascii=False, indent=2) + '\n')
reading = copy.deepcopy(deck)
reading['presentation_mode'] = 'reading'
reading['title'] = '米白环线商务 · 阅读型样例'
reading['slides'][7]['items'][0]['text'] += '每次参访记录需求与疑问，为后续服务提供依据。'
reading['slides'][7]['items'][1]['text'] += '按使用情景组织内容，帮助读者理解具体价值。'
reading['slides'][7]['items'][2]['text'] += '以参与质量和成员反馈评价活动，保持适当节奏。'
(ASSETS / 'deck.reading.example.json').write_text(json.dumps(reading, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'slides': len(slides), 'original_assets': len(manifest)}, ensure_ascii=False))
