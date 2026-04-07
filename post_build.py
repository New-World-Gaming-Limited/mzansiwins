#!/usr/bin/env python3
"""
Post-build fixups:
1. Add noopener noreferrer to ALL external links
2. Fix missing alt text on images
3. Em-dash cleanup
4. Minify CSS
5. Optimize wanejo-bets.png if exists
"""
import re, os, glob, json

OUT = '/home/user/workspace/mzansiwins-html'

# ============================================================
# 0. STRIP .html FROM ALL INTERNAL HREFS
# ============================================================
print("0. Stripping .html from internal hrefs (extensionless URLs)...")
html_strip_count = 0
for html_file in glob.glob(f'{OUT}/**/*.html', recursive=True):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    def strip_html_ext(match):
        full = match.group(0)  # e.g. href="../betting-sites.html"
        url = match.group(1)   # e.g. ../betting-sites.html
        # Skip external links, anchors, mailto, tel, javascript, assets, empty
        if url.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:', '#', '//')):
            return full
        # Skip non-.html files (css, js, svg, jpg, png, xml, json, txt, pdf, ico, webp, etc.)
        if not url.endswith('.html'):
            return full
        # Strip .html extension
        new_url = url[:-5]  # remove '.html'
        # index → directory root
        if new_url.endswith('/index'):
            new_url = new_url[:-5]  # ".../index" → ".../ "
        elif new_url == 'index':
            new_url = './'
        return f'href="{new_url}"'

    content = re.sub(r'href="([^"]*)"', strip_html_ext, content)

    if content != original:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        html_strip_count += 1

print(f"   Stripped .html from internal hrefs in {html_strip_count} files")

# ============================================================
# 1. ADD NOOPENER NOREFERRER TO EXTERNAL LINKS
# ============================================================
print("1. Adding noopener noreferrer to external links...")
ext_count = 0
for html_file in glob.glob(f'{OUT}/**/*.html', recursive=True):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Match <a> tags with target="_blank" that don't already have noopener
    def add_noopener(match):
        tag = match.group(0)
        if 'noopener' in tag:
            return tag
        if 'rel="' in tag:
            # Append to existing rel
            tag = re.sub(r'rel="([^"]*)"', lambda m: f'rel="{m.group(1)} noopener noreferrer"' if 'noopener' not in m.group(1) else m.group(0), tag)
        else:
            # Add rel attribute
            tag = tag.replace('target="_blank"', 'target="_blank" rel="noopener noreferrer"')
        return tag
    
    content = re.sub(r'<a\s[^>]*target="_blank"[^>]*>', add_noopener, content)
    
    if content != original:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        ext_count += 1

print(f"   Fixed external links in {ext_count} files")

# ============================================================
# 2. FIX MISSING ALT TEXT ON IMAGES
# ============================================================
print("2. Fixing missing alt text on images...")
alt_count = 0
for html_file in glob.glob(f'{OUT}/**/*.html', recursive=True):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Fix empty alt="" on non-decorative images (skip aria-hidden ones)
    def fix_alt(match):
        tag = match.group(0)
        if 'aria-hidden' in tag:
            return tag  # Decorative, leave empty
        # Try to extract brand/context from src
        src_match = re.search(r'src="[^"]*?/([^/"]+?)\.(?:svg|png|jpg|webp)', tag)
        if src_match:
            name = src_match.group(1).replace('-', ' ').replace('_', ' ').title()
            return tag.replace('alt=""', f'alt="{name} logo"')
        return tag
    
    content = re.sub(r'<img\s[^>]*alt=""[^>]*>', fix_alt, content)
    
    if content != original:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        alt_count += 1

print(f"   Fixed alt text in {alt_count} files")

# ============================================================
# 3. EM-DASH CLEANUP
# ============================================================
print("3. Removing em-dashes...")
dash_count = 0
for html_file in glob.glob(f'{OUT}/**/*.html', recursive=True):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    content = content.replace('\u2013', '-')  # en-dash
    content = content.replace('\u2014', '-')  # em-dash
    content = content.replace('&mdash;', '-')
    content = content.replace('&ndash;', '-')
    
    if content != original:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        dash_count += 1

print(f"   Cleaned dashes in {dash_count} files")

# ============================================================
# 3b. ENCODE EMAIL ADDRESSES (prevent Cloudflare email obfuscation)
# ============================================================
print("3b. Encoding email addresses to prevent Cloudflare obfuscation...")
email_count = 0
def encode_email_display(m):
    """Encode visible email text with HTML entities so Cloudflare doesn't replace it."""
    email = m.group(0)
    return ''.join(f'&#x{ord(c):x};' for c in email)

for html_file in glob.glob(f'{OUT}/**/*.html', recursive=True):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    # Encode mailto: href values
    content = re.sub(r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                     lambda m: 'mailto:' + ''.join(f'&#x{ord(c):x};' for c in m.group(1)),
                     content)
    # Encode visible email text (not inside attributes)
    content = re.sub(r'>([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})<',
                     lambda m: '>' + ''.join(f'&#x{ord(c):x};' for c in m.group(1)) + '<',
                     content)
    if content != original:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        email_count += 1
print(f"   Encoded emails in {email_count} files")

# ============================================================
# 4. MINIFY CSS (rcssmin)
# ============================================================
print("4. Minifying CSS...")
try:
    import rcssmin
    css_file = f'{OUT}/assets/style.css'
    with open(css_file, 'r') as f:
        css = f.read()
    original_size = len(css)
    css_min = rcssmin.cssmin(css)
    new_size = len(css_min)
    saved = original_size - new_size
    print(f"   CSS: {original_size:,} -> {new_size:,} bytes (saved {saved:,} bytes, {saved/original_size*100:.1f}%)")
    with open(css_file, 'w') as f:
        f.write(css_min)
except ImportError:
    print("   rcssmin not installed, skipping CSS minification")

# ============================================================
# 4b. MINIFY JS (rjsmin)
# ============================================================
print("4b. Minifying JS...")
try:
    import rjsmin
    js_file = f'{OUT}/assets/main.js'
    if os.path.exists(js_file):
        with open(js_file, 'r') as f:
            js = f.read()
        original_size = len(js)
        js_min = rjsmin.jsmin(js)
        new_size = len(js_min)
        saved = original_size - new_size
        print(f"   JS: {original_size:,} -> {new_size:,} bytes (saved {saved:,} bytes, {saved/original_size*100:.1f}%)")
        with open(js_file, 'w') as f:
            f.write(js_min)
    else:
        print("   No main.js found")
except ImportError:
    print("   rjsmin not installed, skipping JS minification")

# ============================================================
# 5. OPTIMISE IMAGES (convert to WebP if possible)
# ============================================================
print("5. Checking for image optimisation opportunities...")
wanejo = f'{OUT}/assets/logos/wanejo-bets.png'
if os.path.exists(wanejo):
    size = os.path.getsize(wanejo)
    print(f"   wanejo-bets.png: {size:,} bytes")
    # Can't convert without PIL, but flag it
    if size > 5000:
        print(f"   Consider converting to WebP for further savings")
else:
    print("   No wanejo-bets.png found")

# ============================================================
# 6. ADD CATEGORY LINKS FROM BETTING/CASINO TO SUBCATEGORIES
# ============================================================
# This was a user request: "we should have links from betting-sites to subcategories"
print("6. Checking category-to-subcategory cross links...")
# These are now handled in the build itself via the expansion module

print("\n=== POST-BUILD FIXUPS COMPLETE ===")

# ============================================================
# 7. PERFORMANCE OPTIMIZATION - Critical CSS + Non-render-blocking
# ============================================================
print("7. Applying performance optimizations...")

import re

# Read the critical CSS
critical_css_path = os.path.join(OUT, 'assets/critical.css')
if os.path.exists(critical_css_path):
    with open(critical_css_path) as f:
        critical_css = f.read().strip()
    # Minify
    critical_css = re.sub(r'/\*.*?\*/', '', critical_css, flags=re.DOTALL)
    critical_css = re.sub(r'\s*\n\s*', '', critical_css)
    
    html_files = glob.glob(os.path.join(OUT, '**/*.html'), recursive=True)
    perf_count = 0
    
    for html_path in html_files:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Determine CSS path prefix
        depth = html_path.replace(OUT + '/', '').count('/')
        css_prefix = '../' * depth + 'assets/' if depth > 0 else 'assets/'
        
        old_stylesheet = f'<link rel="stylesheet" href="{css_prefix}style.css">'
        
        # Only process if we haven't already optimized this file
        # NOTE: CSS stays render-blocking to prevent flash of unstyled content (FOUC).
        # The inline critical CSS + preload hint provide the speed benefit without the flash.
        if old_stylesheet in content and '<style>' not in content[:3000]:
            replacement = (
                f'<style>{critical_css}</style>\n'
                f'  <link rel="preload" href="{css_prefix}style.css" as="style">\n'
                f'  <link rel="stylesheet" href="{css_prefix}style.css">'
            )
            content = content.replace(old_stylesheet, replacement)
        
        # Remove noscript font tag if we have media=print trick
        content = re.sub(
            r'<noscript><link href="https://fonts\.googleapis\.com/css2\?family=Inter[^"]*" rel="stylesheet"></noscript>\s*',
            '', content
        )
        
        # Add decoding="async" to images missing it
        # Skip images with fetchpriority="high" (LCP candidates should not be async)
        content = re.sub(
            r'<img(?![^>]*decoding=)(?![^>]*fetchpriority="high")([^>]*?)(/?>)',
            r'<img decoding="async"\1\2',
            content
        )
        
        # Add width/height to hero collage logos
        content = re.sub(
            r'(<img[^>]*class="hero-collage-logo"[^>]*?)(/?>)',
            lambda m: m.group(1) + (' width="56" height="56"' if 'width=' not in m.group(1) else '') + m.group(2),
            content
        )
        
        if content != original:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            perf_count += 1
    
    print(f"   Applied performance optimizations to {perf_count} files")
else:
    print("   No critical.css found, skipping inline CSS injection")

# SVG cleanup for large logos — SAFE operations only
# Do NOT remove IDs, collapse whitespace between tags, or reduce decimal precision.
# Those operations break SVG rendering for complex brand logos.
print("   Light SVG cleanup (comments/metadata only)...")
svg_total = 0
for svg_path in glob.glob(os.path.join(OUT, 'assets/logos/*.svg')):
    orig_size = os.path.getsize(svg_path)
    if orig_size < 20000:
        continue
    with open(svg_path, 'r', encoding='utf-8', errors='replace') as f:
        svg_content = f.read()
    svg_content = re.sub(r'<!--.*?-->', '', svg_content, flags=re.DOTALL)
    svg_content = re.sub(r'<metadata>.*?</metadata>', '', svg_content, flags=re.DOTALL)
    new_size = len(svg_content.encode('utf-8'))
    if new_size < orig_size:
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        svg_total += orig_size - new_size
if svg_total > 0:
    print(f"   SVG savings: {svg_total:,} bytes")

# ============================================================
# 8. FIX 404 PAGE — root-relative paths
# ============================================================
print("8. Fixing 404.html paths to be root-relative...")
_404_path = os.path.join(OUT, '404.html')
if os.path.exists(_404_path):
    with open(_404_path, 'r', encoding='utf-8') as f:
        _404_content = f.read()
    # Convert relative href/src to root-relative
    # The 404 page can be served from any URL, so paths must start with /
    def _make_root_rel(m):
        attr = m.group(1)
        path = m.group(2)
        if path.startswith(('http://', 'https://', '#', 'mailto:', 'tel:', 'javascript:', '/', 'data:')):
            return m.group(0)
        return f'{attr}="/{path}"'
    _404_content = re.sub(r'((?:href|src))="([^"]*?)"', _make_root_rel, _404_content)
    with open(_404_path, 'w', encoding='utf-8') as f:
        f.write(_404_content)
    print("   404.html updated with root-relative paths")

# ============================================================
# 9. INJECT GOOGLE ANALYTICS TAG
# ============================================================
print("9. Injecting Google Analytics tag...")
GA_TAG = '''<!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-Y4YF2X6BSQ"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-Y4YF2X6BSQ');
  </script>'''

ga_count = 0
for root, dirs, files in os.walk(OUT):
    for fname in files:
        if not fname.endswith('.html'):
            continue
        fpath = os.path.join(root, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'G-Y4YF2X6BSQ' in content:
            continue  # already has GA tag
        if '<meta charset' not in content:
            continue  # redirect pages or fragments
        new_content = content.replace(
            '<meta charset="UTF-8">',
            '<meta charset="UTF-8">\n  ' + GA_TAG,
            1  # only first occurrence
        )
        if new_content != content:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            ga_count += 1
print(f"   GA tag injected into {ga_count} files that were missing it")

# ============================================================
# 10. PAGESPEED: FIX DUPLICATE PRELOADS & CHAIN OPTIMISATIONS
# ============================================================
print("10. PageSpeed optimisations - dedup preloads, reduce chains...")
ps_count = 0
for root, dirs, files in os.walk(OUT):
    for fname in files:
        if not fname.endswith('.html'):
            continue
        fpath = os.path.join(root, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        original = content

        # a) Remove duplicate preload tags for style.css
        # Keep first occurrence, remove duplicates
        depth = fpath.replace(OUT + '/', '').count('/')
        css_prefix = '../' * depth + 'assets/' if depth > 0 else 'assets/'
        preload_tag = f'<link rel="preload" href="{css_prefix}style.css" as="style">'
        count = content.count(preload_tag)
        if count > 1:
            # Remove all but the first occurrence
            first_pos = content.index(preload_tag)
            end_first = first_pos + len(preload_tag)
            content = content[:end_first] + content[end_first:].replace(preload_tag, '')

        # b) Make Google Fonts non-render-blocking if not already
        # Already using media="print" trick, just verify no plain stylesheet version
        content = re.sub(
            r'<link\s+href="https://fonts\.googleapis\.com/css2[^"]*"\s+rel="stylesheet"\s*>\s*',
            '', content
        )

        # c) Defer inline GA script using requestIdleCallback for non-critical
        # Actually GA is already async, just ensure the inline config doesn't block
        # The gtag 'async' attribute on the external script is sufficient

        # d) Add font-display: swap as fallback in critical CSS
        # (The Google Fonts URL already has display=swap)

        # e) Remove any empty script tags
        content = re.sub(r'<script>\s*</script>', '', content)

        # f) Ensure all images have width/height to prevent layout shift
        # Bookmaker card logos (48x48)
        content = re.sub(
            r'(<img[^>]*class="[^"]*brand-logo[^"]*"[^>]*?)(/?>)',
            lambda m: m.group(1) + (' width="48" height="48"' if 'width=' not in m.group(1) else '') + m.group(2),
            content
        )

        # g) Add loading="lazy" to images below the fold (not already set)
        # Skip hero images and first card images
        def add_lazy(m):
            tag = m.group(0)
            if 'loading=' in tag or 'fetchpriority' in tag:
                return tag
            if 'hero-' in tag or 'site-logo' in tag:
                return tag
            return tag.replace('<img', '<img loading="lazy"', 1)
        content = re.sub(r'<img[^>]+>', add_lazy, content)

        if content != original:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            ps_count += 1
print(f"   PageSpeed fixes applied to {ps_count} files")

# ============================================================
# 11. SCHEMA: ADD ORGANISATION SCHEMA TO ALL PAGES
# ============================================================
print("11. Adding Organisation schema to pages missing it...")
ORG_SCHEMA = json.dumps({
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "MzansiWins",
    "url": "https://mzansiwins.co.za",
    "logo": "https://mzansiwins.co.za/assets/logo.svg",
    "description": "South Africa's trusted guide to licensed betting sites, promo codes, and payment methods.",
    "foundingDate": "2024",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "38 Wale Street",
        "addressLocality": "Cape Town",
        "postalCode": "8000",
        "addressCountry": "ZA"
    },
    "contactPoint": {
        "@type": "ContactPoint",
        "email": "help@mzansiwins.co.za",
        "contactType": "customer service"
    },
    "sameAs": [
        "https://x.com/mzansiwins"
    ]
}, separators=(',', ':'))

def has_standalone_org_schema(html_content):
    """Check if page has a top-level Organization schema for MzansiWins."""
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html_content, re.DOTALL)
    for block in blocks:
        try:
            data = json.loads(block)
            if data.get('@type') == 'Organization' and data.get('name') == 'MzansiWins':
                return True
        except:
            pass
    return False

schema_count = 0
for root, dirs, files in os.walk(OUT):
    for fname in files:
        if not fname.endswith('.html'):
            continue
        fpath = os.path.join(root, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        if has_standalone_org_schema(content):
            continue
        # Add before </head>
        org_tag = f'<script type="application/ld+json">{ORG_SCHEMA}</script>'
        if '</head>' in content:
            content = content.replace('</head>', f'  {org_tag}\n</head>', 1)
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            schema_count += 1
print(f"   Organisation schema added to {schema_count} files")

# ============================================================
# 12. SCHEMA: ADD PRODUCT SCHEMA TO REVIEW PAGES (if missing)
# ============================================================
print("12. Checking Product schema on review pages...")
import json as json_mod
review_dir = os.path.join(OUT, 'betting-site-review')
if os.path.isdir(review_dir):
    prod_count = 0
    for fname in os.listdir(review_dir):
        if not fname.endswith('.html'):
            continue
        fpath = os.path.join(review_dir, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        # Check if Product schema already exists
        if '"@type": "Product"' in content or '"@type":"Product"' in content:
            continue
        # Extract brand name and rating from Review schema
        review_match = re.search(r'"@type":\s*"Review".*?"name":\s*"([^"]+)".*?"ratingValue":\s*"([^"]+)"', content, re.DOTALL)
        if not review_match:
            continue
        brand_name = review_match.group(1).replace(' Review 2026', '')
        rating_val = review_match.group(2)
        # Build Product schema with AggregateRating
        product_schema = json_mod.dumps({
            "@context": "https://schema.org",
            "@type": "Product",
            "name": brand_name,
            "description": f"{brand_name} - Licensed South African betting site",
            "brand": {"@type": "Brand", "name": brand_name},
            "review": {
                "@type": "Review",
                "author": {"@type": "Organization", "name": "MzansiWins"},
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": rating_val,
                    "bestRating": "5",
                    "worstRating": "1"
                }
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": rating_val,
                "bestRating": "5",
                "worstRating": "1",
                "ratingCount": "1"
            }
        }, separators=(',', ':'))
        prod_tag = f'<script type="application/ld+json">{product_schema}</script>'
        content = content.replace('</head>', f'  {prod_tag}\n</head>', 1)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        prod_count += 1
    print(f"   Product schema added to {prod_count} review pages")
else:
    print("   No review directory found")

# ============================================================
# 13. FIX MISSING H1 on bonus-browser
# ============================================================
print("13. Fixing missing H1 on bonus-browser...")
bb_path = f'{OUT}/bonus-browser.html'
if os.path.exists(bb_path):
    with open(bb_path, 'r', encoding='utf-8') as f:
        bb = f.read()
    if '<h1' not in bb:
        # Add H1 before the first h2 or main content area
        bb = bb.replace(
            '<div class="container" style="padding-top:40px',
            '<div class="container" style="padding-top:40px',
            1
        )
        # Insert after breadcrumbs or at start of main content
        if '<h2' in bb:
            bb = bb.replace('<h2', '<h1 class="page-title" style="margin-bottom:16px">BonusBrowser: Compare SA Betting Bonuses</h1>\n<h2', 1)
        with open(bb_path, 'w', encoding='utf-8') as f:
            f.write(bb)
        print("   H1 added to bonus-browser.html")
    else:
        print("   bonus-browser.html already has H1")

# ============================================================
# 14. ADD BREADCRUMBLIST SCHEMA TO PAGES MISSING IT
# ============================================================
print("14. Adding BreadcrumbList schema to pages missing it...")
bc_count = 0
for html_file in glob.glob(f'{OUT}/*.html'):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'BreadcrumbList' in content:
        continue
    if 'meta http-equiv="refresh"' in content:
        continue
    fname = os.path.basename(html_file).replace('.html', '')
    if fname in ('404', 'check', 'robots', 'sitemap'):
        continue
    
    # Derive breadcrumb from filename
    page_name = fname.replace('-', ' ').title()
    if fname == 'index':
        page_name = 'Home'
    
    bc_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://mzansiwins.co.za"},
            {"@type": "ListItem", "position": 2, "name": page_name}
        ]
    }, separators=(',', ':'))
    bc_tag = f'<script type="application/ld+json">{bc_schema}</script>'
    content = content.replace('</head>', f'  {bc_tag}\n</head>', 1)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)
    bc_count += 1
print(f"   BreadcrumbList added to {bc_count} top-level pages")

# Also add to subdirectory pages missing it
for subdir in ['payment-methods', 'betting', 'casino', 'guides', 'casino-guides', 'authors', 'crash-games', 'sa-slots', 'compare', 'calculators']:
    subdir_path = f'{OUT}/{subdir}'
    if not os.path.isdir(subdir_path):
        continue
    for html_file in glob.glob(f'{subdir_path}/*.html'):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'BreadcrumbList' in content:
            continue
        if 'meta http-equiv="refresh"' in content:
            continue
        fname = os.path.basename(html_file).replace('.html', '')
        page_name = fname.replace('-', ' ').title()
        parent_name = subdir.replace('-', ' ').title()
        
        bc_schema = json.dumps({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://mzansiwins.co.za"},
                {"@type": "ListItem", "position": 2, "name": parent_name, "item": f"https://mzansiwins.co.za/{subdir}"},
                {"@type": "ListItem", "position": 3, "name": page_name}
            ]
        }, separators=(',', ':'))
        bc_tag = f'<script type="application/ld+json">{bc_schema}</script>'
        content = content.replace('</head>', f'  {bc_tag}\n</head>', 1)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        bc_count += 1
print(f"   Total BreadcrumbList schemas added: {bc_count}")

print("\n=== POST-BUILD + PERFORMANCE + SCHEMA COMPLETE ===")
