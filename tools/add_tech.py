#!/usr/bin/env python3
"""依品名／特殊素材／概述／成分判斷每個款號用到的機能素材，寫入 data.js：
  tg   = [[標章名, 中文簡述, 中文說明], ...]（款卡顯示用）
  tech = 同內容的純文字（Excel「材質與科技」欄）
  fab  = 成分中文化（保留原文）
用法：python3 tools/add_tech.py data.js   （可重複執行）"""
import re, json, sys

D = {  # key: (標章名, 簡述, 說明)
 'GTX_PRO3L': ('GORE-TEX PRO 3L','防水透氣・專業級','三層貼合結構（外布＋防水透氣膜＋內層合為一體）。GORE-TEX 最耐用、透氣性最好的等級，給長時間待在惡劣天候的登山者使用，附「保證讓您乾爽」承諾。'),
 'GTX_3L':    ('GORE-TEX 3L','防水透氣・三層貼合','三層貼合結構，外布、防水透氣膜、內層貼合成一體，沒有鬆散內裡，比 2L 輕、耐用、透氣。持久防水、完全防風。'),
 'GTX_2L':    ('GORE-TEX 2L','防水透氣・兩層','兩層結構：外布與防水透氣膜貼合，內側另加獨立內裡。穿起來柔軟、適合日常與雪地使用。持久防水、完全防風。'),
 'GTX':       ('GORE-TEX','防水透氣','防水透氣膜：持久防水、完全防風，同時讓汗氣排出，濕冷天氣也不悶。'),
 'GTX_SHOE':  ('GORE-TEX 鞋款','防水透氣內襯','鞋內襯使用 GORE-TEX 防水透氣膜，防水、防風，同時讓腳汗氣散出。'),
 'GTX_INVIS': ('GORE-TEX INVISIBLE FIT','防水透氣・內襯貼合鞋面','GORE-TEX 鞋款技術：防水透氣膜與鞋面直接貼合，不另加內套，鞋身較輕、貼腳。'),
 'WSP':       ('GORE-TEX WINDSTOPPER','全防風・透氣保暖','正式名 WINDSTOPPER by GORE-TEX LABS（前稱 GORE-TEX INFINIUM）：持久防風、透氣、保暖舒適，適合多風寒冷或陣雨天氣；不保證完全防水。'),
 'PT_ALPHA':  ('POLARTEC ALPHA','主動保暖層','美國 Polartec 的主動式保暖（Active Insulation）：開放網格結構，保暖又極度透氣，運動中不悶熱，也不必常常穿脫。型號後的數字為 Alpha 系列規格。'),
 'PT_DELTA':  ('POLARTEC DELTA','涼感排汗','美國 Polartec 貼身針織：疏水與親水紗線並用，增加透氣、減少濕黏貼身、加快汗水蒸發，天熱也保持涼爽。'),
 'PT_GRID':   ('POLARTEC POWER GRID','輕量保暖透氣','美國 Polartec 雙組成針織：輕量、不厚重卻有保暖效果，透氣好、排汗佳，適合內層或運動時穿。'),
 'PT_DRY':    ('POLARTEC POWER DRY','貼身排汗速乾','美國 Polartec 貼身排汗布：雙組成針織、排汗力強、輕量、快乾，貼身穿著舒適。'),
 'PT_STRETCH':('POLARTEC POWER STRETCH','四向彈性','美國 Polartec 雙面針織：四向彈性、保形、透氣、排汗、快乾，動作不受限。'),
 'PT_TP':     ('POLARTEC THERMAL PRO','柔軟保暖刷毛','美國 Polartec 保暖刷毛系列：柔軟、保暖、透氣、耐用。'),
 'PT_FLEECE': ('POLARTEC FLEECE','刷毛保暖','美國 Polartec 刷毛布料：柔軟保暖，用於中層或單穿。'),
 'PT_GEN':    ('POLARTEC','機能布料','美國 Polartec 機能布料，依系列分為排汗、保暖、透氣等。'),
 'PERTEX':    ('PERTEX','輕量防風・抗潑水','英國 Pertex 高密度輕量布料：輕、柔軟、有抗潑水處理，常用於輕量外套與羽絨表布（依系列另有防風、防水款）。'),
 'PRIMALOFT': ('PRIMALOFT','合成保暖棉','PrimaLoft 超細纖維合成保暖棉（原為美軍開發）：濕了仍保暖、快乾、防潑水、可壓縮收納。'),
 'GLOFT':     ('G-LOFT Si','合成保暖填充','G-LOFT Si 合成纖維保暖填充：不吸濕，濕冷環境保暖力穩定，有形狀記憶、洗後仍蓬鬆，輕量好收納。'),
 'DOWN':      ('羽絨 DOWN','羽絨保暖','羽絨保暖填充。「90/10」是 90% 絨＋10% 羽毛；FP 是蓬鬆度（Fill Power），數字越高越輕、保暖效率越好。'),
 'CORDURA':   ('CORDURA','高耐磨尼龍','高強度耐磨尼龍布（INVISTA 出品）：耐磨、耐撕裂、耐用，常用於背包、褲子膝臀等容易摩擦處，質輕且多有抗潑水處理。'),
 'DYNEEMA':   ('DYNEEMA','超輕高強度纖維','超高分子量聚乙烯（UHMWPE）纖維：同重量下強度約為鋼的 15 倍，輕到可浮在水面，耐磨耐撕裂，織入布料可大幅提高耐用度。'),
 'SCHOELLER': ('SCHOELLER','瑞士彈性機能布','瑞士 Schoeller 單層機能梭織布：彈性、舒適、耐用，是登山褲、軟殼常用的布料。'),
 'MERINO':    ('MERINO 美麗諾羊毛','保暖吸濕不易臭','美麗諾羊毛：纖維細軟親膚、保暖、吸濕透氣，穿久不易有異味。'),
 'VIBRAM':    ('VIBRAM 大底','抓地耐磨','義大利 Vibram 橡膠大底：抓地力強、耐磨，常用於登山與越野鞋款。'),
}
ORDER = ['GTX_PRO3L','GTX_3L','GTX_2L','GTX','GTX_SHOE','GTX_INVIS','WSP','PT_ALPHA','PT_DELTA','PT_GRID','PT_DRY','PT_STRETCH','PT_TP','PT_FLEECE','PT_GEN','PERTEX','PRIMALOFT','GLOFT','DOWN','CORDURA','DYNEEMA','SCHOELLER','MERINO','VIBRAM']

def down_desc(T):
    fp = re.search(r'FP\s?(\d{3})', T)
    typ = '鵝絨' if '鵝絨' in T else ('鴨絨' if '鴨絨' in T else '')
    r = re.search(r'(\d{2})\s?[/:]\s?(\d{2})', T)
    parts = []
    if typ: parts.append(typ)
    if r and int(r.group(1)) + int(r.group(2)) == 100: parts.append(f'{r.group(1)}/{r.group(2)}（{r.group(1)}% 絨＋{r.group(2)}% 羽毛）')
    if fp: parts.append(f'蓬鬆度 FP{fp.group(1)}')
    short = ' '.join([typ] + ([f'FP{fp.group(1)}'] if fp else []) + ([f'{r.group(1)}/{r.group(2)}'] if r else [])).strip() or '羽絨保暖'
    spec = '、'.join(parts)
    base = D['DOWN'][2]
    return short, (f'本款：{spec}。' if spec else '') + base

def detect(items):
    icon = ' '.join(i.get('icon') or '' for i in items).upper()
    non = ' '.join(' '.join([i.get('en') or '', i.get('zh') or '', i.get('ov') or '', i.get('fab') or '']) for i in items)
    NON = non.upper(); T = icon + ' ' + NON
    shoe = any(i.get('sheet') == '鞋款' for i in items)
    keys = []
    wsp = bool(re.search(r'WINDSTOPPER|\bWSP\b', T))
    plain_pat = r'GORE[- ]?TEX(?![ \-]*(?:WSP|WINDSTOPPER))|GTX'
    plain = bool(re.search(plain_pat, NON)) or ('GORE-TEX' in icon and not wsp)
    if wsp and 'GORE-TEX' in icon and not re.search(r'GORE[- ]?TEX[ \-]*(?:WSP|WINDSTOPPER)', NON) and re.search(plain_pat, NON): plain = True
    if plain:
        if shoe: keys.append('GTX_SHOE')
        elif re.search(r'\bPRO\b', NON): keys.append('GTX_PRO3L')
        elif re.search(r'\b3L\b', NON): keys.append('GTX_3L')
        elif re.search(r'\b2L\b', NON): keys.append('GTX_2L')
        else: keys.append('GTX')
        if 'INVISIBLE FIT' in NON: keys.append('GTX_INVIS')
    if wsp: keys.append('WSP')
    if 'POLARTEC' in T:
        sub = []
        if re.search(r'ALPHA', T): sub.append('PT_ALPHA')
        if 'DELTA' in T: sub.append('PT_DELTA')
        if 'POWER GRID' in T: sub.append('PT_GRID')
        if 'POWER DRY' in T: sub.append('PT_DRY')
        if 'POWER STRETCH' in T: sub.append('PT_STRETCH')
        if 'THERMAL PRO' in T: sub.append('PT_TP')
        if not sub and re.search(r'FLEECE|刷毛', T): sub.append('PT_FLEECE')
        keys += sub or ['PT_GEN']
    if 'PERTEX' in T: keys.append('PERTEX')
    if 'PRIMALOFT' in T: keys.append('PRIMALOFT')
    if re.search(r'G-?LOFT', T): keys.append('GLOFT')
    if re.search(r'\bDOWN\b|絨|\bFP\d{3}\b', non, re.I) and not re.search(r'DOWNPROOF', T): keys.append('DOWN')
    if 'CORDURA' in T: keys.append('CORDURA')
    if 'DYNEEMA' in T: keys.append('DYNEEMA')
    if 'SCHOELLER' in T: keys.append('SCHOELLER')
    if re.search(r'MERINO|美麗諾', T): keys.append('MERINO')
    if 'VIBRAM' in T: keys.append('VIBRAM')
    return [k for k in ORDER if k in keys], T, non

FIB = [('Merino Wool','美麗諾羊毛'),('Goat Leather','山羊皮'),('Synthetic Rubber','合成橡膠'),('Polyurethane(TPU Film)','聚氨酯 PU（TPU 膜）'),
 ('Polyurethane','聚氨酯 PU'),('Polyuretane','聚氨酯 PU'),('Polyester','聚酯纖維'),('Polyethylene','聚乙烯'),('Nylon','尼龍'),('Mylon','尼龍（原廠寫 Mylon）'),
 ('Acrylic','壓克力纖維'),('Wool','羊毛'),('Cotton','棉'),('Modal','莫代爾'),('Tencell','天絲 Tencel'),('Rayon','嫘縈'),('Spandex','彈性纖維 Spandex'),
 ('Span','彈性纖維 Spandex'),('Leather','皮革'),('Gore-tex','GORE-TEX'),('Phylon','Phylon 中底'),('TPU','TPU')]
LAB = [('[UPPER]','鞋面'),('[LINING]','鞋內裡'),('[SOLE]','鞋底'),('Material','材質'),('Contrast','拼接'),('Shell','外層'),('Sell','外層'),('Lining','內裡'),('Filling','填充'),('Thumb','拇指'),('Palm','掌心')]
def fab_zh(s):
    o = s
    for a, b in LAB: o = o.replace(a, '\0' + b + '\0')
    for a, b in FIB: o = re.sub(re.escape(a) + r'(?![A-Za-z])', b, o)
    o = o.replace('\0', '')
    return re.sub(r'[ \t]+', ' ', o).replace(' :', '：').replace(': ', '：').replace(':', '：').strip()

def common(a,b):
    n=0
    for x,y in zip(a,b):
        if x!=y: break
        n+=1
    return n

def pick_similar(st, its, pool):
    """pool: {style: (items, value)}；回傳最相近款的 value 與款號（同分頁、同品類為底線）"""
    me=its[0]; best=None
    for s2,(its2,val) in pool.items():
        o=its2[0]
        if o['sheet']!=me['sheet'] or o['cat']!=me['cat']: continue
        sc=(4 if o['en'] and o['en']==me['en'] else 0)+(2 if o['mon']==me['mon'] else 0)+(1 if o['gen']==me['gen'] else 0)
        key=(sc, common(st,s2))
        if best is None or key>best[0]: best=(key,s2,val)
    return (best[2],best[1]) if best else (None,None)

def run(path):
    s = open(path).read()
    m = re.match(r'(window\.SDR_ITEMS=)(\[.*?\])(;\s*window.*)$', s, re.S)
    items = json.loads(m.group(2)); by = {}
    for i in items: by.setdefault(i['style'], []).append(i)
    n_tg = 0; det = {st: detect(its) for st, its in by.items()}; borrowed = []
    GEN = {'GTX':['GTX_PRO3L','GTX_3L','GTX_2L'], 'PT_GEN':['PT_ALPHA','PT_DELTA','PT_GRID','PT_DRY','PT_STRETCH','PT_TP','PT_FLEECE']}
    for g, specs in GEN.items():
        pool = {st: (by[st], [k for k in d[0] if k in specs][0]) for st, d in det.items() if any(k in specs for k in d[0])}
        for st, (keys, T, non) in det.items():
            if g in keys:
                v, src = pick_similar(st, by[st], pool)
                if v: keys[keys.index(g)] = v; borrowed.append((st, g, v, src))
    dpool = {}
    for st, (keys, T, non) in det.items():
        if 'DOWN' in keys and re.search(r'FP\s?\d{3}|鵝絨|鴨絨', non): dpool[st] = (by[st], non)
    for st, (keys, T, non) in list(det.items()):
        if 'DOWN' in keys and not re.search(r'FP\s?\d{3}|鵝絨|鴨絨', non):
            v, src = pick_similar(st, by[st], dpool)
            if v: det[st] = (keys, T, v); borrowed.append((st, 'DOWN', '', src))
    for st, its in by.items():
        keys, T, non = det[st]
        tg = []
        for k in keys:
            n, sh, d = D[k]
            if k == 'DOWN': sh, d = down_desc(non)
            tg.append([n, sh, d])
        n_tg += bool(tg)
        for i in its:
            if tg: i['tg'] = tg; i['tech'] = '\n'.join(f'{a}（{b}）：{c}' for a, b, c in tg)
            else: i.pop('tg', None); i['tech'] = ''
            f = i.get('fab') or ''
            if '\n原文：' in f: f = f.split('\n原文：', 1)[1]
            i['fab'] = (fab_zh(f) + '\n原文：' + f) if f else ''
    open(path, 'w').write(m.group(1) + json.dumps(items, ensure_ascii=False) + m.group(3))
    print(path, 'styles', len(by), 'with 機能素材', n_tg)
    for b in borrowed: print('  借相近款', b)

if __name__ == '__main__':
    for p in sys.argv[1:]: run(p)
