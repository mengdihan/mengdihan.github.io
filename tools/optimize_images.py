"""Create responsive display images; preserve original links for zoom/download."""
from pathlib import Path
from urllib.parse import urlsplit, unquote
import hashlib
from lxml import html
from PIL import Image, ImageOps

def optimize_images(root):
    root=Path(root);cache={};used=0;before=after=0
    target=root/'images/optimized';target.mkdir(parents=True,exist_ok=True)
    for page in root.rglob('*.html'):
        if any(part in ('preview','outputs','tools') for part in page.relative_to(root).parts):continue
        try:doc=html.parse(str(page))
        except (ValueError,html.etree.ParserError):continue
        changed=False
        for node in doc.xpath('//img[@src]'):
            src=node.get('src');url=urlsplit(src)
            if url.scheme or url.netloc or '/optimized/' in url.path or '/previews/' in url.path:continue
            source=(root/unquote(url.path).lstrip('/')) if url.path.startswith('/') else (page.parent/unquote(url.path)).resolve()
            if not source.is_relative_to(root.resolve()) or not source.is_file() or source.suffix.lower() not in ('.jpg','.jpeg','.png','.webp'):continue
            if source.stat().st_size<80000:continue
            if source not in cache:
                with Image.open(source) as original:
                    if getattr(original,'is_animated',False):cache[source]=None;continue
                    im=ImageOps.exif_transpose(original)
                    if im.mode not in ('RGB','RGBA'):im=im.convert('RGBA' if 'transparency' in im.info else 'RGB')
                    key=hashlib.sha256(source.read_bytes()).hexdigest()[:20]
                    variants=[]
                    for width in sorted(set([min(640,im.width),min(1280,im.width)])):
                        copy=im.copy();copy.thumbnail((width,100000))
                        dest=target/f'{key}-{width}.webp';copy.save(dest,'WEBP',quality=84,method=4)
                        variants.append(('/'+str(dest.relative_to(root)),copy.width,copy.height,dest.stat().st_size))
                    cache[source]=variants if variants[-1][3]<source.stat().st_size*.9 else None
            variants=cache[source]
            if not variants:continue
            node.set('data-original-src',src)
            node.set('src',variants[-1][0]);node.set('srcset',', '.join(f'{v[0]} {v[1]}w' for v in variants))
            node.set('sizes','(max-width: 700px) 100vw, 960px')
            node.set('width',str(variants[-1][1]));node.set('height',str(variants[-1][2]))
            node.set('decoding','async')
            if not node.get('loading'):node.set('loading','lazy')
            if node.get('fetchpriority')=='high':node.set('loading','eager')
            used+=1;before+=source.stat().st_size;after+=variants[-1][3];changed=True
        if changed:page.write_bytes(html.tostring(doc,encoding='utf8',doctype='<!DOCTYPE html>'))
    print(f'Optimized {used} image placements: {before:,} -> {after:,} bytes (desktop previews); original links preserved.')

if __name__=='__main__':
    import sys
    optimize_images(Path(sys.argv[1]).resolve())
