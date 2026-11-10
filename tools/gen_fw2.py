# 27FW 2026/11 更新版：來源是原廠 11/9 提供的「KOREA TARGET 27FW RAWDATA」（已去掉計畫量、MD、設計師、工廠等內部欄位）
# 用法：python3 gen_fw2.py <repo 目錄>
import sys, os, json, re, collections
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from fw2_zh import NEW
from gen2 import zh_color, twd, szkey, SZLABEL, FX
out=sys.argv[1]
SRC=json.load(open(HERE+'/fw2_src.json'))          # [{style,group,kr,en,cat,line,mat,gen,cc,color,size,krw,batch,origin,comp,cad}]
OLD=json.load(open(HERE+'/fw_old_items.json'))     # 2026/10 版 150 筆（中文品名、說明、系列、CAD 對應）
SAMPLE=set(json.load(open(HERE+'/fw_tagon_styles.json')))  # 中國 TAG-ON 清單上的款號＝有寄樣品
oz={o['style']:o for o in OLD}
EXTRA={'L/SILVER':'淺銀','COBALT BLUE':'鈷藍','FOG':'霧灰綠','MUSTARD':'芥末黃','URBAN BLUE':'都會藍','GRAPE FRUIT':'葡萄柚粉','GRAPEFRUIT':'葡萄柚粉','L/GRAY':'淺灰','D/GRAY':'深灰','M/GRAY':'中灰','M.GRAY':'中灰','K/GRAY':'卡其灰','B/CHOCO':'巧克力','L/PURPLE':'淺紫','V/NAVY':'復古海軍藍','TEAL NAVY':'藍綠海軍','FRENCH GRAY':'法式灰','B/ROSE':'磚玫瑰','BLUE DEPTHS':'深海藍','CLAY':'陶土','ACID YELLOW':'螢光黃','DUSTY PINK':'霧粉','BITTER CHOCOLATE':'苦巧克力','RED BROWN':'紅棕','D/BROWN':'深棕','SAND':'沙','VIOLET':'紫羅蘭','MIX':'混色','D.NAVY':'深海軍藍','D/NAVY':'深海軍藍','B/CHARCOAL':'黑炭灰','L/BEIGE':'淺米','D/KHAKI':'深卡其','L/KHAKI':'淺卡其','OLIVE':'橄欖綠','WINE':'酒紅','CREAM':'奶油白','L/PINK':'淺粉','D/GREEN':'深綠','L/GREEN':'淺綠','LIME OLIVE':'萊姆橄欖','OLIVE GREEN':'橄欖綠','BONE':'骨白','DUSTY IVORY':'霧象牙白','TBD':'顏色待原廠提供','P.BLUE':'粉藍','BEIGE BROWN':'米棕','CRAPE FRUIT':'葡萄柚粉','GRAYISH VIOLET':'灰紫','MELANGE L/GRAY':'麻花淺灰','COLOUR PENDING':'顏色待原廠提供','COLOR PENDING':'顏色待原廠提供'}
def zc(c):
    c=(c or '').strip()
    if c.upper() in EXTRA: z=EXTRA[c.upper()]; return z if '待' in z else f'{z} {c}'
    return zh_color(c.upper()) if zh_color(c.upper())!=c.upper() else c
CAT={'Down Parkas':'羽絨外套','Pants':'長褲','Jackets':'外套','Zip-up T-Shirts':'拉鍊T恤','Crew-neck T-Shirts':'長袖T恤','Padded Jackets':'鋪棉外套','GORE-TEX Jackets':'GORE-TEX外套','Vests':'背心','Fleece Jackets':'刷毛外套','Shorts':'短褲','OtherT-Shirts':'其他T恤','Caps & Hats':'帽子','Gloves':'手套','Socks':'襪子','Backpacks':'背包','Accessory Bags':'配件包','Accessories':'其他配件','Shoes':'鞋'}
LOWER={'長褲','短褲'}
G={'Men':'男','M':'男','Women':'女','W':'女','U':'中性','Unisex':'中性'}
LINE={'Alpine A':'ALPINE A','ALPINE B':'ALPINE B','DNS':'DNS 頂規線','Climbing':'攀岩','Trail Running':'越野跑','SKI':'滑雪','BCC':'bcc'}
SER=['ALPINE A','ALPINE B','TOUGH SHIELD','THERMO SHIELD','越野跑','攀岩','滑雪','DNS 頂規線','中國專屬款','背包／包款','帽子','手套','頸圍／頭帶','襪子／綁腿','健行鞋','越野跑鞋','休閒／保暖鞋']
# 韓國入倉批次 → 月份（依中國訂貨會手冊的上市月：秋 8、9 月，冬 10、11 月）；台灣上市再往後一個月
BATCH={'가을1':8,'가을2':9,'겨울1':10,'겨을1':10,'겨울2':11,'겨울3':12}
def tw_month(b):
    if b in BATCH: m=BATCH[b]+1; return (2028,m-12) if m>12 else (2027,m)
    return None
def clean(x): return (x or '').replace('\\[','[').replace('\\]',']').replace('\\~','~').strip()

# ---------- 台灣主打款（依台灣氣候與通路選；理由顯示在卡片上） ----------
HERO={
  '27WUPA301':'x','27WUPA300':'x','27WUPA302':'STONE MASTER 輕量短版，女生與年輕客層的入門款',
 '27WMPA050':'超輕量羽絨，台灣冬季洋蔥式穿搭的量販主力','27WWPA051':'超輕量羽絨，台灣冬季洋蔥式穿搭的量販主力',
 '27WMVS016':'圓領球型鋪棉背心，價格帶低、好當內搭','27WWVS016':'圓領球型鋪棉背心，價格帶低、好當內搭',
 '27FMGJ030':'GORE-TEX 2L 基本款，東北季風雨季的必備防水殼','27FWGJ031':'GORE-TEX 2L 基本款，東北季風雨季的必備防水殼',
 '27FMJK032':'週末防雨外套，價格比 GORE-TEX 好入手',
 '27FMJK064':'TOUGH SHIELD 防風外套，山區強風與機車族都用得到','27FWJK065':'TOUGH SHIELD 防風外套，山區強風與機車族都用得到',
 '27FMJK002':'刷毛中層入門價，秋冬最好帶的加購款','27FWJK002':'刷毛中層入門價，秋冬最好帶的加購款',
 '27WMRT063':'POLARTEC 鬆餅格長袖，可單穿可當中層','27WWRT019':'POLARTEC 鬆餅格長袖，可單穿可當中層',
 '27FMPN071':'TL-3000 CORDURA 登山褲，耐磨，台灣登山客全年穿長褲','27FWPN070':'TL-3000 CORDURA 登山褲，耐磨，台灣登山客全年穿長褲',
 '27FMPN073':'基本款長褲，日常與郊山通用，可列量販','27FWPN072':'基本款長褲，日常與郊山通用，可列量販',
 '27FMPN303':'攀岩 365 工作褲，街頭穿搭客層','27FWPN301':'攀岩 365 工作褲，街頭穿搭客層',
 '27FMRT657':'越野跑透氣長袖，台灣秋冬跑山與健行都合用','27FWRT658':'越野跑透氣長袖，台灣秋冬跑山與健行都合用',
 'EXUM TR GTX':'GORE-TEX 中筒健行鞋，台灣多雨濕滑，郊山到百岳都能穿',
 'EXUM TR LOW GTX':'GORE-TEX 低筒健行鞋，郊山與日常兩用',
 'TRAIL-X SKY 2':'品牌越野跑代表鞋款，VIBRAM 大底',
 '343 NOVA STEP D GTX':'旋鈕 GORE-TEX 健行鞋，好穿脫，熟齡登山客接受度高',
 '27FWKS02':'品牌長銷背包，30L 是台灣單日百岳與郊山最常用容量',
 '27FWXX19':'腰包、斜背兩用，低單價好帶',
 '27FWHT06':'美麗諾羊毛毛帽，低單價的冬季加購品',
}
def tw_note(it):
    n=(it['en']+' '+it['zh']+' '+it['icon']+' '+it['ov']).upper(); c=it['cat']; ln=it['mon']
    if it['sheet']=='鞋款':
        if 'MULE' in n or 'SLIP' in n: return '保暖／休閒鞋在台灣屬於露營與日常穿搭，建議少量試水溫'
        if 'GTX' in n or 'GORE' in n: return '台灣多雨潮濕，GORE-TEX 防水鞋在郊山與高山都有需求，可列主力'
        return '台灣越野跑賽事多在山區、路面濕滑，抓地好的越野跑鞋需求穩定'
    if c=='背包': return ('30L 上下是台灣單日行程最常用的容量，可列主力' if re.search(r'\b30\b',n) else '大容量與技術型背包以高山、長程客為主，建議少量')
    if c=='配件包': return '收納小物與腰包單價低，適合放櫃檯帶加購'
    if c=='手套': return ('厚款保暖手套在台灣平地用不到，主要給高山與出國賞雪客，建議少量' if re.search(r'MITTEN|PADDED|GTX|WINTER',n) else '薄手套台灣冬季騎車、登山都用得到，可備基本量')
    if c=='帽子': return ('飛行帽、護耳帽在台灣偏高山與出國用，建議少量' if re.search(r'TROOPER|EARFLAP|WINTER CAP|FLEECE',n) else '毛帽是台灣冬季最好帶的低單價加購品，可多備')
    if c=='襪子': return '羊毛登山襪四季都賣，適合搭鞋款做組合'
    if c=='其他配件': return ('綁腿屬高山與雪地裝備，建議少量' if 'GAITER' in n else '頭套屬高山與雪地裝備，建議少量' if 'BALACLAVA' in n else '頸圍、頭帶輕薄好帶，台灣秋冬登山與騎車都用得到')
    if ln=='滑雪' or 'SKI' in n: return '台灣沒有滑雪場，客群是赴日韓滑雪的旅客，建議少量、集中在出國旺季前'
    if re.search(r'EXPEDITION|BIB|WATUSI|TILICHO|SUIT',n): return '遠征等級保暖，台灣只有極少數海外遠征客會買，建議當形象陳列'
    if c=='羽絨外套':
        if re.search(r'LONG|長版|HEAVY|中厚|ALAYA|ICD|HIMA WSP DOWN|GTX|GORE',n) and not re.search(r'LIGHT|輕量',n): return '台灣冬季短、1 月平地均溫約 16–20°C，厚羽絨與長版以高山、寒流與出國客為主，建議少量'
        return '輕量羽絨適合台灣冬季洋蔥式穿搭，也好收納，建議主力'
    if c=='背心': return '背心在台灣秋冬穿著期最長，早晚溫差與冷氣房都用得到，建議主力'
    if c=='鋪棉外套': return ('化纖保暖在台灣潮濕天氣比羽絨好照顧，輕量款可列主力' if re.search(r'LIGHT|輕量|VEST|60|G2',n) else '厚鋪棉在台灣平地穿著期短，建議少量')
    if c=='GORE-TEX外套' or re.search(r'GORE|RAIN|防雨|防水',n): return ('GORE-TEX PRO 等級以百岳、雪季客為主，建議少量但一定要有，撐專業形象' if 'PRO' in n else '台灣秋冬東北季風帶來北部與東部降雨，防水外套全年有需求，可列主力')
    if c=='刷毛外套' or re.search(r'FLEECE|刷毛',n): return '刷毛中層在台灣秋冬最好搭，建議主力'
    if c=='外套': return ('東北季風與山區強風，防風／軟殼外套實用，可列主力' if re.search(r'WIND|SOFTSHELL|SOFT SHELL|軟殼|防風|TOUGH SHIELD|PERTEX',n) else '台灣秋冬早晚溫差大，薄外套穿著期長')
    if c in ('長袖T恤','拉鍊T恤','其他T恤','連帽衫','短袖T恤','套裝外套'):
        if re.search(r'S/S|短袖|SLEEVELESS|無袖',n): return '台灣 10 月還很熱，短袖與無袖在秋季仍賣得動'
        if re.search(r'WOOL|羊毛|BRUSHED|刷毛內裡|기모|THERMAL|WAFFLE|鬆餅',n): return '保暖長袖適合 12–2 月與高山行程，平地可單穿，建議中等量'
        return '台灣秋冬溫差大，長袖T與中層是常備款，建議主力'
    if c in ('長褲','套裝長褲'):
        if re.search(r'DOWN|PADD|鋪棉|羽絨|BIB',n): return '鋪棉與羽絨長褲在台灣只有高山雪季用得到，建議少量'
        if re.search(r'BRUSHED|WINTER|BONDING|刷毛|FLEECE',n): return '刷毛、貼合長褲適合 12–2 月與高山，建議中等量'
        return '台灣登山客全年穿長褲（防曬、防蚊、防刮），秋冬款可列主力'
    if c=='短褲': return '台灣秋季仍熱，短褲穿著期到 11 月，越野跑客群需求穩定'
    return ''

ROWZH=[('STONEMASTER LIGHT HOODED',('攀岩 STONE MASTER LIGHT 連帽羽絨外套','')),('STONEMASTER LIGHT STAND NECK',('攀岩 STONE MASTER LIGHT 立領羽絨外套','')),
 ('STONEMASTER LIGHT SHORT',('攀岩 STONE MASTER LIGHT 短版羽絨外套','')),('STONEMASTER HOODED',('攀岩 STONE MASTER 連帽羽絨外套','')),('STONEMASTER STAND NECK',('攀岩 STONE MASTER 立領羽絨外套','')),
 ('HOTMELT POCKET PULLOVER',('CORDURA 熱熔口袋套頭長袖T','')),('HOTMELT POCKET ZIP-UP',('CORDURA 熱熔口袋拉鍊長袖T',''))]
_names=collections.defaultdict(set)
for r in SRC: _names[r['style']].add(re.sub(r'^\[[^\]]*\]\s*','',clean(r['en'])).upper())
MULTI={k for k,v in _names.items() if len(v)>1 and k!='27FMGJ030'}
L=[]; runs={}; seen=set()
for r in SRC:
    key=r['style']; base=key[:9]; o=oz.get(key) or oz.get(base)
    g=G.get(r['gen'],'中性'); cat=CAT.get(r['cat'],'')
    en=clean(r['en']); kr=clean(r['kr'])
    china=bool(re.search(r'CHINA (EXCLUSIVE|ONLY)|중국단독',(en+kr).upper()))
    en=re.sub(r'^\[[^\]]*\]\s*','',en)
    if 'pending' in en.lower(): en=''
    en={'27FMGJ030':'MEN BASIC GORE-TEX GTX JACKET'}.get(key,en)
    U=en.upper(); rz=None
    for kw,v in ROWZH:
        if kw in U: rz=v; break
    if rz: zh,ov=rz[0],(rz[1] or (o['ov'] if o and 'STONEMASTER' in U else ''))
    elif key in NEW: zh,ov=NEW[key]
    elif o: zh,ov=re.sub(r'（[男女中性]+）$','',o['zh']),o['ov']
    else: zh,ov=en,''
    if r['cat']=='Other Apparel':
        u=en.upper(); cat='套裝外套' if 'TRAINING JACKET' in u else '套裝長褲' if 'TRAINING PANTS' in u else '連帽衫' if 'HOOD' in u else '長褲' if 'PANT' in u or 'PNAT' in u else '其他T恤'
    if cat=='長袖T恤' and re.search(r'S/S',en.upper()): cat='短袖T恤'
    if r['group']=='Footwear':
        sheet='鞋款'; ln=r['line'].upper(); mon='越野跑鞋' if 'TRAIL' in ln else '休閒／保暖鞋' if ln in ('ESSENTIAL','WINTER') else '健行鞋'; cat=mon
    elif r['group']=='Accessories':
        sheet='配件'; mon={'背包':'背包／包款','配件包':'背包／包款','帽子':'帽子','手套':'手套','襪子':'襪子／綁腿'}.get(cat) or ('襪子／綁腿' if 'GAITER' in en.upper() else '頸圍／頭帶')
    else:
        sheet='下身' if cat in LOWER|{'套裝長褲'} else '上身'
        u=(en+' '+zh).upper()
        mon='中國專屬款' if china else (o['mon'] if o else None) or ('TOUGH SHIELD' if 'TOUGH SHIELD' in u else 'THERMO SHIELD' if 'THERMO' in u else LINE.get(r['line']) or 'ALPINE A')
        if 'THERMO' in u and not china: mon='THERMO SHIELD'
    cc=r['cc'].strip(); col=clean(r['color'])
    iid=f"{key}-{cc or re.sub(r'[^A-Z0-9]','',col.upper())[:6] or 'X'}"
    n=2
    while iid in seen: iid=f"{iid.split('~')[0]}~{n}"; n+=1
    seen.add(iid)
    sz=r['size'].strip()
    if sz in ('미확정',''): sizes=['ASSORTED']
    elif sz=='ONE SIZE': sizes=['999']
    else: sizes=[{'S':'00S','M':'00M','L':'00L','XL':'0XL','XS':'0XS'}.get(x.strip(),x.strip()) for x in sz.split(',')]
    tm=tw_month(r['batch'])
    launch=f'{tm[0]}/{tm[1]:02d}' if tm else ''
    note=[]
    if base in SAMPLE or key in SAMPLE: note.append('展示會有樣品')
    elif r['group']=='Apparel': note.append('無樣品，請看款式圖下單')
    if china: note.append('中國專屬款，韓國售價待原廠提供' if not r['krw'] else '中國專屬款')
    elif not r['krw']: note.append('售價待原廠提供')
    if sizes==['ASSORTED']: note.append('尺寸段待原廠提供，先填總件數')
    if key in MULTI: note.append('原廠同一款號有兩種品名，下單請看品名')
    if re.match(r'\d{4}-',r['batch'] or ''): note.append('延續款')
    if r['batch']=='비시즌': note.append('原廠標示：非當季款')
    krw=int(r['krw']) if r['krw'] else None
    hero=HERO.get(key) or HERO.get(base)
    if key=='27WUPA301': hero='全球主推 STONE MASTER 輕量版，'+('立領好搭' if 'STAND' in U else '連帽款')+'，台灣冬天穿得到'
    if key=='27WUPA300': hero='STONE MASTER 形象款，櫥窗與主牆陳列用，量不用深'
    if key=='27WMRT063' and 'WAFFLE' not in U: hero=None
    it=dict(id=iid,sheet=sheet,no='',mon=mon,monTag=(f'台灣預計 {tm[1]} 月上市' if tm else ''),theme=mon,drop=('DNS' if r['line']=='DNS' else 'FOOTWEAR' if sheet=='鞋款' else 'CORE'),cat=cat,gen=g,style=key,
        zh=f'{zh}（{g}）' if sheet in ('上身','下身') else zh,en=en or '英文品名待原廠提供',color=zc(col),cc=cc,sku=key+(('-'+cc) if cc else ''),icon=r['mat'],
        fab=clean(r['comp']),series=('產地 越南' if r['origin']=='Vietnam' else ''),ov=ov,dt='',tech='',note='；'.join(note),launch=launch,eta='',
        krw=krw,sizes=sizes,doll=(o['doll'] if o else ''),run=key,part='top',whl=bool(hero),whlr=hero or '')
    it['price']=twd(krw); it['tw']=tw_note(it)
    runs.setdefault(key,[])
    for z in sizes:
        if z not in runs[key]: runs[key].append(z)
    L.append(it)
order=['上身','下身','配件','鞋款']; idx={id(x):n for n,x in enumerate(L)}
L.sort(key=lambda x:(order.index(x['sheet']),SER.index(x['mon']) if x['mon'] in SER else 99,idx[id(x)]))
runs={k:sorted(v,key=szkey) for k,v in runs.items()}
sheets=[s for s in order if any(i['sheet']==s for i in L)]
mons=[m for m in SER if any(i['mon']==m for i in L)]+[m for m in dict.fromkeys(i['mon'] for i in L) if m not in SER]
so=sorted({z for v in runs.values() for z in v},key=szkey)
cfg=dict(season='27FW',fx=FX,sheets=sheets,months=mons,szOrder=so,szLabel=SZLABEL)
with open(out+'/data.js','w') as f:
    f.write('window.SDR_ITEMS='+json.dumps(L,ensure_ascii=False)+';\n')
    f.write('window.BY_RUNS='+json.dumps(runs,ensure_ascii=False)+';\n')
    f.write('window.BY_CFG='+json.dumps(cfg,ensure_ascii=False)+';\n')
c=collections.Counter
print(len(L),'styles',len({i['style'] for i in L}),c(i['sheet'] for i in L)); print(c(i['mon'] for i in L)); print(c(i['cat'] for i in L))
print('img',sum(1 for i in L if i['doll']),'hero',sum(1 for i in L if i['whl']),len({i['style'] for i in L if i['whl']}),'tw',sum(1 for i in L if i['tw']),'launch',sum(1 for i in L if i['launch']),'noprice',sum(1 for i in L if not i['krw']),'sample',sum(1 for i in L if '有樣品' in i['note']))
print('hero missing',[k for k in HERO if not any(i['style']==k or i['style'][:9]==k for i in L)])
print('untranslated colors',c(i['color'] for i in L if re.fullmatch(r'[A-Z0-9 /.\-]+',i['color'])).most_common(60))
