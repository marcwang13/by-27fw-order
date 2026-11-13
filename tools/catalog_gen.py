"""BLACK YAK 27FW 訂單目錄（款卡版 A4）產生器。
用法：python3 catalog.py <data.js> <imgs.js> <out_dir>
產出 internal.html（陳列+清點版）與 customer.html（客戶版），再用 Chrome 轉 PDF。
"""
import json, re, sys, math, html, base64, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catalog_bj import load_bj, N, en_of

DATA, IMGS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
START_NO = 350
items = json.loads(re.search(r'window\.SDR_ITEMS=(\[.*?\]);\s*\n', open(DATA).read(), re.S).group(1))
cfg = json.loads(re.search(r'window\.BY_CFG=(\{.*?\});', open(DATA).read(), re.S).group(1))
s = open(IMGS).read(); IMG = json.loads(s[len('window.SDR_IMG='):].rstrip().rstrip(';'))
LOGO = 'data:image/png;base64,' + base64.b64encode(open('/tmp/ppt/logo_s.png', 'rb').read()).decode()

TIER = {('上身','ALPINE A'):'主力',('上身','ALPINE B'):'中等量',('上身','TOUGH SHIELD'):'主力',('上身','THERMO SHIELD'):'中等量',
 ('上身','越野跑'):'中等量',('上身','攀岩'):'主力',('上身','DNS 頂規線'):'形象',('上身','中國專屬款'):'少量',
 ('下身','ALPINE A'):'主力',('下身','ALPINE B'):'少量',('下身','TOUGH SHIELD'):'主力',('下身','越野跑'):'中等量',('下身','攀岩'):'主力',
 ('下身','DNS 頂規線'):'形象',('下身','中國專屬款'):'少量',
 ('配件','背包／包款'):'主力',('配件','帽子'):'主力',('配件','手套'):'中等量',('配件','頸圍／頭帶'):'中等量',('配件','襪子／綁腿'):'中等量',
 ('鞋款','健行鞋'):'主力',('鞋款','越野跑鞋'):'中等量',('鞋款','休閒／保暖鞋'):'少量'}
SHOE_NOTE = '此款號展示會有樣品，樣品是哪個顏色以現場為準'
esc = html.escape

def split_color(c):
    en = en_of(c)
    zh = c[:len(c) - len(en)].strip() if en else c
    return zh, en

def month(it):
    m = re.search(r'/(\d{1,2})', it.get('launch') or '')
    return int(m.group(1)) if m else None

# ---- group into series / styles ----
# 同款號跨系列（中國專屬色）併到該款的主系列，一款一張卡
prim = {}
for i in items:
    if i['mon'] != '中國專屬款': prim.setdefault(i['style'], i['mon'])
for i in items:
    i['_mon'] = prim.get(i['style'], i['mon'])
series = []
for sh in cfg['sheets']:
    for mon in cfg['months']:
        L = [i for i in items if i['sheet'] == sh and i['_mon'] == mon]
        if not L: continue
        styles = {}
        for i in L: styles.setdefault(i['style'], []).append(i)
        series.append(dict(sheet=sh, mon=mon, styles=list(styles.items()), tier=TIER.get((sh, mon), '')))
no = START_NO
style_no = {}
for se in series:
    se['first'] = no
    for st, L in se['styles']:
        style_no[st] = no; no += 1
    se['last'] = no - 1
LAST_NO = no - 1

def has_sample(i): return (i.get('note') or '').startswith('展示會有樣品')
def style_level(L): return any((i.get('note') or '').startswith('此款') for i in L)
def style_has(L): return any(has_sample(i) or (i.get('note') or '').startswith('此款') for i in L)

# ---- layout constants (mm) ----
PW, PH = 210, 297
X0, X1 = 22, 200          # 左 16mm 裝訂邊
Y0, Y1 = 20, 284
TW, TG, CP = 30.0, 1.6, 2.4
PER_LINE = 5
GAP = 3.0

def tile_h(internal): return 30 + 3.8 + 3.0 + (4.0 if internal else 0) + 1.2 + 7.0
def card_dims(L, internal, hero):
    n = len(L); per = min(n, PER_LINE); lines = math.ceil(n / PER_LINE)
    w = 2 * CP + per * TW + (per - 1) * TG
    w = max(w, 60)
    h = 2 * CP + lines * tile_h(internal) + (lines - 1) * TG + 17.5 + (4.2 if internal and style_level(L) else 0) + (6 if hero else 0)
    return w, h

def tile_html(i, internal, shoe_level):
    zh, en = split_color(i['color'])
    h = i.get('doll') or ((i.get('photos') or [None])[0])
    if h and h in IMG:
        img = f'<img src="{IMG[h]}">'
        ref = i.get('ref')
        rn = ('<div class="ref">同款他色圖，僅供參考</div>' if ref == 1 else '<div class="ref">另一性別圖，僅供參考</div>' if ref else '')
    else:
        img = '<div class="noimg">圖待補</div>'; rn = ''
    tag = ''
    if internal and not shoe_level:
        tag = '<div class="tag on">有樣品</div>' if has_sample(i) else '<div class="tag off">無樣品</div>'
    return (f'<div class="tile"><div class="im">{img}{rn}</div><div class="czh">{esc(zh or en)}</div>'
            f'<div class="cen">{esc(en if zh else "")}</div>{tag}<div class="qty"></div></div>')

def card_html(st, L, se, internal, x, y, w, h):
    hero = any(i.get('whl') for i in L)
    shoe_level = style_level(L)
    names = []
    for i in L:
        if i['zh'] not in names: names.append(i['zh'])
    prices = sorted({i['price'] for i in L if i.get('price')})
    if not prices: ptxt = '價格原廠待定'
    elif len(prices) == 1: ptxt = f'NT${prices[0]:,}'
    else: ptxt = f'NT${prices[0]:,}–{prices[-1]:,}'
    ms = sorted({month(i) for i in L if month(i)})
    mtxt = f'{ms[0]} 月上市' if ms else ''
    tier = se['tier'] if se['tier'] in ('主力', '中等量') else ''
    tiles = ''.join(tile_html(i, internal, shoe_level) for i in L)
    out = [f'<div class="card{" hero" if hero else ""}" style="left:{x:.2f}mm;top:{y:.2f}mm;width:{w:.2f}mm;height:{h:.2f}mm">']
    if hero: out.append('<div class="herobar">★ 台灣主打</div>')
    out.append(f'<div class="tiles" style="width:{min(len(L),PER_LINE)*TW+(min(len(L),PER_LINE)-1)*TG:.2f}mm">{tiles}</div>')
    out.append(f'<div class="foot"><div class="l1"><span class="no">{style_no[st]}</span><span class="st">{esc(st)}</span>'
               + (f'<span class="tier{" mid" if tier=="中等量" else ""}">{tier}</span>' if tier else '') + '</div>'
               f'<div class="nm">{esc("／".join(names))}</div>'
               f'<div class="meta">{esc(L[0]["gen"])}　{ptxt}　{mtxt}</div>'
               + (f'<div class="snote">{SHOE_NOTE}</div>' if internal and shoe_level else '') + '</div></div>')
    return ''.join(out)

def page(content, hdr_r='', pno=None, cls=''):
    hd = (f'<div class="hdr"><span>BLACK YAK 27FW 訂單目錄</span><span>{esc(hdr_r)}</span></div>' if hdr_r else '')
    pn = f'<div class="pno">{pno}</div>' if pno else ''
    return f'<section class="page pg-{cls}">{hd}{content}{pn}</section>'

def cats(se):
    c = []
    for st, L in se['styles']:
        for i in L:
            if i['cat'] not in c: c.append(i['cat'])
    return c

def build(internal):
    pages = []
    # cover
    notes = ['本目錄供展示會現場看樣對照使用，詳細資訊與彩色圖片請看線上訂單網站。']
    if internal:
        notes += ['有樣品：這個顏色展示會現場有樣品。', '此款號有樣品：這個款號展示會有樣品，樣品是哪個顏色以現場為準。']
    pages.append(('cover', f'''<div class="cover"><img class="logo" src="{LOGO}"><h1>27FW 訂單目錄</h1><div class="rule"></div>
      <div class="sub">EMERS GROUP　經銷商展示會</div><div class="cust">客戶：<span></span></div>
      <div class="cnotes">{"".join(f"<p>{esc(n)}</p>" for n in notes)}</div></div>''', ''))
    # overview placeholder (filled after pagination)
    pages.append(('ov', None, ''))
    pages.append(('ov', None, ''))
    series_page = {}
    for se in series:
        nst = len(se['styles']); ncol = sum(len(L) for _, L in se['styles'])
        nsm = sum(1 for _, L in se['styles'] if style_has(L))
        ms = sorted({month(i) for _, L in se['styles'] for i in L if month(i)})
        mt = (f'台灣預計 {ms[0]} 月上市' if len(ms) == 1 else f'台灣預計 {ms[0]} 到 {ms[-1]} 月陸續上市') if ms else ''
        txt = f'共 {nst} 款、{ncol} 個顏色，品類有{"、".join(cats(se))}。{mt}。'
        if internal:
            txt += f'其中 {nsm} 款展示會有樣品。' if nsm else '這個主題展示會沒有樣品，請看款式圖下單。'
        if se['mon'] == '中國專屬款':
            txt += '原廠標示中國專屬款，能不能下以原廠確認為準；標「價格原廠待定」的款式價格確定後另行通知。'
        series_page[(se['sheet'], se['mon'])] = len(pages) + 1
        pages.append(('div', f'<div class="divider"><div class="k">27FW　{esc(se["sheet"])}</div><h2>{esc(se["mon"])}</h2><div class="rule"></div><p>{esc(txt)}</p></div>', ''))
        # cards
        hdr = f'{se["sheet"]}｜{se["mon"]}'
        y = Y0; row = []; rowh = 0; buf = []
        def flush_row():
            nonlocal y, row, rowh
            if not row: return
            tot = sum(w for w, _, _, _ in row) + GAP * (len(row) - 1)
            x = X1 - tot
            for w, h, st, L in row:
                buf.append(card_html(st, L, se, internal, x, y, w, h)); x += w + GAP
            y += rowh + GAP; row = []; rowh = 0
        for st, L in se['styles']:
            hero = any(i.get('whl') for i in L)
            w, h = card_dims(L, internal, hero)
            used = sum(c[0] for c in row) + GAP * len(row)
            if row and used + w > (X1 - X0):
                flush_row()
            if y + max(rowh, h) > Y1:
                flush_row() if row and y + rowh <= Y1 else None
                if buf:
                    pages.append(('cards', ''.join(buf), hdr)); buf = []; y = Y0
            row.append((w, h, st, L)); rowh = max(rowh, h)
        flush_row()
        if y > Y1:  # safety
            pass
        if buf: pages.append(('cards', ''.join(buf), hdr))
    # checklist
    ck_start = len(pages) + 1
    if internal:
        for p in checklist_pages(): pages.append(('ck', p, ''))
    # overview content
    a, b = overview(series_page, internal, ck_start)
    pages[1] = ('ov', a, ''); pages[2] = ('ov', b, '')
    return ''.join(page(c, h, n + 1 if t != 'cover' else None, t) for n, (t, c, h) in enumerate(pages)), len(pages)

def overview(series_page, internal, ck_start):
    nst = sum(len(se['styles']) for se in series)
    nsm = sum(1 for se in series for _, L in se['styles'] if style_has(L))
    head = f'BLACK YAK 27FW　共 {nst} 款（編號 {START_NO}–{LAST_NO}）'
    if internal: head += f'，有樣品 {nsm} 款，清點明細在第 {ck_start} 頁'
    out = [f'<div class="ov"><h2>目錄總覽</h2><div class="ovsub">{esc(head)}</div>']
    parts = []
    for sh in cfg['sheets']:
        if sh == '配件':
            out.append('</div>'); parts.append(''.join(out)); out = ['<div class="ov"><h2>目錄總覽（續）</h2><div class="ovsub"></div>']
        S = [se for se in series if se['sheet'] == sh]
        if not S: continue
        a = sum(len(se['styles']) for se in S); b = sum(1 for se in S for _, L in se['styles'] if style_has(L))
        cs = []
        for se in S:
            for c in cats(se):
                if c not in cs: cs.append(c)
        out.append(f'<div class="ovsh"><b>{sh}</b>　<b>{a} 款</b>' + (f'　<span class="g">有樣品 {b} 款</span>' if internal else '') + '</div>')
        out.append(f'<div class="ovcat">品類：{esc("、".join(cs))}</div>')
        out.append('<table class="ovt"><tr><th class="l">系列</th><th>台灣建議</th><th>款數</th><th>編號</th><th>頁數</th></tr>')
        for se in S:
            b2 = sum(1 for _, L in se['styles'] if style_has(L))
            out.append(f'<tr><td class="l">{esc(se["mon"])}' + (f'　<span class="g">有樣品 {b2} 款</span>' if internal else '') +
                       f'</td><td>{se["tier"]}</td><td>{len(se["styles"])}</td><td>{se["first"]}–{se["last"]}</td><td>{series_page[(sh, se["mon"])]}</td></tr>')
        out.append('</table>')
    out.append('</div>'); parts.append(''.join(out))
    return parts

def checklist_pages():
    rows = load_bj()
    by = {}
    for i in items: by.setdefault(N(i['style']), []).append(i)
    inn, outr = [], []
    for r in rows:
        L = by.get(N(r['style']))
        note = r['note']
        if L:
            m = [i for i in L if N(en_of(i['color'])) == N(r['color'])]
            it = m[0] if m else L[0]
            if it['mon'] == '中國專屬款': note = '；'.join(x for x in [note, '中國專屬款'] if x)
            color = r['color'] if r['color'] != '?' else ('（清單未列）' if it['sheet'] == '鞋款' else '（顏色待定）')
            inn.append((style_no[L[0]['style']], r['style'] if it['sheet'] != '鞋款' else '（無款號）', it['zh'], it['en'], color, r['qty'], note))
        else:
            nm = {'27WMPD501': ('ALPINE SKI 滑雪鋪棉外套（男）', 'MEN ALPINE SKI PADDING JACKET'),
                  '27WWPD501': ('ALPINE SKI 滑雪鋪棉外套（女）', 'WOMEN ALPINE SKI PADDING JACKET')}.get(r['style'], ('', ''))
            outr.append(('', r['style'], nm[0], nm[1], r['color'], r['qty'], '目錄沒有此款'))
    inn.sort(key=lambda x: (x[0], x[1], x[4]))
    total_rows = len(rows); total_q = sum(r['qty'] for r in rows)
    def tr(r):
        return (f'<tr><td>{r[0]}</td><td class="mono">{esc(r[1])}</td><td class="nmc">{esc(r[2])}<br><small>{esc(r[3])}</small></td>'
                f'<td>{esc(r[4])}</td><td class="c b">{r[5]}</td><td class="c"><span class="ln"></span></td><td class="c"><span class="bx"></span></td><td class="nt">{esc(r[6])}</td></tr>')
    seq = [('sec', '目錄裡有的款')] + [('r', r) for r in inn] + [('sec', '目錄沒有的款（有寄來）')] + [('r', r) for r in outr]
    PER = 25
    pages = []; cur = []; cnt = 0; first = True
    head = ('<tr><th>No.</th><th>款號</th><th>品名</th><th>顏色</th><th>應到</th><th>實收</th><th>✓</th><th>備註</th></tr>')
    for kind, v in seq:
        cur.append(f'<tr class="sec"><td colspan="8">{esc(v)}</td></tr>' if kind == 'sec' else tr(v)); cnt += 1
        if cnt >= (PER - 3 if first else PER):
            pages.append(cur); cur = []; cnt = 0; first = False
    if cur: pages.append(cur)
    out = []
    for k, p in enumerate(pages):
        top = (f'<h2>樣品清點明細</h2><div class="cksub">北京寄來：Beijing Invoice 1109_update1　共 {total_rows} 列、應到 {total_q} 件<br>'
               'No. 是目錄編號，可以翻回款卡對照。實收寫件數，對上打勾。</div>' if k == 0 else '')
        out.append(f'<div class="ck">{top}<table class="ckt">{head}{"".join(p)}</table></div>')
    return out

CSS = '''
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Noto Sans CJK TC","Noto Sans CJK HK",sans-serif;color:#141414;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:210mm;height:297mm;position:relative;overflow:hidden;page-break-after:always;background:#fff}
.hdr{position:absolute;left:22mm;right:10mm;top:9mm;display:flex;justify-content:space-between;font-size:7.5pt;color:#6b6b70;border-bottom:.3mm solid #c8c8c8;padding-bottom:1.2mm}
.pno{position:absolute;bottom:7mm;left:22mm;right:10mm;text-align:center;font-size:8pt;color:#6b6b70}
.cover{position:absolute;left:30mm;right:18mm;top:60mm}
.cover .logo{width:34mm;filter:invert(1)}
.cover h1{font-size:34pt;font-weight:900;margin-top:12mm;letter-spacing:.5pt}
.rule{height:.8mm;background:#141414;margin:5mm 0 4mm}
.cover .sub{font-size:11pt;color:#555}
.cust{margin-top:55mm;font-size:17pt;font-weight:700;display:flex;align-items:flex-end}
.cust span{display:inline-block;width:95mm;border-bottom:.4mm solid #141414;margin-left:3mm;height:8mm}
.cnotes{margin-top:22mm;font-size:8.5pt;color:#555;line-height:1.8}
.ov{position:absolute;left:22mm;right:10mm;top:16mm}
.ov h2,.ck h2{font-size:22pt;font-weight:900}
.ovsub,.cksub{font-size:8.5pt;color:#555;margin:1.5mm 0 6mm;line-height:1.6}
.ovsh{font-size:13pt;border-bottom:.5mm solid #141414;padding-bottom:1mm;margin-top:5mm}
.g{color:#1d6b35;font-weight:700;font-size:.85em}
.ovcat{font-size:8pt;margin:1.5mm 0 1mm;color:#333}
.ovt{width:100%;border-collapse:collapse;font-size:9pt}
.ovt th{font-weight:400;color:#6b6b70;font-size:7.5pt;border-bottom:.3mm solid #999;padding:1.2mm 0}
.ovt td{border-bottom:.2mm solid #ddd;padding:1.6mm 0;text-align:center}
.ovt .l{text-align:left}
.divider{position:absolute;left:30mm;right:18mm;top:120mm}
.divider .k{font-size:10pt;color:#6b6b70;letter-spacing:2pt}
.divider h2{font-size:36pt;font-weight:900;margin-top:3mm}
.divider p{font-size:10.5pt;line-height:1.9;color:#333}
.card{position:absolute;border:.3mm solid #c8c8c8;border-radius:1.5mm;padding:2.4mm;background:#fff}
.card.hero{border:.6mm solid #f2b100}
.herobar{margin:-2.4mm -2.4mm 2mm;background:#f2b100;height:5.4mm;line-height:5.4mm;padding-left:2.4mm;font-weight:900;font-size:9pt}
.tiles{display:flex;flex-wrap:wrap;gap:1.6mm}
.tile{width:30mm;text-align:center}
.im{width:30mm;height:30mm;position:relative;display:flex;align-items:center;justify-content:center;background:#fff}
.im img{max-width:100%;max-height:100%;object-fit:contain}
.noimg{width:100%;height:100%;background:#f1f1ef;color:#999;font-size:8pt;display:flex;align-items:center;justify-content:center}
.ref{position:absolute;bottom:0;left:0;right:0;font-size:5.6pt;color:#8a5a00;background:rgba(255,255,255,.85)}
.czh{font-size:7.6pt;margin-top:.6mm;line-height:3.2mm;white-space:nowrap;overflow:hidden}
.cen{font-size:5.6pt;color:#6b6b70;line-height:2.8mm;white-space:nowrap;overflow:hidden}
.tag{height:3.6mm;line-height:3.6mm;font-size:6.6pt;margin-top:.4mm;border-radius:.6mm}
.tag.on{background:#1d6b35;color:#fff;font-weight:700}
.tag.off{color:#aaa;border:.2mm solid #ddd}
.qty{height:7mm;border:.3mm solid #999;border-radius:.6mm;margin-top:1.2mm}
.foot{margin-top:2mm}
.l1{display:flex;align-items:center;gap:1.6mm}
.no{background:#141414;color:#fff;font-weight:900;font-size:9pt;padding:0 1.6mm;height:5mm;line-height:5mm;border-radius:.6mm}
.st{font-weight:700;font-size:8.5pt;font-family:"DejaVu Sans Mono",monospace}
.tier{background:#c8452a;color:#fff;font-size:7pt;padding:0 1.4mm;height:4.2mm;line-height:4.2mm;border-radius:.6mm}
.tier.mid{background:#7a7a7a}
.nm{font-weight:900;font-size:9.5pt;margin-top:1mm;line-height:4.6mm;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.meta{font-size:7.6pt;color:#444;margin-top:.4mm}
.snote{margin-top:1mm;background:#1d6b35;color:#fff;font-size:6.8pt;padding:.5mm 1.4mm;border-radius:.6mm;font-weight:700}
.ck{position:absolute;left:22mm;right:10mm;top:14mm}
.ckt{width:100%;border-collapse:collapse;font-size:7.4pt}
.ckt th{background:#141414;color:#fff;font-weight:700;padding:1.2mm 1mm;text-align:left}
.ckt td{border-bottom:.2mm solid #ccc;padding:1.1mm 1mm;vertical-align:middle;height:9.4mm}
.ckt small{font-size:5.6pt;color:#777}
.ckt .mono{font-family:"DejaVu Sans Mono",monospace;font-size:6.8pt}
.ckt .c{text-align:center}.ckt .b{font-weight:700}
.ckt .nmc{width:62mm}
.ckt .nt{font-size:6.4pt;color:#8a3a00;width:30mm}
.ln{display:inline-block;width:10mm;border-bottom:.3mm solid #333}
.bx{display:inline-block;width:3.2mm;height:3.2mm;border:.3mm solid #333}
.sec td{background:#ebebe8;font-weight:700;height:6mm}
'''
os.makedirs(OUT, exist_ok=True)
for name, internal in (('internal', True), ('customer', False)):
    body, n = build(internal)
    open(f'{OUT}/{name}.html', 'w').write(f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>')
    print(name, 'pages', n)
print('styles', len(style_no), 'numbers', START_NO, LAST_NO)
