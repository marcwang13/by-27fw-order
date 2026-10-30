import sys,re,json,xml.etree.ElementTree as ET
ns={'s':'urn:schemas-microsoft-com:office:spreadsheet'}
def load(p):
    root=ET.parse(p).getroot()
    out={}
    for ws in root.findall('s:Worksheet',ns):
        rows=[]
        for r in ws.findall('.//s:Row',ns):
            vals=[];
            for c in r.findall('s:Cell',ns):
                idx=c.get('{urn:schemas-microsoft-com:office:spreadsheet}Index')
                if idx:
                    while len(vals)<int(idx)-1: vals.append(None)
                d=c.find('s:Data',ns); vals.append(d.text if d is not None else None)
            rows.append(vals)
        out[ws.get('{urn:schemas-microsoft-com:office:spreadsheet}Name')]=rows
    return out
if __name__=='__main__':
    d=load(sys.argv[1])
    for k,v in d.items():
        print('==',k,len(v)); print(v[0]);
        for r in v[1:4]: print([ (x[:80] if isinstance(x,str) else x) for x in r])
