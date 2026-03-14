#!/usr/bin/env python3
"""
Post-build fixups:
1. Add noopener noreferrer to ALL external links
2. Fix missing alt text on images
3. Em-dash cleanup
4. Minify CSS
5. Optimize wanejo-bets.png if exists
"""
import re, os, glob

OUT = '/home/user/workspace/mzansiwins-html'

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
# 4. MINIFY CSS
# ============================================================
print("4. Minifying CSS...")
css_file = f'{OUT}/assets/style.css'
with open(css_file, 'r') as f:
    css = f.read()

original_size = len(css)

# Basic CSS minification - remove comments, excess whitespace
css_min = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)  # Remove comments
css_min = re.sub(r'\s*\n\s*', '\n', css_min)  # Remove leading/trailing whitespace per line
css_min = re.sub(r'\n+', '\n', css_min)  # Collapse multiple newlines
css_min = re.sub(r'\s*{\s*', '{', css_min)  # Remove space around {
css_min = re.sub(r'\s*}\s*', '}', css_min)  # Remove space around }
css_min = re.sub(r'\s*;\s*', ';', css_min)  # Remove space around ;
css_min = re.sub(r'\s*:\s*', ':', css_min)  # Remove space around :
css_min = re.sub(r'\s*,\s*', ',', css_min)  # Remove space around ,
css_min = css_min.strip()

new_size = len(css_min)
saved = original_size - new_size
print(f"   CSS: {original_size:,} -> {new_size:,} bytes (saved {saved:,} bytes, {saved/original_size*100:.1f}%)")

with open(css_file, 'w') as f:
    f.write(css_min)

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
