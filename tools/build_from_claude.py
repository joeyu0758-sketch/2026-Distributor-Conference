#!/usr/bin/env python3
"""Turn the Claude version of the site (one HTML file with embedded photos)
into this GitHub Pages site: index.html plus photos in img/.

Usage:  python3 tools/build_from_claude.py <claude-page.html> [<repo-dir>]

The Claude version stays the master copy. Run this after every change there,
then commit and push; GitHub Pages republishes automatically.
"""
import base64, hashlib, json, os, sys

TAG = '<script type="application/json" id="site-data">'

HEAD = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="{desc}">
<meta name="theme-color" content="#F2F0EB">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<style>:root{{color-scheme:light;box-sizing:border-box}}body{{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#F2F0EB;color:#141413}}img{{max-width:100%}}[hidden]:not([hidden=until-found i]){{display:none!important}}</style>
</head><body>
'''


def main(src, repo):
    s = open(src, encoding='utf-8').read()
    i = s.find(TAG)
    if i < 0:
        sys.exit('site data not found in ' + src)
    i += len(TAG)
    j = s.find('</script>', i)
    data = json.loads(s[i:j])

    img_dir = os.path.join(repo, 'img')
    os.makedirs(img_dir, exist_ok=True)
    keep = set()

    def extract(items, prefix):
        for k, h in enumerate(items):
            v = h.get('img') if isinstance(h, dict) else None
            if isinstance(v, str) and v.startswith('data:'):
                raw = base64.b64decode(v.split(',', 1)[1])
                # the content hash in the name means a changed photo never shows a stale cached copy
                name = f'{prefix}-{k + 1:02d}-{hashlib.sha1(raw).hexdigest()[:8]}.jpg'
                with open(os.path.join(img_dir, name), 'wb') as f:
                    f.write(raw)
                h['img'] = 'img/' + name
            if isinstance(h, dict) and isinstance(h.get('img'), str) and h['img'].startswith('img/'):
                keep.add(h['img'][4:])

    extract(data.get('wheel', []), 'wheel')
    extract(data.get('layers', {}).get('items', []), 'layers')
    extract(data.get('rides', {}).get('items', []), 'rides')

    removed = 0
    for f in os.listdir(img_dir):
        if f not in keep:
            os.remove(os.path.join(img_dir, f))
            removed += 1

    js = json.dumps(data, ensure_ascii=False, indent=1).replace('</', '<\\/')
    s = s[:i] + js + s[j:]

    # swap Claude's page wrapper for a normal web-page head
    t = s.find('<title>')
    title = data.get('site', {}).get('title') or 'Maxxis 2026 Distributor Conference'
    s = HEAD.format(desc=title.replace('"', '&quot;')) + s[t:]
    if not s.rstrip().endswith('</html>'):
        s = s.rstrip() + '\n</body></html>\n'

    with open(os.path.join(repo, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(s)
    print(f'index.html written ({len(s):,} bytes); {len(keep)} photos in img/; {removed} old photo files removed')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
