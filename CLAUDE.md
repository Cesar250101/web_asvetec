# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Module identity

`web_asvetec` is an Odoo 16 module that renders the full ASVETEC storefront (RyS ASVETEC Ltda., industrial equipment/services in northern Chile) at `/asvetec`, plus a themed override of the native `/shop`. It has its own git repo (branches `16.0` / `master`) nested inside the Odoo `addons/` tree.

- Manifest version is the contract: bumping `version` in `__manifest__.py` triggers the matching script under `migrations/<version>/post-migrate.py` on `-u web_asvetec`.
- Depends only on `website` and `website_sale` — no sibling internal modules.

## Common commands

Run from a shell that has the Odoo venv active (Windows host, `python` resolves to Odoo's interpreter):

```powershell
# Install / upgrade only this module against a database
python "c:\Program Files\Odoo 16\server\odoo-bin" -c odoo.conf -d <db> -u web_asvetec --stop-after-init

# Regenerate the brochure PDF (one-off asset, not run automatically)
python addons\web_asvetec\static\generate_brochure.py
```

There is no lint/test/build pipeline checked in, and no `tests/` folder — Odoo's `--test-tags` runner is available but unused today.

## Architecture — the big picture

### 1. Everything is self-contained per snippet — there is no page controller assembling data
[views/pages/home.xml](views/pages/home.xml) (`asv_home`) is just eight `t-call`s to the snippet templates, in a plain `oe_structure` (drag/reorder/remove works in the website editor). Each snippet template in `views/snippets/s_asv_*.xml` queries `request.env[...].sudo().search(...)` directly at render time — e.g. [s_asv_featured_products.xml](views/snippets/s_asv_featured_products.xml) pulls `product.template` filtered by the `product.ribbon` whose `html` matches "en stock", derives its own filter-category list and an SVG icon fallback pool, all inline in QWeb. When adding a new snippet, follow this pattern rather than passing data from a controller — there is no controller route that renders the homepage with a data dict (`AsvController.home` in [controllers/main.py](controllers/main.py) just resolves `web_asvetec.asv_home` **by numeric view id via `env.ref`**, not by xml_id string — this is deliberate, to dodge COW id-vs-key lookup issues once the view has a `website_id`).

### 2. Category icons are SVG-first, PNG is a generated fallback
`product.public.category` is extended with `asv_svg_icon` (Text, inline SVG markup) in [models/category_icon.py](models/category_icon.py). Every snippet and the shop override renders this SVG directly with `t-raw`. Separately, `hooks.py::assign_category_icons` generates a **PNG** version of each category's icon (via Pillow — colored circle on light-blue background, one accent color per category keyed by xmlid in `_CAT_ICON_COLORS`) and writes it to `image_1920`, purely so the category has *some* image for other Odoo views (backend, generic themes) that don't know about `asv_svg_icon`. If you add a new category, add its xmlid+color to `_CAT_ICON_COLORS` too, or it silently gets no PNG icon.

### 3. Data lifecycle: data files vs. hooks vs. migrations
- **`data/categories_data.xml`** (no `noupdate` — reloads on every upgrade) — declares the 8 `product.public.category` records with their inline SVGs. Editing an SVG here takes effect on `-u`.
- **`data/website_data.xml`** (`noupdate="1"`) — declares the `website` record (`ASVETEC`). Only applied on install.
- **`hooks.py::post_init_hook`** — runs once on install: calls `assign_category_icons(force=False)`, then sets the site's default language and creates top-menu items (`Catálogo → /shop`, `Quiénes somos → /asvetec#nosotros`, etc.), skipping any that already exist by URL.
- **`migrations/<version>/post-migrate.py`** — runs on every `-u` after the manifest version bump. History here matters: 1.1.0 first assigned PNG icons; 1.2.0 re-ran `assign_category_icons(force=True)` because the 1.1.0 PNGs were hand-built with `struct`/`zlib` and some environments rejected them (Pillow is now the only PNG path); 1.3.0 removed the in-page `#contacto` menu entry in favor of the native `/contactus` page. Follow this precedent: new migrations should stay narrowly scoped to the delta the version bump requires, and reuse `assign_category_icons`/menu-search-then-create helpers from `hooks.py` rather than re-implementing them.

### 4. Quote form has an email fallback, not just CRM
`POST /asvetec/cotizar` in [controllers/main.py](controllers/main.py) tries to create a `crm.lead`; if that raises for any reason, it falls back to sending a plain `mail.mail` to `ventas@asvetec.cl` instead of failing the request. Both paths render the same `asv_cotizar_ok` confirmation page. If you touch this route, preserve the try/except fallback — it is the only thing standing between a broken CRM config and a lost lead.

### 5. Site isolation pattern for shop/layout overrides
Overrides of shared Odoo templates are gated by `t-if="website and website.name == 'ASVETEC'"` so they don't leak to other websites on the same instance:
- [views/layout/asv_header.xml](views/layout/asv_header.xml) injects Google Fonts and an `asv-body` class onto `#wrapwrap` via `inherit_id="website.layout"`.
- [views/layout/asv_shop_overrides.xml](views/layout/asv_shop_overrides.xml) replaces the `website_sale.filmstrip_categories` `<li>` entirely (via `position="replace"`) to swap the native PNG category thumbnails for `asv_svg_icon`, falling back to the stock rendering (`t-else`) for every other site.

### 6. Snippet authoring convention
Each snippet is a matched set of files, named `s_asv_<name>`:
```
views/snippets/s_asv_<name>.xml           — <template id="s_asv_<name>"> with the section markup
static/src/scss/snippets/s_asv_<name>.scss — styles
static/src/js/snippets/s_asv_<name>/000.js  — publicWidget, only where interactivity is needed (hero, brands carousel, featured-products filter/pagination)
views/snippets/snippets.xml                 — registers the snippet in the ASVETEC editor panel via inherit_id="website.snippets"
```
A snippet not added to `snippets.xml` won't appear in the drag-and-drop panel even if its template/SCSS/JS exist.

### 7. Asset bundle order matters
In `__manifest__.py::assets['web.assets_frontend']`: `asv_tokens.scss` (CSS custom properties — colors, spacing, font stacks, radii, shadows) must load **first**, before `asv_layout.scss`/`asv_footer.scss`/`asv_shop.scss` and any per-snippet SCSS, since everything else consumes those `--asv-*` variables. New tokens go in `asv_tokens.scss`; snippet-local styles stay in the snippet's own file.

## Brand reference (used in SCSS tokens, [asv_tokens.scss](static/src/scss/asv_tokens.scss))
Palette: navy `#1c1a44`/`#2c2c61`, purple `#360e63`, blue `#2f5a93`/`#518abc`, cyan `#0f9fe6` (primary accent). Fonts: Barlow Condensed (display, injected via Google Fonts only on the ASVETEC site) + Open Sans (body).
