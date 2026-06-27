# Logo Replacement Report

## Root Cause

The deployed SVG at `/static/frontend/brand-logo.svg` was correct, but `MainLayout.jsx` still used the previous build-time logo reference and old logo classes:

- `BRAND_LOGO = ${import.meta.env.BASE_URL}brand-logo.svg`
- `brand-logo brand-logo-sidebar`
- `brand-logo brand-logo-header`

Those classes and references allowed the old header/logo styling and cached bundle behavior to remain visible in the header.

## Replacement

The site logo in `frontend/src/layouts/MainLayout.jsx` was replaced with the explicit static asset path:

```jsx
<img
  src="/static/frontend/brand-logo.svg"
  alt="Axborot Texnologiyalari va Menejment Universiteti"
  className="site-logo"
/>
```

This replacement was applied in:

- Sidebar brand area
- Header/topbar brand area
- Login page logo
- Landing/course list hero logo

## CSS Update

Added `site-logo` styling:

- `height: 48px` on desktop
- `height: 36px` on mobile
- `width: auto`
- `object-fit: contain`
- `border-radius: 0`
- `background: transparent`
- `box-shadow: none`

Removed obsolete header/sidebar logo CSS references:

- `.brand-logo-sidebar`
- `.brand-logo-header`
- `.sidebar-collapsed .brand-logo-sidebar`

## Obsolete References Removed

Removed from `MainLayout.jsx`:

- `BRAND_LOGO`
- Header/sidebar `brand-logo-*` logo classes
- Build-time logo path through `import.meta.env.BASE_URL`

Removed from `LoginPage.jsx` and `CourseListPage.jsx`:

- Remaining `BRAND_LOGO` constants
- Remaining build-time logo paths through `import.meta.env.BASE_URL`

No hardcoded SVG, Lucide icon, Bootstrap icon, or React icon is used as the site logo in `MainLayout.jsx`.

## Build And Static Files

The frontend was rebuilt and copied into Django static/template output:

- `backend/templates/frontend/index.html`
- `backend/static/frontend/`

## Verification

Verified source references:

- `MainLayout.jsx` uses only `/static/frontend/brand-logo.svg` for the site logo.
- `MainLayout.jsx` uses `className="site-logo"` for the site logo.
- `frontend/src/styles.css` defines desktop and mobile `site-logo` sizing.

Commands run:

```bash
npm ci
powershell -ExecutionPolicy Bypass -File scripts/build_cpanel_static.ps1
python manage.py check
python manage.py collectstatic --noinput
```
