from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from datetime import datetime,timezone
import json
from workflow import ROOT,OUT,validate_slides,slides
class Page(HTMLParser):
 def __init__(self,p):
  super().__init__();self.ids=set();self.links=[];self.h1=0;self.lang=False;self.feed(p.read_text(encoding='utf-8'))
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='html':self.lang=a.get('lang')=='zh-Hant'
  if t=='h1':self.h1+=1
  if 'id' in a:assert a['id'] not in self.ids;self.ids.add(a['id'])
  for k in ['href','src']:
   if a.get(k):self.links.append(a[k])
  if t=='img':assert a.get('alt')
pages={p.resolve():Page(p) for p in OUT.rglob('*.html')}
links=0
for p,page in pages.items():
 assert page.h1==1 and page.lang,(p,'heading/language')
 for url in page.links:
  u=urlsplit(url)
  if u.scheme or u.netloc:continue
  assert not u.path.startswith('/'),(p,url,'absolute URL')
  target=(p.parent/unquote(u.path)).resolve() if u.path else p
  assert target.is_relative_to(OUT.resolve()) and target.is_file(),(p,url,'broken link')
  if u.fragment and target.suffix=='.html':assert unquote(u.fragment) in pages[target].ids,(p,url,'anchor')
  links+=1
assert len(slides)==15 and not validate_slides(slides)
sources=json.loads((ROOT/'records/ingest-manifest.json').read_text(encoding='utf-8'))
assert len(sources)>=5
result=dict(time=datetime.now(timezone.utc).isoformat(),status='pass',html_pages=len(pages),local_urls=links,independent_ingested_sources=len(sources),slides=15,claim_mapping_errors=0,scope='Structural checks only, not semantic or ANSYS verification')
for p in [ROOT/'records/validation.json',OUT/'records/validation.json']:p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
