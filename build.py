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

WARNING='These are my personal projects and experiments. Do not use them in place of normal safety equipment, established dive procedures, training, manufacturer instructions, official charts or maps, or independent dive planning.'
NAV=[('Software','projects/'),('Photography','photos/'),('Blog','log/'),('Designs','designs/'),('My gear','gear/')]

def shell(title,body,active='',description=None):
    nav=''.join(f'<a href="{url(path)}"'+(' aria-current="page"' if label==active else '')+f'>{label}</a>' for label,path in NAV)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} | RunTime Dive Systems</title><meta name="description" content="{E(description or SITE['description'],quote=True)}"><meta name="theme-color" content="#0c1014"><meta property="og:title" content="{E(title,quote=True)} | RunTime Dive Systems"><meta property="og:description" content="{E(description or SITE['description'],quote=True)}"><meta property="og:type" content="website"><link rel="icon" href="{url('assets/runtime-monogram.png')}" type="image/png"><link rel="stylesheet" href="{url('assets/site.css')}"><script src="{url('assets/site.js')}" defer></script></head><body><a class="skip" href="#main">Skip to content</a><header><div class="wrap header-inner"><a class="brand" href="{url()}" aria-label="RunTime home"><img class="mark" src="{url('assets/runtime-monogram.png')}" alt=""><img class="wordmark" src="{url('assets/runtime-logo.png')}" alt="RunTime Technical Diving"></a><button class="menu" aria-expanded="false" aria-controls="navigation" type="button">Menu</button><nav id="navigation" aria-label="Main navigation">{nav}</nav></div></header><main id="main" class="wrap">{body}</main><footer><div class="wrap"><div class="footer-top"><span>© {dt.date.today().year} RunTime Dive Systems · Josh · Pacific Northwest</span><nav aria-label="Footer"><a href="{url('about/')}">About</a><a href="{url('status/')}">Project status</a><a href="{url('privacy/')}">Privacy</a><a href="{url('safety/')}">Project-use warning</a></nav></div><p class="footer-warning">{E(WARNING)} <a href="{url('safety/')}">Read the full warning.</a></p></div></footer></body></html>'''

def head(kicker,title,intro=''):
    return f'<div class="page-head"><p class="eyebrow">{E(kicker)}</p><h1>{E(title)}</h1>'+ (f'<p class="intro">{E(intro)}</p>' if intro else '')+'</div>'

def section(title,path,body,intro='',link='View all'):
    return f'<section class="section"><div class="section-heading"><h2>{E(title)}</h2><a href="{url(path)}">{E(link)} →</a></div>'+ (f'<p class="section-intro">{E(intro)}</p>' if intro else '')+body+'</section>'

def project_card(p,design=False):
    target=('designs/' if design else 'projects/')+p['slug']+'/'
    launch=''
    if p.get('url'):launch=f'<a href="{E(p["url"],quote=True)}" target="_blank" rel="noopener">{E(p.get("link_label","Open project"))} ↗</a>'
    return f'<article class="project"><div class="project-meta"><h3><a href="{url(target)}">{E(p["name"])}</a></h3>{badge(p)}</div><p>{E(p["description"])}</p><div class="small-links"><a href="{url(target)}">Project notes →</a>{launch}</div></article>'

def logrow(p):
    return f'''<article class="log-row" data-post="{E((p['title']+' '+p['excerpt']+' '+p['project']).lower(),quote=True)}" data-project="{E(p['project'],quote=True)}"><time datetime="{p['date']}">{dt.date.fromisoformat(p['date']).strftime('%b %d, %Y')}</time><div><h3><a href="{url('log/'+p['slug']+'/')}">{E(p['title'])}</a></h3><p>{E(p['excerpt'])}</p><div class="log-project">{E(p['project'])}</div></div></article>'''

def media_caption(item):
    return "<figcaption>"+E(item["caption"])+"</figcaption>" if item.get("caption") else ""

def photos_block(limit=None):
    selected=GALLERY if limit is None else GALLERY[:limit]
    if not selected:return '<div class="photo-empty"><strong>From below the surface.</strong><p>A place for my underwater photographs. The first collection is coming soon.</p></div>'
    result='<div class="gallery">'
    for p in selected:
        source=E(safe_link(p['file']),quote=True);alt=E(p['alt'],quote=True);caption=E(p.get('caption',''),quote=True)
        preview=E(safe_link(p.get("thumbnail",p["file"])),quote=True)
        label=f"<span>{caption}</span>" if caption else ""
        result+=f'<button type="button" data-photo="{source}" data-alt="{alt}" data-caption="{caption}" aria-label="View {alt}"><img src="{preview}" alt="{alt}" loading="lazy" decoding="async">{label}</button>'
    return result+'</div><dialog id="photo-dialog" aria-label="Photo viewer"><button type="button">Close</button><img alt=""><p></p></dialog>'

def gear_block():
    return '<ul class="gear-list">'+''.join(f'<li><span class="category">{E(p["category"])}</span><div><strong>{E(p["name"])}</strong><p>{E(p["note"])}</p></div></li>' for p in GEAR['items'])+'</ul>'

if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir();shutil.copytree(ROOT/'assets',OUT/'assets')
# Publish the standalone trimix calculator
shutil.copytree(ROOT/'software'/'trimix', OUT/'software'/'trimix')
body=f'''<section class="hero"><img class="hero-logo" src="{url('assets/runtime-logo.png')}" alt="RunTime Technical Diving"><p class="eyebrow">Pacific Northwest</p><h1>I'm Josh, a PNW diver.</h1><p>These are the projects I've made and the things I'm still working on: software, dive gear, underwater photography, and a few ideas from the workbench.</p><div class="links"><a href="#software">See my projects ↓</a><a href="{url('about/')}">A little about me →</a></div></section>'''
body+='<div id="software">'+section('Software projects','projects/','<div class="projects">'+''.join(project_card(p) for p in PROJECTS)+'</div>','Tools that are running, projects still in development, and links to try them.')+'</div>'
body+=section('Underwater photography','photos/',photos_block(3),'Cold water, wrecks, and marine life in the Pacific Northwest.','View photographs')
body+=section('Products & designs','designs/','<div class="projects">'+''.join(project_card(p,True) for p in PRODUCTS)+'</div>','Things I have made for diving, plus the projects still on the bench.')
body+=section('Blog','log/',''.join(logrow(p) for p in POSTS[:3]),'Updates about what I am building, changing, or finishing.','All posts')
body+=section('My gear & configuration','gear/',gear_block(),GEAR['intro'],'See my setup')
write('index.html',shell('Josh’s projects, photography & diving',body))
write('projects/index.html',shell('Software projects',head('Software','Current projects.','Finished or unfinished, this is where I keep the tools I am working on.')+'<div class="page-content projects">'+''.join(project_card(p) for p in PROJECTS)+'</div>','Software'))
for p in PROJECTS:
    label=p.get('link_label','Open project')
    launch=f'<a class="button" href="{E(p["url"],quote=True)}" target="_blank" rel="noopener">{E(label)} ↗</a>' if p.get('url') else ''
    body=head('Software',p['name'],p['description'])+f'<article class="page-content prose"><div class="detail-meta">{badge(p)}<a href="{url("projects/")}">All software projects</a></div><p>{E(p["body"])}</p>{launch}<div class="notice">{E(p["note"])}</div><p><a href="{url("log/")}">Read the blog →</a></p></article>'
    write('projects/'+p['slug']+'/index.html',shell(p['name'],body,'Software',p['description']))
write('designs/index.html',shell('Products & designs',head('Made for diving','Products & designs.','My dive projects, custom parts, and designs. This is a showcase; the listings do not imply an item is for sale or certified.')+'<div class="page-content projects">'+''.join(project_card(p,True) for p in PRODUCTS)+'</div>','Designs'))
for p in PRODUCTS:
    images=''.join(f'<figure><img src="{E(safe_link(i["file"]),quote=True)}" alt="{E(i["alt"],quote=True)}" loading="lazy">{media_caption(i)}</figure>' for i in p.get('images',[]))
    if images: images='<div class="design-gallery">'+images+'</div>'
    videos=''.join(f'<figure><video controls playsinline preload="none" poster="{E(safe_link(v["poster"]),quote=True)}" aria-label="{E(v.get("alt",v.get("caption","Build video")),quote=True)}"><source src="{E(safe_link(v["file"]),quote=True)}" type="video/mp4"><a href="{E(safe_link(v["file"]),quote=True)}">Watch the video</a></video>{media_caption(v)}</figure>' for v in p.get('videos',[]))
    if videos: videos='<h2>From the workbench</h2><div class="design-gallery">'+videos+'</div>'
    body=head(p['type'],p['name'],p['description'])+f'<article class="page-content prose"><div class="detail-meta">{badge(p)}<a href="{url("designs/")}">All designs</a></div><p>{E(p["body"])}</p>{images}{videos}<div class="notice">Personal project documentation. Suitability, dimensions, material properties, attachment security, and failure consequences must be evaluated for the actual use. <a href="{url("safety/")}">Read the project-use warning.</a></div><p><a href="{url("log/")}">Build notes in the blog →</a></p></article>'
    write('designs/'+p['slug']+'/index.html',shell(p['name'],body,'Designs',p['description']))
# Preserve links from the first site version.
write('projects/tricell/index.html',shell('TriCell',head('Project moved','TriCell oxygen analyzer.','This project now lives with my products and designs.')+f'<div class="page-content"><a href="{url("designs/tricell/")}">Read the TriCell project notes →</a></div>','Designs'))
write('photos/index.html',shell('Underwater photography',head('Photography','Below the surface.','My underwater photography, with a focus on the Pacific Northwest.')+'<div class="page-content">'+photos_block()+'</div>','Photography'))
options=''.join(f'<option>{E(x)}</option>' for x in sorted({p['project'] for p in POSTS}))
body=head('Blog','Notes from the workbench.','Project updates, things I have finished, and the work still in progress.')+f'<div class="page-content"><div class="filters"><label for="search">Find a post</label><input id="search" type="search" placeholder="Search posts…"><select id="category" aria-label="Filter posts by project"><option value="">All projects</option>{options}</select></div>'+''.join(logrow(p) for p in POSTS)+'<p id="no-results" hidden>No posts match that search.</p></div>'
write('log/index.html',shell('Blog',body,'Blog'))
for p in POSTS:
    body=head(p['project']+' · '+p['date'],p['title'],p['excerpt'])+f'<article class="page-content prose">{p["body"]}<p class="detail-meta">Written by {E(SITE["author"])}</p><p><a href="{url("log/")}">← All blog posts</a></p></article>'
    write('log/'+p['slug']+'/index.html',shell(p['title'],body,'Blog',p['excerpt']))
gear_photos=''.join(f'<figure><img src="{E(safe_link(i["file"]),quote=True)}" alt="{E(i["alt"],quote=True)}" loading="lazy">{media_caption(i)}</figure>' for i in GEAR.get('images',[]))
body=head('Gear','My gear & configuration.',GEAR['intro'])+'<div class="page-content">'+gear_block()+f'<div class="prose"><h2>Configuration notes</h2><p>{E(GEAR["configuration"])}</p>{gear_photos}</div></div>'
write('gear/index.html',shell('My gear & configuration',body,'My gear'))
body=head('About','Hi, I’m Josh.','I am a Pacific Northwest diver who likes making things for diving.')+f'<article class="page-content prose"><p>RunTime is where I keep my software projects, custom dive designs, underwater photography, and notes from what I am working on. Some projects are finished. Others are still being worked out.</p><p>I dive a JJ-CCR and use a DPV. The diving here, from Lake Washington wrecks to Puget Sound marine life, gives me plenty of reasons to keep exploring and building.</p><p>Giant Pacific octopuses and sixgill sharks are among the things I love about these waters.</p><p><a href="{url("projects/")}">Software projects</a> · <a href="{url("designs/")}">Products & designs</a> · <a href="{url("gear/")}">My gear</a></p></article>'
write('about/index.html',shell('About Josh',body))
all_projects=PROJECTS+PRODUCTS
rows=''.join(f'<tr><td><a href="{url(("projects/" if p in PROJECTS else "designs/")+p["slug"]+"/")}">{E(p["name"])}</a></td><td>{badge(p)}</td></tr>' for p in all_projects)
write('status/index.html',shell('Project status',head('Projects','Where things stand.','These labels describe development progress, not monitored uptime, independent testing, or certification.')+'<div class="page-content"><table class="status-table"><thead><tr><th>Project</th><th>Stage</th></tr></thead><tbody>'+rows+'</tbody></table></div>'))
privacy='''## What this policy covers

This policy covers the RunTime Dive Systems portfolio and blog at runtimedivesystems.com. It does not cover the separate applications linked from this site.

## What this site collects

This version of the site has no visitor accounts, contact forms, comments, checkout, email subscriptions, advertising, or analytics scripts. RunTime does not set application cookies or use browser storage on these pages. This site uses system fonts and serves its logos, scripts, and photographs with the site; no third-party font or social-media embeds are loaded.

## Hosting and technical data

The site is hosted using GitHub Pages. GitHub and its infrastructure providers may process technical request information, such as IP addresses, browser details, requested pages, and request times, to deliver and protect the service. Their handling and retention of that information are governed by their own policies. I do not promise that hosting logs are never collected or retained.

[Read GitHub's privacy statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement).

## Linked apps and websites

Opening a software project or another external link takes you to a separate service. That service may collect data, use accounts or storage, or have different privacy practices. Check its own policy before using it. In particular, this portfolio's privacy statements do not describe the data handling of Innerspace, Gas Label Studio, the DPV Planner, or Dive Current.

## Information you choose to share

If you post an issue or comment on GitHub, your submission may be public. GitHub handles that submission under its terms and privacy policy. Do not post private information there.

## Questions and updates

For questions about this site's privacy practices, contact Josh through the [RunTime repository](https://github.com/Jdd227/runtime-dive-systems). If the site adds forms, analytics, sales, or other data collection, this policy will be updated to describe those changes.
'''
write('privacy/index.html',shell('Privacy policy',head('Privacy','Privacy policy.','Last updated October 28, 2026.')+'<article class="page-content prose">'+markdown(privacy)+'</article>'))
safety='''## Personal projects, not safety systems

These are my personal projects, designs, experiments, and notes. They are shared to show what I am working on. A project being listed as made, live, or complete does not mean it has been independently tested, certified, or approved for diving use.

Do not use anything on this site in place of normal safety products or equipment, established procedures, appropriate training, manufacturer instructions, official charts or maps, or independent dive planning.

## Software, maps, and navigation

Software may contain errors, and data may be missing, inaccurate, or out of date. Positions, route distances, bearings, bathymetry, forecasts, gas labels, and calculated outputs must be independently checked. These projects are not primary underwater navigation systems, official hydrographic charts, or substitutes for current local information, suitable instruments, gas analysis, bailout planning, and competent judgment.

## Designs, modifications, and equipment

Custom parts, mounts, weights, electronics, printed designs, and equipment modifications can fail or change the behavior of a system. Materials, print settings, fit, corrosion, load, depth, rigging, and attachment methods matter. A photograph or shared file does not demonstrate suitability for your equipment or dive. Follow manufacturer instructions and obtain qualified advice before making or using a modification. Development prototypes must not be treated as validated life-support instruments.

## My gear is a personal record

My equipment and configuration are shown for documentation. They are not a prescription for anyone else's setup or a claim that a configuration is suitable for a particular dive.

## No guarantee of suitability

The content and projects are provided as available, without a promise of accuracy, reliability, availability, performance, or fitness for a particular purpose. Stop using a project if its behavior or output is uncertain. This warning is not training, a risk assessment, or a replacement for applicable legal rights and responsibilities.
'''
write('safety/index.html',shell('Project-use warning',head('Please read','Project-use warning.','Personal work, shared for documentation.')+'<article class="page-content prose">'+markdown(safety)+'</article>'))
write('404.html',shell('Page not found',head('404','Page not found.')+f'<div class="page-content"><a href="{url()}">Back to RunTime →</a></div>'))
write('.nojekyll','')
for path in OUT.rglob('*.html'):
    for target in re.findall(r'(?:href|src)="([^"]+)"',path.read_text()):
        target=html.unescape(target)
        if urlparse(target).scheme or target.startswith('#'):continue
        resolved=target.removeprefix(BASE).lstrip('/').split('#')[0]
        local=OUT/resolved
        
# Automatically generate Google sitemap and robots.txt
SITE_URL = "https://runtimedivesystems.com"

pages = []
for page in OUT.rglob("index.html"):
    route = page.parent.relative_to(OUT).as_posix()
    if route == "projects/tricell":
        continue  # Exclude old moved-project page
    address = SITE_URL + ("/" if route == "." else f"/{route}/")
    pages.append(address)

xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for address in sorted(pages):
    xml += f"  <url><loc>{html.escape(address)}</loc></url>\n"
xml += "</urlset>\n"

write("sitemap.xml", xml)
write("robots.txt",
      f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")

        if not local.is_file() and not (local/'index.html').is_file():raise ValueError(f'Broken internal link in {path}: {target}')
print(f'Built {len(list(OUT.rglob("*.html")))} pages; {len(POSTS)} published posts; all internal links valid.')
