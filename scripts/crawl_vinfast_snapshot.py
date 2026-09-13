"""A bounded national snapshot; never claim a census or infer sales from disappearance."""
import json,time,urllib.request,urllib.parse
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    dest=ROOT/'data'/'raw'/'snapshots'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dest.mkdir(parents=True,exist_ok=False)
    seen=set(); records=[]; pages=[]
    for page in range(20):
        params={'cg':2010,'fuel':4,'carbrand':80,'limit':50,'offset':page*50}
        url='https://gateway.chotot.com/v1/public/ad-listing?'+urllib.parse.urlencode(params)
        fetched=datetime.now(timezone.utc).isoformat()
        event={'page':page,'url':url,'fetched_at_utc':fetched}
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'VinFast-Market-Research/1.0','Accept':'application/json'})
            with urllib.request.urlopen(req,timeout=25) as res: payload=json.load(res)
            ads=payload.get('ads',[]); event.update(status=200,rows=len(ads))
            new=[r for r in ads if r.get('list_id') is not None and r['list_id'] not in seen]
            event['new_ids']=len(new)
            for r in ads: records.append({'crawl_date':fetched,'source_url':url,'page':page,'ad':r})
            seen.update(r['list_id'] for r in new)
            pages.append(event); print(page,len(ads),len(seen),flush=True)
            if not ads or not new: break
        except Exception as exc:
            event.update(status=getattr(exc,'code','error'),error=str(exc)); pages.append(event); break
        time.sleep(1.5)
    (dest/'chotot_vinfast_snapshot.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    (dest/'manifest.json').write_text(json.dumps({'query_scope':'national first 20 pages; source ordering; not representative','records':len(records),'unique_ids':len(seen),'pages':pages},ensure_ascii=False,indent=2),encoding='utf-8')
    print(dest)
if __name__=='__main__': main()
