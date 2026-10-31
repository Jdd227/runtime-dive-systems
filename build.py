"""RunTime static publisher. Python 3.10+, no third-party dependencies."""
from pathlib import Path
import datetime as dt
import html
import json
import os
import re
import shutil
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
BASE = os.environ.get('BASE_PATH', '').rstrip('/')
SITE = json.loads((ROOT/'content/site.json').read_text())
PROJECTS = json.loads((ROOT/'content/projects.json').read_text())
GALLERY = json.loads((ROOT/'content/gallery.json').read_text())
E = html.escape

def url(path=''):
    return BASE + '/' + path.lstrip('/')

def safe_link(path):
    if urlparse(path).scheme not in ('', 'http', 'https', 'mailto'):
        raise ValueError(f'Unsupported link: {path}')
    return path if urlparse(path).scheme or path.startswith('#') else url(path)

def inline(text):
    # Escape all author HTML; support a deliberately small, documented Markdown subset.
    tokens=[]
    def token(value):
        tokens.append(value)
        return f'\x00{len(tokens)-1}\x00'
    def image(m):
        return token(f'<img src="{E(safe_link(m[2]),quote=True)}" alt="{E(m[1],quote=True)}" loading="lazy">')
    text=re.sub(r'!\[([^\]]*)\]\(([^\s)]+)\)',image,text)
    text=re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)',lambda m:token(f'<a href="{E(safe_link(m[2]),quote=True)}">{E(m[1])}</a>'),text)
    text=E(text)
    text=re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    text=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',text)
    for n,value in enumerate(tokens): text=text.replace(f'\x00{n}\x00',value)
    return text

def markdown(text):
    result=[]; paragraph=[]; items=[]; code=None
    def flush():
        if paragraph: result.append('<p>'+inline(' '.join(paragraph))+'</p>');paragraph.clear()
        if items: result.append('<ul>'+''.join('<li>'+inline(x)+'</li>' for x in items)+'</ul>');items.clear()
    for line in text.splitlines():
        if line.startswith('```'):
            flush()
            if code is None: code=[]
            else: result.append('<pre><code>'+E('\n'.join(code))+'</code></pre>');code=None
            continue
        if code is not None:code.append(line);continue
        if not line.strip():flush();continue
        if m:=re.match(r'^(#{1,3}) (.+)$',line):
            flush(); level=max(2,len(m[1]));result.append(f'<h{level}>'+inline(m[2])+f'</h{level}>')
        elif line.startswith('- '):
            if paragraph:flush()
            items.append(line[2:])
        elif line.startswith('> '):flush();result.append('<blockquote>'+inline(line[2:])+'</blockquote>')
        else:
            if items:flush()
            paragraph.append(line)
    if code is not None:raise ValueError('Unclosed code block')
    flush();return '\n'.join(result)


PRODUCTS = json.loads((ROOT/"content/products.json").read_text())
GEAR = json.loads((ROOT/"content/gear.json").read_text())

POSTS=[]
for path in (ROOT/'content/posts').glob('*.md'):
    parts=path.read_text().split('---',2)
    if len(parts)!=3 or parts[0].strip():raise ValueError(f'Invalid front matter: {path.name}')
    meta={}
    for line in parts[1].strip().splitlines():
        key,sep,value=line.partition(':')
        if not sep:raise ValueError(f'Invalid metadata in {path.name}')
        meta[key.strip()]=value.strip()
    for key in ('title','date','project','excerpt','draft'):
        if not meta.get(key):raise ValueError(f'Missing {key} in {path.name}')
    dt.date.fromisoformat(meta['date'])
    if meta['draft'] not in ('true','false'):raise ValueError('draft must be true or false')
    if meta['draft']=='true':continue
    if not re.fullmatch(r'[a-z0-9-]+',path.stem):raise ValueError('Use lowercase letters, numbers, and hyphens in post filenames')
    meta.update(slug=path.stem,body=markdown(parts[2]));POSTS.append(meta)
POSTS.sort(key=lambda p:(p['date'],p['slug']),reverse=True)


def write(path,content):
    dest=OUT/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(content)

def badge(p):
    cls='dev' if p['status'] in ('In development','Pilot') else ''
    return f'<span class="status {cls}">{E(p["status"])}</span>'
