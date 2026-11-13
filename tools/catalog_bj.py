import json,re
def load_bj():
  rows=[]
  for ln in open('/tmp/w/bj_list.txt'):
    ln=ln.strip()
    if not ln or ln.startswith('#'): continue
    st,rest=ln.split('|',1)
    # split by ; but notes may contain ; no
    for part in rest.split(';'):
      bits=part.split('|'); c,q=bits[0].rsplit('=',1)
      rows.append(dict(style=st,color=c,qty=int(q),note=bits[1] if len(bits)>1 else ''))
  return rows
def items(path='/home/claude/by-27fw-order/data.js'):
  return json.loads(re.search(r'window\.SDR_ITEMS=(\[.*?\]);\s*\n',open(path).read(),re.S).group(1))
N=lambda s:re.sub(r'[^A-Z0-9]','',(s or '').upper())
def en_of(c):
  m=re.search(r'([A-Z][A-Z0-9 ./&\-]*)$',c or ''); return m.group(1).strip() if m else ''
