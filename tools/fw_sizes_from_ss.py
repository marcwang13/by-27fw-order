"""27FW 服裝尺寸段：原廠還沒給，先照 27SS 同性別、同類型款式最常見的尺寸段填。
用法：python3 tools/fw_sizes_from_ss.py <FW data.js> <SS data.js> [--write]
規則：
- 以「款」為單位統計 27SS 尺寸段，取同（分頁、性別、類型）至少 1/3 款有的尺寸（寧可多給，不要擋住客人要下的尺寸）。
- FW 類型對照：羽絨／刷毛／鋪棉／套裝外套 → 外套；長袖／短袖／其他T恤 → 圓領T恤；其餘同名。
- 27SS 該性別沒有的類型：中性改用男款，仍沒有就用同分頁同性別全部款式。
- 下身 27SS 有英文字母（S/M/L）與腰圍數字兩套，FW 長褲／短褲沿用 27SS 該類型款數較多的那套。
"""
import json,re,sys,collections as C
fwp,ssp=sys.argv[1],sys.argv[2]; write='--write' in sys.argv
def load(p):
    s=open(p,encoding='utf-8').read()
    return {a:json.loads(b) for a,b in re.findall(r'window\.(\w+)=(.*?);\n(?=window\.|$)',s,re.S)}
fw,ss=load(fwp),load(ssp)
CATMAP={'羽絨外套':['外套'],'刷毛外套':['外套'],'鋪棉外套':['鋪棉外套','外套'],'套裝外套':['套裝外套','外套'],
        '長袖T恤':['圓領T恤'],'短袖T恤':['圓領T恤'],'其他T恤':['圓領T恤']}
styles={}
for i in ss['SDR_ITEMS']:
    if i['sheet'] in('上身','下身'): styles[i['style']]=(i['sheet'],i['gen'],i['cat'],tuple(i['sizes']))
pool=C.defaultdict(C.Counter)
for sh,g,c,sz in styles.values(): pool[(sh,g,c)][sz]+=1
ORDER=ss['BY_CFG']['szOrder']
def isnum(sz): return all(z.isdigit() for z in sz)
def pick(counter):
    # 下身先選款數較多的那套（字母／腰圍數字），再取該套裡至少 1/3 款有的尺寸，避免漏掉客人要下的尺寸
    sysn=C.Counter()
    for sz,c in counter.items(): sysn[isnum(sz)]+=c
    use=max(sysn.items(),key=lambda kv:(kv[1],kv[0]))[0]
    sub={sz:c for sz,c in counter.items() if isnum(sz)==use}
    tot=sum(sub.values()); freq=C.Counter()
    for sz,c in sub.items():
        for z in sz: freq[z]+=c
    keep=[z for z in freq if freq[z]*3>=tot]
    return tuple(sorted(keep,key=ORDER.index))
def lookup(sheet,gen,cat):
    cats=CATMAP.get(cat,[])+[cat] if cat not in CATMAP.get(cat,[]) else CATMAP[cat]
    seen=[]
    for g in ([gen] if gen!='中性' else ['中性','男']) + ([] ):
        for c in dict.fromkeys(CATMAP.get(cat,[])+[cat]):
            if (sheet,g,c) in pool:
                return pick(pool[(sheet,g,c)]),f'{g}{c}'
    cnt=C.Counter()
    for (sh,g,c),v in pool.items():
        if sh==sheet and g==('男' if gen=='中性' else gen): cnt.update(v)
    return pick(cnt),f'{sheet}{gen}全部'
n=0; log=C.Counter(); bystyle={}
for i in fw['SDR_ITEMS']:
    if i['sizes']!=['ASSORTED']: continue
    if i['style'] not in bystyle:
        bystyle[i['style']]=lookup(i['sheet'],i['gen'],i['cat'])
    sz,src=bystyle[i['style']]
    i['sizes']=list(sz)
    i['note']=re.sub(r'(^|；)尺寸段待原廠提供，先填總件數','',i['note']).lstrip('；')
    n+=1
for st,(sz,src) in bystyle.items():
    fw['BY_RUNS'][st]=list(sz); log[(src,sz)]+=1
print('items',n,'styles',len(bystyle))
for (src,sz),c in sorted(log.items()): print(f'{c:3d} 款 ← 27SS {src}: {"/".join(sz)}')
# 尺寸排序與標籤用 27SS 的（含數字尺碼），FW 原有的尺寸另外補在後面
order=list(ss['BY_CFG']['szOrder'])
for z in fw['BY_CFG']['szOrder']:
    if z not in order: order.append(z)
fw['BY_CFG']['szOrder']=order
if write:
    open(fwp,'w',encoding='utf-8').write(''.join(f'window.{a}={json.dumps(v,ensure_ascii=False)};\n' for a,v in fw.items()))
    print('written')
