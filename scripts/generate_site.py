from pathlib import Path
import json, csv, re, html, hashlib
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT/'content/articles'
THUMB_DIR = ROOT/'assets/images/generated-thumbnails'


def parse_frontmatter(text):
    if not text.startswith('---'):
        raise ValueError('front matter がありません')
    parts=text.split('---',2)
    fm_lines=parts[1].strip().splitlines(); body=parts[2].lstrip('\n')
    data={}; current=None
    for raw in fm_lines:
        line=raw.rstrip()
        if not line.strip(): continue
        if re.match(r'^\s+-\s+',line) and current:
            data.setdefault(current,[]).append(re.sub(r'^\s+-\s+','',line).strip().strip('"\'')); continue
        if ':' not in line: continue
        key,value=line.split(':',1); key=key.strip(); value=value.strip(); current=key
        data[key]=[] if not value else value.strip('"\'')
    return data,body

def inline(text):
    text=html.escape(text)
    text=re.sub(r'\*\*(.+?)\*',r'<strong>\1</strong>',text)
    text=re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    text=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'<a href="\2" rel="noopener" target="_blank">\1</a>',text)
    return text

def md_to_html(md):
    lines=md.splitlines(); out=[]; para=[]; in_ul=False; in_ol=False
    def fp():
        nonlocal para
        if para: out.append('<p>'+inline(' '.join(x.strip() for x in para))+'</p>'); para=[]
    def cl():
        nonlocal in_ul,in_ol
        if in_ul: out.append('</ul>'); in_ul=False
        if in_ol: out.append('</ol>'); in_ol=False
    for line in lines:
        if not line.strip(): fp(); cl(); continue
        m=re.match(r'^!\[([^]]*)\]\(([^)]+)\)$', line.strip())
        if m:
            fp(); cl(); alt,url=m.group(1),m.group(2); out.append(f'<figure class="article-scene"><img src="{html.escape(url, quote=True)}" alt="{html.escape(alt)}" loading="lazy"><figcaption>{html.escape(alt)}</figcaption></figure>'); continue
        m=re.match(r'^(#{2,4})\s+(.+)$',line)
        if m:
            fp(); cl(); n=len(m.group(1)); title=m.group(2).strip(); out.append(f'<h{n}>{inline(title)}</h{n}>'); continue
        m=re.match(r'^[-*]\s+(.+)$',line)
        if m:
            fp();
            if in_ol: out.append('</ol>'); in_ol=False
            if not in_ul: out.append('<ul>'); in_ul=True
            out.append('<li>'+inline(m.group(1))+'</li>'); continue
        m=re.match(r'^\d+\.\s+(.+)$',line)
        if m:
            fp();
            if in_ul: out.append('</ul>'); in_ul=False
            if not in_ol: out.append('<ol>'); in_ol=True
            out.append('<li>'+inline(m.group(1))+'</li>'); continue
        para.append(line)
    fp(); cl(); return '\n'.join(out)

def shell(title, body, prefix='../', desc=''):
    return f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{html.escape(desc)}"><title>{html.escape(title)} | チラカラン</title><link rel="stylesheet" href="{prefix}assets/css/style.css"></head><body data-root="{prefix}"><header class="site-header"><div class="container header-inner"><a class="brand text-brand" href="{prefix}index.html"><span class="brand-mark"><svg class="brand-house" viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 10.5 12 3.8l8.5 6.7v9.2a1 1 0 0 1-1 1h-15a1 1 0 0 1-1-1z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M9 20.7v-6.4h6v6.4M8.3 9.6h7.4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg></span><span><strong>チラカラン</strong><small>ズボラでも、ちゃんと散らからん。</small></span></a><button class="menu-btn" aria-label="メニュー">☰</button><nav class="nav"><a href="{prefix}index.html">ホーム</a><a href="{prefix}index.html#categories">カテゴリ</a><a href="{prefix}articles.html">記事一覧</a><a href="{prefix}about.html">このサイトについて</a></nav><form class="header-search" action="{prefix}search.html"><input name="q" type="search" placeholder="めんどくさいことを検索…"><button>🔍</button></form></div></header>{body}<footer class="footer"><div class="container footer-inner"><div><strong>チラカラン</strong><div style="font-size:12px;color:#73806f">ズボラでも、ちゃんと散らからん。</div></div><div class="footer-links"><a href="{prefix}index.html">ホーム</a><a href="{prefix}articles.html">記事一覧</a><a href="{prefix}about.html">このサイトについて</a><a href="{prefix}privacy.html">プライバシーポリシー</a></div></div><p class="copyright">© 2026 チラカラン</p></footer><script src="{prefix}assets/js/site.js"></script></body></html>'''

categories=json.loads((ROOT/'data/categories.json').read_text(encoding='utf-8'))
tags=json.loads((ROOT/'data/tags.json').read_text(encoding='utf-8'))
catmap={x['slug']:x for x in categories}; tagmap={x['slug']:x for x in tags}
affiliate_cfg=json.loads((ROOT/'data/affiliate-shops.json').read_text(encoding='utf-8'))
affiliate_shops=[x for x in affiliate_cfg.get('shops',[]) if x.get('enabled') and x.get('url_template')]
affiliate_disclosure=affiliate_cfg.get('disclosure','')
articles=[]; bodies={}; fms={}
for fp in sorted(x for x in CONTENT.glob('*.md') if not x.name.startswith('_')):
    fm,body=parse_frontmatter(fp.read_text(encoding='utf-8')); slug=fp.stem
    for k in ['title','date','category','tags','description']:
        if k not in fm: raise ValueError(f'{fp.name}: {k} がありません')
    if fm['category'] not in catmap: raise ValueError(f'{fp.name}: 未登録カテゴリ')
    bad=[t for t in fm['tags'] if t not in tagmap]
    if bad: raise ValueError(f'{fp.name}: 未登録タグ {bad}')
    generated=f'assets/images/generated-thumbnails/{slug}.webp'
    fallback='assets/images/thumbnail-fallback.svg'
    thumb=generated if (ROOT/generated).exists() else fallback
    a={'slug':slug,'title':fm['title'],'date':fm['date'],'category':fm['category'],'tags':fm['tags'],'description':fm['description'],'thumbnail':thumb,'x_post':fm.get('x_post',''),'related_products':fm.get('related_products',[])}
    articles.append(a); bodies[slug]=body; fms[slug]=fm
articles.sort(key=lambda a:(a['date'],a['slug']),reverse=True)
(ROOT/'data/articles.json').write_text(json.dumps(articles,ensure_ascii=False,indent=2),encoding='utf-8')

# analytics rows
csv_path=ROOT/'data/analytics-pageviews.csv'; old={}
if csv_path.exists():
    with csv_path.open(encoding='utf-8') as f:
        for r in csv.DictReader(f): old[r['path']]=r.get('views','0')
with csv_path.open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f); w.writerow(['path','views'])
    for a in articles: w.writerow([f"/articles/{a['slug']}.html",old.get(f"/articles/{a['slug']}.html",'0')])

adir=ROOT/'articles'; adir.mkdir(exist_ok=True)
for p in adir.glob('*.html'): p.unlink()
for a in articles:
    cat=catmap[a['category']]
    chips=''.join(f'<a class="tag-link" href="../tags/{t}.html">{html.escape(tagmap[t]["name"])}</a>' for t in a['tags'])
    products=''
    if a['related_products']:
        cards=[]
        for product in a['related_products']:
            # 記事側には商品名/検索キーワードだけ保存。各ショップへのリンクは中央設定から生成。
            keyword=str(product).strip()
            buttons=[]
            for shop in affiliate_shops:
                url=shop['url_template'].replace('{query}', quote(keyword, safe='')).replace('{query_raw}', keyword)
                buttons.append(f'<a class="shop-btn shop-{html.escape(shop["id"])}" href="{html.escape(url, quote=True)}" rel="nofollow sponsored noopener" target="_blank">{html.escape(shop["name"])}で見る</a>')
            if buttons:
                action='<div class="shop-buttons">'+''.join(buttons)+'</div>'
            else:
                action='<p class="affiliate-pending">ショップ連携後に購入先ボタンが表示されます。</p>'
            cards.append(f'<div class="product-card"><strong>{html.escape(keyword)}</strong>{action}</div>')
        disclosure=f'<p class="affiliate-disclosure">{html.escape(affiliate_disclosure)}</p>' if affiliate_disclosure else ''
        products=f'<section class="product-note"><h2>この悩みで使いやすいアイテム</h2>{disclosure}<div class="product-cards">{"".join(cards)}</div></section>'
    page=f'''<main class="article-main"><div class="container article-layout"><article class="article-body"><div class="breadcrumb"><a href="../index.html">ホーム</a> › <a href="../categories/{cat['slug']}.html">{html.escape(cat['name'])}</a></div><div class="meta"><span class="chip">{html.escape(cat['name'])}</span>{chips}<time>{a['date'].replace('-','.')}</time></div><h1>{html.escape(a['title'])}</h1><p class="lead">{html.escape(a['description'])}</p><img src="../{a['thumbnail']}" alt="{html.escape(a['title'])}のサムネイル" class="article-thumb">{md_to_html(bodies[a['slug']])}{products}<div class="point yellow"><strong>チラカランの考え方</strong><p>頑張る回数を増やすより、頑張らなくても回る仕組みを。</p></div><h2>関連記事</h2><div class="article-grid" data-related data-category="{a['category']}" data-slug="{a['slug']}"></div></article><aside><div class="sidebox"><h3>この記事のカテゴリ</h3><a class="outline-btn" href="../categories/{cat['slug']}.html">{html.escape(cat['name'])} →</a></div><div class="sidebox"><h3>人気のタグ</h3><div class="tag-cloud" data-popular-tags></div></div></aside></div></main>'''
    (adir/f"{a['slug']}.html").write_text(shell(a['title'],page,desc=a['description']),encoding='utf-8')

# category/tag pages
cdir=ROOT/'categories'; cdir.mkdir(exist_ok=True)
for p in cdir.glob('*.html'): p.unlink()
for c in categories:
    body=f'''<main><section class="page-hero"><div class="container"><div class="breadcrumb"><a href="../index.html">ホーム</a> › {html.escape(c['name'])}</div><h1>{c['icon']} {html.escape(c['name'])}</h1><p>{html.escape(c['description'])}</p></div></section><section class="section"><div class="container"><div class="list-grid" data-collection="category" data-key="{c['slug']}"></div></div></section></main>'''
    (cdir/f"{c['slug']}.html").write_text(shell(c['name'],body),encoding='utf-8')
tdir=ROOT/'tags'; tdir.mkdir(exist_ok=True)
for p in tdir.glob('*.html'): p.unlink()
for t in tags:
    body=f'''<main><section class="page-hero"><div class="container"><h1>#{html.escape(t['name'])}</h1></div></section><section class="section"><div class="container"><div class="list-grid" data-collection="tag" data-key="{t['slug']}"></div></div></section></main>'''
    (tdir/f"{t['slug']}.html").write_text(shell('タグ：'+t['name'],body),encoding='utf-8')
print(f'Generated {len(articles)} articles')
