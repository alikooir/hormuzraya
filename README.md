# Hormoz Raya website

Read-only website for **Hormoz Raya Smart Solutions** (راهکارهای هوشمند هرمز رایا), a technology core at Hormozgan Science & Technology Park, Bandar Abbas.

Main address: **https://hormozraya.ir**. `hormuzraya.ir` and the `www` names redirect to it.

## Layout

| Path | What it is |
|---|---|
| `public/` | **The finished website.** Upload this folder to the host. |
| `site/content.py` | All the text, in Farsi and English. Edit copy here. |
| `site/build.py` | Turns the content into the pages in `public/`. |
| `site/assets/` | Stylesheet, script, fonts (Vazirmatn, self-hosted), icons, link-preview images |
| `site/tools/make-images.js` | Regenerates the icons and link-preview images |
| `deploy/nginx.conf` | Server config with HTTPS and the domain redirects |

## Pages

Farsi pages are at `/`, English pages under `/en/`, with the same structure:

- `/` home
- `/products/` and one page per product: `tejaros`, `zebel`, `mapmarketing`, `map-services`, `site-builder`
- `/services/` (each service has an anchor, such as `/services/#export-development`)
- `/platform/` the Raya and map-data engines
- `/about/`
- `/contact/`

## Changing text

1. Edit `site/content.py` (product, service and contact text) or `site/build.py` (home, about and platform page text). Every text is a pair: `L("فارسی", "English")`.
2. Run `python3 site/build.py` (Python 3.11+, no extra packages).
3. Upload the new `public/` folder.

`python3 site/build.py --preview` builds a copy whose links end in `index.html`, for clicking through the pages straight from disk.

## SEO built in

- Separate URL per page and language, with `hreflang` links between translations
- Own title and description on every page
- Canonical URLs on `https://hormozraya.ir`
- Open Graph and Twitter tags with a link-preview image per language
- JSON-LD structured data: Organization, WebSite, BreadcrumbList, SoftwareApplication or Service, FAQPage
- `sitemap.xml` (with language alternates) and `robots.txt`
- Self-hosted fonts, so pages load quickly in Iran

After launch, add the site to Google Search Console and submit `https://hormozraya.ir/sitemap.xml`.

## Hosting

Any static host works. On a Linux server with Nginx, use `deploy/nginx.conf` (the steps are at the top of the file).
