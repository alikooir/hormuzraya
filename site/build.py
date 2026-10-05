#!/usr/bin/env python3
"""Build the Hormoz Raya website into ../public.

    python3 site/build.py            # production build into public/
    python3 site/build.py --preview  # same pages, links end in index.html (for opening from disk)

Farsi pages live at /, English pages under /en/. Each page gets its own title, description,
canonical URL, hreflang alternates, Open Graph tags and JSON-LD. sitemap.xml and robots.txt
are generated too.
"""
import html
import json
import shutil
import sys
from datetime import date
from pathlib import Path

from content import L, SITE, NAV, PRODUCTS, ENGINES, SERVICES, STEPS, SECTORS, PILLARS

ROOT = Path(__file__).resolve().parent
PREVIEW = "--preview" in sys.argv
OUT = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else ROOT.parent / "public"
DOMAIN = SITE["domain"]
TODAY = date.today().isoformat()
PRODUCT = {p["slug"]: p for p in PRODUCTS}


def e(s):
    return html.escape(s, quote=True)


def lang_prefix(lang):
    return "en/" if lang == "en" else ""


def abs_url(path, lang):
    return f"{DOMAIN}/{lang_prefix(lang)}{path}"


class Page:
    """One page in one language. `path` is '' for home or like 'products/zebel/'."""

    def __init__(self, path, lang):
        self.path, self.lang = path, lang
        self.depth = (lang_prefix(lang) + path).count("/")
        self.absolute = False  # 404 pages are served at any URL, so they use root-absolute links

    def _base(self):
        return "/" if self.absolute else "../" * self.depth

    def t(self, pair):
        return pair[self.lang]

    def link(self, path, lang=None, anchor=""):
        lang = lang or self.lang
        href = self._base() + lang_prefix(lang) + path
        if PREVIEW and not self.absolute:
            href += "index.html"
        elif href == "":
            href = "./"
        return href + (f"#{anchor}" if anchor else "")

    def asset(self, name):
        return self._base() + "assets/" + name


# ---------------------------------------------------------------- shared chrome

LOGO = """<svg viewBox="0 0 40 40" aria-hidden="true">
<circle cx="20" cy="20" r="18" fill="none" stroke="var(--sea)" stroke-width="1.5"/>
<path d="M6 24c5-3 9 3 14 0s9-3 14 0" fill="none" stroke="var(--sea)" stroke-width="1.5" opacity=".5"/>
<path d="M8 29c5-3 9 3 14 0s8-3 12-1" fill="none" stroke="var(--sea)" stroke-width="1.5" opacity=".3"/>
<line x1="13" y1="14" x2="25" y2="11" stroke="var(--fg)" stroke-width="1.2"/><line x1="25" y1="11" x2="23" y2="20" stroke="var(--fg)" stroke-width="1.2"/><line x1="13" y1="14" x2="23" y2="20" stroke="var(--fg)" stroke-width="1.2"/>
<circle cx="13" cy="14" r="2.6" fill="var(--fg)"/><circle cx="25" cy="11" r="2.6" fill="var(--fg)"/><circle cx="23" cy="20" r="3.2" fill="var(--soil)"/>
</svg>"""


def org_ld():
    return {
        "@type": "Organization",
        "@id": f"{DOMAIN}/#org",
        "name": SITE["legal"]["en"],
        "alternateName": SITE["alt_names"],
        "url": f"{DOMAIN}/",
        "logo": f"{DOMAIN}/assets/logo-512.png",
        "email": SITE["email"],
        "telephone": SITE["phone_tel"],
        "address": {"@type": "PostalAddress", "addressLocality": "Bandar Abbas", "addressRegion": "Hormozgan", "addressCountry": "IR",
                    "streetAddress": "Hormozgan Science and Technology Park"},
        "description": "AI-driven market intelligence, lead generation and smart business solutions, from Bandar Abbas, Iran.",
        "sameAs": ["https://hormuzraya.ir/"],
    }


def breadcrumbs_ld(pg, trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": abs_url(path, pg.lang)} for i, (name, path) in enumerate(trail)]}


def head(pg, title, desc, ld, og_type="website"):
    other = "en" if pg.lang == "fa" else "fa"
    graph = {"@context": "https://schema.org", "@graph": ld}
    return f"""<!doctype html>
<html lang="{pg.lang}" dir="{'rtl' if pg.lang == 'fa' else 'ltr'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{abs_url(pg.path, pg.lang)}">
<link rel="alternate" hreflang="fa" href="{abs_url(pg.path, 'fa')}">
<link rel="alternate" hreflang="en" href="{abs_url(pg.path, 'en')}">
<link rel="alternate" hreflang="x-default" href="{abs_url(pg.path, 'fa')}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{e(pg.t(SITE['legal']))}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{abs_url(pg.path, pg.lang)}">
<meta property="og:image" content="{DOMAIN}/assets/og-{pg.lang}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{'fa_IR' if pg.lang == 'fa' else 'en_US'}">
<meta property="og:locale:alternate" content="{'en_US' if pg.lang == 'fa' else 'fa_IR'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b6b72">
<link rel="icon" href="{pg.asset('favicon.svg')}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{pg.asset('apple-touch-icon.png')}">
<link rel="preload" href="{pg.asset('fonts/vazirmatn-var.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{pg.asset('site.css')}">
<script type="application/ld+json">{json.dumps(graph, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">{'پرش به محتوا' if pg.lang == 'fa' else 'Skip to content'}</a>
{header(pg, other)}
<main id="main">
"""


def header(pg, other):
    section = pg.path.split("/")[0]
    current = ' aria-current="page"'
    links = "".join(
        f'<a href="{pg.link(key + "/")}"{current if section == key else ""}>{e(pg.t(label))}</a>' for key, label in NAV)
    return f"""<header class="top"><div class="wrap">
<a class="brand" href="{pg.link('')}" aria-label="{e(pg.t(SITE['name']))}">{LOGO}<b>{e(pg.t(SITE['name']))}</b></a>
<nav class="nav" aria-label="{'منوی اصلی' if pg.lang == 'fa' else 'Main'}">{links}</nav>
<details class="menu"><summary>{'منو' if pg.lang == 'fa' else 'Menu'}</summary><nav aria-label="{'منو' if pg.lang == 'fa' else 'Menu'}">{links}</nav></details>
<a class="lang" href="{pg.link(pg.path, other)}" hreflang="{other}" lang="{other}">{'English' if other == 'en' else 'فارسی'}</a>
</div></header>"""


def footer(pg):
    t = pg.t
    prods = "".join(f'<li><a href="{pg.link("products/" + p["slug"] + "/")}">{e(t(p["name"]))}</a></li>' for p in PRODUCTS)
    svcs = "".join(f'<li><a href="{pg.link("services/", anchor=s["id"])}">{e(t(s["name"]))}</a></li>' for s in SERVICES)
    year = "۱۴۰۵" if pg.lang == "fa" else "2026"
    return f"""</main>
<footer class="foot"><div class="wrap">
<div class="cols">
<div style="display:grid;gap:10px;align-content:start">
<a class="brand" href="{pg.link('')}">{LOGO}<b>{e(t(SITE['name']))}</b></a>
<p>{e(t(SITE['park']))}</p>
<p><span class="mono">{e(SITE['phone_display'])}</span><br><span class="mono">{e(SITE['email'])}</span></p>
</div>
<div><h2>{e(t(L('محصولات', 'Products')))}</h2><ul>{prods}</ul></div>
<div><h2>{e(t(L('خدمات', 'Services')))}</h2><ul>{svcs}</ul></div>
<div><h2>{e(t(L('شرکت', 'Company')))}</h2><ul>
<li><a href="{pg.link('about/')}">{e(t(L('درباره ما', 'About us')))}</a></li>
<li><a href="{pg.link('platform/')}">{e(t(L('زیرساخت فناوری', 'Technology platform')))}</a></li>
<li><a href="{pg.link('contact/')}">{e(t(L('تماس با ما', 'Contact us')))}</a></li>
</ul></div>
</div>
<div class="base"><span>© {year} {e(t(SITE['legal']))}</span><span>{e(t(L('بندرعباس، هرمزگان', 'Bandar Abbas, Hormozgan')))}</span></div>
</div></footer>
<script src="{pg.asset('site.js')}" defer></script>
</body>
</html>
"""


def crumbs(pg, trail):
    items = []
    for i, (name, path) in enumerate(trail):
        if i == len(trail) - 1:
            items.append(f'<li aria-current="page">{e(name)}</li>')
        else:
            items.append(f'<li><a href="{pg.link(path)}">{e(name)}</a></li>')
    return f'<nav aria-label="{"مسیر" if pg.lang == "fa" else "Breadcrumb"}"><ol class="crumbs">{"".join(items)}</ol></nav>'


def page_hero(pg, trail, h1, lead, extra="", after=""):
    return f"""<section class="phero"><div class="wrap">
{crumbs(pg, trail)}
{extra}
<h1>{e(h1)}</h1>
<p class="lead">{e(lead)}</p>
{after}
</div></section>"""


def cta_band(pg):
    t = pg.t
    return f"""<section class="band"><div class="wrap">
<div><h2>{e(t(L('مسئله‌ای دارید که می‌خواهید هوشمند حل شود؟', 'Have a problem you want solved intelligently?')))}</h2>
<p>{e(t(L('درباره کسب‌وکار و مسئله‌تان بگویید. بررسی می‌کنیم کدام محصول یا چه راهکاری به کارتان می‌آید.', 'Tell us about your business and your problem. We will work out which product or solution fits.')))}</p></div>
<a class="btn solid" href="{pg.link('contact/')}">{e(t(L('تماس با ما', 'Contact us')))}</a>
</div></section>"""


def home_crumb(pg):
    return (pg.t(L("خانه", "Home")), "")


def product_card(pg, p, wide=False):
    t = pg.t
    return f"""<a class="card{' wide' if wide else ''}" href="{pg.link('products/' + p['slug'] + '/')}">
<div class="head"><h3>{e(t(p['name']))}</h3><span class="latin">{e(p['latin'])}</span></div>
<span class="for">{e(t(p['for']))}</span>
<p>{e(t(p['summary']))}</p>
<span class="more">{e(t(L('بیشتر بدانید', 'Learn more')))} {'←' if pg.lang == 'fa' else '→'}</span>
</a>"""


def engine_block(pg, key, link_products=True):
    t = pg.t
    en = ENGINES[key]
    pts = "".join(f"<li><span>{e(t(x))}</span></li>" for x in en["points"])
    used = [p for p in PRODUCTS if p["built_on"] == key]
    chips = ""
    if link_products and used:
        chips = '<div class="chips">' + "".join(f'<a href="{pg.link("products/" + p["slug"] + "/")}">{e(t(p["name"]))}</a>' for p in used) + "</div>"
    return f"""<div class="engine" id="{key}">
<div><span class="kind">{e(t(en['kind']))}</span><h3>{e(t(en['name']))}</h3><p>{e(t(en['text']))}</p>{chips}</div>
<ul class="dots">{pts}</ul>
</div>"""


def steps_list(pg, steps):
    return '<ol class="steps">' + "".join(f"<li><h3>{e(pg.t(a))}</h3><p>{e(pg.t(b))}</p></li>" for a, b in steps) + "</ol>"


def pillars(pg):
    return '<div class="pillars">' + "".join(f"<div><h3>{e(pg.t(a))}</h3><p>{e(pg.t(b))}</p></div>" for a, b in PILLARS) + "</div>"


def sectors(pg):
    return '<ul class="who">' + "".join(f"<li>{e(pg.t(s))}</li>" for s in SECTORS) + "</ul>"


# ---------------------------------------------------------------- pages

def home(lang):
    pg = Page("", lang)
    t = pg.t
    title = t(L("هرمز رایا | راهکارهای هوشمند تجاری، تحلیل بازار و سرنخ فروش با هوش مصنوعی",
                "Hormoz Raya | AI market intelligence, lead generation and smart business solutions"))
    desc = t(L("راهکارهای هوشمند هرمز رایا، هسته فناور پارک علم و فناوری هرمزگان: شناخت بازیگران و روابط بازارها با هوش مصنوعی و تبدیل آن به مشتری، فروش و تصمیم.",
               "Hormoz Raya Smart Solutions, a technology core at Hormozgan Science & Technology Park: AI that maps the players and relationships in markets and turns them into customers, sales and decisions."))
    ld = [org_ld(), {"@type": "WebSite", "@id": f"{DOMAIN}/#site", "url": f"{DOMAIN}/", "name": SITE["legal"][lang],
                     "inLanguage": lang, "publisher": {"@id": f"{DOMAIN}/#org"}}]
    out = head(pg, title, desc, ld)
    lead_svc = SERVICES[0]
    svc_links = "".join(f'<a href="{pg.link("services/", anchor=s["id"])}"><h3>{e(t(s["name"]))}</h3><p>{e(t(s["short"]))}</p></a>' for s in SERVICES[1:])
    out += f"""<section class="hero">
<canvas id="chart" aria-hidden="true"></canvas>
<div class="wrap">
<span class="tag"><i></i>{e(t(SITE['park']))}</span>
<h1>{t(L('بازار را مثل یک نقشه می‌خوانیم؛ <em>بازیگرانش، روابطش، فرصت‌هایش.</em>', 'We read markets like a chart: <em>their players, their links, their openings.</em>'))}</h1>
<p class="lead">{e(t(L('راهکارهای هوشمند هرمز رایا با هوش مصنوعی، وب‌کاوی و تحلیل داده، اطلاعات پراکنده بازار را به محصولات و خدماتی تبدیل می‌کند که مشتری پیدا می‌کنند، فروش را ساده می‌کنند و تصمیم را دقیق‌تر.',
    'Hormoz Raya Smart Solutions uses AI, web mining and data analysis to turn scattered market information into products and services that find customers, simplify selling and sharpen decisions.')))}</p>
<div class="cta"><a class="btn solid" href="{pg.link('products/')}">{e(t(L('محصولات ما', 'Our products')))}</a>
<a class="btn ghost" href="{pg.link('services/')}">{e(t(L('راهکار برای کسب‌وکار شما', 'A solution for your business')))}</a></div>
<div class="coords mono"><span>27.18°N 56.27°E</span><span>BANDAR ABBAS · STRAIT OF HORMUZ</span></div>
</div></section>

<section class="block"><div class="wrap split">
<header><span class="eyebrow">{e(t(L('درباره ما', 'ABOUT')))}</span><h2>{e(t(L('یک موتور، چند محصول', 'One engine, many products')))}</h2></header>
<div class="stack"><div class="prose">
<p>{e(t(L('اطلاعاتی که کسب‌وکارها برای فروش و توسعه بازار لازم دارند در منابع زیاد و پراکنده است. جمع کردن و تحلیل آن معمولاً دستی، کند و پرهزینه است و فرصت‌ها در همین فاصله از دست می‌روند.',
    'The information businesses need to sell and grow sits in many scattered sources. Collecting and analysing it is usually manual, slow and expensive, and opportunities slip away in the meantime.')))}</p>
<p>{e(t(L('هرمز رایا زیرساختی هوشمند ساخته است که بازیگران، روابط و فرصت‌های هر بازار را شناسایی و ارزیابی می‌کند. هر محصول ما یک کاربرد از همین زیرساخت است: از تجارت بین‌الملل و صادرات تا فروشگاه‌های کوچک و کسب‌وکارهای روی نقشه.',
    'Hormoz Raya has built intelligent infrastructure that identifies and evaluates the players, relationships and opportunities in any market. Each of our products applies it, from international trade and export to small shops and businesses on the map.')))}</p>
<p><a href="{pg.link('about/')}">{e(t(L('بیشتر درباره ما', 'More about us')))}</a></p>
</div>{pillars(pg)}</div>
</div></section>

<section class="block"><div class="wrap">
<header class="shead"><span class="eyebrow">{e(t(L('محصولات', 'PRODUCTS')))}</span><h2>{e(t(L('از تجارت بین‌الملل تا مغازه سر کوچه', 'From international trade to the corner shop')))}</h2>
<p class="muted">{e(t(L('هر محصول یک مسئله مشخص را برای یک گروه مشخص از مشتریان حل می‌کند.', 'Each product solves one specific problem for one specific group of customers.')))}</p></header>
<div class="cards">{product_card(pg, PRODUCTS[0], wide=True)}{''.join(product_card(pg, p) for p in PRODUCTS[1:])}</div>
</div></section>

<section class="block"><div class="wrap split">
<header><span class="eyebrow">{e(t(L('خدمات', 'SERVICES')))}</span><h2>{e(t(L('مسئله‌تان را بگویید', 'Tell us your problem')))}</h2>
<p class="muted">{e(t(L('همان موتورها، داده‌ها و تیمی که محصولات ما را ساخته‌اند، در اختیار پروژه شما قرار می‌گیرند.', 'The engines, data and team behind our products are available for your project.')))}</p></header>
<div class="stack">
<div class="svc lead-svc"><div><span class="k">{e(t(L('خدمت اصلی', 'Core service')))}</span><h2>{e(t(lead_svc['name']))}</h2></div>
<div><p>{e(t(lead_svc['text']))}</p><a href="{pg.link('services/', anchor=lead_svc['id'])}">{e(t(L('جزئیات این خدمت', 'About this service')))}</a></div></div>
<div class="svc-list">{svc_links}</div>
</div></div></section>

<section class="block"><div class="wrap split">
<header><span class="eyebrow">{e(t(L('زیرساخت', 'PLATFORM')))}</span><h2>{e(t(L('موتورهایی که زیر همه محصولات کار می‌کنند', 'The engines under every product')))}</h2>
<p class="muted">{e(t(L('هر بهبود در موتورها همه محصولات را بهتر می‌کند.', 'Every improvement to them improves every product.')))}</p>
<p><a href="{pg.link('platform/')}">{e(t(L('درباره زیرساخت', 'About the platform')))}</a></p></header>
<div class="stack">{engine_block(pg, 'raya')}{engine_block(pg, 'extractor')}</div>
</div></section>
{cta_band(pg)}
"""
    return pg, out + footer(pg)


def about(lang):
    pg = Page("about/", lang)
    t = pg.t
    title = t(L("درباره هرمز رایا | هسته فناور هوش مصنوعی و تحلیل بازار در بندرعباس", "About Hormoz Raya | AI and market intelligence core in Bandar Abbas"))
    desc = t(L("راهکارهای هوشمند هرمز رایا، هسته فناور مستقر در پارک علم و فناوری هرمزگان است که با هوش مصنوعی و داده، برای مسائل تجاری و صنعتی راهکار هوشمند می‌سازد.",
               "Hormoz Raya Smart Solutions is a technology core at Hormozgan Science & Technology Park that builds AI and data solutions for commercial and industrial problems."))
    trail = [home_crumb(pg), (t(L("درباره ما", "About us")), "about/")]
    out = head(pg, title, desc, [org_ld(), breadcrumbs_ld(pg, trail)])
    out += page_hero(pg, trail, t(L("ما برای مسئله مشتری راهکار هوشمند پیدا می‌کنیم", "We find intelligent solutions to our clients' problems")),
                     t(L("راهکارهای هوشمند هرمز رایا هسته فناوری در پارک علم و فناوری هرمزگان است. زمینه کار ما ارائه راهکارهای هوشمند تجاری و صنعتی با هوش مصنوعی، داده‌کاوی و تحلیل داده است.",
                         "Hormoz Raya Smart Solutions is a technology core at Hormozgan Science & Technology Park. We build intelligent commercial and industrial solutions with AI, data mining and data analysis.")))
    out += f"""<section class="block"><div class="wrap split">
<header><span class="eyebrow">{e(t(L('داستان ما', 'OUR STORY')))}</span><h2>{e(t(L('از بازار قیر تا زیرساخت هوشمند', 'From the bitumen market to intelligent infrastructure')))}</h2></header>
<div class="prose">
<p>{e(t(L('هرمز رایا حاصل چند سال کار عملی در تجارت بین‌الملل، بازاریابی صنعتی و صادرات فرآورده‌های نفتی و معدنی است. در همین کار روزمره دیدیم که پیدا کردن خریدار، شناخت رقبا و فهم یک بازار چقدر به جستجوی دستی، واسطه‌ها و روابط شخصی وابسته است.',
    'Hormoz Raya grew out of years of hands-on work in international trade, industrial marketing and the export of petroleum and mineral products. That daily work showed how much finding buyers, knowing competitors and understanding a market depend on manual searching, intermediaries and personal networks.')))}</p>
<p>{e(t(L('پیش از نوشتن نرم‌افزار، همین روش را با ترکیب نیروی انسانی و ابزارهای هوش مصنوعی در بازارهای قیر و گوگرد آزمودیم و یک پایگاه داده تخصصی از فعالان این بازارها ساختیم که در توسعه بازار واقعی به کار رفت. نتیجه نشان داد این مدل کار می‌کند.',
    'Before writing software, we tested the method in the bitumen and sulphur markets, combining people with AI tools, and built a specialist database of those markets’ players that was used in real market development. It showed the model works.')))}</p>
<p>{e(t(L('امروز همان منطق در قالب یک زیرساخت نرم‌افزاری درآمده است که بازیگران هر بازار را پیدا می‌کند و تصویر بزرگ آن را می‌سازد. محصولات ما، از تجاروس برای صادرکنندگان تا زبل برای فروشگاه‌های کوچک، روی همین زیرساخت ساخته شده‌اند.',
    'Today that logic is software infrastructure that finds the players in any market and draws its big picture. Our products, from Tejaros for exporters to Zebel for small shops, are built on it.')))}</p>
</div></div></section>

<section class="block"><div class="wrap split">
<header><span class="eyebrow">{e(t(L('چرا هرمزگان', 'WHY HORMOZGAN')))}</span><h2>{e(t(L('در دروازه تجارت ایران', 'At Iran’s gateway for trade')))}</h2></header>
<div class="prose">
<p>{e(t(L('بندرعباس بزرگ‌ترین دروازه تجاری ایران و کنار تنگه هرمز است؛ جایی که نفت، فرآورده‌های نفتی، مواد معدنی و کالاهای صادراتی از آن به دنیا می‌روند. نزدیکی به این جریان تجارت و صنایع بزرگ استان، مسائل واقعی و مشتریان واقعی را جلوی چشم ما گذاشته است.',
    'Bandar Abbas is Iran’s largest trade gateway, on the Strait of Hormuz, where oil, petroleum products, minerals and export goods leave for the world. Being close to that trade and to the province’s large industries puts real problems and real customers in front of us.')))}</p>
<p>{e(t(L('استقرار در پارک علم و فناوری هرمزگان به ما امکان می‌دهد با صنایع، صادرکنندگان و نهادهای تجاری منطقه از نزدیک همکاری کنیم.',
    'Being based at Hormozgan Science & Technology Park lets us work closely with the region’s industries, exporters and trade bodies.')))}</p>
</div></div></section>

<section class="block"><div class="wrap">
<header class="shead"><span class="eyebrow">{e(t(L('توانمندی‌ها', 'CAPABILITIES')))}</span><h2>{e(t(L('سه چیزی که با هم ترکیب می‌کنیم', 'Three things we combine')))}</h2></header>
{pillars(pg)}
</div></section>

<section class="block" id="approach"><div class="wrap">
<header class="shead"><span class="eyebrow">{e(t(L('روش کار', 'HOW WE WORK')))}</span><h2>{e(t(L('از مسئله تا نتیجه قابل اندازه‌گیری', 'From problem to measurable result')))}</h2></header>
{steps_list(pg, STEPS)}
</div></section>

<section class="block"><div class="wrap">
<header class="shead"><span class="eyebrow">{e(t(L('حوزه‌ها', 'SECTORS')))}</span><h2>{e(t(L('حوزه‌هایی که در آن تجربه داریم', 'Sectors we know')))}</h2></header>
{sectors(pg)}
</div></section>
{cta_band(pg)}
"""
    return pg, out + footer(pg)


def platform(lang):
    pg = Page("platform/", lang)
    t = pg.t
    title = t(L("زیرساخت فناوری هرمز رایا | گراف هوشمند بازار رایا و موتور داده نقشه", "Hormoz Raya platform | Raya market graph and map data engine"))
    desc = t(L("دو موتور داخلی هرمز رایا: رایا، گراف هوشمند بازیگران و روابط بازار، و استخراج‌گر داده نقشه برای داده کسب‌وکارهای محلی.",
               "Hormoz Raya's two in-house engines: Raya, the intelligence graph of market players and relationships, and the map data extractor for local business data."))
    trail = [home_crumb(pg), (t(L("زیرساخت", "Platform")), "platform/")]
    out = head(pg, title, desc, [org_ld(), breadcrumbs_ld(pg, trail)])
    out += page_hero(pg, trail, t(L("موتورهایی که زیر همه محصولات ما کار می‌کنند", "The engines under every product we make")),
                     t(L("به جای ساختن هر محصول از صفر، دو موتور مشترک ساخته‌ایم. هر محصول یک کاربرد تازه از آن‌هاست و هر بهبود در موتورها همه محصولات را بهتر می‌کند.",
                         "Instead of building each product from scratch, we built two shared engines. Each product is a new application of them, and every improvement to them improves every product.")))
    principles = [
        (L("چند منبع، یک حقیقت", "Many sources, one truth"), L("داده از منابع متعدد جمع می‌شود و پیش از استفاده یکسان و بدون تکرار می‌شود.", "Data comes from many sources and is standardised and de-duplicated before use.")),
        (L("امتیاز بر پایه شواهد", "Scores from evidence"), L("هر رتبه و امتیاز به داده واقعی پشت آن برمی‌گردد.", "Every rank and score traces back to the real data behind it.")),
        (L("محاسبه فقط وقتی لازم است", "Compute only when needed"), L("نتایج سنگین ذخیره می‌شوند و فقط وقتی داده تغییر کند دوباره محاسبه می‌شوند؛ پاسخ سریع و هزینه کمتر.", "Expensive results are cached and recomputed only when the data changes: faster answers, lower cost.")),
        (L("مستقل از مدل هوش مصنوعی", "Model-agnostic AI"), L("ارائه‌دهنده‌های مختلف هوش مصنوعی قابل جایگزینی‌اند، با مدل مناسب برای فارسی و انگلیسی.", "AI providers are interchangeable, with the right model for Farsi and for English.")),
        (L("فارسی و انگلیسی", "Farsi and English"), L("همه موتورها از ابتدا برای کار با هر دو زبان طراحی شده‌اند.", "Every engine is designed for both languages from the start.")),
        (L("ماژولار", "Modular"), L("هر بازار یا کاربرد تازه یک ماژول روی همان زیرساخت است.", "Each new market or use is a module on the same infrastructure.")),
    ]
    feats = "".join(f"<div><h3>{e(t(a))}</h3><p>{e(t(b))}</p></div>" for a, b in principles)
    out += f"""<section class="block"><div class="wrap stack">
{engine_block(pg, 'raya')}
{engine_block(pg, 'extractor')}
</div></section>
<section class="block"><div class="wrap">
<header class="shead"><span class="eyebrow">{e(t(L('اصول طراحی', 'DESIGN PRINCIPLES')))}</span><h2>{e(t(L('چطور ساخته شده‌اند', 'How they are built')))}</h2></header>
<div class="features">{feats}</div>
</div></section>
{cta_band(pg)}
"""
    return pg, out + footer(pg)


def products_index(lang):
    pg = Page("products/", lang)
    t = pg.t
    title = t(L("محصولات هرمز رایا | تجاروس، زبل، مپ‌مارکتینگ، خدمات نقشه و وبینوا",
                "Hormoz Raya products | Tejaros, Zebel, MapMarketing, Map Services and Webinova"))
    desc = t(L("محصولات هوشمند هرمز رایا برای صادرکنندگان، فروشگاه‌ها، تیم‌های فروش و کسب‌وکارهای محلی.",
               "Hormoz Raya's intelligent products for exporters, shops, sales teams and local businesses."))
    trail = [home_crumb(pg), (t(L("محصولات", "Products")), "products/")]
    items = {"@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": abs_url(f"products/{p['slug']}/", lang), "name": p["name"][lang]} for i, p in enumerate(PRODUCTS)]}
    out = head(pg, title, desc, [org_ld(), breadcrumbs_ld(pg, trail), items])
    out += page_hero(pg, trail, t(L("محصولات ما", "Our products")),
                     t(L("هر محصول یک مسئله مشخص را برای یک گروه مشخص از مشتریان حل می‌کند و روی زیرساخت مشترک ما ساخته شده است.",
                         "Each product solves one specific problem for one specific group of customers, built on our shared infrastructure.")))
    out += f"""<section class="block"><div class="wrap">
<div class="cards">{product_card(pg, PRODUCTS[0], wide=True)}{''.join(product_card(pg, p) for p in PRODUCTS[1:])}</div>
</div></section>
{cta_band(pg)}
"""
    return pg, out + footer(pg)


def product_page(p, lang):
    pg = Page(f"products/{p['slug']}/", lang)
    t = pg.t
    trail = [home_crumb(pg), (t(L("محصولات", "Products")), "products/"), (t(p["name"]), pg.path)]
    if p["slug"] == "map-services":
        main_ld = {"@type": "Service", "name": p["name"][lang], "description": p["seo_desc"][lang], "provider": {"@id": f"{DOMAIN}/#org"},
                   "areaServed": "IR", "url": abs_url(pg.path, lang)}
    else:
        main_ld = {"@type": "SoftwareApplication", "name": p["name"][lang], "description": p["seo_desc"][lang], "applicationCategory": "BusinessApplication",
                   "operatingSystem": "Web", "publisher": {"@id": f"{DOMAIN}/#org"}, "inLanguage": ["fa", "en"], "url": abs_url(pg.path, lang)}
    if p.get("url"):
        main_ld["sameAs"] = [p["url"]]
    faq_ld = {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q[lang], "acceptedAnswer": {"@type": "Answer", "text": a[lang]}} for q, a in p["faq"]]}
    out = head(pg, t(p["seo_title"]), t(p["seo_desc"]), [org_ld(), breadcrumbs_ld(pg, trail), main_ld, faq_ld])
    visit = ""
    if p.get("url"):
        domain = p["url"].split("//", 1)[1]
        visit = f'<div class="cta"><a class="btn solid" href="{p["url"]}" rel="noopener">{e(t(L("ورود به", "Visit")))} <span class="mono">{domain}</span></a></div>'
    out += page_hero(pg, trail, f"{t(p['name'])}: {t(p['tagline'])}", t(p["summary"]), extra=f'<span class="for">{e(t(p["for"]))}</span>', after=visit)
    problem = "".join(f"<p>{e(t(x))}</p>" for x in p["problem"])
    feats = "".join(f"<div><h3>{e(t(a))}</h3><p>{e(t(b))}</p></div>" for a, b in p["features"])
    who = '<ul class="who">' + "".join(f"<li>{e(t(x))}</li>" for x in p["audience"]) + "</ul>"
    faq = "".join(f"<details><summary>{e(t(q))}</summary><p>{e(t(a))}</p></details>" for q, a in p["faq"])
    note = f'<p class="muted">{e(t(p["note"]))}</p>' if p.get("note") else ""
    built = ""
    if p["built_on"]:
        built = f"""<section class="block"><div class="wrap">
<header class="shead"><span class="eyebrow">{e(t(L('زیرساخت', 'PLATFORM')))}</span><h2>{e(t(L('ساخته‌شده روی', 'Built on')))} {e(t(ENGINES[p['built_on']]['name']))}</h2></header>
{engine_block(pg, p['built_on'], link_products=False)}
<p style="margin-top:16px"><a href="{pg.link('platform/')}">{e(t(L('درباره زیرساخت ما', 'About our platform')))}</a></p>
</div></section>"""
    related = [s for s in SERVICES if s["related"] == p["slug"]]
    rel = ""
    if related:
        rel_links = "".join(f'<a href="{pg.link("services/", anchor=s["id"])}"><h3>{e(t(s["name"]))}</h3><p>{e(t(s["short"]))}</p></a>' for s in related)
        rel = f"""<section class="block"><div class="wrap">
<header class="shead"><span class="eyebrow">{e(t(L('خدمات مرتبط', 'RELATED SERVICES')))}</span><h2>{e(t(L('اگر بخواهید ما برایتان انجام دهیم', 'If you would rather we did it for you')))}</h2></header>
<div class="svc-list">{rel_links}</div></div></section>"""
    others = [x for x in PRODUCTS if x["slug"] != p["slug"]]
    other_links = '<div class="chips">' + "".join(f'<a href="{pg.link("products/" + x["slug"] + "/")}">{e(t(x["name"]))}</a>' for x in others) + "</div>"
    out += f"""<section class="block"><div class="wrap split">
<header><span class="eyebrow">{e(t(L('مسئله', 'THE PROBLEM')))}</span><h2>{e(t(L('چرا', 'Why')))} {e(t(p['name']))}</h2></header>
<div class="prose">{problem}{note}</div>
</div></section>
<section class="block"><div class="wrap">
<header class="shead"><span class="eyebrow">{e(t(L('امکانات', 'FEATURES')))}</span><h2>{e(t(L('چه کاری انجام می‌دهد', 'What it does')))}</h2></header>
<div class="features">{feats}</div>
</div></section>
<section class="block"><div class="wrap">
<header class="shead"><span class="eyebrow">{e(t(L('روند کار', 'HOW IT WORKS')))}</span><h2>{e(t(L('چطور کار می‌کند', 'How it works')))}</h2></header>
{steps_list(pg, p['how'])}
</div></section>
<section class="block"><div class="wrap split">
<header><span class="eyebrow">{e(t(L('مخاطبان', 'WHO IT IS FOR')))}</span><h2>{e(t(L('برای چه کسانی است', 'Who it is for')))}</h2></header>
<div>{who}</div>
</div></section>
{built}
<section class="block"><div class="wrap split">
<header><span class="eyebrow">{e(t(L('پرسش‌های رایج', 'FAQ')))}</span><h2>{e(t(L('پرسش‌های رایج', 'Common questions')))}</h2></header>
<div class="faq">{faq}</div>
</div></section>
{rel}
<section class="block"><div class="wrap" style="display:grid;gap:14px">
<span class="eyebrow">{e(t(L('محصولات دیگر', 'OTHER PRODUCTS')))}</span>{other_links}
</div></section>
{cta_band(pg)}
"""
    return pg, out + footer(pg)


def services(lang):
    pg = Page("services/", lang)
    t = pg.t
    title = t(L("خدمات هرمز رایا | راهکار هوشمند اختصاصی، توسعه بازار صادراتی و تحلیل بازار",
                "Hormoz Raya services | Custom AI solutions, export market development and market research"))
    desc = t(L("راهکار هوشمند اختصاصی برای مسئله کسب‌وکار شما، توسعه بازار صادراتی با کارمزد از معامله موفق، گزارش بازار، پنل سازمانی، داده و API، حضور روی نقشه و فروش چندکاناله.",
               "Custom intelligent solutions for your business problem, export market development paid on successful deals, market reports, enterprise panels, data and API, map presence and multi-channel selling."))
    trail = [home_crumb(pg), (t(L("خدمات", "Services")), "services/")]
    svc_ld = [{"@type": "Service", "@id": abs_url(f"services/#{s['id']}", lang), "name": s["name"][lang], "description": s["text"][lang],
               "provider": {"@id": f"{DOMAIN}/#org"}, "areaServed": "IR"} for s in SERVICES]
    out = head(pg, title, desc, [org_ld(), breadcrumbs_ld(pg, trail)] + svc_ld)
    out += page_hero(pg, trail, t(L("خدماتی که ارائه می‌دهیم", "Services we provide")),
                     t(L("همان موتورها، داده‌ها و تیمی که محصولات ما را ساخته‌اند، برای حل مسئله کسب‌وکار شما به کار می‌افتند.",
                         "The engines, data and team behind our products go to work on your business problem.")))
    blocks = ""
    for s in SERVICES:
        gets = "".join(f"<li>{e(t(x))}</li>" for x in s["gets"])
        rel = ""
        if s["related"]:
            rp = PRODUCT[s["related"]]
            rel = f'<p class="muted">{e(t(L("محصول مرتبط:", "Related product:")))} <a href="{pg.link("products/" + rp["slug"] + "/")}">{e(t(rp["name"]))}</a></p>'
        k = f'<span class="k">{e(t(L("خدمت اصلی", "Core service")))}</span>' if s.get("lead") else ""
        blocks += f"""<article class="svc{' lead-svc' if s.get('lead') else ''}" id="{s['id']}">
<div>{k}<h2>{e(t(s['name']))}</h2><p class="muted">{e(t(s['short']))}</p></div>
<div class="prose" style="font-size:1rem"><p>{e(t(s['text']))}</p>
<p><strong>{e(t(L('آنچه دریافت می‌کنید', 'What you get')))}</strong></p><ul>{gets}</ul>{rel}</div>
</article>"""
    out += f"""<section class="block"><div class="wrap">{blocks}</div></section>
<section class="block"><div class="wrap">
<header class="shead"><span class="eyebrow">{e(t(L('روش کار', 'HOW WE WORK')))}</span><h2>{e(t(L('از مسئله تا نتیجه قابل اندازه‌گیری', 'From problem to measurable result')))}</h2></header>
{steps_list(pg, STEPS)}
</div></section>
{cta_band(pg)}
"""
    return pg, out + footer(pg)


def contact(lang):
    pg = Page("contact/", lang)
    t = pg.t
    title = t(L("تماس با هرمز رایا | بندرعباس، پارک علم و فناوری هرمزگان", "Contact Hormoz Raya | Bandar Abbas, Hormozgan Science & Technology Park"))
    desc = t(L("برای معرفی محصولات، جلسه نمایش یا گفت‌وگو درباره یک راهکار هوشمند اختصاصی با هرمز رایا تماس بگیرید.",
               "Contact Hormoz Raya for a product introduction, a demo or a conversation about a custom intelligent solution."))
    trail = [home_crumb(pg), (t(L("تماس", "Contact")), "contact/")]
    out = head(pg, title, desc, [org_ld(), breadcrumbs_ld(pg, trail), {"@type": "ContactPage", "url": abs_url(pg.path, lang), "about": {"@id": f"{DOMAIN}/#org"}}])
    out += page_hero(pg, trail, t(L("درباره مسئله‌تان با ما صحبت کنید", "Talk to us about your problem")),
                     t(L("برای معرفی محصولات، جلسه نمایش یا گفت‌وگو درباره یک راهکار اختصاصی با ما تماس بگیرید.",
                         "Get in touch for a product introduction, a demo or a conversation about a custom solution.")))
    copy = e(t(L("کپی", "Copy")))
    tips = [L("کسب‌وکار شما چیست و به چه کسانی می‌فروشد", "What your business does and who it sells to"),
            L("مسئله‌ای که می‌خواهید حل شود", "The problem you want solved"),
            L("محصول یا خدمتی که به آن علاقه دارید، اگر می‌دانید", "The product or service you are interested in, if you know")]
    tips_html = "".join(f"<li>{e(t(x))}</li>" for x in tips)
    out += f"""<section class="block"><div class="wrap stack">
<div class="contact">
<div><span class="eyebrow">{e(t(L('تلفن', 'Phone')))}</span><a class="v mono" id="phone" href="tel:{SITE['phone_tel']}">{e(SITE['phone_display'])}</a><button class="copy" type="button" data-copy="phone">{copy}</button></div>
<div><span class="eyebrow">{e(t(L('ایمیل', 'Email')))}</span><a class="v mono" id="email" href="mailto:{SITE['email']}">{e(SITE['email'])}</a><button class="copy" type="button" data-copy="email">{copy}</button></div>
<div><span class="eyebrow">{e(t(L('نشانی', 'Address')))}</span><span class="v">{e(t(SITE['address']))}</span></div>
</div>
<div class="prose"><h2>{e(t(L('برای یک گفت‌وگوی مفید', 'For a useful first conversation')))}</h2>
<p>{e(t(L('اگر این‌ها را در پیام اول بگویید، سریع‌تر می‌توانیم راهکار مناسب را پیشنهاد کنیم:', 'If your first message covers these, we can suggest the right solution faster:')))}</p>
<ul>{tips_html}</ul></div>
</div></section>
"""
    return pg, out + footer(pg)


def not_found(lang):
    pg = Page("", lang)
    pg.absolute = True
    t = pg.t
    out = head(pg, t(L("صفحه پیدا نشد | هرمز رایا", "Page not found | Hormoz Raya")), t(L("این صفحه وجود ندارد.", "This page does not exist.")), [org_ld()])
    out = out.replace('<link rel="canonical"', '<meta name="robots" content="noindex">\n<link rel="canonical"', 1)
    out += f"""<section><div class="wrap notfound">
<span class="mono">404</span>
<h1 style="font-size:var(--step-3)">{e(t(L('این صفحه پیدا نشد', 'This page was not found')))}</h1>
<p class="muted">{e(t(L('شاید نشانی تغییر کرده باشد. از صفحه اصلی شروع کنید.', 'The address may have changed. Start from the home page.')))}</p>
<a class="btn solid" href="{pg.link('')}">{e(t(L('صفحه اصلی', 'Home page')))}</a>
</div></section>
"""
    return pg, out + footer(pg)


# ---------------------------------------------------------------- write

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    urls = []
    for lang in ("fa", "en"):
        builders = [home, about, platform, products_index, services, contact] + [lambda l, p=p: product_page(p, l) for p in PRODUCTS]
        for build in builders:
            pg, doc = build(lang)
            target = OUT / lang_prefix(lang) / pg.path / "index.html"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(doc, encoding="utf-8")
            if lang == "fa":
                urls.append(pg.path)
        pg, doc = not_found(lang)
        (OUT / lang_prefix(lang) / "404.html").write_text(doc, encoding="utf-8")

    entries = []
    for path in urls:
        for lang in ("fa", "en"):
            alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{abs_url(path, l)}"/>' for l in ("fa", "en"))
            alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{abs_url(path, "fa")}"/>'
            prio = "1.0" if path == "" else ("0.9" if path.startswith("products/") or path == "services/" else "0.7")
            entries.append(f"  <url>\n    <loc>{abs_url(path, lang)}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <priority>{prio}</priority>{alts}\n  </url>")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(entries) + "\n</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")
    print(f"Built {len(urls) * 2} pages + 2 not-found pages into {OUT}")


if __name__ == "__main__":
    main()
