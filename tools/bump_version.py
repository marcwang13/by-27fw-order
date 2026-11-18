#!/usr/bin/env python3
"""每次改完要上線前跑：python3 tools/bump_version.py
更新 index.html 內的版本號（V 與 script 的 ?v=）和 version.json。
網頁開啟時會先問 version.json（不走快取），發現自己是舊版就自動換成新版網址，
所以不管從哪個入口進來、瀏覽器存了什麼舊檔，都會拿到最新的。"""
import re, time, json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')
v = time.strftime('%Y%m%d%H%M%S', time.gmtime())
h = open('index.html').read()
h = re.sub(r"var V='[0-9a-z]*';", f"var V='{v}';", h)
h = re.sub(r'(<script src="(?:config|story|data|imgs|photos)\.js)\?v=[0-9a-z]+"', lambda m: f'{m.group(1)}?v={v}"', h)
open('index.html', 'w').write(h)
json.dump({'v': v}, open('version.json', 'w'))
print('version', v)
