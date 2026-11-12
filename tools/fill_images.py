"""讓每個款色都有款式圖（2026-11-12 Marc 指示：都要有圖最重要）。
用法：python3 tools/fill_images.py <data.js> [<移除前的 data.js>] [--write]
沒圖的款色依序借：1) 同款號其他顏色的圖 2)（若給移除前版本）自己原本被移除的小圖工藝單 3) 同品名、同品類、不同性別的款。
借來的圖顏色可能不同，卡片上仍標自己的色名。重產資料後要再跑。"""
import json,re,sys,os
from PIL import Image
import numpy as np
args=[a for a in sys.argv[1:] if not a.startswith('--')]; write='--write' in sys.argv
p=args[0]; s=open(p,encoding='utf-8').read()
d={a:json.loads(b) for a,b in re.findall(r'window\.(\w+)=(.*?);\n(?=window\.|$)',s,re.S)}; it=d['SDR_ITEMS']
prev={}
if len(args)>1:
    ps=open(args[1],encoding='utf-8').read()
    prev={i['id']:i.get('doll','') for i in json.loads(re.search(r'window\.SDR_ITEMS=(.*?);\nwindow\.',ps,re.S).group(1))}
base=re.compile(r'（[男女中性]+）')
def key(i): return base.sub('',i['zh'])
n0=sum(1 for i in it if not i.get('doll')); st={}
for i in it:
    if i.get('doll'): st.setdefault(i['style'],i['doll'])
cnt={'同款其他色':0,'原小圖':0,'同名他性別':0}
nm={}
for i in it:
    if i.get('doll'): nm.setdefault((key(i),i['cat'],i['sheet']),i['doll'])
for i in it:
    if i.get('doll'): continue
    if i['style'] in st: i['doll']=st[i['style']]; cnt['同款其他色']+=1
    elif prev.get(i['id']): i['doll']=prev[i['id']]; cnt['原小圖']+=1
    elif (key(i),i['cat'],i['sheet']) in nm: i['doll']=nm[(key(i),i['cat'],i['sheet'])]; cnt['同名他性別']+=1
# 同款借圖後，同款色可能還有 prev 小圖，不再處理
left=[i['id'] for i in it if not i.get('doll')]
print('原本沒圖',n0,'補圖',cnt,'仍沒圖',len(left),left[:40])
if write: open(p,'w',encoding='utf-8').write(''.join(f'window.{a}={json.dumps(v,ensure_ascii=False)};\n' for a,v in d.items()))
