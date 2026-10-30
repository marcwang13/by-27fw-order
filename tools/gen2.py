import sys, os, json, re, io, hashlib, base64, collections
sys.path.insert(0, os.path.dirname(__file__))
from parse import load
FX = 0.0245
def twd(k): return int(round(k*FX/10.0))*10 if k else None
DL='/mnt/user-data/uploads/Downloads/'
BASE={'BLACK':'黑','BLACK BEAUTY':'深黑','WHITE':'白','O.WHITE':'米白','IVORY':'象牙白','ECRU':'本白','OATMEAL':'燕麥','BEIGE':'米','GRAYISH BEIGE':'灰米','SILVER BEIGE':'銀米','TAUPE':'灰褐','TAUPE GRAY':'灰褐','GRAY':'灰','MELANGE GRAY':'麻花灰','SILVER GRAY':'銀灰','SILVER':'銀','CHARCOAL':'炭灰','IRON GATE':'鐵灰','FROST':'霧灰','NAVY':'海軍藍','BLUE':'藍','L/BLUE':'淺藍','SKY BLUE':'天藍','AQUA':'水藍','AQUA BLUE':'水藍','BLUE GRAY':'灰藍','GRAYISH BLUE':'灰藍','BLUE NIGHT':'夜藍','DENIM':'丹寧藍','TEAL':'藍綠','TURQUOISE':'土耳其藍','MINT':'薄荷綠','GREEN':'綠','KHAKI':'卡其','KHAKI GREEN':'卡其綠','KHAKI GRAY':'卡其灰','NEON GREEN':'螢光綠','LIME':'萊姆綠','PISTACHIO':'開心果綠','BROWN':'棕','COCOA':'可可','BURGUNDY':'酒紅','RED':'紅','FIERY RED':'火焰紅','CORAL':'珊瑚','ORANGE':'橘','YELLOW':'黃','PINK':'粉','ROSE':'玫瑰','ROSE PINK':'玫瑰粉','GRAYISH PINK':'灰粉','NEON PINK':'螢光粉','PURPLE':'紫','LAVENDER':'薰衣草紫','COBALT VIOLET':'鈷紫'}
PRE={'D':'深','L':'淺','B':'黑','G':'灰','K':'卡其'}
def zh_color(c):
    c=(c or '').strip()
    if c in BASE: z=BASE[c]
    else:
        m=re.match(r'^([A-Z])/(.+)$',c)
        z=(PRE.get(m.group(1),'')+BASE.get(m.group(2),m.group(2))) if m else ''
    if not z: return c
    if not z.endswith(('色','白','黑','灰','藍','綠','紅','粉','紫','米','褐','棕','黃','橘','銀','卡其','可可','燕麥','珊瑚','玫瑰')): pass
    return f'{z}色 {c}' if len(z)<=1 else f'{z} {c}'
KCOL={'블랙':'黑','BLACK':'黑','아이보리':'象牙白','틸네이비':'藍綠海軍','K그레이':'卡其灰','B차콜':'黑炭灰','실버베이지2':'銀米'}
def zh_color_kr(c):
    c=(c or '').strip().replace('\n',' ')
    if c in ('','ASSORTED'): return '多色（色別待原廠提供）'
    if '필요' in c and ('BLACK' in c.upper() or '블랙' in c): return '需有黑色（色別待確認）'
    if '어두운' in c: return '深色系（黑／炭灰／深灰，待確認）'
    if '상의 매칭' in c: return '搭配上衣（深色系，待確認）'
    if '마나슬루' in c: return '搭配 MANASLU 色系（待確認）'
    if c.startswith('D/NAVY'): return '深藍、深灰（不做黑）'
    parts=[p.strip() for p in c.split(',')]
    return '、'.join(KCOL.get(p,p) for p in parts)

# ---------- 系列 ----------
def series_ss(r, en):
    n=(en or '').upper(); pl=r.get('Product Line') or ''; sm=(r.get('Special Material') or '').upper()
    if r.get('Pricing Class')=='DNS': return 'DNS 頂規線'
    if pl=='Trail' or 'TRAIL RUNNING' in n or 'LIGHTFLOW' in n or 'LIGHT FLOW' in n or 'FLIGHT' in n: return '越野跑'
    if re.search(r'CLIMB|HOLD MASTER|RIDGE MASTER|BOULDER',n): return '攀岩'
    if 'GORE' in sm or 'GORE' in n or 'RAIN' in n: return 'GORE-TEX／防水'
    if re.search(r'\bICE\b|COOL|FRESH|AERO|SEERSUCKER',n): return '涼感透氣'
    if pl in ('Trekking','Mountain','Basic Performance') or re.search(r'TL-\d|SPEED ?HIKER|DYNEEMA|CORDURA',n+sm): return '登山健行'
    if pl=='Collection' or pl=='BCC': return 'Collection'
    return '日常機能'
SER_ORDER_SS=['日常機能','涼感透氣','登山健行','越野跑','攀岩','GORE-TEX／防水','DNS 頂規線','Collection','健行鞋','越野跑鞋','登山鞋']
LINE_FW={'알파인A':'ALPINE A','ALPINE B':'ALPINE B','터프쉴드':'TOUGH SHIELD','트레일러닝':'越野跑','클라이밍':'攀岩','SKI':'滑雪'}
SER_ORDER_FW=['ALPINE A','ALPINE B','TOUGH SHIELD','越野跑','攀岩','滑雪']
# ---------- 部位 ----------
UPPER={'圓領T恤','POLO衫','拉鍊T恤','其他T恤','襯衫','連帽衫','外套','GORE-TEX外套','鋪棉外套','套裝外套','背心','羽絨外套','刷毛外套','軟殼外套','高領T恤','長袖T恤'}
LOWER={'長褲','短褲','套裝長褲','內搭褲'}
def part_of(cat):
    if cat in LOWER: return '下身'
    if cat in UPPER: return '上身'
    return None
# ---------- 台灣市場建議（依中央氣象署：梅雨 5–6 月、7 月起颱風季、1 月平地均溫約 16–20°C） ----------
def tw_ss(it):
    n=(it['en']+' '+it['zh']+' '+it['icon']).upper(); c=it['cat']
    if c in ('健行鞋','登山鞋'): return '台灣多雨潮濕，GORE-TEX 防水健行鞋在郊山與高山都有需求，可列主力'
    if c=='越野跑鞋': return '台灣越野跑賽事多在山區、路面濕滑，抓地好的越野跑鞋需求穩定'
    if re.search(r'PRIMALOFT|PADD|鋪棉|INSUL',n) or c=='鋪棉外套': return '台灣春夏平地用不到保暖鋪棉，主要給高山與出國客，建議少量'
    if re.search(r'POLARTEC|FLEECE|刷毛',n): return '刷毛中層在台灣春夏用途有限，適合高山行程，建議少量'
    if 'GORE' in n or 'RAIN' in n or '雨' in n or c=='GORE-TEX外套': return '5–6 月梅雨、7 月起颱風與山區午後雷陣雨，防水外套全年有需求，可列主力'
    if re.search(r'\bICE\b|COOL|FRESH|AERO|涼感|泡泡紗|SEERSUCKER|MESH',n): return '台灣 4–10 月濕熱，涼感透氣款銷售期長，建議加深'
    if c in ('短褲',): return '台灣夏季長，短褲銷售期長，可多備'
    if c in ('POLO衫','圓領T恤','拉鍊T恤','其他T恤') and ('LONG' in n or '長袖' in n): return '台灣登山客重防曬，薄長袖很好賣，建議主力'
    if c in ('POLO衫','圓領T恤','拉鍊T恤','其他T恤'): return '台灣夏季長，吸濕排汗短袖是基本盤，建議主力'
    if c=='長褲': return '台灣登山多穿長褲（防曬、防蚊、防刮），建議主力'
    if c in ('外套',) : return '春季早晚溫差與山區防風用，輕薄可收納款較好賣'
    if c in ('帽子','其他配件','手套') : return '防曬需求高，帽款、袖套是好帶的加購品'
    if c in ('背包','配件包'): return '日常與郊山兩用的中小容量包在台灣較好賣'
    if c in ('健行鞋','登山鞋','越野跑鞋'): return '台灣多雨潮濕，GORE-TEX 防水鞋在郊山與高山都有需求'
    return ''
def tw_fw(it, sub, wv):
    n=it['zh']+' '+it['ov']
    if '羽絨' in n and ('長版' in n or sub=='중헤비'): return '台灣冬季短、1 月平地均溫約 16–20°C，厚羽絨與長版以高山、出國客為主，建議少量'
    if '羽絨' in n or '鋪棉' in n: return '輕量羽絨、背心適合台灣冬季洋蔥式穿搭，建議主力'
    if sub=='방수' or 'GORE-TEX' in n or '防水' in n: return '台灣秋冬東北季風帶來北部與東部降雨，防水外套全年有需求'
    if sub in ('방풍','저지') or '防風' in n or '軟殼' in n: return '東北季風與山區強風，防風／軟殼外套實用，可列主力'
    if '刷毛' in n or 'POLARTEC' in n.upper(): return '刷毛中層在台灣秋冬最好搭，建議主力'
    if sub in ('라운드넥','집업','카라','후디','터틀넥') : return '台灣秋冬溫差大，長袖T與中層是常備款'
    if wv=='바지' or '長褲' in n: return '台灣登山多穿長褲，秋冬款可列主力；刷毛／鋪棉長褲建議少量'
    return ''

def b64thumb(raw):
    from PIL import Image
    im=Image.open(io.BytesIO(raw)).convert('RGB'); big=im.copy(); big.thumbnail((1200,1200))
    t=im.copy(); t.thumbnail((360,360)); bio=io.BytesIO(); t.save(bio,'JPEG',quality=72)
    return big, 'data:image/jpeg;base64,'+base64.b64encode(bio.getvalue()).decode()

LETTER=['0XS','00S','00M','00L','0XL','XXL','3XL']
SZLABEL={'0XS':'XS','00S':'S','00M':'M','00L':'L','0XL':'XL','XXL':'2XL','3XL':'3XL','999':'F','ASSORTED':'數量'}
def szkey(z):
    z=str(z)
    if z in LETTER: return (0,LETTER.index(z),0)
    if z=='999': return (4,0,0)
    try: v=int(z); return ((1 if 85<=v<=130 else 2 if v<85 else 3),v,0)
    except: return (5,0,0)

def build_ss():
    rows=load(DL+'BLACKYAK_TW_27SS_Order_2026-10-30.xls')['Order Sheet']; h=rows[0]; R=[dict(zip(h,r)) for r in rows[1:]]
    v10=json.load(open('/home/claude/by/src/v10_map.json'))
    dump=json.load(open(DL+'blackyak_27ss_sku_dump.json')); cadk={x['full_sku']:x.get('cad_key') for x in dump['rows']}
    fwj=json.load(open(DL+'by27ss_fw.json'))
    imgs={k:(base64.b64decode(v) if isinstance(v,str) else base64.b64decode(v.get('b',''))) for k,v in dump['imgs'].items() if v}
    for k,v in fwj['imgs'].items(): imgs[k]=base64.b64decode(v['b'])
    items=collections.OrderedDict(); runs=collections.defaultdict(set)
    for r in R:
        st=r['Product Code']; cc=r['Color Code'] or ''; key=f'{st}-{cc}'; z=r['Size']
        if key not in items:
            m=v10.get(key,{}); en=r['Product Name (English)'] or ''
            if 'pending' in en.lower(): en=''
            zh=m.get('zh') or ''
            cat=m.get('cat') or ''
            gen='男' if '（男）' in zh else '女' if '（女）' in zh else '中性'
            part=part_of(cat)
            sheet=part or '配件'
            inb=r['Yongin Inbound'] or ''; mon=(str(int(inb[5:7]))+'月') if inb else ''
            ser=series_ss(r,en)
            note=[]
            if r['Category']=='Special-price Apparel': note.append('特價商品')
            it=dict(id=key,sheet=sheet,no='',mon=ser,monTag=(f'{mon}韓國入倉' if mon else ''),theme=ser,drop=r['Pricing Class'],cat=cat,gen=gen,style=st,
                zh=zh,en=en or '英文品名待原廠提供',color=zh_color(r['Color Name']),cc=cc,sku=st+cc,icon=r['Special Material'] or '',
                fab='',series=('產地 '+r['Country of Origin']) if r['Country of Origin'] not in (None,'-') else '',ov='',dt='',tech='',
                note='；'.join(note),launch=inb.replace('-','/'),eta=inb.replace('-','/'),krw=int(float(r['KR SRP'])) if r['KR SRP'] else None,
                sizes=[],doll='',run=st,part='top',whl=bool(m.get('whl')),whlr=(m.get('reason') or ''))
            it['price']=twd(it['krw']); it['tw']=tw_ss(it)
            ck=cadk.get(r['Full SKU'])
            it['_img']=imgs.get(ck) if ck else None
            items[key]=it
        it=items[key]
        if z not in it['sizes']: it['sizes'].append(z)
        runs[st].add(z)
    # footwear
    for x in fwj['rows']:
        if x['pricing_class']!='FOOTWEAR': continue
        st=x['internal_product_code']; cc=x['color_code']; key=f'{st}-{cc}'; z=str(x['size'])
        if key not in items:
            m=v10.get(key,{}); zh=m.get('zh') or ''; cat=m.get('cat') or '健行鞋'
            gen='男' if '（男）' in zh else '女' if '（女）' in zh else '中性'
            inb=x.get('final_inbound_date') or ''; mon=(str(int(inb[5:7]))+'月') if inb else ''
            it=dict(id=key,sheet='鞋款',no='',mon=cat,monTag=(f'{mon}韓國入倉' if mon else ''),theme=cat,drop='FOOTWEAR',cat=cat,gen=gen,style=st,zh=zh,en=x['product_name_en'],
                color=zh_color(x['color_name']),cc=cc,sku=st+cc,icon=x.get('special_material') or '',fab='',series='產地 越南' if x.get('origin')=='베트남' else '',
                ov=f"原廠型號 {x['product_code']}",dt='',tech='',note='',launch=inb.replace('-','/'),eta=inb.replace('-','/'),krw=x['kr_srp'],sizes=[],doll='',run=st,part='top',
                whl=bool(m.get('whl')),whlr=m.get('reason') or '')
            it['price']=twd(it['krw']); it['tw']=tw_ss(it); it['_img']=imgs.get(x['cad_key']); items[key]=it
        it=items[key]
        if z not in it['sizes']: it['sizes'].append(z)
        runs[st].add(z)
    L=list(items.values())
    for it in L: it['sizes'].sort(key=szkey)
    order=['上身','下身','配件','鞋款']
    idx={id(x):n for n,x in enumerate(L)}
    L.sort(key=lambda x:(order.index(x['sheet']), SER_ORDER_SS.index(x['mon']) if x['mon'] in SER_ORDER_SS else 99, idx[id(x)]))
    return L, {k:sorted(v,key=szkey) for k,v in runs.items()}, order, SER_ORDER_SS

def build_fw():
    sys.path.insert(0,'/home/claude/by/tools'); from fw_zh import ZH
    d=json.load(open('/home/claude/by/src/fw_raw.json')); R=d['rows']
    imgs={k:base64.b64decode(v['b']) for k,v in d['imgs'].items() if v and v.get('b')}
    WV={'바지':'長褲','파카':'羽絨外套','자켓':'外套','라운드티셔츠':'長袖T恤','집업티셔츠':'拉鍊T恤','후드티셔츠':'連帽衫','조끼':'背心','셋업':'套裝','카라티셔츠':'POLO衫','패딩':'鋪棉外套','반바지':'短褲','고어자켓':'GORE-TEX外套','셔츠':'襯衫','세트':'套組'}
    SUB={'일반':'','라운드넥':'圓領','경량':'輕量','중헤비':'中厚','집업':'拉鍊','후디':'連帽','방풍':'防風','플리스':'刷毛','충전재':'填充保暖','패딩':'鋪棉','카라':'有領','셋업바지':'套裝長褲','레깅스팬츠':'短褲','2L':'2L 防水','방수':'防水','저지':'針織','터틀넥':'高領','셋업자켓':'套裝外套'}
    G={'남성':'男','여성':'女','공용':'中性'}
    L=[]; runs={}
    for i,r in enumerate(R):
        zh,ov=ZH[i]; wv=r['workbook_variety']; sub=r['subcategory']
        cat=WV.get(wv,'')
        if not cat: cat='拉鍊T恤' if 'ZT' in r['product_code'] else '其他'
        if sub=='레깅스팬츠': cat='短褲'
        if sub=='플리스' and cat=='外套': cat='刷毛外套'
        if sub=='저지' and cat=='外套': cat='軟殼外套'
        if wv=='셋업': cat='套裝外套' if sub=='셋업자켓' or 'SJ' in r['product_code'] else '套裝長褲'
        sheet='套裝' if wv in ('셋업','세트') else ('下身' if cat in LOWER else '上身')
        g=G.get(r['gender'],'中性')
        szr=(r['size'] or '').replace('\n','／'); szr='' if szr=='ASSORTED' else szr
        line=LINE_FW.get(r['product_line'],r['product_line'])
        st=r['progress_status']; note=[]
        if st=='선진행': note.append('原廠標示：先行款')
        if szr: note.append('尺寸段：'+szr)
        key=r['full_sku']
        it=dict(id=key,sheet=sheet,no='',mon=line,monTag='',theme=line,drop=r['pricing_class'],cat=cat,gen=g,style=r['product_code'],
            zh=f'{zh}（{g}）',en=r['product_name_kr'].split('\n')[0],color=zh_color_kr(r['color_name']),cc='',sku=key,
            icon=r['special_material'] or SUB.get(sub,''),fab='',series='',ov=ov,dt='',tech='',note='；'.join(note),launch='',eta='',
            krw=r['kr_srp'] or None,sizes=['ASSORTED'],doll='',run=key,part='top',whl=False,whlr='')
        it['price']=twd(it['krw']); it['tw']=tw_fw(it,sub,wv); it['_img']=imgs.get(r['cad_key'])
        runs[key]=['ASSORTED']; L.append(it)
    order=['上身','下身','套裝']
    idx={id(x):n for n,x in enumerate(L)}
    L.sort(key=lambda x:(order.index(x['sheet']), SER_ORDER_FW.index(x['mon']) if x['mon'] in SER_ORDER_FW else 99, idx[id(x)]))
    return L, runs, order, SER_ORDER_FW

def write(season, L, runs, order, sord, out):
    os.makedirs(out+'/big',exist_ok=True)
    for f in os.listdir(out+'/big'): os.remove(out+'/big/'+f)
    IMG={}
    for it in L:
        raw=it.pop('_img',None)
        if not raw: continue
        h=hashlib.md5(raw).hexdigest()[:12]
        if h not in IMG:
            big,th=b64thumb(raw); big.save(f'{out}/big/{h}.jpg',quality=85); IMG[h]=th
        it['doll']=h
    sheets=[s for s in order if any(i['sheet']==s for i in L)]
    mons=[m for m in sord if any(i['mon']==m for i in L)]+[m for m in dict.fromkeys(i['mon'] for i in L) if m not in sord]
    so=sorted({z for v in runs.values() for z in v},key=szkey)
    cfg=dict(season=season,fx=FX,sheets=sheets,months=mons,szOrder=so,szLabel=SZLABEL)
    with open(out+'/data.js','w') as f:
        f.write('window.SDR_ITEMS='+json.dumps(L,ensure_ascii=False)+';\n')
        f.write('window.BY_RUNS='+json.dumps(runs,ensure_ascii=False)+';\n')
        f.write('window.BY_CFG='+json.dumps(cfg,ensure_ascii=False)+';\n')
    with open(out+'/imgs.js','w') as f: f.write('window.SDR_IMG='+json.dumps(IMG)+';\n')
    c=collections.Counter
    print(season,len(L),'imgs',len(IMG),'noimg',sum(1 for i in L if not i['doll']),c(i['sheet'] for i in L),c(i['mon'] for i in L),
          'nozh',sum(1 for i in L if not i['zh']),'whl',sum(1 for i in L if i['whl']),'tw',sum(1 for i in L if i['tw']),'nocat',sum(1 for i in L if not i['cat']))

if __name__=='__main__':
    s=sys.argv[1]; out=sys.argv[2]
    L,r,o,so=(build_ss() if s=='27SS' else build_fw()); write(s,L,r,o,so,out)
