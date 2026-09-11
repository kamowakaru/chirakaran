from pathlib import Path
import json, hashlib
try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
except ImportError:
    raise SystemExit('Pillow が必要です: pip install pillow')

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets/images/thumbnail-source'
OUT=ROOT/'assets/images/generated-thumbnails'; OUT.mkdir(parents=True,exist_ok=True)
articles=json.loads((ROOT/'data/articles.json').read_text(encoding='utf-8'))

def font(size):
    candidates=['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
    for p in candidates:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def wrap(draw,text,f,maxw):
    lines=[]; cur=''
    for ch in text:
        if draw.textbbox((0,0),cur+ch,font=f)[2] <= maxw: cur+=ch
        else:
            if cur: lines.append(cur)
            cur=ch
    if cur: lines.append(cur)
    return lines[:3]

for a in articles:
    files=[]
    d=SRC/a['category']
    if d.exists(): files=[p for p in d.iterdir() if p.suffix.lower() in {'.jpg','.jpeg','.png','.webp'}]
    if files:
        idx=int(hashlib.sha256(a['slug'].encode()).hexdigest()[:8],16)%len(files)
        im=Image.open(sorted(files)[idx]).convert('RGB').resize((1200,630))
        im=ImageEnhance.Brightness(im).enhance(.72)
    else:
        im=Image.new('RGB',(1200,630),(239,239,223))
    draw=ImageDraw.Draw(im); f=font(60); small=font(27)
    y=175
    for line in wrap(draw,a['title'],f,1000):
        draw.text((100,y),line,font=f,fill='white',stroke_width=2,stroke_fill=(40,50,35)); y+=82
    draw.text((103,520),'チラカラン  |  ズボラでも、ちゃんと散らからん。',font=small,fill='white')
    im.save(OUT/f"{a['slug']}.webp",'WEBP',quality=86,method=6)
print(f'Generated {len(articles)} thumbnails')
