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

# Original vector artwork, not photographs or navigational charts.
COMPASS='<svg viewBox="0 0 64 64" fill="none" aria-hidden="true"><circle cx="32" cy="32" r="26" stroke="currentColor"/><path d="M32 1v13m0 36v13M1 32h13m36 0h13M20 44l7-17 17-7-7 17z" stroke="currentColor" stroke-width="2"/><path d="m27 27 10 10" stroke="currentColor"/></svg>'
SHARK='''<svg viewBox="0 0 650 230" fill="none" aria-hidden="true"><path d="M42 141C97 114 156 88 262 98l44-41-6 46c83 3 144 22 194 33l65-48-18 61 45 43-80-27c-70 21-166 24-247 7l-45 36-3-47C137 152 81 150 42 141Z" fill="currentColor" fill-opacity=".1" stroke="currentColor" stroke-width="2"/><path d="m337 125-8 34m19-31-8 33m19-30-8 32m19-29-8 31m19-28-8 29m19-26-8 27M81 139l34 4" stroke="currentColor" stroke-width="2"/><circle cx="131" cy="122" r="3" fill="currentColor"/></svg>'''

def chart():
    lines=''.join(f'<ellipse cx="305" cy="290" rx="{75+i*23}" ry="{100+i*20}" transform="rotate(-30 305 290)"/>' for i in range(11))
    return f'''<svg viewBox="0 0 600 600" fill="none" aria-hidden="true"><defs><pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse"><path d="M50 0H0V50" stroke="#29454a" stroke-width=".5"/></pattern></defs><rect x="1" y="1" width="598" height="598" fill="url(#grid)" stroke="#29454a"/><g stroke="#42645e" stroke-width=".7" opacity=".65">{lines}</g><path d="M87 480 175 397 285 350 375 230 500 125" stroke="#e9915e" stroke-dasharray="5 7"/><g stroke="#e9915e"><circle cx="87" cy="480" r="7"/><circle cx="375" cy="230" r="7"/><circle cx="500" cy="125" r="7"/></g><g transform="translate(65 45)"><path d="M40 5v70M5 40h70M25 55l10-20 20-10-10 20Z" stroke="#a7ccbd"/><text x="36" y="0" fill="#a7ccbd" font-size="10" font-family="monospace">N</text></g><g transform="translate(90 95) rotate(-12 220 220)" stroke="#b1c6b3" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M174 212c-22-23-29-73-7-108 21-34 69-36 94-3 26 35 18 83-6 111 7 19 25 35 44 45 34 18 65-4 56-29-7-21-33-15-28 3" fill="#173531"/><path d="M174 211c-25 9-48 3-68-20-17-20-36-23-47-9-11 14 2 32 14 20M180 222c-26 27-53 40-83 33-36-9-58 6-51 27 5 14 26 16 30 4M190 230c-19 45-40 73-70 75-32 1-40 24-23 36 13 9 30-3 23-15M203 238c-1 52-12 77-40 95-22 15-12 43 10 39 16-3 18-24 4-24M218 238c24 34 21 69 10 97-12 29 8 49 27 37 14-9 6-27-7-24M232 231c29 18 48 39 57 69 9 29 36 30 45 11 8-16-9-31-20-19M248 219c32 16 57 14 78-2 28-21 54-8 49 13-3 15-23 17-27 5"/><path d="M178 208c20 16 53 20 78 0M175 129c-7 23-5 43 3 59" opacity=".5"/><ellipse cx="184" cy="200" rx="8" ry="6" fill="#091a1e"/><ellipse cx="243" cy="200" rx="8" ry="6" fill="#091a1e"/><g stroke-width="1" opacity=".5"><circle cx="154" cy="280" r="3"/><circle cx="140" cy="292" r="3"/><circle cx="180" cy="302" r="3"/><circle cx="177" cy="316" r="3"/><circle cx="240" cy="292" r="3"/><circle cx="243" cy="305" r="3"/><circle cx="280" cy="268" r="3"/><circle cx="290" cy="280" r="3"/></g></g><g fill="#8fa9a3" font-family="monospace" font-size="9" letter-spacing="1"><text x="405" y="40">PUGET SOUND / PNW</text><text x="30" y="565">ILLUSTRATIVE CHART</text><text x="421" y="565">RUNTIME / 001</text></g></svg>'''

def art(kind):
    if kind=='chart':return chart()
    if kind=='label':return '''<svg viewBox="0 0 600 225" fill="none" aria-hidden="true"><g transform="translate(170 30) rotate(-6 125 80)"><rect width="260" height="170" rx="3" fill="#e9e6d6"/><rect width="260" height="33" fill="#d9b344"/><text x="130" y="24" text-anchor="middle" fill="#12272a" font-size="20" font-family="monospace" font-weight="bold">TRIMIX</text><text x="130" y="86" text-anchor="middle" fill="#12272a" font-size="43" font-family="monospace" font-weight="bold">18 / 45</text><path d="M20 103h220" stroke="#12272a"/><text x="130" y="130" text-anchor="middle" fill="#12272a" font-size="13" font-family="monospace">ANALYZE · VERIFY · LABEL</text><text x="130" y="153" text-anchor="middle" fill="#12272a" font-size="9" font-family="monospace">RUNTIME DIVE SYSTEMS</text></g></svg>'''
    if kind=='team':return '''<svg viewBox="0 0 600 225" fill="none" aria-hidden="true"><g stroke="currentColor"><circle cx="300" cy="110" r="62"/><circle cx="300" cy="110" r="83" stroke-dasharray="2 7"/><path d="M90 112h125m170 0h125M300 18v25m0 134v30"/><circle cx="90" cy="112" r="9"/><circle cx="510" cy="112" r="9"/><path d="M280 115v-15a20 20 0 0 1 40 0v15m-46 20v-17h52v17m-34-40h16v22h-16z"/></g><text x="300" y="160" text-anchor="middle" fill="currentColor" font-family="monospace" font-size="9" letter-spacing="3">INNERSPACE</text></svg>'''
    return '''<svg viewBox="0 0 600 225" fill="none" aria-hidden="true"><g stroke="currentColor"><rect x="170" y="40" width="260" height="145" rx="30"/><circle cx="235" cy="110" r="30"/><circle cx="300" cy="110" r="30"/><circle cx="365" cy="110" r="30"/><path d="M235 97v26m65-26v26m65-26v26M190 60h15m190 0h15"/></g><text x="300" y="164" text-anchor="middle" fill="currentColor" font-family="monospace" font-size="10" letter-spacing="4">TRICELL / PROTOTYPE</text></svg>'''

def shell(title,body,active='Home',description=None):
    nav=''.join(f'<a href="{url(path)}"'+(' aria-current="page"' if name==active else '')+f'>{name}</a>' for name,path in [('Projects','projects/'),('Workshop log','log/'),('Photos','photos/'),('About','about/')])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} | RunTime Dive Systems</title><meta name="description" content="{E(description or SITE['description'],quote=True)}"><meta name="theme-color" content="#091a1e"><meta property="og:title" content="{E(title,quote=True)} | RunTime Dive Systems"><meta property="og:description" content="{E(description or SITE['description'],quote=True)}"><meta property="og:type" content="website"><link rel="icon" href="{url('assets/favicon.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{url('assets/site.css')}"><script src="{url('assets/site.js')}" defer></script></head><body><a class="skip" href="#main">Skip to content</a><header><div class="wrap header-inner"><a class="brand" href="{url()}" aria-label="RunTime Dive Systems home">{COMPASS}<span><strong>RUNTIME</strong><small>DIVE SYSTEMS</small></span></a><button class="menu" type="button" aria-controls="navigation" aria-expanded="false">Menu</button><nav id="navigation" aria-label="Main navigation">{nav}<a class="nav-button" href="{url('status/')}">Project status ↗</a></nav></div></header><main id="main">{body}</main><footer class="wrap"><div class="footer-row"><span>© {dt.date.today().year} RunTime Dive Systems<br><span class="mono">Pacific Northwest · Built by a diver</span></span><div class="footer-links"><a href="{url('projects/')}">Projects</a><a href="{url('log/')}">Workshop log</a><a href="{url('status/')}">Status</a><a href="{url('about/')}">About</a></div></div></footer></body></html>'''

def badge(p):return '<span class="badge '+('dev' if p['status']!='Running' else '')+'">'+E(p['status'])+'</span>'
def card(p):
    return f'''<article class="project-card"><a href="{url('projects/'+p['slug']+'/')}" class="project-art" aria-label="About {E(p['name'],quote=True)}"><span class="art-label">{E(p['category'])}</span>{art(p['art'])}</a><div class="project-content"><div class="project-meta"><span>{E(p['category'])}</span>{badge(p)}</div><h3><a href="{url('projects/'+p['slug']+'/')}">{E(p['name'])}</a></h3><p>{E(p['description'])}</p><a class="text-link" href="{url('projects/'+p['slug']+'/')}">Explore project <span aria-hidden="true">↗</span></a></div></article>'''

def head(kicker,title,intro):return f'<div class="wrap page-head"><p class="eyebrow">{E(kicker)}</p><h1>{E(title)}</h1><p class="intro">{E(intro)}</p></div>'
def write(path,content):
    dest=OUT/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(content)

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

def logrow(p):
    return f'''<article class="log-row" data-post="{E((p['title']+' '+p['excerpt']+' '+p['project']).lower(),quote=True)}" data-project="{E(p['project'],quote=True)}"><time datetime="{p['date']}">{dt.date.fromisoformat(p['date']).strftime('%b %d, %Y').upper()}</time><div><p class="eyebrow">{E(p['project'])}</p><h3><a href="{url('log/'+p['slug']+'/')}">{E(p['title'])}</a></h3><p>{E(p['excerpt'])}</p></div><a class="arrow" href="{url('log/'+p['slug']+'/')}" aria-label="Read {E(p['title'],quote=True)}">↗</a></article>'''

if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir();shutil.copytree(ROOT/'assets',OUT/'assets')
write('assets/favicon.svg',COMPASS.replace('aria-hidden="true"','xmlns="http://www.w3.org/2000/svg"').replace('currentColor','#f18a54'))
hero=f'''<div class="wrap hero"><div><p class="eyebrow">Independent tools / Pacific Northwest</p><h1>Built for the<br>dives <em>we do.</em></h1><p class="intro">Technical diving tools, ideas from the workshop, and a connection to the cold water that inspires them.</p><div class="actions"><a class="button" href="{url('projects/')}">Explore the projects <span>↗</span></a><a class="text-link" href="{url('log/')}">Read the workshop log</a></div><p class="hero-foot">CCR · DPV · FILL STATION · DIVE COMMUNITY</p></div><div class="hero-art">{chart()}</div></div><div class="wrap strip"><span>● &nbsp; FROM THE WORKSHOP TO THE WATER</span><span>INDEPENDENTLY DEVELOPED</span><span>EST. IN THE PACIFIC NORTHWEST</span></div>'''
body=hero+f'''<section class="section wrap"><div class="section-top"><div><p class="eyebrow">01 / The projects</p><h2>Different tools.<br>One diving life.</h2></div><a class="text-link" href="{url('status/')}">Where things stand ↗</a></div><div class="project-grid">{''.join(card(p) for p in PROJECTS)}</div></section><section class="section wrap"><div class="section-top"><div><p class="eyebrow">02 / Workshop log</p><h2>The work between dives.</h2></div><a class="text-link" href="{url('log/')}">All updates ↗</a></div><div class="journal">{''.join(logrow(p) for p in POSTS[:3])}</div></section><section class="wrap about"><div><p class="eyebrow">03 / Below the surface</p>{SHARK}<p class="ocean-note">Giant Pacific octopus / Bluntnose sixgill</p></div><div><h2>Cold water.<br>Plenty to be curious about.</h2><p>RunTime is where Josh's technical diving and project development come together. From Lake Washington wrecks to Puget Sound marine life, the next idea usually starts with a reason to get in the water.</p><a class="text-link" href="{url('about/')}">The story behind RunTime ↗</a></div></section>'''
write('index.html',shell('Built for the dives we do',body))
write('projects/index.html',shell('Projects',head('The RunTime ecosystem','Tools with a reason to exist.','A place for the tools that are running, the ideas being tested, and the projects still on the bench.')+'<section class="wrap page-content"><div class="project-grid">'+''.join(card(p) for p in PROJECTS)+'</div></section>','Projects'))
for p in PROJECTS:
    launch=f'<a class="button" href="{E(p["url"],quote=True)}" target="_blank" rel="noopener">Open {E(p["name"])} ↗</a>' if p['url'] else '<p class="muted">Development updates will appear in the workshop log.</p>'
    body=head(p['category'],p['name'],p['short'])+f'''<div class="wrap page-content detail-layout"><article class="prose"><div class="project-art">{art(p['art'])}</div><h2>What it is</h2><p>{E(p['description'])}</p><p>{E(p['body'])}</p><div class="actions">{launch}</div><div class="notice">{E(p['note'])}</div></article><aside><p class="eyebrow">Project file</p><h3>{E(p['name'])}</h3>{badge(p)}<p style="margin-top:20px">Part of RunTime Dive Systems.</p><a class="text-link" href="{url('log/')}">Read the workshop log ↗</a></aside></div>'''
    write('projects/'+p['slug']+'/index.html',shell(p['name'],body,'Projects',p['description']))
options=''.join(f'<option>{E(x)}</option>' for x in sorted({p['project'] for p in POSTS}))
body=head('Notes from the process','Workshop log.','Build notes, project updates, and the things worth writing down along the way.')+f'<section class="wrap page-content"><div class="filters"><label class="mono" for="search">Find an update</label><input id="search" type="search" placeholder="Search the workshop log…"><select id="category" aria-label="Filter by project"><option value="">All projects</option>{options}</select></div><div class="journal">'+''.join(logrow(p) for p in POSTS)+'</div><p id="no-results" hidden>No updates match that search.</p></section>'
write('log/index.html',shell('Workshop log',body,'Workshop log'))
for p in POSTS:
    body=head(p['project']+' / '+p['date'],p['title'],p['excerpt'])+f'<article class="wrap page-content"><div class="prose">{p["body"]}<div class="notice">Written by {E(SITE["author"])}</div><div class="actions"><a class="text-link" href="{url("log/")}">← All workshop updates</a></div></div></article>'
    write('log/'+p['slug']+'/index.html',shell(p['title'],body,'Workshop log',p['excerpt']))
body=head('From the water and the bench','Photo log.','A place for underwater images, workshop details, and projects taking shape.')
if not GALLERY:body+='<section class="wrap page-content"><div class="empty"><p class="eyebrow">The collection starts here</p><h2>First frames coming soon.</h2><p>Workshop photos and images from the Pacific Northwest will appear here as the collection grows.</p></div></section>'
else:
    cards=[]
    for photo in GALLERY:
        src=E(safe_link(photo['file']),quote=True);alt=E(photo['alt'],quote=True);caption=E(photo['caption'],quote=True)
        cards.append(f'<button type="button" data-photo="{src}" data-alt="{alt}" data-caption="{caption}" aria-label="View {alt}"><img src="{src}" alt="{alt}" loading="lazy"><span>{caption}</span></button>')
    body+='<section class="wrap page-content"><div class="gallery">'+''.join(cards)+'</div></section><dialog id="photo-dialog" aria-label="Photo viewer"><button type="button">Close</button><img alt=""><p></p></dialog>'
write('photos/index.html',shell('Photo log',body,'Photos'))
body=head('Behind the projects','Built by a diver.','RunTime Dive Systems is a home for the tools and ideas Josh is developing around technical diving.')+f'''<section class="wrap page-content"><div class="prose"><h2>From a practical problem to a project.</h2><p>Route planning, gas labels, organizing a dive group, and building something useful on the workbench. Each project starts with a part of diving that could work a little better.</p><p>RunTime brings those projects together, with space to document the development and share what comes next.</p><h2>Pacific Northwest, above and below.</h2><p>Cold-water diving, wrecks, giant Pacific octopuses, and sixgill sharks shape the visual world of this site. The chart lines and marine-life artwork are a nod to those waters.</p>{SHARK}<div class="actions"><a class="button" href="{url('projects/')}">Find the tools ↗</a><a class="text-link" href="{url('log/')}">Follow the workshop</a></div></div></section>'''
write('about/index.html',shell('About',body,'About'))
rows=''.join(f'<tr><td><a href="{url("projects/"+p["slug"]+"/")}">{E(p["name"])}</a></td><td>{badge(p)}</td><td class="mono">{E(p["category"])}</td></tr>' for p in PROJECTS)
write('status/index.html',shell('Project status',head('Development board','Where things stand.','Development labels describe the project stage. This page is not a live uptime monitor.')+f'<section class="wrap page-content"><table class="status-table"><thead><tr><th>Project</th><th>Stage</th><th>Area</th></tr></thead><tbody>{rows}</tbody></table><p class="notice">Status is maintained manually. Check each project for current features and availability.</p></section>'))
write('404.html',shell('Page not found',head('404 / Off the chart','Let’s get you back on course.','That page could not be found.')+f'<div class="wrap page-content"><a class="button" href="{url()}">Back to RunTime ↗</a></div>'))
write('.nojekyll','')
# Validate every internal href and asset before publishing.
for path in OUT.rglob('*.html'):
    for target in re.findall(r'(?:href|src)="([^"]+)"',path.read_text()):
        target=html.unescape(target)
        if urlparse(target).scheme or target.startswith('#'):continue
        resolved=target.removeprefix(BASE).lstrip('/').split('#')[0]
        local=OUT/resolved
        if not local.is_file() and not (local/'index.html').is_file():raise ValueError(f'Broken internal link in {path}: {target}')
print(f'Built {len(list(OUT.rglob("*.html")))} pages; {len(POSTS)} published posts; all internal links valid.')
