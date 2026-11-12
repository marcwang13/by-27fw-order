"""2026-11-12 分類與款式圖更正（直接改 data.js）。用法：python3 tools/post_1112_fix.py <data.js> ss|fw
重產資料（gen_fw2.py／gen2.py）後要再跑一次。"""
import json,re,sys,os
p,which=sys.argv[1],sys.argv[2]
s=open(p,encoding='utf-8').read()
d={a:json.loads(b) for a,b in re.findall(r'window\.(\w+)=(.*?);\n(?=window\.|$)',s,re.S)}
it=d['SDR_ITEMS']; log=[]
def setf(pred,**kw):
    n=0
    for i in it:
        if pred(i):
            for k,v in kw.items(): i[k]=v
            n+=1
    return n
def spec_sheet_hashes():
    # 原廠整頁工藝單縮成 118 像素寬的小圖（韓文表格、尺寸、設計師欄位），看不清也不該給經銷商：小圖且整體偏亮
    from PIL import Image
    import numpy as np
    big=os.path.join(os.path.dirname(os.path.abspath(p)),'big'); out=set()
    for h in {i['doll'] for i in it if i.get('doll')}:
        im=Image.open(os.path.join(big,h+'.jpg'))
        if im.size[0]<=150 and np.asarray(im.convert('L')).mean()>=215: out.add(h)
    return out
if which=='ss':
    sp=spec_sheet_hashes(); log.append(('工藝單縮圖 %d 張'%len(sp),'移除款式圖',setf(lambda i:i.get('doll') in sp,doll='')))
    # 配件分頁裡的衣服 → 上身
    mv={'1BYETMW003':'排汗衣','1BYETMW004':'排汗衣','1BYETMW503':'排汗衣','1BYETMW504':'排汗衣','1BYETMW505':'排汗衣',
        '1BYETMW001':'背心','1BYETMW501':'背心','1BYETMW002':'無袖上衣','1BYETMW502':'無袖上衣','1BYETMW901':'無袖上衣','1BYETSW001':'連帽衫'}
    for st,c in mv.items(): log.append((st,'配件→上身 '+c,setf(lambda i:i['style']==st,sheet='上身',cat=c)))
    for st in ('2BYHTMW501','2BYHTMW502','2BYHTXW501'): log.append((st,'性別→女',setf(lambda i:i['style']==st,gen='女')))
else:
    log.append(('27XWET070','性別 男→女',setf(lambda i:i['style']=='27XWET070',gen='女',zh='網眼緹花底層無袖上衣（女）')))
    for st,c in (('27FMKT042','POLO衫'),('27FWKT005','POLO衫'),('27WMKT060','POLO衫'),('27FMYS037','襯衫'),('27FMYS038','襯衫'),('27XMET070','無袖上衣'),('27XWET070','無袖上衣'),
                 ('27WMPD652','背心'),('27WWPD653','背心'),('27WUHD309','連帽衫')):
        log.append((st,'品類→'+c,setf(lambda i:i['style']==st,cat=c)))
    log.append(('遠征羽絨外套 中性 背心','品類→羽絨外套',setf(lambda i:i['id']=='English name pending-0~4',cat='羽絨外套')))
    bad={'db1896a9b928':'布料吊牌實拍照','1c636148f831':'韓文表頭設計稿，且外套與長褲共用'}
    for h,why in bad.items(): log.append((h,'移除款式圖：'+why,setf(lambda i:i.get('doll')==h,doll='')))
    for st in ('27WMSB070','27WWSB070'): log.append((st,'移除款式圖：長褲誤用外套圖',setf(lambda i:i['style']==st and i.get('doll'),doll='')))
    for iid,why in (('27FWRT008-TN','布料吊牌實拍'),('27UWPA156-HE','空白圖')):
        log.append((iid,'移除款式圖：'+why,setf(lambda i:i['id']==iid,doll='')))
    log.append(('27WWPA101-DU','移除款式圖：模特兒實拍',setf(lambda i:i['id']=='27WWPA101-DU',doll='')))
for l in log: print(l)
open(p,'w',encoding='utf-8').write(''.join(f'window.{a}={json.dumps(v,ensure_ascii=False)};\n' for a,v in d.items()))
