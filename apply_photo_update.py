#!/usr/bin/env python3
"""Small, repeatable RunTime photo update; run from within the website repository.

Run:
    python3 apply_photo_update.py

Or from another directory:
    python3 apply_photo_update.py /path/to/runtime-dive-systems
"""
from pathlib import Path
import sys
import json
import shutil

repo = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv)>1 else Path.cwd()
source = Path(__file__).resolve().parent
build = repo / 'build.py'
products = repo / 'content/products.json'
assert build.is_file() and products.is_file(), f'Run this against the RunTime repo, not an arbitrary folder: {repo}'

# Check both expected source locations before making any changes.
b = build.read_text()
p = products.read_text()
about_asset = 'assets/photos/about-josh-ccr.jpg'
mount_asset = 'assets/photos/dpv-light-ball-mount-installed.jpg'
needle = '<article class="page-content prose"><p>RunTime is where I keep'
insert = '<article class="page-content prose"><img src="{url("assets/photos/about-josh-ccr.jpg")}" alt="Josh diving a JJ-CCR underwater" width="1448" height="1086" loading="lazy"><p>RunTime is where I keep'
anchor = '"file": "assets/photos/dpv-light-ball-mount-built-01.webp",'
new_entry = ('"file": "assets/photos/dpv-light-ball-mount-installed.jpg",\n'
             '        "alt": "Ball mount secured to a DPV with a strap",\n'
             '        "caption": ""\n'
             '      },\n      {\n        ')
assert about_asset in b or needle in b, 'About page template no longer matches. Stop rather than overwriting it.'
assert mount_asset in p or anchor in p, 'Ball mount project no longer matches. Stop rather than overwriting it.'
assert '"slug": "dpv-light-holders"' in p, 'DPV light holder project missing.'
if about_asset not in b:
    b=b.replace(needle,insert,1)
if mount_asset not in p:
    p=p.replace(anchor,new_entry+anchor,1)
json.loads(p)
# Verify the new template is syntactically sound before writing.
compile(b,str(build),'exec')
for name in ['about-josh-ccr.jpg','dpv-light-ball-mount-installed.jpg']:
    src=source/'assets/photos'/name
    assert src.is_file(), f'Missing image: {src}'

for name in ['about-josh-ccr.jpg','dpv-light-ball-mount-installed.jpg']:
    dest=repo/'assets/photos'/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source/'assets/photos'/name,dest)
if build.read_text()!=b:
    build.write_text(b)
if products.read_text()!=p:
    products.write_text(p)
print('Updated About photo, DPV ball mount gallery, and the two photo files.')
print('Review git diff and commit the changes. No other site content was changed.')
