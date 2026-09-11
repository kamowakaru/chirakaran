from pathlib import Path
import json, hashlib
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets/images/thumbnail-source'
SCENES=ROOT/'assets/images/article-scenes'
OUT=ROOT/'assets/images/generated-thumbnails'; OUT.mkdir(parents=True,exist_ok=True)
articles=json.loads((ROOT/'data/articles.json').read_text(encoding='utf-8'))

def candidates(article):
    files=[]
    d=SRC/article['category']
    if d.exists():
        files += [p for p in d.iterdir() if p.suffix.lower() in {'.jpg','.jpeg','.png','.webp'}]
    # Existing lifestyle scenes are valid fallbacks. They may be reused until each category gets its own photo bank.
    if not files and SCENES.exists():
        files += [p for p in SCENES.iterdir() if p.suffix.lower() in {'.jpg','.jpeg','.png','.webp'}]
    return sorted(files)

for a in articles:
    files=candidates(a)
    if files:
        idx=int(hashlib.sha256(a['slug'].encode()).hexdigest()[:8],16)%len(files)
        with Image.open(files[idx]) as src:
            im=src.convert('RGB')
            im=ImageOps.fit(im,(1600,900),method=Image.Resampling.LANCZOS,centering=(0.5,0.5))
    else:
        im=Image.new('RGB',(1600,900),(239,239,223))
    # Photo only: no title, label, logo or other baked-in text.
    im.save(OUT/f"{a['slug']}.webp",'WEBP',quality=92,method=6)
print(f'Generated {len(articles)} photo-only thumbnails')
