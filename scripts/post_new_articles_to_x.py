from pathlib import Path
import json, os
ROOT=Path(__file__).resolve().parents[1]
need=['X_API_KEY','X_API_SECRET','X_ACCESS_TOKEN','X_ACCESS_TOKEN_SECRET','SITE_URL']
if any(not os.environ.get(k) for k in need):
    print('X設定が未登録なので自動投稿をスキップします')
    raise SystemExit(0)
import tweepy
arts=json.loads((ROOT/'data/articles.json').read_text(encoding='utf-8'))
status_path=ROOT/'data/x-posted.json'
posted=json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else {}
client=tweepy.Client(consumer_key=os.environ['X_API_KEY'],consumer_secret=os.environ['X_API_SECRET'],access_token=os.environ['X_ACCESS_TOKEN'],access_token_secret=os.environ['X_ACCESS_TOKEN_SECRET'])
base=os.environ['SITE_URL'].rstrip('/')
changed=False
for a in reversed(arts):
    slug=a['slug']
    if posted.get(slug): continue
    copy=(a.get('x_post') or a['title']).strip()
    url=f'{base}/articles/{slug}.html'
    text=f'{copy}\n\n{url}'
    if len(text)>275: text=text[:270].rstrip()+'…\n'+url
    r=client.create_tweet(text=text)
    posted[slug]=str(r.data.get('id','posted'))
    changed=True
if changed:
    status_path.write_text(json.dumps(posted,ensure_ascii=False,indent=2),encoding='utf-8')
print('X posting complete')
