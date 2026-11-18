#!/usr/bin/env python3
"""把原廠 27FW 整合策略簡報（Visual Strategy ZH）裡款名對得上的商品資訊寫進 data.js 的 info 欄（商品資訊）。
只放商品本身資訊（材質、規格、機能、搭配），不放價格與銷售數字。對不上的內容放 story.js。
重跑安全：每次先清掉 info 再寫。用法：python3 tools/add_pdf_info.py
注意：gen_fw2.py 重產 data.js 後要再跑一次。"""
import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')
s = open('data.js', encoding='utf-8').read()
i = s.find('window.SDR_ITEMS='); j = s.find('];', i) + 1
head, tail = s[:i], s[j:]
items = json.loads(s[i + len('window.SDR_ITEMS='):j])

def has(it, *keys):
    t = ' '.join([it['zh'], it['en'], it['style']]).upper()
    return any(k.upper() in t for k in keys)

DNS = lambda it: it['mon'] == 'DNS 頂規線'
RULES = [
    (lambda it: has(it, 'HIMA', 'ALAYA'), [
        'Hima & Alaya：消費者熟悉的冬季羽絨版型，這季保留經典設計，修正版型與細節。']),
    (lambda it: it['mon'] == 'TOUGH SHIELD' or has(it, 'TOUGH SHIELD', 'TOUGHSHIELD'), [
        'Tough Shield：從長褲擴大成整套穿搭，外層、中層、內層互相搭配；立體剪裁、耐用布料。',
        '原廠秋季健行搭配：Javari GTX 外套＋EXUM GTX 快速健行鞋。']),
    (lambda it: has(it, 'STONE MASTER', 'STONEMASTER'), [
        'Stone Master：攀岩出身的保暖系列，訴求輕、暖，也適合冬季日常；原廠材質方向為 10D 布料搭配石墨烯相關材質，有女款專屬版型。',
        '原廠冬季活動搭配：LV2 帽子手套＋LOAF 鞋款。']),
    (lambda it: DNS(it) and it['cat'] == 'GORE-TEX外套' or (DNS(it) and has(it, 'GORE-TEX') and it['sheet'] == '下身'), [
        'DNS 洋蔥式系列的外層／防護：GORE-TEX 硬殼，擋風雨。',
        '內搭 DNS 保暖層，寒冷時再加厚羽絨。']),
    (lambda it: DNS(it) and has(it, 'LANGAR'), [
        'DNS 洋蔥式系列的保暖層：Langar 依活動強度設計，活動中保暖不悶。',
        '外面可加 GORE-TEX 硬殼外套。']),
    (lambda it: DNS(it) and has(it, 'TILICHO', 'WATUSI', 'YURINO'), [
        'DNS 洋蔥式系列的厚羽絨／高山層：源自遠征規格的羽絨，為高山打造的保暖。']),
    (lambda it: has(it, 'DYNEEMA') and it['sheet'] == '上身', [
        'Dyneema 羽絨：DNS 頂規線的高山保暖款，原廠寒冷高山搭配 LV3 配件與 YAK LOAD PRO。']),
    (lambda it: DNS(it) and has(it, 'TERI'), [
        'DNS 頂規線的中層：可搭 GORE-TEX 硬殼外層組成洋蔥式穿搭。']),
    (lambda it: has(it, 'YAK HORN'), [
        'YAK HORN：BLACK YAK 經典登山包系列，這季翻新。',
        '原廠秋季健行搭配：Javari GTX＋Tough Shield 服裝、EXUM GTX 鞋。']),
    (lambda it: has(it, 'MODULAR'), [
        '模組背包：外掛系統，可依需要擴充容量與裝備。']),
    (lambda it: has(it, 'DNS UL'), [
        'DNS UL：技術型背負，結構依登山用途設計。']),
    (lambda it: it['sheet'] == '配件' and it['mon'] == '手套' and has(it, 'WINDSTOPPER', 'GTX GLOVES'), [
        '手套用途：防風／活動保暖，擋風，健行與活動用。']),
    (lambda it: it['sheet'] == '配件' and it['mon'] == '手套' and has(it, 'PADDED', 'MITTEN'), [
        '手套用途：寒冷／多層搭配，厚保暖，可搭內層手套。']),
    (lambda it: it['sheet'] == '配件' and it['mon'] == '手套' and has(it, 'MERINO', 'POWER STRETCH GLOVES'), [
        '手套用途：輕量／日常，輕薄好活動，也可當內層手套。']),
    (lambda it: it['sheet'] == '鞋款' and has(it, 'EXUM'), [
        'EXUM GTX：Vibram 大底、Y-FRAME 支撐、CORDURA 鞋面，適合快速健行。',
        '配色和 Javari GTX、Tough Shield 服裝同步，可成套穿。']),
    (lambda it: it['sheet'] == '鞋款' and has(it, '343'), [
        '343 系列：BOA 旋鈕＋GORE-TEX 防水，穿脫與調整鬆緊都快。']),
    (lambda it: it['sheet'] == '鞋款' and has(it, 'LOAF'), [
        'LOAF：好穿脫，戶外到日常都適合。',
        '原廠冬季活動搭配：Stone Master＋LV2 配件。']),
]

n = 0
for it in items:
    lines = []
    for cond, txt in RULES:
        if cond(it):
            lines += [x for x in txt if x not in lines]
    if lines:
        it['info'] = '\n'.join(lines); n += 1
    else:
        it.pop('info', None)
open('data.js', 'w', encoding='utf-8').write(head + 'window.SDR_ITEMS=' + json.dumps(items, ensure_ascii=False) + tail)
print('款色', n, '款', len({it['style'] for it in items if it.get('info')}))
