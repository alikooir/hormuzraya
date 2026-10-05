# Hormoz Raya website

Read-only bilingual (Farsi / English) website for **Hormoz Raya Smart Solutions** (راهکارهای هوشمند هرمز رایا), a technology core at Hormozgan Science & Technology Park, Bandar Abbas.

The whole site is one static file, `index.html`. It has no build step and no server code: put it on any static host (Nginx, Apache, GitHub Pages, Cloudflare Pages).

- Opens in Farsi (RTL). The header button switches to English (LTR), and the browser remembers the choice.
- Follows the visitor's light or dark system setting.
- Fonts load from Google Fonts (Reem Kufi, Vazirmatn, IBM Plex Mono), with system fonts as fallback.

## Editing content

Every piece of text appears twice, once per language:

```html
<span class="fa">متن فارسی</span><span class="en">English text</span>
```

Edit both when you change copy. Sections: `#about`, `#engines`, `#products`, `#services`, `#approach`, `#contact`.
