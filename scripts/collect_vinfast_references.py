"""Bounded public collection, timestamped outputs; stop a source on HTTP errors."""
import json, re, time, hashlib, urllib.request, urllib.error
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.skip=0; self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','noscript'): self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style','noscript') and self.skip: self.skip-=1
    def handle_data(self,data):
        if not self.skip and data.strip(): self.parts.append(re.sub(r'\s+',' ',data.strip()))

def main():
    stamp=datetime.now(timezone.utc)
    dest=ROOT/'data'/'external'/('vinfast_'+stamp.strftime('%Y%m%dT%H%M%SZ'))
    dest.mkdir(parents=True,exist_ok=False)
    urls={
      'VF3':'https://shop.vinfastauto.com/vn_vi/dat-coc-xe-dien-vf3.html',
      'VF5':'https://shop.vinfastauto.com/vn_vi/dat-coc-xe-dien-vf5.html',
      'VF6':'https://shop.vinfastauto.com/vn_vi/dat-coc-xe-dien-vf6.html',
      'VF7':'https://shop.vinfastauto.com/vn_vi/dat-coc-xe-dien-vf7.html',
      'VF8':'https://shop.vinfastauto.com/vn_vi/dat-coc-xe-vf8.html',
      'VF9':'https://shop.vinfastauto.com/vn_vi/dat-coc-xe-vf9.html',
      'warranty':'https://vinfastauto.com/vn_vi/chinh-sach-bao-hanh-oto',
      'chotot_probe':'https://gateway.chotot.com/v1/public/ad-listing?cg=2010&fuel=4&carbrand=80&limit=50&offset=0',
      'otodien_probe':'https://otodien.vn/oto',
    }
    manifest=[]
    for key,url in urls.items():
        record={'source_key':key,'source_url':url,'retrieved_at_utc':datetime.now(timezone.utc).isoformat()}
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'VinFast-Market-Research/1.0','Accept':'text/html,application/json'})
            with urllib.request.urlopen(req,timeout=25) as response:
                blob=response.read(); record.update(status=response.status,final_url=response.url,sha256=hashlib.sha256(blob).hexdigest())
            if key=='chotot_probe':
                data=json.loads(blob); ads=data.get('ads',[])
                record['record_count']=len(ads)
                (dest/(key+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
            else:
                html=blob.decode('utf-8',errors='replace')
                (dest/(key+'.html')).write_text(html,encoding='utf-8')
                parser=Text(); parser.feed(html)
                (dest/(key+'.txt')).write_text('\n'.join(parser.parts),encoding='utf-8')
                record['text_lines']=len(parser.parts)
        except Exception as exc:
            record.update(status=getattr(exc,'code','error'),error=str(exc))
        manifest.append(record)
        print(key,record['status'],flush=True)
        time.sleep(1)
    (dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(dest)
if __name__=='__main__': main()
