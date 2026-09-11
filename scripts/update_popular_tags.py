from pathlib import Path
import csv, json
BASE=Path(__file__).resolve().parents[1]
articles=json.loads((BASE/'data/articles.json').read_text(encoding='utf-8'))
tags=json.loads((BASE/'data/tags.json').read_text(encoding='utf-8'))
views={}
with (BASE/'data/analytics-pageviews.csv').open(encoding='utf-8') as f:
    for r in csv.DictReader(f):
        try: views[r['path']]=int(r['views'])
        except: views[r['path']]=0
scores={t['slug']:0 for t in tags}
counts={t['slug']:0 for t in tags}
for a in articles:
    v=views.get(f"/articles/{a['slug']}.html",0)
    for t in a['tags']:
        scores[t]+=v; counts[t]+=1
# アクセス数がまだ無いときは記事数を仮スコアにする
for t in scores:
    if sum(scores.values())==0: scores[t]=counts[t]
name={t['slug']:t['name'] for t in tags}
out=[{'slug':k,'name':name[k],'score':v} for k,v in scores.items() if v>0]
out=sorted(out,key=lambda x:(-x['score'],x['name']))[:8]
(BASE/'data/popular-tags.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('updated popular-tags.json')
