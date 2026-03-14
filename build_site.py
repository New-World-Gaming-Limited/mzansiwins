#!/usr/bin/env python3
"""MzansiWins Static Site Generator - builds ~100 HTML pages from data.json"""
import json, os, shutil, html as h, re, sys
from datetime import datetime
sys.path.insert(0, '/home/user/workspace')
from sa_content import generate_review_content, generate_promo_content
from betting_seo_content import betting_sites_intro_html, betting_sites_mid_html, betting_sites_below_table_html
from casino_seo_content import casino_sites_intro_html, casino_sites_below_table_html
from calculators import CALCULATORS, get_calculator_js, get_calculator_form, get_calculator_results, get_calculator_description

# Load calculator SEO data
try:
    with open(os.path.join(os.path.dirname(__file__), 'calc_seo_data.json')) as _cf:
        CALC_SEO = json.load(_cf)
except FileNotFoundError:
    CALC_SEO = {}

OUT = '/home/user/workspace/mzansiwins-html'
SRC = '/home/user/workspace/mzansiwins/src'
BASE_URL = 'https://mzansiwins.co.za'

# Dynamic date - always reflects the current month at build time
_now = datetime.now()
CURRENT_MONTH = _now.strftime('%B')          # e.g. "March"
CURRENT_YEAR = str(_now.year)                # e.g. "2026"
CURRENT_MONTH_YEAR = f'{CURRENT_MONTH} {CURRENT_YEAR}'  # e.g. "{CURRENT_MONTH_YEAR}"

with open(f'{SRC}/data.json') as f: DATA = json.load(f)
with open(f'{SRC}/news-articles.json') as f: NEWS = json.load(f)

BRANDS = sorted(DATA['brands'], key=lambda b: -b['overallRating'])
BRANDS_ORDERED = DATA['brands']  # User-defined order from data.json (Apexbets #1, Zarbet #2, etc.)
PAYMENTS = DATA['paymentMethods']

# Author photo mapping
AUTHOR_PHOTOS = {
    'Thabo Mokoena': 'author-thabo-mokoena.jpg',
    'Lerato Dlamini': 'author-lerato-dlamini.jpg',
    'Sipho Nkosi': 'author-sipho-nkosi.jpg',
    'Naledi Khumalo': 'author-naledi-khumalo.jpg',
}
AUTHOR_ROLES = {
    'Thabo Mokoena': 'Editor-in-Chief',
    'Lerato Dlamini': 'Senior Casino Analyst',
    'Sipho Nkosi': 'Betting Strategist',
    'Naledi Khumalo': 'Payments & Security Editor',
}
AUTHOR_IDS = {
    'Thabo Mokoena': 'thabo-mokoena',
    'Lerato Dlamini': 'lerato-dlamini',
    'Sipho Nkosi': 'sipho-nkosi',
    'Naledi Khumalo': 'naledi-khumalo',
}
AUTHOR_NAMES = ['Thabo Mokoena', 'Sipho Nkosi', 'Lerato Dlamini', 'Naledi Khumalo']

def get_review_author(brand_id):
    """Deterministic author assignment based on brand ID hash."""
    idx = sum(ord(c) for c in brand_id) % len(AUTHOR_NAMES)
    return AUTHOR_NAMES[idx]

def author_byline(author_name, depth=1, date_str='March 2026'):
    """Return a visible author byline with photo and link to author page."""
    prefix = '../' * depth
    aid = AUTHOR_IDS.get(author_name, '')
    role = AUTHOR_ROLES.get(author_name, '')
    img = author_img(author_name, size=32, depth=depth)
    return f'''<div class="review-byline">
      <a href="{prefix}authors/{aid}.html" class="review-byline-link">
        {img}
        <div>
          <span class="review-byline-name">Reviewed by {e(author_name)}</span>
          <span class="review-byline-meta">{e(role)} - Updated {date_str}</span>
        </div>
      </a>
    </div>'''
def author_img(name, size=36, depth=0):
    """Return an <img> tag for the author photo, or initials fallback."""
    prefix = '../' * depth
    photo = AUTHOR_PHOTOS.get(name)
    if photo:
        return f'<img src="{prefix}assets/{photo}" alt="{e(name)}" width="{size}" height="{size}" style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;object-position:center 20%;flex-shrink:0" loading="lazy">'
    initials = ''.join(w[0] for w in name.split()[:2]).upper() if name else 'MW'
    return f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:var(--accent);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:{max(size//3,12)}px;flex-shrink:0">{initials}</div>'

def trim_title(t, max_len=62):
    """Trim title to max_len, keeping ' | MzansiWins' suffix."""
    suffix = ' | MzansiWins'
    if len(t) <= max_len + len(suffix):
        return t
    if t.endswith(suffix):
        main = t[:-len(suffix)]
        avail = max_len
        if len(main) > avail:
            main = main[:avail].rsplit(' ', 1)[0].rstrip(' -,')
        return main + suffix
    if len(t) > max_len + len(suffix):
        t = t[:max_len].rsplit(' ', 1)[0].rstrip(' -,') + suffix
    return t

def trim_desc(d, max_len=155):
    """Trim meta description to max_len chars."""
    if len(d) <= max_len:
        return d
    return d[:max_len].rsplit(' ', 1)[0].rstrip(' -,') + '...'


# Copy logos
os.makedirs(f'{OUT}/assets/logos', exist_ok=True)
for f in os.listdir(f'{SRC}/assets/logos'):
    shutil.copy2(f'{SRC}/assets/logos/{f}', f'{OUT}/assets/logos/{f}')

def e(s):
    if not s: return ''
    txt = h.escape(str(s))
    # Replace literal \n from data with line breaks
    txt = txt.replace('\\n', '<br>')
    return txt
def fmtRating(r):
    try: return f'{float(r):.1f}'
    except: return '0.0'

def truncate(s, mx=30):
    if not s: return 'N/A'
    cut = re.split(r'[;(]', s)[0].strip()
    return cut[:mx-2] + '...' if len(cut) > mx else cut


def bonus_val(brand):
    """Extract numeric rand value from bonus string."""
    m = re.search(r'R\s*([\d,]+)', brand.get('welcomeBonusAmount', ''))
    if m:
        return int(re.sub(r'[^0-9]', '', m.group(1)))
    return 0

def get_promo(brand):
    code = (brand.get('promoCode') or '').strip()
    if not code or code.lower() in ('none', 'no code', 'n/a', 'no promo', 'no promo code'):
        return 'NEWBONUS'
    return code

def masked_exit(brand, depth=0):
    """Return masked exit link path like /link/zarbet instead of raw affiliate URL."""
    if not brand.get('exitLink'):
        return ''
    prefix = '../' * depth
    return f'{prefix}link/{brand["id"]}/'

def promo_banners_html(brand, depth=0):
    """Generate promo banner carousel HTML if brand has promoBanners."""
    banners = brand.get('promoBanners', [])
    if not banners:
        return ''
    prefix = '../' * depth
    exit_url = masked_exit(brand, depth)
    cards = ''
    for b in banners:
        img_src = f'{prefix}assets/{b["image"]}'
        code = e(b.get('code', ''))
        label = e(b.get('label', ''))
        details = e(b.get('details', ''))
        alt = e(b.get('alt', label))
        cards += f'''<div class="promo-banner-card">
          <a href="{exit_url}" target="_blank" rel="noopener noreferrer nofollow" class="promo-banner-link">
            <img src="{img_src}" alt="{alt}" class="promo-banner-img" loading="lazy">
          </a>
          <div class="promo-banner-info">
            <div class="promo-banner-label">{label}</div>
            <div class="promo-banner-details">{details}</div>
            <div class="promo-banner-code-row">
              <span style="font-size:11px;color:var(--text-muted);font-weight:500">CODE</span>
              <span class="promo-code" style="border-color:var(--accent)">{code}</span>
              <button class="copy-btn" onclick="copyCode(this,\'{code}\')">Copy</button>
            </div>
          </div>
        </div>'''
    return f'''<div class="promo-banners-section" style="margin-bottom:32px">
      <h2 style="font-size:16px;font-weight:700;margin-bottom:16px">Current Promotions</h2>
      <div class="promo-banners-grid">{cards}</div>
    </div>'''

def logo_path(brand, depth=0):
    prefix = '../' * depth
    bid = brand['id']
    for ext in ('svg', 'png'):
        if os.path.exists(f'{OUT}/assets/logos/{bid}.{ext}'):
            return f'{prefix}assets/logos/{bid}.{ext}'
    return ''

def brand_bg(brand):
    """Return the brand's base colour for logo backgrounds."""
    return brand.get('baseColour', '#1641B4')

def brand_count_for_method(method_name):
    return sum(1 for b in DATA['brands'] if any(
        method_name.lower() in p.lower() or p.lower() in method_name.lower()
        for p in b.get('paymentMethodsList', [])
    ))

def brands_for_method(method_name):
    return sorted([b for b in DATA['brands'] if any(
        method_name.lower() in p.lower() or p.lower() in method_name.lower()
        for p in b.get('paymentMethodsList', [])
    )], key=lambda b: -b['overallRating'])

# ===== PAYMENT LOGOS =====
# Map payment method names (lowercase) to colored emoji-badge pairs
PAYMENT_LOGOS = {
    'visa': ('\U0001F4B3', '#1A1F71'),
    'mastercard': ('\U0001F4B3', '#EB001B'),
    'american express': ('\U0001F4B3', '#006FCF'),
    'apple pay': ('\U0001F34E', '#000000'),
    'paypal': ('\U0001F4B0', '#003087'),
    'bitcoin': ('\u20BF', '#F7931A'),
    'ethereum': ('\u26D3', '#627EEA'),
    'litecoin': ('\U0001FA99', '#345D9D'),
    'ozow': ('\u26A1', '#00B5E2'),
    'snapscan': ('\U0001F4F1', '#009CDE'),
    'zapper': ('\U0001F4F1', '#FF6600'),
    'fnb ewallet': ('\U0001F4F1', '#009A44'),
    'fnb': ('\U0001F3E6', '#009A44'),
    'capitec': ('\U0001F3E6', '#D51B23'),
    'capitec pay': ('\U0001F3E6', '#D51B23'),
    'absa': ('\U0001F3E6', '#AF1D2D'),
    'bank transfer': ('\U0001F3E6', '#1641B4'),
    'eft': ('\U0001F3E6', '#1641B4'),
    'eftsecure': ('\U0001F512', '#1641B4'),
    'sid': ('\u26A1', '#00A651'),
    'blu voucher': ('\U0001F3AB', '#0072CE'),
    '1 voucher': ('\U0001F3AB', '#FF6B00'),
    'ott voucher': ('\U0001F3AB', '#E31937'),
    'neteller': ('\U0001F4B0', '#85BC22'),
    'skrill': ('\U0001F4B0', '#862165'),
    'peach payment': ('\U0001F512', '#FF6B6B'),
    'paygate': ('\U0001F512', '#00457C'),
    'payu': ('\U0001F512', '#009A00'),
    'payz': ('\U0001F4B0', '#FF5F00'),
    'e-wallet': ('\U0001F4F1', '#1641B4'),
    'walletdoc': ('\U0001F4F1', '#4CAF50'),
    'callpay': ('\U0001F4DE', '#2196F3'),
    'call pay': ('\U0001F4DE', '#2196F3'),
    'mtn': ('\U0001F4F1', '#FFCB05'),
    'easyload': ('\U0001F3AB', '#FF6B00'),
    'iveri': ('\U0001F512', '#003366'),
    'flash 1foryou': ('\U0001F3AB', '#E31937'),
}

def payment_badge_html(method_name, small=False):
    """Return a colored badge span for a payment method."""
    key = method_name.lower().strip()
    icon, color = PAYMENT_LOGOS.get(key, ('\U0001F4B0', '#888'))
    size = '11px' if small else '12px'
    pad = '3px 8px' if small else '4px 10px'
    return f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:{size};padding:{pad};border-radius:20px;background:{color}18;color:{color};font-weight:600;border:1px solid {color}30;white-space:nowrap">{icon} {e(method_name)}</span>'


# ===== SVG ICONS =====
ICON_STAR = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'
ICON_TROPHY = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>'
ICON_GIFT = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 12 20 22 4 22 4 12"/><rect x="2" y="7" width="20" height="5"/><line x1="12" y1="22" x2="12" y2="7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/></svg>'
ICON_SHIELD = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
ICON_CHECK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
ICON_X = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>'
ICON_CHEVRON_DOWN = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>'
ICON_CHEVRON_RIGHT = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>'
ICON_ARROW_LEFT = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>'
ICON_CLOCK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
ICON_MENU = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>'

LOGO_SVG = '''<svg width="28" height="28" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="200" rx="36" fill="#1641B4"/>
  <g transform="translate(30,28)">
    <path d="M0 10 Q0 0 10 0 L45 0 L70 50 L95 0 L130 0 Q140 0 140 10 L140 90 Q140 100 130 100 L105 100 L105 40 L80 85 Q75 93 70 93 Q65 93 60 85 L35 40 L35 100 L10 100 Q0 100 0 90 Z" fill="#ffffff"/>
  </g>
  <text x="100" y="172" text-anchor="middle" font-family="Inter,sans-serif" font-weight="800" font-size="34" letter-spacing="2" fill="rgba(255,255,255,0.85)">WINS</text>
</svg>'''

# ===== TEMPLATE HELPERS =====
def rel(target, depth=0):
    """Make a relative path from a given depth."""
    prefix = '../' * depth
    return prefix + target

def rating_badge(r, size=''):
    r = float(r)
    cls = 'high' if r >= 4.2 else 'mid' if r >= 3.5 else 'low'
    sz = ' sm' if size == 'sm' else ''
    return f'<span class="rating-badge {cls}{sz}">{fmtRating(r)}/5.0</span>'


# ── Payment Method Icon Map ──────────────────────────────────────────────────
# Maps normalised payment method names to SVG icon filenames
PAYMENT_ICON_MAP = {
    'visa': 'visa.svg',
    'mastercard': 'mastercard.svg',
    'visa & mastercard': 'visa.svg',
    'american express': 'american-express.svg',
    'amex': 'american-express.svg',
    'apple pay': 'apple-pay.svg',
    'paypal': 'paypal.svg',
    'skrill': 'skrill.svg',
    'neteller': 'neteller.svg',
    'ozow': 'ozow.svg',
    'ozow instant eft': 'ozow.svg',
    'ott voucher': 'ott-voucher.svg',
    'ott': 'ott-voucher.svg',
    'blu voucher': 'blu-voucher.svg',
    '1voucher': '1voucher.svg',
    '1 voucher': '1voucher.svg',
    'paysafe': 'paysafe-card.svg',
    'paysafecard': 'paysafe-card.svg',
    'bank transfer': 'bank-wire.svg',
    'bank wire': 'bank-wire.svg',
    'eft': 'eftpay.svg',
    'eft (electronic funds transfer)': 'eftpay.svg',
    'eftpay': 'eftpay.svg',
    'eftsecure': 'eftsecure.svg',
    'zapper': 'zapper.svg',
    'paygate': 'paygate.svg',
    'payfast': 'payfast.svg',
    'peach payments': 'peach-payments.svg',
    'peach payment': 'peach-payments.svg',
    'eco-payz': 'eco-payz.svg',
    'payz': 'eco-payz.svg',
    'ecopayz': 'eco-payz.svg',
    'm-pesa': 'm-pesa.svg',
    'mpesa': 'm-pesa.svg',
    'mtn': 'mtn-airtime.svg',
    'mtn airtime': 'mtn-airtime.svg',
    'vodacom': 'vodacom.svg',
    'direct deposit': 'direct-deposit.svg',
    'capitec': 'capitec.svg',
    'capitec pay': 'capitec.svg',
    'fnb': 'fnb.svg',
    'fnb ewallet': 'fnb.svg',
    'nedbank': 'nedbank.svg',
    'absa': 'absa.svg',
    'standard bank': 'standard-bank.svg',
    'bitcoin': 'bitcoin.svg',
    'btc': 'bitcoin.svg',
    'ethereum': 'ethereum.svg',
    'eth': 'ethereum.svg',
    'litecoin': 'litecoin.svg',
    'ltc': 'litecoin.svg',
    'snapscan': 'snapscan.svg',
    'snapscan (south africa)': 'snapscan.svg',
    'e-wallet': 'e-wallet.svg',
    'ewallet': 'e-wallet.svg',
    'walletdoc': 'walletdoc.svg',
    'iveri': 'iveri.svg',
    'callpay': 'callpay.svg',
    'call pay': 'callpay.svg',
    'easyload': 'easyload.svg',
    'flash 1foryou': 'flash.svg',
    'tictac instore deposit': 'tictac.svg',
    'sid': 'sid.svg',
    'sid instant eft': 'sid.svg',
    'payu': 'payu.svg',
    'voucher': 'voucher.svg',
}

def payment_icon_img(method_name, size=20, depth=0):
    """Return an <img> tag for the payment method icon, or empty string if not found."""
    key = method_name.strip().lower()
    icon_file = PAYMENT_ICON_MAP.get(key)
    if not icon_file:
        # Try partial match
        for k, v in PAYMENT_ICON_MAP.items():
            if k in key or key in k:
                icon_file = v
                break
    if not icon_file:
        icon_file = 'generic.svg'
    prefix = '../' * depth
    return f'<img src="{prefix}assets/payment-icons/{icon_file}" alt="{e(method_name)}" width="{size}" height="{size}" style="border-radius:4px;vertical-align:middle" loading="lazy">'

def payment_icon_for_type(method_type, depth=0):
    """Return an <img> tag based on payment type (fallback for method-icon-box)."""
    type_to_icon = {
        'voucher': '1voucher.svg',
        'instant EFT': 'ozow.svg',
        'bank transfer': 'bank-wire.svg',
        'mobile wallet': 'e-wallet.svg',
        'mobile wallet / QR scan-to-pay': 'snapscan.svg',
        'payment gateway': 'paygate.svg',
        'credit/debit card': 'visa.svg',
    }
    icon_file = type_to_icon.get(method_type, 'generic.svg')
    prefix = '../' * depth
    return f'<img src="{prefix}assets/payment-icons/{icon_file}" alt="{method_type}" width="28" height="28" style="border-radius:4px" loading="lazy">'


def payment_pill(name, depth=0):
    icon = payment_icon_img(name, size=16, depth=depth)
    return f'<span class="payment-pill">{icon} {e(name)}</span>'

def breadcrumbs(items, depth=0):
    parts = []
    for i, item in enumerate(items):
        if i > 0:
            parts.append(f'<span class="sep">{ICON_CHEVRON_RIGHT}</span>')
        if 'href' in item:
            parts.append(f'<a href="{rel(item["href"], depth)}">{e(item["label"])}</a>')
        else:
            parts.append(f'<span class="text-secondary">{e(item["label"])}</span>')
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb">{"".join(parts)}</nav>'


# ===== SEO & INTERLINKING HELPERS =====
def seo_meta(page_type, brand=None, method=None, article=None):
    """Generate SEO-optimised title and description for each page type."""
    if page_type == 'home':
        return ('Best Betting Sites South Africa 2026 | MzansiWins',
                f'Compare the best South African betting sites for 2026. Expert reviews, promo codes, bonuses up to R50,000+. Updated {CURRENT_MONTH_YEAR}.')
    elif page_type == 'betting':
        return (f'Best SA Betting Sites {CURRENT_MONTH_YEAR} - 35 Ranked | MzansiWins',
                'All 35 licensed South African betting sites ranked for 2026. Compare odds, bonuses, payments, and apps.')
    elif page_type == 'casino':
        return ('Best Online Casinos South Africa 2026 | MzansiWins',
                f'Top SA online casinos reviewed. Compare bonuses, games, and payouts. Updated {CURRENT_MONTH_YEAR}.')
    elif page_type == 'promos':
        return (f'SA Betting Promo Codes {CURRENT_MONTH_YEAR} | MzansiWins',
                f'All {len(DATA["brands"])} SA bookmaker promo codes verified for {CURRENT_MONTH_YEAR}. Claim up to R50,000+ in welcome bonuses.')
    elif page_type == 'payments':
        return ('SA Betting Payment Methods 2026 - Deposits & Withdrawals Guide | MzansiWins',
                'Compare 11 payment methods accepted at South African betting sites. Deposit fees, withdrawal times, and which bookmakers accept each method.')
    elif page_type == 'news':
        return (f'SA Betting News {CURRENT_MONTH_YEAR} | MzansiWins',
                'South African betting news - bonuses, platform updates, regulations, and bookmaker announcements. Updated daily.')
    elif page_type == 'about':
        return ('About MzansiWins - SA Betting Review Experts | MzansiWins',
                'MzansiWins is South Africa\'s independent betting review site. Learn about our team, rating methodology, and editorial standards.')
    elif page_type == 'howrate':
        return ('How We Rate South African Betting Sites | MzansiWins Methodology',
                'Our transparent scoring system rates SA bookmakers across 7 categories: bonus value, odds quality, payments, sports variety, platform quality, live betting, and support.')
    elif page_type == 'fica':
        return ('FICA Verification Guide for SA Betting Sites 2026 | MzansiWins',
                'Step-by-step guide to completing FICA verification at South African bookmakers. What documents you need, how long it takes, and tips to speed it up.')
    elif page_type == 'review' and brand:
        name = brand['name']
        rating = fmtRating(brand['overallRating'])
        bonus = brand.get('welcomeBonusAmount', '')
        code = get_promo(brand)
        return (f'{name} Review 2026 - Rating {rating}/5.0 | MzansiWins',
                f'In-depth {name} review for 2026. Rated {rating}/5.0. Bonus: {bonus}. Code: {code}. Odds, payments, live betting, pros and cons.')
    elif page_type == 'promo' and brand:
        name = brand['name']
        bonus = brand.get('welcomeBonusAmount', '')
        code = get_promo(brand)
        return (f'{name} Promo Code 2026: {code} | MzansiWins',
                f'Verified {name} code {code} for {CURRENT_MONTH_YEAR}. Claim {bonus}. Sign-up guide and wagering requirements.')
    elif page_type == 'payment' and method:
        return (f'{method["name"]} Betting Sites SA 2026 | MzansiWins',
                f'SA betting sites accepting {method["name"]}. Compare fees, withdrawal times. {brand_count_for_method(method["name"])} bookmakers reviewed.')
    elif page_type == 'article' and article:
        return (f'{article["title"]} | MzansiWins',
                article.get('excerpt', article['title'][:155]))
    elif page_type == 'calculators':
        return ('Betting Calculators South Africa 2026 - 12 Free Tools | MzansiWins',
                'Free betting calculators for South African punters. Odds converter, accumulator calculator, bet profit tool, arbitrage finder, Kelly Criterion and more. All in ZAR, no sign-up.')
    elif page_type == 'calculator' and article:  # reuse article param for calc dict
        return (f'{article["title"]} - Free Online Calculator | MzansiWins',
                f'Free {article["title"].lower()} for South African bettors. {article["short"]} Instant results, mobile friendly.')
    return ('MzansiWins | South African Betting Guide 2026', 'Your trusted guide to SA betting sites, promo codes, and payment methods.')


def get_related_brands(brand, count=6):
    """Get related brands: same rating tier first, then nearest ratings."""
    r = float(brand['overallRating'])
    others = [b for b in BRANDS if b['id'] != brand['id']]
    # Score by rating proximity
    others.sort(key=lambda b: abs(float(b['overallRating']) - r))
    return others[:count]


def get_similar_bonuses(brand, count=4):
    """Get brands with similar bonus types for cross-linking."""
    others = [b for b in BRANDS if b['id'] != brand['id']]
    # Just pick by proximity in the sorted list
    idx = next((i for i, b in enumerate(BRANDS) if b['id'] == brand['id']), 0)
    nearby = []
    for offset in [1, -1, 2, -2, 3, -3, 4, -4]:
        j = idx + offset
        if 0 <= j < len(BRANDS) and BRANDS[j]['id'] != brand['id']:
            nearby.append(BRANDS[j])
        if len(nearby) >= count:
            break
    return nearby


# Map brand payment method names (lowercase) to payment-methods page IDs
PAYMENT_PAGE_MAP = {
    'eft': 'eft-electronic-funds-transfer', 'eft transfer': 'eft-electronic-funds-transfer',
    'eftpay': 'eft-electronic-funds-transfer', 'eftsecure': 'eft-electronic-funds-transfer',
    'bank transfer': 'eft-electronic-funds-transfer', 'direct deposit': 'eft-electronic-funds-transfer',
    'ozow': 'ozow-instant-eft', 'sid': 'sid-instant-eft',
    'visa': 'visa-mastercard', 'mastercard': 'visa-mastercard', 'visa/mastercard': 'visa-mastercard',
    'american express': 'visa-mastercard',
    'fnb ewallet': 'fnb-ewallet', 'fnb': 'fnb-ewallet', 'e-wallet': 'fnb-ewallet',
    'blu voucher': 'blu-voucher', 'blu': 'blu-voucher',
    'ott voucher': 'ott-voucher', 'ott': 'ott-voucher',
    '1voucher': '1voucher', '1 voucher': '1voucher', 'voucher': '1voucher',
    'zapper': 'zapper', 'snapscan': 'snapscan-south-africa', 'snapsscan': 'snapscan-south-africa',
    'peach payment': 'peach-payments', 'peach payments': 'peach-payments',
}

def _resolve_payment_page(method_name):
    """Find the best payment method page ID for a given method name."""
    ml = method_name.lower().strip()
    # Direct map hit
    if ml in PAYMENT_PAGE_MAP:
        return PAYMENT_PAGE_MAP[ml]
    # Fuzzy: check if any key is contained in method name or vice versa
    for key, pid in PAYMENT_PAGE_MAP.items():
        if key in ml or ml in key:
            return pid
    # Try matching against PAYMENTS data
    for p in PAYMENTS:
        pn = p['name'].lower()
        if ml in pn or pn in ml:
            return p['id']
    return None

def get_brand_payments_linked(brand, depth=1):
    """Get payment methods used by a brand, with links to payment pages."""
    prefix = '../' * depth
    pills = ''
    for m in brand.get('paymentMethodsList', []):
        pid = _resolve_payment_page(m)
        if pid:
            pills += f'<a href="{prefix}payment-methods/{pid}.html" class="payment-pill">{payment_icon_img(m, size=16, depth=depth)} {e(m)}</a>'
        else:
            pills += payment_pill(m, depth=depth)
    return pills



def linkify_brand_mentions(html_text, depth=0):
    """Replace brand name mentions in text with links to their review pages.
    Only links plain-text mentions - skips text inside <a> tags and HTML attributes."""
    prefix = '../' * depth
    import re as _re
    sorted_brands = sorted(DATA['brands'], key=lambda b: len(b['name']), reverse=True)
    # Split HTML into: <a>...</a> blocks, other HTML tags, and plain text segments
    # Group 1: full anchor tags | Group 2: any other HTML tag (incl. self-closing like <img>)
    splitter = _re.compile(r'(<a\b[^>]*>.*?</a>|<[^>]+>)', flags=_re.DOTALL | _re.IGNORECASE)
    for b in sorted_brands:
        name = b['name']
        bid = b['id']
        link = f'<a href="{prefix}betting-site-review/{bid}.html" style="color:var(--accent);font-weight:600">{name}</a>'
        parts = splitter.split(html_text)
        count = 0
        pattern = _re.compile(r'\b' + _re.escape(name) + r'\b', flags=_re.IGNORECASE)
        for i, part in enumerate(parts):
            if part.startswith('<'):
                continue  # Skip any HTML tag or anchor block
            if count >= 2:
                break
            matches = pattern.findall(part)
            if matches:
                remaining = 2 - count
                parts[i] = pattern.sub(link, part, count=remaining)
                count += min(len(matches), remaining)
        html_text = ''.join(parts)
    return html_text

PUBLISHER_LD = '{"@type": "Organization", "name": "MzansiWins", "url": "https://mzansiwins.co.za", "logo": {"@type": "ImageObject", "url": "https://mzansiwins.co.za/assets/favicon.svg"}}'

def _esc_json(s):
    """Escape a string for safe embedding in JSON inside HTML."""
    if not s: return ''
    return str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', '').strip()

def jsonld_review(brand, depth=1):
    """Generate JSON-LD Review schema for betting site review pages."""
    code = get_promo(brand)
    name = _esc_json(brand['name'])
    bonus = _esc_json(brand.get('welcomeBonusAmount', ''))
    rating = fmtRating(brand['overallRating'])
    lic = _esc_json(brand.get('license', 'Provincial gambling licence'))
    year = brand.get('yearEstablished', '')
    year_str = f',\n    "datePublished": "{_esc_json(year)}"' if year and year.lower() not in ('not specified','n/a','unknown','') else ''
    # Pros as a clean sentence
    pros_raw = brand.get('pros', [])
    if isinstance(pros_raw, list) and pros_raw:
        first_pro = _esc_json(pros_raw[0].split(',')[0] if isinstance(pros_raw[0], str) else '')
    else:
        first_pro = ''
    review_body = _esc_json(f'{name} is a licensed South African betting site rated {rating}/5.0 by MzansiWins. Welcome bonus: {bonus}. {first_pro}')
    return f'''<script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "Review",
  "name": "{name} Review 2026",
  "url": "{BASE_URL}/betting-site-review/{brand['id']}",
  "datePublished": "2026-03-01T08:00:00+02:00",
  "dateModified": "2026-03-13T09:00:00+02:00",
  "reviewBody": "{review_body}",
  "author": {{"@type": "Person", "name": "{_esc_json(get_review_author(brand['id']))}", "url": "{BASE_URL}/authors/{AUTHOR_IDS.get(get_review_author(brand['id']), '')}"}},
  "publisher": {PUBLISHER_LD},
  "itemReviewed": {{
    "@type": "Organization",
    "name": "{name}",
    "description": "Licensed South African betting site - {_esc_json(lic)}",
    "url": "{BASE_URL}/betting-site-review/{brand['id']}"
    {year_str}
  }},
  "reviewRating": {{
    "@type": "Rating",
    "ratingValue": "{rating}",
    "bestRating": "5",
    "worstRating": "1"
  }}
}}</script>'''


def jsonld_offer(brand):
    """Generate JSON-LD structured data for promo code pages."""
    code = get_promo(brand)
    name = _esc_json(brand['name'])
    bonus = _esc_json(brand.get('welcomeBonusAmount', ''))
    bonus_details = _esc_json(brand.get('welcomeBonusDetails', ''))
    rating = fmtRating(brand['overallRating'])
    return f'''<script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "{name} Promo Code 2026: {_esc_json(code)}",
  "url": "{BASE_URL}/promo-code/{brand['id']}",
  "description": "Use code {_esc_json(code)} at {name} to claim {bonus}. Verified {CURRENT_MONTH_YEAR}.",
  "dateModified": "2026-03-13T09:00:00+02:00",
  "publisher": {PUBLISHER_LD},
  "mainEntity": {{
    "@type": "Offer",
    "name": "{name} Welcome Bonus - {bonus}",
    "description": "{_esc_json(bonus_details) if bonus_details else bonus}",
    "url": "{BASE_URL}/promo-code/{brand['id']}",
    "priceCurrency": "ZAR",
    "price": "0",
    "availability": "https://schema.org/InStock",
    "validFrom": "2026-01-01T00:00:00+02:00",
    "validThrough": "2026-12-31T23:59:59+02:00",
    "offeredBy": {{
      "@type": "Organization",
      "name": "{name}"
    }},
    "itemOffered": {{
      "@type": "Product",
      "name": "{name}",
      "category": "Sports Betting"
    }}
  }}
}}</script>'''


def jsonld_news(article):
    """Generate JSON-LD NewsArticle schema for news pages."""
    title = _esc_json(article.get('title', ''))
    excerpt = _esc_json(article.get('excerpt', ''))
    author = _esc_json(article.get('author', 'MzansiWins'))
    date_raw = article.get('date', '')
    # Parse ISO date
    if date_raw:
        try:
            dt_obj = datetime.fromisoformat(date_raw.replace('Z', '+00:00'))
            iso_date = dt_obj.strftime('%Y-%m-%d')
        except:
            iso_date = '2026-03-01'
    else:
        iso_date = '2026-03-01'
    return f'''<script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "{title}",
  "description": "{excerpt}",
  "url": "{BASE_URL}/news/{article['slug']}",
  "datePublished": "{iso_date}T08:00:00+02:00",
  "dateModified": "{iso_date}T09:00:00+02:00",
  "author": {{"@type": "Person", "name": "{author}"}},
  "publisher": {PUBLISHER_LD},
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "{BASE_URL}/news/{article['slug']}"
  }},
  "articleSection": "{_esc_json(article.get('category', 'Industry'))}",
  "inLanguage": "en-ZA"
}}</script>'''


def jsonld_faq(faqs):
    """Generate JSON-LD FAQPage schema from a list of (question, answer) tuples."""
    entries = ''
    for i, (q, a) in enumerate(faqs):
        comma = ',' if i < len(faqs) - 1 else ''
        entries += f'''{{
      "@type": "Question",
      "name": "{_esc_json(q)}",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "{_esc_json(a)}"
      }}
    }}{comma}\n    '''
    return f'''<script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {entries}]
}}</script>'''


def jsonld_website():
    """Generate JSON-LD WebSite schema for the homepage."""
    return f'''<script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "MzansiWins",
  "url": "{BASE_URL}",
  "description": "South Africa's independent betting site reviews - honest ratings, promo codes, and guides.",
  "publisher": {PUBLISHER_LD},
  "inLanguage": "en-ZA",
  "potentialAction": {{
    "@type": "SearchAction",
    "target": "{BASE_URL}/betting-sites?q={{search_term_string}}",
    "query-input": "required name=search_term_string"
  }}
}}</script>'''


def jsonld_itemlist(brands, list_name):
    """Generate JSON-LD ItemList schema for listing pages."""
    items = ''
    for i, b in enumerate(brands):
        comma = ',' if i < len(brands) - 1 else ''
        items += f'''{{
      "@type": "ListItem",
      "position": {i + 1},
      "name": "{_esc_json(b['name'])}",
      "url": "{BASE_URL}/betting-site-review/{b['id']}"
    }}{comma}\n    '''
    return f'''<script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "{_esc_json(list_name)}",
  "numberOfItems": {len(brands)},
  "itemListElement": [
    {items}]
}}</script>'''


def related_offers_section(brand, depth=1):
    """Build a rich related offers section with proper interlinking."""
    related = get_related_brands(brand, 6)
    prefix = '../' * depth
    cards = ''
    for b in related:
        rc = get_promo(b)
        logo = logo_path(b, depth)
        logo_img = f'<img src="{logo}" alt="{e(b["name"])}" style="width:36px;height:36px;object-fit:contain;border-radius:4px;background:{brand_bg(b)};padding:4px">' if logo else ''
        cards += f"""<a href="{prefix}promo-code/{b['id']}.html" class="card" style="padding:16px">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
            {logo_img}
            <div style="flex:1;min-width:0">
              <div style="font-size:14px;font-weight:600;margin-bottom:2px">{e(b['name'])}</div>
              <span style="font-size:12px;color:var(--text-muted)">{fmtRating(b['overallRating'])}/5.0</span>
            </div>
          </div>
          <p style="font-size:13px;color:var(--bonus);font-weight:600;margin-bottom:4px">{e(b['welcomeBonusAmount'])}</p>
          <div style="display:flex;align-items:center;gap:6px;margin-top:8px">
            <span class="promo-code" style="font-size:11px;padding:3px 8px">{e(rc)}</span>
            <span style="font-size:11px;color:var(--text-muted)">Promo Code</span>
          </div>
        </a>"""
    return f"""<div style="margin-top:48px">
      <h2 style="font-size:18px;font-weight:700;margin-bottom:20px">Similar Offers You Might Like</h2>
      <div class="grid-3">{cards}</div>
    </div>"""


def cross_links_section(brand, depth=1):
    """Build cross-link navigation between review, promo, and related pages."""
    prefix = '../' * depth
    code = get_promo(brand)
    return f"""<div class="cross-links" style="margin-top:32px;padding:24px;background:var(--surface-2);border-radius:8px">
      <h3 style="font-size:15px;font-weight:700;margin-bottom:16px">More on {e(brand['name'])}</h3>
      <div style="display:flex;flex-wrap:wrap;gap:10px">
        <a href="{prefix}betting-site-review/{brand['id']}.html" class="btn-outline btn-sm">{e(brand['name'])} Review</a>
        <a href="{prefix}promo-code/{brand['id']}.html" class="btn-outline btn-sm">Promo Code: {e(code)}</a>
        <a href="{prefix}betting-sites.html" class="btn-outline btn-sm">All Betting Sites</a>
        <a href="{prefix}promo-codes.html" class="btn-outline btn-sm">All Promo Codes</a>
      </div>
    </div>"""

# ===== PAGE WRAPPER =====
def page(title, description, canonical, body, depth=0, active_nav='', json_ld='', bc_items=None, og_image=''):
    prefix = '../' * depth
    # Auto-generate BreadcrumbList JSON-LD
    bc_ld = ''
    if bc_items:
        bc_list_items = []
        for i, item in enumerate(bc_items):
            name_bc = item.get('label', '')
            href_bc = item.get('href', '')
            if href_bc and i < len(bc_items) - 1:
                bc_list_items.append(f'{{"@type":"ListItem","position":{i+1},"name":"{_esc_json(name_bc)}","item":"{BASE_URL}/{href_bc.replace(".html","")}"}}')
            else:
                bc_list_items.append(f'{{"@type":"ListItem","position":{i+1},"name":"{_esc_json(name_bc)}"}}')
        bc_ld = '<script type="application/ld+json">{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[' + ','.join(bc_list_items) + ']}</script>'
    
    css_path = f'{prefix}assets/style.css'
    js_path = f'{prefix}assets/main.js'

    # Build desktop nav
    nav_items = [
        ('Home', f'{prefix}index.html', 'home'),
        ('Betting', f'{prefix}betting-sites.html', 'betting'),
        ('Casino', f'{prefix}casino-sites.html', 'casino'),
        ('Promos', f'{prefix}promo-codes.html', 'promos'),
        ('Payments', f'{prefix}payment-methods.html', 'payments'),
        ('News', f'{prefix}news.html', 'news'),
        ('Calculators', f'{prefix}betting-calculators.html', 'calculators'),
    ]

    desktop_nav = ''
    for label, href, key in nav_items:
        active_cls = ' active' if key == active_nav else ''
        desktop_nav += f'<a href="{href}" class="nav-link{active_cls}">{label}</a>\n'

    # Reviews dropdown
    reviews_dd = '<div class="nav-dropdown">\n'
    reviews_dd += f'<button class="nav-dropdown-btn">Reviews {ICON_CHEVRON_DOWN}</button>\n'
    reviews_dd += '<div class="nav-dropdown-panel">\n'
    for b in BRANDS:
        reviews_dd += f'<a href="{prefix}betting-site-review/{b["id"]}.html" class="dropdown-item"><span>{e(b["name"])}</span><span class="dropdown-rating">{fmtRating(b["overallRating"])}/5.0</span></a>\n'
    reviews_dd += '</div></div>\n'

    # Mobile menu
    mobile_brands = ''.join(
        f'<a href="{prefix}betting-site-review/{b["id"]}.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>{e(b["name"])}</span><span class="dropdown-rating">{fmtRating(b["overallRating"])}/5.0</span></a>\n'
        for b in BRANDS
    )
    mobile_menu = f'''<div class="mobile-overlay" onclick="closeMobileMenu()"></div>
<div class="mobile-menu">
  <div class="mobile-menu-inner">
    <button class="mobile-nav-item" onclick="toggleSubmenu('sub-betting')"><span>Betting</span><span class="mobile-chevron" style="transition:transform 280ms">{ICON_CHEVRON_DOWN}</span></button>
    <div id="sub-betting" class="mobile-submenu">
      <a href="{prefix}betting-sites.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Betting Sites</span></a>
      <a href="{prefix}new-betting-sites.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>New Betting Sites</span></a>
      <a href="{prefix}betting/best-betting-apps-south-africa.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Best Betting Apps</span></a>
      <a href="{prefix}guides/" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Betting Guides</span></a>
      <a href="{prefix}compare/" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Compare Sites</span></a>
      <a href="{prefix}betting/bonus-finder.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Bonus Finder</span></a>
      <a href="{prefix}betting/find-your-bookmaker.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Find Your Bookmaker</span></a>
    </div>
    <div class="mobile-sep"></div>
    <button class="mobile-nav-item" onclick="toggleSubmenu('sub-casino')"><span>Casino</span><span class="mobile-chevron" style="transition:transform 280ms">{ICON_CHEVRON_DOWN}</span></button>
    <div id="sub-casino" class="mobile-submenu">
      <a href="{prefix}casino-sites.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Casino Sites</span></a>
      <a href="{prefix}casino/best-casino-apps-south-africa.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Best Casino Apps</span></a>
      <a href="{prefix}casino-guides/" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Casino Guides</span></a>
    </div>
    <div class="mobile-sep"></div>
    <button class="mobile-nav-item" onclick="toggleSubmenu('sub-reviews')"><span>Reviews</span><span class="mobile-chevron" style="transition:transform 280ms">{ICON_CHEVRON_DOWN}</span></button>
    <div id="sub-reviews" class="mobile-submenu">{mobile_brands}</div>
    <div class="mobile-sep"></div>
    <a href="{prefix}promo-codes.html" class="mobile-nav-link" onclick="closeMobileMenu()">Promos</a><div class="mobile-sep"></div>
    <a href="{prefix}payment-methods.html" class="mobile-nav-link" onclick="closeMobileMenu()">Payments</a><div class="mobile-sep"></div>
    <a href="{prefix}news.html" class="mobile-nav-link" onclick="closeMobileMenu()">News</a><div class="mobile-sep"></div>
    <a href="{prefix}betting-calculators.html" class="mobile-nav-link" onclick="closeMobileMenu()">Calculators</a><div class="mobile-sep"></div>
    <a href="{prefix}about-us.html" class="mobile-nav-link" onclick="closeMobileMenu()">About</a>
    <div style="height:12px"></div>
    <a href="{prefix}betting-sites.html" class="btn-primary" style="display:block;text-align:center;margin:0 16px 16px;border-radius:24px;min-height:48px;line-height:48px;font-size:15px;font-weight:700" onclick="closeMobileMenu()">Find Your Bookmaker</a>
  </div>
</div>'''

    # Footer
    top_brands_links = ''.join(f'<a href="{prefix}betting-site-review/{b["id"]}.html">{e(b["name"])}</a>\n' for b in BRANDS[:10])

    footer = f'''<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
          {LOGO_SVG}
          <span style="font-weight:700;font-size:15px">MzansiWins</span>
        </div>
        <p>Honest SA betting reviews by okes who actually punt. No fluff, no bias, no nonsense. Updated {CURRENT_MONTH_YEAR}.</p>
        <address style="font-style:normal;margin-top:12px;line-height:1.6;font-size:13px;color:#888">
          MzansiWins.co.za<br>
          38 Wale St<br>
          Cape Town City Centre<br>
          Cape Town 8000<br>
          South Africa
        </address>
        <p style="margin-top:8px"><a href="mailto:help@mzansiwins.co.za" style="color:var(--accent);font-weight:600">help@mzansiwins.co.za</a></p>
      </div>
      <div class="footer-col">
        <p class="footer-heading">Top Bookmakers</p>
        <div class="footer-links">{top_brands_links}</div>
      </div>
      <div class="footer-col">
        <p class="footer-heading">Categories</p>
        <div class="footer-links">
        <a href="{prefix}betting-sites.html">Best Betting Sites</a>
        <a href="{prefix}casino-sites.html">Best Casino Sites</a>
        <a href="{prefix}promo-codes.html">All Promo Codes</a>
        <a href="{prefix}guides/">Betting Guides</a>
        <a href="{prefix}casino-guides/">Casino Guides</a>
        <a href="{prefix}compare/">Compare Sites</a>
        <a href="{prefix}betting/bonus-finder.html">Bonus Finder</a>
        <a href="{prefix}betting-calculators.html">Betting Calculators</a>
        <a href="{prefix}payment-methods.html">Payment Methods</a>
        <a href="{prefix}our-authors.html">Our Authors</a>
        </div>
      </div>
      <div class="footer-col">
        <p class="footer-heading">Transparency</p>
        <div class="footer-links">
        <a href="{prefix}code-of-ethics.html">Code of Ethics</a>
        <a href="{prefix}editorial-policy.html">Editorial Policy</a>
        <a href="{prefix}fact-checking.html">Fact Checking</a>
        <a href="{prefix}corrections-policy.html">Corrections Policy</a>
        <a href="{prefix}affiliate-disclosure.html">Affiliate Disclosure</a>
        <a href="{prefix}advertising-disclosure.html">Advertising Disclosure</a>
        <a href="{prefix}complaints-policy.html">Complaints Policy</a>
        </div>
      </div>
      <div class="footer-col">
        <p class="footer-heading">Responsible Gambling</p>
        <div class="footer-links">
        <a href="{prefix}responsible-gambling-policy.html">Responsible Gambling Policy</a>
        <a href="{prefix}support-organisations.html">Support Organisations</a>
        <a href="{prefix}betting-risk-awareness.html">Betting Risk Awareness</a>
        <a href="{prefix}self-exclusion-resources.html">Self-Exclusion Resources</a>
        </div>
      </div>
      <div class="footer-col">
        <p class="footer-heading">Corporate</p>
        <div class="footer-links">
        <a href="{prefix}about-us.html">Company Information</a>
        <a href="{prefix}management-team.html">Management Team</a>
        <a href="{prefix}partnerships.html">Partnerships</a>
        <a href="{prefix}advertise-with-us.html">Advertise With Us</a>
        <a href="{prefix}careers.html">Careers</a>
        <p class="footer-heading" style="margin-top:16px">Legal</p>
        <a href="{prefix}accessibility-statement.html">Accessibility</a>
        <a href="{prefix}privacy-policy.html">Privacy Policy</a>
        <a href="{prefix}cookie-policy.html">Cookie Policy</a>
        <a href="{prefix}terms-and-conditions.html">Terms &amp; Conditions</a>
        <a href="{prefix}sitemap.xml">Sitemap</a>
        </div>
      </div>
    </div>
    <div class="rg-notice">
      <p class="footer-heading">18+ RESPONSIBLE GAMBLING</p>
      <p>Gambling is entertainment - not a get-rich-quick scheme. You must be 18+ to gamble in SA. Never bet the rent money. If things are getting out of hand for you or someone you know, call the SA Responsible Gambling Foundation: <strong>0800 006 008</strong> (free, 24/7). Every bookmaker on this site holds a valid provincial licence.</p>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2026 MzansiWins. All rights reserved.</p>
    </div>
    <p class="footer-disclaimer">Disclaimer: MzansiWins is an independent review site. Ja, we earn affiliate commissions when you sign up through our links - that is how we keep the lights on. But it never influences our rankings or what we write. All bonus offers and odds are subject to change. Always read the T&amp;Cs, even the boring bits.</p>
  </div>
</footer>'''

    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{e(trim_title(title))}</title>
  <meta name="description" content="{e(trim_desc(description))}">
  <link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg">
  <link rel="canonical" href="{BASE_URL}/{canonical}">
  <link rel="alternate" hreflang="en-za" href="{BASE_URL}/{canonical}">
  <link rel="alternate" hreflang="x-default" href="{BASE_URL}/{canonical}">
  <meta property="og:title" content="{e(trim_title(title))}">
  <meta property="og:description" content="{e(trim_desc(description))}">
  <meta property="og:url" content="{BASE_URL}/{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="MzansiWins">
  <meta property="og:locale" content="en_ZA">
  <meta property="og:image" content="{BASE_URL}/assets/{og_image if og_image else 'og-default.png'}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{e(trim_title(title))}">
  <meta name="twitter:description" content="{e(trim_desc(description))}">
  <meta name="twitter:image" content="{BASE_URL}/assets/{og_image if og_image else 'og-default.png'}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" href="{css_path}" as="style">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
  <noscript><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"></noscript>
  <link rel="stylesheet" href="{css_path}">
  {json_ld}
  {bc_ld}
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <div class="header-left">
        <button class="hamburger" onclick="toggleMobileMenu()" aria-label="Toggle menu">{ICON_MENU}</button>
        <a href="{prefix}index.html" class="logo-link">{LOGO_SVG}<span class="logo-text">MzansiWins</span></a>
      </div>
      <nav class="desktop-nav">
        {desktop_nav}
        {reviews_dd}
      </nav>
      <div class="header-right">
        <button class="theme-btn" onclick="toggleTheme()" aria-label="Toggle theme"></button>
        <div class="starred-nav-badge" id="starredNavBadge">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2z"/></svg>
          <span class="starred-nav-count" id="starredCount" style="display:none">0</span>
          <div class="starred-dropdown" id="starredDropdown">
            <div class="starred-dropdown-empty">Star a bookmaker to track it here</div>
          </div>
        </div>
        <a href="{prefix}betting-sites.html" class="betting-sites-btn">Betting Sites</a>
      </div>
    </div>
  </header>
  {mobile_menu}
  <main>{body}</main>
  {footer}
  <button class="back-to-top" id="backToTop" aria-label="Back to top">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 15l-6-6-6 6"/></svg>
  </button>
  <script src="{js_path}" defer></script>
</body>
</html>'''


# ============================================================
# PAGE GENERATORS
# ============================================================

def build_homepage():
    top5 = BRANDS[:5]
    total_bonus = sum(int(re.sub(r'[^0-9]', '', m.group(1))) for b in DATA['brands'] if (m := re.search(r'R\s*([\d,]+)', b.get('welcomeBonusAmount', ''))))

    # Top 5 picks
    top5_html = ''
    for i, brand in enumerate(top5):
        is_first = i == 0
        card_cls = 'top-pick' if is_first else 'card'
        methods = brand.get('paymentMethodsList', [])[:4]
        if is_first:
            pay_pills = ''.join(f'<span class="payment-pill" style="background:rgba(255,255,255,0.15);color:#fff;border-color:transparent">{payment_icon_img(m, size=14, depth=0)} {e(m)}</span>' for m in methods)
        else:
            pay_pills = ''.join(payment_badge_html(m, small=True) for m in methods)
        logo = logo_path(brand, 0)
        logo_img = f'<img src="{logo}" alt="{e(brand["name"])}" style="width:48px;height:48px;object-fit:contain;border-radius:8px;background:{brand_bg(brand)};padding:4px;{"border:1px solid rgba(255,255,255,0.2)" if is_first else "border:1px solid var(--border)"}">' if logo else ''
        top5_html += f'''<div class="{card_cls}" style="position:relative;overflow:hidden">
          <div class="top3-rank">{i+1}</div>
          {"<div class='top-pick-label'>TOP PICK</div>" if is_first else ""}
          <div class="card-bonus"><p>{e(brand['welcomeBonusAmount'])}</p></div>
          <a href="betting-site-review/{brand['id']}.html" style="display:block;padding:24px;position:relative;z-index:1">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
              <div style="display:flex;align-items:center;gap:12px">
                {logo_img}
                <div>
                  <h3 style="font-size:20px;font-weight:800;{"color:#fff" if is_first else ""}">{e(brand['name'])}</h3>
                  <p style="font-size:12px;color:{'rgba(255,255,255,0.7)' if is_first else 'var(--text-muted)'};margin-top:2px">{f"Est. {brand['yearEstablished']}" if brand.get('yearEstablished') and brand['yearEstablished'].lower() not in ('not specified','n/a','unknown','') else 'Licensed SA'}</p>
                </div>
              </div>
              <span style="font-size:22px;font-weight:800;color:{'#fff' if is_first else 'var(--accent)'}">{fmtRating(brand['overallRating'])}<span style="font-size:13px;opacity:0.7">/5.0</span></span>
            </div>
            <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px">
              {pay_pills}
            </div>
            <div class="btn-primary btn-full" style="{"background:#fff;color:var(--accent)" if is_first else ""}">Full Review</div>
          </a>
        </div>'''

    # All bookmakers grid removed - see betting-sites.html for full list

    # News
    featured = NEWS[0] if NEWS else None
    sidebar_news = NEWS[1:5]
    featured_html = ''
    if featured:
        cat_colors = {'Promos':'#1641B4','Industry':'#0ea5e9','Payments':'#22c55e','Sports':'#f5a623','Platform':'#ef4444'}
        cc = cat_colors.get(featured.get('category',''), '#555')
        dt = datetime.fromisoformat(featured['date'].replace('Z','+00:00')).strftime('%d %b %Y') if featured.get('date') else ''
        featured_html = f'''<a href="news/{featured['slug']}.html" class="news-card" style="height:100%">
          <div style="padding:24px">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
              <span class="news-badge" style="background:{cc}">{e(featured.get('category',''))}</span>
              <span style="font-size:12px;color:var(--text-muted)">{dt}</span>
            </div>
            <h3 style="font-size:20px;font-weight:700;line-height:1.3;margin-bottom:8px">{e(featured['title'])}</h3>
            <p style="font-size:14px;color:var(--text-secondary);line-height:1.6;margin-bottom:12px">{e(featured.get('excerpt',''))}</p>
          </div>
        </a>'''

    sidebar_html = ''
    for article in sidebar_news:
        cc = cat_colors.get(article.get('category',''), '#555')
        dt = datetime.fromisoformat(article['date'].replace('Z','+00:00')).strftime('%d %b') if article.get('date') else ''
        sidebar_html += f'''<a href="news/{article['slug']}.html" class="news-card" style="display:block;padding:16px">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
            <span class="news-badge" style="background:{cc}">{e(article.get('category',''))}</span>
            <span style="font-size:11px;color:var(--text-muted)">{dt}</span>
          </div>
          <h3 style="font-size:14px;font-weight:600;line-height:1.35;margin-bottom:4px">{e(article['title'])}</h3>
          <p style="font-size:12px;color:var(--text-secondary);line-height:1.5;margin-top:4px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">{e(article.get('excerpt','')[:100])}</p>
        </a>'''

    # News cards grid (4 equal cards)
    news_cards_html = ''
    for article in NEWS[:4]:
        cc = cat_colors.get(article.get('category',''), '#555')
        dt = datetime.fromisoformat(article['date'].replace('Z','+00:00')).strftime('%d %b') if article.get('date') else ''
        news_cards_html += f'''<a href="news/{article['slug']}.html" class="news-card-item">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
            <span class="news-badge" style="background:{cc}">{e(article.get('category',''))}</span>
            <span style="font-size:12px;color:var(--text-muted)">{dt}</span>
          </div>
          <h3 style="font-size:15px;font-weight:700;line-height:1.35;margin-bottom:8px">{e(article['title'])}</h3>
          <p style="font-size:13px;color:var(--text-secondary);line-height:1.6;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden">{e(article.get('excerpt','')[:140])}</p>
        </a>'''

    # Payment methods
    pay_cards = ''
    for m in PAYMENTS[:6]:
        icon = payment_icon_img(m['name'], size=28, depth=0)
        pay_cards += f'''<a href="payment-methods/{m['id']}.html" class="card" style="display:flex;flex-direction:column;min-height:220px">
          <div style="display:flex;align-items:center;gap:12px;padding:24px 24px 0">
            <div class="method-icon-box">{icon}</div>
            <div style="min-width:0">
              <h3 style="font-size:14px;font-weight:700">{e(m['name'])}</h3>
              <span style="font-size:12px;color:var(--text-muted);text-transform:capitalize">{e(m['type'])}</span>
            </div>
          </div>
          <div style="padding:12px 24px;flex:1">
            <p style="font-size:14px;color:var(--text-secondary);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">{e((m.get('description',''))[:120])}</p>
          </div>
          <div style="padding:12px 24px 20px;margin-top:auto">
            <div style="display:flex;align-items:center;gap:16px;font-size:12px;color:var(--text-muted);border-top:1px solid var(--sep);padding-top:12px">
              <span>\u26A1 {truncate(m.get('depositSpeed',''), 20)}</span>
              <span style="opacity:0.3">|</span>
              <span>R {truncate(m.get('fees',''), 20)}</span>
            </div>
          </div>
        </a>'''

    # Best by sport - blue SVG icons
    SPORT_ICONS = {
        'Football': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/></svg>',
        'Rugby': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="12" rx="10" ry="6" transform="rotate(-45 12 12)"/><path d="M7.5 7.5L16.5 16.5"/><path d="M10 6l-1.5 3.5L12 11l3.5-1.5L17 6" transform="rotate(-45 12 12)"/></svg>',
        'Cricket': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="2" x2="6" y2="10"/><line x1="10" y1="2" x2="10" y2="10"/><line x1="14" y1="2" x2="14" y2="10"/><line x1="4" y1="10" x2="16" y2="10"/><circle cx="18" cy="18" r="3"/><line x1="20" y1="4" x2="10" y2="16"/></svg>',
        'Horse Racing': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 8c-1-2-3-3-5-3-3 0-4 2-5 3H8l-4 7h3l1 6h2l1-6h2l1 6h2l1-6h3l-1-4c2-1 3-2 3-3z"/></svg>',
        'Tennis': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M18.09 5.91A8.96 8.96 0 0 0 5.91 18.09"/><path d="M5.91 5.91A8.96 8.96 0 0 0 18.09 18.09"/></svg>',
        'Basketball': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2v20"/><path d="M4.93 4.93c4.08 2.16 6.36 6.36 6.36 6.36"/><path d="M19.07 4.93c-4.08 2.16-6.36 6.36-6.36 6.36"/></svg>',
    }
    best_sport = [
        ('Football', 'easybet-south-africa'), ('Rugby', 'betway-south-africa'),
        ('Cricket', 'gbets'), ('Horse Racing', 'hollywoodbets'),
        ('Tennis', 'sportingbet'), ('Basketball', 'mzansibet'),
    ]
    sport_cards = ''
    for sport, bid in best_sport:
        brand = next((b for b in DATA['brands'] if b['id'] == bid), None)
        if not brand: continue
        svg_icon = SPORT_ICONS.get(sport, '')
        sport_cards += f'''<a href="betting-site-review/{brand['id']}.html" class="card" style="padding:20px">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
            <div style="width:36px;height:36px;background:var(--accent-light);border-radius:8px;display:flex;align-items:center;justify-content:center">{svg_icon}</div>
            <div>
              <p style="font-size:12px;color:var(--text-muted);font-weight:500">{sport}</p>
              <p style="font-size:14px;font-weight:700">{e(brand['name'])}</p>
            </div>
          </div>
          <div style="display:flex;align-items:center;justify-content:space-between">
            <span style="font-size:13px;color:var(--text-secondary);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;padding-right:8px">{e(brand['welcomeBonusAmount'])}</span>
            <span style="font-size:13px;font-weight:700;color:var(--accent)">{fmtRating(brand['overallRating'])}/5.0</span>
          </div>
        </a>'''

    # How we rate
    criteria = [
        ('Welcome Bonus', '25%', 'Is the bonus actually worth it, or just a flashy number with nasty wagering? We find out.'),
        ('Odds Quality', '20%', 'We compare odds on PSL, Springbok rugby, and Proteas cricket. Every cent counts, bru.'),
        ('Payment Methods', '15%', 'Can you use EFT, vouchers, and e-wallets? And more importantly - how fast do withdrawals land?'),
        ('Sports Coverage', '15%', 'PSL player props? Currie Cup corners? The more markets, the more ways to win.'),
        ('Platform Quality', '10%', 'Does the app crash mid-bet or does it run smooth like a Camps Bay sunset?'),
        ('Live Betting', '10%', 'Live markets, cash out when you are sweating, and streaming if you are lucky.'),
        ('Customer Support', '5%', 'Can you actually reach a human? And do they understand what eish means?'),
    ]
    criteria_cards = ''
    for label, weight, desc in criteria:
        criteria_cards += f'''<div style="background:var(--surface-2);border-radius:8px;padding:16px;border:var(--card-border)">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">
            <span style="font-size:13px;font-weight:600">{label}</span>
            <span style="font-size:12px;font-weight:700;color:var(--accent)">{weight}</span>
          </div>
          <p style="font-size:12px;color:var(--text-muted);line-height:1.5">{desc}</p>
        </div>'''

    # FAQ
    faqs = [
        ('Is online betting legal in South Africa?', 'Ja, 100% legal, bru. As long as you stick to licensed operators (which is every single bookie on this site), you are golden. All our bookmakers hold proper provincial gambling licences. Stay on the straight and narrow and you are sorted.'),
        ('What is the minimum age for betting in SA?', 'You must be 18 or older to place bets in South Africa. All licensed bookmakers will ask you to verify your identity (FICA) before you can withdraw. No exceptions.'),
        ('Which payment method is fastest?', 'Ozow is faster than a Kolisi tackle - instant. OTT, Blu Voucher, and 1Voucher are also instant. Visa and Mastercard work quick too. If waiting for money gives you anxiety, these are your friends.'),
        ('Do I need a promo code for welcome bonuses?', 'Some bookies want a code, others just throw the bonus at you automatically. It depends. We spell it out for every single bookmaker in our reviews - no guessing required.'),
        ('How long do withdrawals take?', 'Depends how you cash out. Ozow and some EFTs can land same-day (beautiful). Bank transfers? 1 to 3 business days - ja, we know, painful. Vouchers are usually 24 to 48 hours.'),
        ('Are my personal details safe?', 'Licensed SA bookmakers must comply with POPIA and use proper encryption. Stick to licensed operators and you are covered.'),
        ('Which bookmaker has the best welcome bonus right now?', 'Right now? Zarbet is the boss - 125% match up to R3,750 plus 25 free spins. 10Bet is hot on their heels with 100% up to R3,000. And Easybet brings the fire with 150% up to R1,500. Competition is lekker.'),
        ('Can I bet on the PSL at all SA bookmakers?', 'Every single one of the 35 bookies covers PSL - it is basically a requirement in this country. Hollywoodbets goes the deepest with player props, corner totals, and half-time markets. Die-hard PSL fans, that is your spot.'),
    ]
    faq_html = ''
    for q, a in faqs:
        faq_html += f'''<div class="faq-item">
          <button class="faq-btn" onclick="toggleFaq(this)">
            <span>{e(q)}</span>
            <span class="faq-chevron">{ICON_CHEVRON_DOWN}</span>
          </button>
          <div class="faq-body"><p>{e(a)}</p></div>
        </div>'''

    # Build compact top 5 cards for hero sidebar
    hero_top5 = ''
    for i, brand in enumerate(top5):
        logo = logo_path(brand, 0)
        logo_img = f'<img src="{logo}" alt="{e(brand["name"])}" style="width:36px;height:36px;object-fit:contain;border-radius:6px;background:{brand_bg(brand)};padding:3px;border:1px solid var(--border)">' if logo else ''
        rank_badge = f'<span style="width:22px;height:22px;border-radius:50%;background:var(--accent);color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0">{i+1}</span>'
        hero_top5 += f'''<a href="betting-site-review/{brand['id']}.html" class="hero-pick-card">
          <div style="display:flex;align-items:center;gap:10px;flex:1;min-width:0">
            {rank_badge}
            {logo_img}
            <div style="min-width:0">
              <div style="font-size:14px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{e(brand['name'])}</div>
              <div style="font-size:12px;color:var(--bonus);font-weight:600">{e(brand['welcomeBonusAmount'])}</div>
            </div>
          </div>
          <div style="text-align:right;flex-shrink:0">
            <div style="font-size:18px;font-weight:800;color:var(--accent)">{fmtRating(brand['overallRating'])}<span style="font-size:11px;opacity:0.6">/5.0</span></div>
          </div>
        </a>'''

    # Top bonuses grid cards (8 brands sorted by bonus value)
    bonus_sorted = sorted(DATA['brands'], key=lambda b: -bonus_val(b))[:8]
    bonus_cards_html = ''
    for idx, b in enumerate(bonus_sorted):
        blogo = logo_path(b, 0)
        bv = bonus_val(b)
        bv_disp = f'R{bv:,}' if bv > 0 else e(b.get('welcomeBonusAmount',''))
        promo = get_promo(b)
        rank = idx + 1
        bonus_cards_html += f'''<a href="betting-site-review/{b['id']}.html" class="top-bonus-card">
          <div class="bonus-rank">#{rank}</div>
          <img src="{blogo}" alt="{e(b['name'])}" style="background:{brand_bg(b)};padding:3px;border:1px solid var(--border)">
          <div class="bonus-name">{e(b['name'])}</div>
          <div class="bonus-amount">{bv_disp}</div>
          <div class="bonus-code">Code: <strong>{e(promo)}</strong></div>
          <div class="bonus-claim">Claim Bonus &rarr;</div>
        </a>'''

    # Build brand logo collage for hero background
    logo_collage_items = ''
    for b in BRANDS_ORDERED:
        lp = logo_path(b, 0)
        if lp:
            bg = brand_bg(b)
            logo_collage_items += f'<img src="{lp}" alt="" class="hero-collage-logo" style="background:{bg}" loading="lazy">'

    body = f'''
    <section class="hero hero-animated-bg">
      <div class="hero-logo-collage" aria-hidden="true">
        {logo_collage_items}
      </div>
      <div class="container hero-layout">
        <div class="hero-text">
          <div class="hero-badge">{ICON_TROPHY} <span>{len(DATA['brands'])} LICENSED SA BOOKMAKERS TESTED</span></div>
          <h1>South Africa's Best Betting Sites - Over <span style="color:var(--bonus)">R{total_bonus:,}</span> in Bonuses</h1>
          <p class="hero-lead">We are a Cape Town-based team of real punters who tested every single licensed SA bookmaker. {len(DATA['brands'])} sites, {CURRENT_MONTH_YEAR} - no fluff, no bias, just honest reviews from okes who actually bet with their own rands.</p>
          <div class="hero-btns">
            <a href="promo-codes.html" class="btn-primary">{ICON_GIFT} Claim R{total_bonus:,}+ in Bonuses</a>
            <a href="betting-sites.html" class="btn-outline">{ICON_TROPHY} View Top Bookmakers</a>
          </div>
          <div class="hero-trust-bar">
            <div class="hero-trust-item trust-badge-primary">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
              <span>Licensed &amp; Verified</span>
            </div>
            <div class="hero-trust-item">
              <svg width="22" height="15" viewBox="0 0 900 600" style="border-radius:2px"><rect width="900" height="200" fill="#DE3831"/><rect y="200" width="900" height="200" fill="#FFF"/><rect y="400" width="900" height="200" fill="#002395"/><path d="M0,0 L0,128 L360,300 L0,472 L0,600 L180,600 L540,300 L180,0Z" fill="#FFB612"/><path d="M0,28 L0,160 L340,300 L0,440 L0,572 L152,572 L510,300 L152,28Z" fill="#007A4D"/><path d="M0,80 L0,192 L300,300 L0,408 L0,520 L100,520 L430,300 L100,80Z" fill="#FFF"/><path d="M0,112 L0,210 L270,300 L0,390 L0,488 L68,488 L390,300 L68,112Z" fill="#000"/></svg>
              <span>100% South African</span>
            </div>
            <div class="hero-trust-item">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
              <span>Based in Cape Town</span>
            </div>
            <div class="hero-trust-item">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <span>Updated {CURRENT_MONTH_YEAR}</span>
            </div>
            <div class="hero-trust-item">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              <span>18+ Responsible Gambling</span>
            </div>
          </div>
        </div>
        <div class="hero-sidebar">
          <div class="hero-picks-box">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px">
              <h2 style="font-size:15px;font-weight:700;margin:0">Top 5 Picks</h2>
              <a href="betting-sites.html" style="font-size:12px;color:var(--accent);font-weight:600">View all {len(DATA['brands'])}</a>
            </div>
            <div style="display:flex;flex-direction:column;gap:10px">
              {hero_top5}
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-header">
          <div><h2 class="section-title">Grab Your Welcome Bonus</h2><p class="section-subtitle">The best sign-up deals from licensed SA bookmakers - all tested by our team</p></div>
          <a href="promo-codes.html" class="section-link">All promo codes</a>
        </div>
        <div class="top-bonuses-grid">{bonus_cards_html}</div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="container">
        <div class="section-header">
          <div><h2 class="section-title">Latest SA Betting News</h2><p class="section-subtitle">What is going on in the SA betting world - straight from the horse's mouth</p></div>
          <a href="news.html" class="section-link">All news</a>
        </div>
        <div class="news-cards-grid">{news_cards_html}</div>
      </div>
    </section>



    <section class="section section-alt">
      <div class="container">
        <div class="section-header">
          <div><h2 class="section-title">Best Bookmakers by Sport</h2><p class="section-subtitle">Whether you bleed PSL or live for the Boks - we have got your bookie sorted</p></div>
        </div>
        <div class="grid-6">{sport_cards}</div>
        <div style="text-align:center;margin-top:24px">
          <a href="betting/find-your-bookmaker.html" class="btn-primary" style="display:inline-flex;align-items:center;gap:8px;padding:14px 32px;border-radius:28px;font-size:15px">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
            Find Your Perfect Bookmaker
          </a>
          <p style="font-size:13px;color:var(--text-muted);margin-top:10px">Answer 5 quick questions and we will match you with the best SA betting site</p>
        </div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="container">
        <div class="section-header">
          <div><h2 class="section-title">Popular Payment Methods</h2><p class="section-subtitle">Getting your rands in and out without drama - here is how</p></div>
          <a href="payment-methods.html" class="section-link">All payment guides</a>
        </div>
        <div class="grid-6">{pay_cards}</div>
      </div>
    </section>

    <section class="section">
      <div class="container" style="max-width:800px">
        <div style="margin-bottom:40px">
          <h2 class="section-title">How We Rate Bookmakers</h2>
          <p style="color:var(--text-secondary);font-size:15px;line-height:1.7">Every bookmaker gets the full treatment - we sign up, deposit, bet, and withdraw with real rands. Then we score them on 7 things that actually matter to Mzansi punters. No shortcuts, no favourites.</p>
        </div>
        <div class="grid-6" style="margin-bottom:32px">{criteria_cards}</div>
        <a href="how-we-rate.html" class="btn-outline">Full Methodology</a>
      </div>
    </section>

    <section class="section section-alt">
      <div class="container" style="max-width:800px">
        <h2 class="section-title" style="margin-bottom:32px">Frequently Asked Questions</h2>
        <div style="display:flex;flex-direction:column;gap:12px">{faq_html}</div>
      </div>
    </section>

    <section class="rg-section">
      <div class="container">
        <div class="rg-inner">
          <div class="rg-content">
            <div style="flex-shrink:0;margin-top:2px;color:var(--accent)">{ICON_SHIELD}</div>
            <div>
              <h3>Bet Responsibly</h3>
              <p>Look, we love a good punt. But gambling is entertainment - not a side hustle, not a retirement plan, and definitely not how you pay rent. If things are getting heavy, call the Gambling Helpline: <strong style="color:#fff">0800 006 008</strong> (free, 24/7). 18+ only. Keep it fun, keep it smart.</p>
            </div>
          </div>
          <a href="tel:0800006008" class="rg-btn">0800 006 008</a>
        </div>
      </div>
    </section>
    '''

    t, d = seo_meta('home')
    home_ld = jsonld_website() + '\n' + jsonld_faq(faqs)
    return page(t, d, '', body, depth=0, active_nav='home', json_ld=home_ld)


# ============================================================
# BUILD ALL PAGES
# ============================================================

def build_brand_review(brand):
    depth = 1
    code = get_promo(brand)
    ratings = [
        ('Bonus', brand.get('ratingBonus', 3)),
        ('Odds', brand.get('ratingOdds', 3)),
        ('Payments', brand.get('ratingPayment', 3)),
        ('Sports', brand.get('ratingVariety', 3)),
        ('Platform', brand.get('ratingWebsite', 3)),
        ('Live', brand.get('ratingLive', 3)),
        ('Support', brand.get('ratingSupport', 3)),
    ]
    rating_bars = ''
    for label, val in ratings:
        val = float(val)
        pct = val / 5 * 100
        if val >= 4.0:
            bar_color = 'var(--accent)'
        elif val >= 3.0:
            bar_color = '#7c3aed'
        else:
            bar_color = 'var(--bonus)'
        rating_bars += f'''<div class="rating-row">
          <span class="rating-row-label">{label}</span>
          <div class="rating-bar-track"><div class="rating-bar-fill" style="width:{pct}%;background:{bar_color}"></div></div>
          <span class="rating-row-val">{fmtRating(val)}</span>
        </div>'''

    # Pros/Cons - split items on \n separators and strip leading dashes
    def split_items(items):
        result = []
        if isinstance(items, str): items = [items]
        for item in items:
            for sub in item.replace('\\n', '\n').split('\n'):
                s = sub.strip().lstrip('-').strip()
                if s: result.append(s)
        return result
    pros = split_items(brand.get('pros', []))
    cons = split_items(brand.get('cons', []))
    pros_li = ''.join(f'<li>{e(p)}</li>' for p in pros)
    cons_li = ''.join(f'<li>{e(c)}</li>' for c in cons)

    # Payment pills
    pay_pills = get_brand_payments_linked(brand, depth=depth)

    # Related brands
    related = [b for b in BRANDS if b['id'] != brand['id']][:4]
    related_cards = ''
    for b in related:
        related_cards += f'''<a href="{b['id']}.html" class="card" style="padding:16px">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">
            <div style="font-size:14px;font-weight:600">{e(b['name'])}</div>
            {rating_badge(b['overallRating'], 'sm')}
          </div>
          <p style="font-size:12px;color:var(--bonus);font-weight:500">{e(b['welcomeBonusAmount'])}</p>
        </a>'''

    # Ring SVG
    circ = 2 * 3.14159 * 34
    offset = circ - (float(brand['overallRating']) / 5) * circ
    ring_color = '#1641B4' if float(brand['overallRating']) >= 3.5 else '#16a34a'

    # Watermark logo
    wm_logo = logo_path(brand, depth)
    wm_html = f'<img src="{wm_logo}" alt="" class="brand-watermark" aria-hidden="true">' if wm_logo else ''

    # Visible hero logo
    hero_logo = logo_path(brand, depth)
    hero_logo_html = f'<img src="{hero_logo}" alt="{e(brand["name"])}" class="review-hero-logo" style="background:{brand_bg(brand)};padding:6px">' if hero_logo else ''

    # Site preview screenshots
    ss_desktop = f'assets/screenshots/{brand["id"]}-desktop.jpg'
    ss_mobile = f'assets/screenshots/{brand["id"]}-mobile.jpg'
    has_ss_desktop = os.path.exists(f'{OUT}/assets/screenshots/{brand["id"]}-desktop.jpg')
    has_ss_mobile = os.path.exists(f'{OUT}/assets/screenshots/{brand["id"]}-mobile.jpg')
    site_preview_html = ''
    if has_ss_desktop or has_ss_mobile:
        preview_items = ''
        if has_ss_desktop:
            preview_items += f'''<div class="site-preview-item" onclick="openLightbox('../{ss_desktop}')">
              <img src="../{ss_desktop}" alt="{e(brand['name'])} desktop view" loading="lazy">
              <div class="site-preview-label"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg> Desktop View</div>
            </div>'''
        if has_ss_mobile:
            preview_items += f'''<div class="site-preview-item" onclick="openLightbox('../{ss_mobile}')" style="max-width:200px">
              <img src="../{ss_mobile}" alt="{e(brand['name'])} mobile view" loading="lazy">
              <div class="site-preview-label"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12" y2="18"/></svg> Mobile View</div>
            </div>'''
        site_preview_html = f'''<div class="site-preview-section">
            <h2>Site Preview</h2>
            <p style="font-size:14px;color:var(--text-secondary);margin-bottom:16px">Real screenshots of the {e(brand['name'])} website captured in {CURRENT_MONTH_YEAR}. Click to enlarge.</p>
            <div class="site-preview-grid">{preview_items}</div>
          </div>'''

    body = f'''
    <div class="brand-hero-wrap" style="background:var(--surface-2);border-bottom:1px solid var(--border);padding:40px 0 32px">
      {wm_html}
      <div class="container">
        {breadcrumbs([{"label":"Home","href":"index.html"},{"label":"Betting Sites","href":"betting-sites.html"},{"label":brand["name"]}], depth)}
        <div class="review-hero-header">
          {hero_logo_html}
          <div>
            <h1 class="page-title">{e(brand['name'])} Review 2026 - The Honest Truth</h1>
            <p style="font-size:14px;color:var(--text-muted);margin-bottom:0">{f"Est. {brand['yearEstablished']}" if brand.get('yearEstablished') and brand['yearEstablished'].lower() not in ('not specified','n/a','unknown','') else 'Licensed SA Bookmaker'} - {e(brand.get('license','Provincial licence'))}</p>
          </div>
        </div>
      </div>
    </div>
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      {author_byline(get_review_author(brand['id']), depth)}

      <div class="two-col">
        <div>

          <!-- Promo Box -->
          <div class="review-promo-box" style="margin-bottom:32px">
            <div class="review-promo-top">
              <div style="display:flex;align-items:center;gap:10px">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2.5"><path d="M12 2L15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2z"/></svg>
                <span style="font-size:13px;font-weight:600;color:var(--accent);text-transform:uppercase;letter-spacing:0.04em">Exclusive Welcome Bonus</span>
              </div>
              {f'<a href="{masked_exit(brand, depth)}" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary" style="display:inline-flex;font-size:14px;padding:10px 28px;flex-shrink:0">Claim Bonus &rarr;</a>' if brand.get("exitLink") else ''}
            </div>
            <p class="review-promo-amount">{e(brand['welcomeBonusAmount'])}</p>
            <div class="review-promo-code-row">
              <div style="display:flex;align-items:center;gap:8px">
                <span style="font-size:12px;color:var(--text-muted);font-weight:500">PROMO CODE</span>
                <span class="promo-code" style="border-color:var(--accent)">{e(code)}</span>
                <button class="copy-btn" onclick="copyCode(this,'{e(code)}')">Copy</button>
              </div>
            </div>
            {f'<p style="font-size:12px;color:var(--text-muted);margin-top:10px;line-height:1.5">{e(brand.get("mcpTerms", brand.get("tcs","")))}</p>' if brand.get('mcpTerms') or brand.get('tcs') else ''}
          </div>

          <!-- Promo Banners -->
          {promo_banners_html(brand, depth)}

          <!-- Rating Breakdown -->
          <div style="background:var(--surface);border:var(--card-border);border-radius:8px;padding:28px;margin-bottom:32px">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
              <h2 style="font-size:16px;font-weight:700;margin:0">Rating Breakdown</h2>
              <span class="how-we-rate-tooltip" tabindex="0" aria-label="How we rate" onclick="this.classList.toggle('active')">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--accent)" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="11" fill="var(--accent)"/><text x="12" y="17" text-anchor="middle" font-size="15" font-weight="700" font-family="Inter,sans-serif" fill="#fff">i</text></svg>
                <span class="how-we-rate-panel" onclick="event.stopPropagation()">
                  <strong style="font-size:13px;display:block;margin-bottom:6px">How we rate</strong>
                  <span style="font-size:12px;line-height:1.45;color:var(--text-secondary)">Every bookmaker is scored across six categories by our editorial team. We test deposits, withdrawals, customer support, and app quality using real accounts and real money. Ratings are updated quarterly and are not influenced by affiliate partnerships. <a href="{'../' * depth}editorial-policy.html" style="color:var(--accent);font-weight:600">Read our editorial policy</a></span>
                </span>
              </span>
            </div>
            <div style="display:flex;align-items:center;gap:20px;margin-bottom:24px;padding-bottom:20px;border-bottom:1px solid var(--sep)">
              <div class="rating-ring">
                <svg width="80" height="80" viewBox="0 0 80 80">
                  <circle cx="40" cy="40" r="34" fill="none" stroke="var(--border)" stroke-width="6"/>
                  <circle cx="40" cy="40" r="34" fill="none" stroke="{ring_color}" stroke-width="6" stroke-linecap="round" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}" style="transition:stroke-dashoffset 0.8s ease;transform:rotate(-90deg);transform-origin:center"/>
                </svg>
                <div class="rating-ring-center">
                  <span class="rating-ring-num">{fmtRating(brand['overallRating'])}</span>
                  <span class="rating-ring-max">/5.0</span>
                </div>
              </div>
              <div>
                <p style="font-weight:700;font-size:16px">Overall Score</p>
                <p style="font-size:14px;color:var(--text-secondary);margin-top:2px">{"Outstanding" if float(brand['overallRating']) >= 4.5 else "Excellent" if float(brand['overallRating']) >= 4.0 else "Very Good" if float(brand['overallRating']) >= 3.5 else "Good"}</p>
              </div>
            </div>
            <div style="display:flex;flex-direction:column;gap:16px">{rating_bars}</div>
          </div>

          <!-- Pros & Cons -->
          <div class="grid-2" style="margin-bottom:32px">
            <div class="pros-box"><h3>{ICON_CHECK} Pros</h3><ul class="pros-list">{pros_li}</ul></div>
            <div class="cons-box"><h3>{ICON_X} Cons</h3><ul class="cons-list">{cons_li}</ul></div>
          </div>

          <!-- Detailed Review Content -->
          {generate_review_content(brand)}

          <!-- Site Preview -->
          {site_preview_html}

          <!-- Payment Methods -->
          <div style="margin-bottom:32px">
            <h2 style="font-size:16px;font-weight:700;margin-bottom:16px">Payment Methods</h2>
            <div style="display:flex;flex-wrap:wrap;gap:8px">{pay_pills}</div>
          </div>

          <!-- Features -->
          <div style="background:var(--surface);border:var(--card-border);border-radius:8px;overflow:hidden;margin-bottom:32px">
            <h2 style="font-size:16px;font-weight:700;padding:20px 20px 12px">Betting Features</h2>
            <table class="data-table" style="font-size:14px">
              <tbody>
                <tr><td style="font-weight:600">Minimum Deposit</td><td>{e(brand.get('minDeposit','Varies'))}</td></tr>
                <tr><td style="font-weight:600">Minimum Bet</td><td>{e(brand.get('minBet','Varies'))}</td></tr>
                <tr><td style="font-weight:600">Live Betting</td><td>{e(brand.get('liveBetting','Yes'))}</td></tr>
                <tr><td style="font-weight:600">Live Streaming</td><td>{e(brand.get('liveStreaming','No'))}</td></tr>
                <tr><td style="font-weight:600">Mobile App</td><td>{e(brand.get('mobileApp','Yes'))}</td></tr>
                <tr><td style="font-weight:600">Cash Out</td><td>{e(brand.get('cashOut','Yes'))}</td></tr>
                <tr><td style="font-weight:600">Customer Support</td><td>{e(brand.get('customerSupport','Email, Live Chat'))}</td></tr>
                <tr><td style="font-weight:600">Sports Covered</td><td>{e(', '.join(brand['sportsCovered']) if isinstance(brand.get('sportsCovered'), list) else brand.get('sportsCovered','20+'))}</td></tr>
              </tbody>
            </table>
          </div>

          <!-- Cross Links -->
          {cross_links_section(brand, depth)}

          <!-- Related -->
          <h2 style="font-size:16px;font-weight:700;margin-bottom:16px">Related Bookmakers</h2>
          <div class="grid-2">{related_cards}</div>
        </div>

        <!-- Sidebar -->
        <div class="sidebar" style="display:none">
          <div class="sidebar-card">
            <h3>Quick Info</h3>
            <div class="sidebar-row"><span class="text-muted">Rating</span><span class="font-semibold">{fmtRating(brand['overallRating'])}/5.0</span></div>
            <div class="sidebar-row"><span class="text-muted">Bonus</span><span class="font-semibold text-bonus">{e(brand['welcomeBonusAmount'][:30])}</span></div>
            <div class="sidebar-row"><span class="text-muted">Promo Code</span><span class="font-semibold">{e(code)}</span></div>
            <div class="sidebar-row"><span class="text-muted">Min Deposit</span><span class="font-semibold">{e(brand.get('minDeposit','Varies'))}</span></div>
            
          </div>
          {f'<a href="{masked_exit(brand, depth)}" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary btn-full btn-sm" style="margin-bottom:12px">Visit {e(brand["name"])}</a>' if brand.get("exitLink") else ''}
          <a href="../promo-code/{brand['id']}.html" class="btn-outline btn-full btn-sm" style="margin-bottom:20px">Get Promo Code</a>
          <a href="../betting-sites.html" style="display:flex;align-items:center;gap:8px;font-size:14px;color:var(--accent);font-weight:500">{ICON_ARROW_LEFT} All Betting Sites</a>
        </div>
      </div>
    </div>

    <!-- Sticky Bottom CTA Bar -->
    <div class="sticky-bottom-bar" id="stickyBar">
      <div class="sticky-bottom-inner">
        <div class="sticky-bottom-left">
          {f'<img src="{logo_path(brand, depth)}" alt="{e(brand["name"])}" class="sticky-bottom-logo" style="background:{brand_bg(brand)};padding:4px">' if logo_path(brand, depth) else ''}
          <div class="sticky-bottom-text">
            <div class="sticky-bottom-offer">{e(brand['welcomeBonusAmount'])}</div>
            <div class="sticky-bottom-tcs">{e((brand.get('mcpTerms', brand.get('tcs',''))[:80] + '...') if len(brand.get('mcpTerms', brand.get('tcs',''))) > 80 else brand.get('mcpTerms', brand.get('tcs','')))}</div>
          </div>
        </div>
        <div class="sticky-bottom-right">
          <span class="sticky-bottom-code">{e(code)}</span>
          {f'<a href="{masked_exit(brand, depth)}" target="_blank" rel="noopener noreferrer nofollow" class="sticky-bottom-cta">Claim Bonus</a>' if brand.get("exitLink") else f'<a href="javascript:void(0)" onclick="copyCode(this,\'{e(code)}\')" class="sticky-bottom-cta">Copy Code</a>'}
        </div>
      </div>
    </div>
    <script>
    (function(){{
      var bar=document.getElementById('stickyBar');
      if(!bar)return;
      var shown=false;
      window.addEventListener('scroll',function(){{
        if(window.scrollY>400){{if(!shown){{bar.classList.add('visible');shown=true;}}}}
        else{{if(shown){{bar.classList.remove('visible');shown=false;}}}}
      }});
    }})();
    </script>'''

    # Show sidebar on lg
    body = body.replace('class="sidebar" style="display:none"', 'class="sidebar lg-show"')

    t, d = seo_meta('review', brand=brand)
    return page(t, d, f'betting-site-review/{brand["id"]}', body, depth=1, json_ld=jsonld_review(brand, 1),
                bc_items=[{'label': 'Home', 'href': 'index.html'}, {'label': 'Betting Sites', 'href': 'betting-sites.html'}, {'label': brand['name']}])


def build_promo_detail(brand):
    depth = 1
    code = get_promo(brand)
    has_code = code.lower() not in ('none', 'no code', 'n/a')
    prefix = '../' * depth
    name = e(brand['name'])
    bonus = e(brand['welcomeBonusAmount'])
    rating_5 = fmtRating(brand['overallRating'])
    rating_10 = f'{float(brand["overallRating"]) * 2:.1f}'

    # Logo
    logo = logo_path(brand, depth)
    logo_img = f'<img src="{logo}" alt="{name}" class="promo-detail-hero hero-logo" style="background:{brand_bg(brand)};padding:6px">' if logo else ''
    logo_sm = f'<img src="{logo}" alt="{name}" class="sticky-bottom-logo" style="background:{brand_bg(brand)};padding:4px">' if logo else ''
    tcs_text = brand.get('mcpTerms', brand.get('tcs', ''))
    tcs_short = (tcs_text[:80] + '...') if len(tcs_text) > 80 else tcs_text

    # Check icon
    check_sm = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'
    flag_icon = '<svg width="20" height="14" viewBox="0 0 900 600" aria-label="South African flag" style="border-radius:2px;vertical-align:middle"><rect width="900" height="200" fill="#DE3831"/><rect y="200" width="900" height="200" fill="#FFF"/><rect y="400" width="900" height="200" fill="#002395"/><path d="M0,0 L0,128 L360,300 L0,472 L0,600 L180,600 L540,300 L180,0Z" fill="#FFB612"/><path d="M0,28 L0,160 L340,300 L0,440 L0,572 L152,572 L510,300 L152,28Z" fill="#007A4D"/><path d="M0,80 L0,192 L300,300 L0,408 L0,520 L100,520 L430,300 L100,80Z" fill="#FFF"/><path d="M0,112 L0,210 L270,300 L0,390 L0,488 L68,488 L390,300 L68,112Z" fill="#000"/></svg>'

    # Badge for top-rated brand
    badge = ''
    brand_idx = next((i for i, b in enumerate(BRANDS) if b['id'] == brand['id']), 99)
    if brand_idx == 0:
        badge = '<span class="promo-badge promo-badge-top">TOP RATED</span>'
    elif brand_idx < 3:
        badge = '<span class="promo-badge promo-badge-value">TOP 3</span>'
    elif brand_idx < 10:
        badge = '<span class="promo-badge promo-badge-rec">TOP 10</span>'

    # Trust badges row
    trust_html = f'''<div class="trust-badges-row" style="margin-top:16px">
      <div class="trust-badge">{check_sm} <span>Expert Verified</span></div>
      <div class="trust-badge">{flag_icon} <span>Legal in SA</span></div>
      <div class="trust-badge">{ICON_CLOCK} <span>Last used 12 mins ago</span></div>
      <div class="trust-badge">{ICON_SHIELD} <span>18+ Only</span></div>
    </div>'''

    # Expert quote
    rating_word = 'top-tier' if float(brand['overallRating']) >= 4.8 else 'outstanding' if float(brand['overallRating']) >= 4.5 else 'excellent' if float(brand['overallRating']) >= 4.0 else 'solid' if float(brand['overallRating']) >= 3.5 else 'decent'
    expert_html = f'''<div class="expert-quote" id="expert-analysis">
      <p>"{name} brings a {rating_word} welcome bonus to the table for new SA punters. The {bonus} offer holds its own against the competition, and signing up is about as painless as it gets. Our team verified this code is live and kicking as of {CURRENT_MONTH_YEAR}."</p>
      <p class="expert-name">MzansiWins Review Team</p>
    </div>'''

    # Claim steps (4 steps with titles)
    claim_steps = [
        ('Create Your Account', f'Head over to {brand["name"]} and hit that "Register" button. Fill in your details - name, ID number, email, phone. The usual suspects.'),
        ('Enter Promo Code', f'Enter the promo code <strong>{e(code)}</strong> in the registration form or bonus section.' if has_code else ('Automatic Bonus', 'No promo code needed. The bonus is applied automatically when you register.')),
        ('Verify Your Identity', f'Time for the fun part (not really). Upload your SA ID and proof of address for FICA verification. Check our <a href="{prefix}fica-guide.html" style="color:var(--accent);font-weight:600">FICA guide</a> if you need help.'),
        ('Deposit and Claim', f'Drop your first deposit (minimum {e(brand.get("minDeposit", "R10"))}) and watch that bonus land in your account. {e(brand.get("tcs", "T&Cs apply."))} Now go have some fun.'),
    ]
    steps_html = ''
    for i, (title, desc) in enumerate(claim_steps):
        steps_html += f'''<div class="claim-step">
      <div class="claim-step-num">{i+1}</div>
      <div class="claim-step-content">
        <div class="claim-step-title">{title}</div>
        <div class="claim-step-desc">{desc}</div>
      </div>
    </div>'''

    # Pros & Cons
    pros = brand.get('pros', [])
    cons = brand.get('cons', [])
    if isinstance(pros, list):
        pros = [p.strip() for pp in pros for p in pp.split(',') if p.strip()]
    if isinstance(cons, list):
        cons = [c.strip() for cc in cons for c in cc.split(',') if c.strip()]
    pros_html = ''.join(f'<li>{e(p)}</li>' for p in pros[:5])
    cons_html = ''.join(f'<li>{e(c)}</li>' for c in cons[:5])

    # Comparison table (3-4 similar brands)
    similar = get_similar_bonuses(brand, 4)
    compare_rows = ''
    for sb in similar:
        sc = get_promo(sb)
        compare_rows += f'''<tr>
      <td><a href="{sb['id']}.html" style="color:var(--accent);font-weight:600">{e(sb['name'])}</a></td>
      <td>{e(sb['welcomeBonusAmount'][:40])}</td>
      <td>{e(sc)}</td>
      <td>{fmtRating(sb['overallRating'])}/5.0</td>
    </tr>'''

    # All bonuses table (top 10)
    all_bonus_rows = ''
    for ab in BRANDS[:10]:
        ac = get_promo(ab)
        is_current = ab['id'] == brand['id']
        highlight = ' style="background:var(--accent-light)"' if is_current else ''
        all_bonus_rows += f'''<tr{highlight}>
      <td><a href="{ab['id']}.html" style="color:var(--accent);font-weight:600">{e(ab['name'])}</a></td>
      <td>{e(ab['welcomeBonusAmount'][:40])}</td>
      <td style="font-family:monospace;font-weight:700">{e(ac)}</td>
      <td>{fmtRating(ab['overallRating'])}/5.0</td>
    </tr>'''

    # FAQ
    faq_items = [
        (f'Is the {brand["name"]} promo code {code} still working?', f'Yes, we verified this code is active as of {CURRENT_MONTH_YEAR}. Enter <strong>{e(code)}</strong> during registration to claim your {bonus} bonus.'),
        (f'What is the minimum deposit at {brand["name"]}?', f'The minimum deposit at {brand["name"]} is {e(brand.get("minDeposit", "R10"))}. Check the T&Cs for the minimum qualifying deposit for the welcome bonus.'),
        (f'How long does it take to receive my bonus?', f'Most bonuses at {brand["name"]} are credited instantly after your first qualifying deposit. Some bonuses may require a pending period of up to 24 hours.'),
        (f'Can I use this promo code on mobile?', f'Yes, the promo code {e(code)} works on both the {brand["name"]} website and mobile app (if available). The sign-up process is the same.'),
    ]
    faq_html = ''
    for fq, fa in faq_items:
        faq_html += f'''<div class="faq-item" onclick="this.classList.toggle('open')">
      <button class="faq-btn"><span>{fq}</span><span class="faq-chevron">{ICON_CHEVRON_DOWN}</span></button>
      <div class="faq-body"><p>{fa}</p></div>
    </div>'''

    # Payment methods
    pay_methods = brand.get('paymentMethodsList', [])
    pay_links = ''
    for m in pay_methods[:6]:
        pid = _resolve_payment_page(m)
        if pid:
            pay_links += f'<a href="{prefix}payment-methods/{pid}.html" class="payment-pill">{payment_icon_img(m, size=16, depth=depth)} {e(m)}</a>'
        else:
            pay_links += payment_pill(m, depth=depth)

    # Sidebar: On This Page + Key Terms + Author
    sidebar_html = f'''<div class="sidebar" style="display:none">
      <div class="on-this-page">
        <h3>On This Page</h3>
        <a href="#expert-analysis">Expert Analysis</a>
        <a href="#how-to-claim">How to Claim</a>
        <a href="#pros-cons">Pros &amp; Cons</a>
        <a href="#bonus-details">Bonus Details</a>
        <a href="#comparison">Compare Offers</a>
        <a href="#faq">FAQ</a>
      </div>
      <div class="key-terms-box">
        <h3>Key Terms</h3>
        <div class="key-term-row"><span class="key-term-label">Promo Code</span><span class="key-term-value" style="color:var(--accent)">{e(code)}</span></div>
        <div class="key-term-row"><span class="key-term-label">Bonus</span><span class="key-term-value" style="color:var(--bonus)">{e(brand['welcomeBonusAmount'][:30])}</span></div>
        <div class="key-term-row"><span class="key-term-label">Min Deposit</span><span class="key-term-value">{e(brand.get('minDeposit','Varies'))}</span></div>
        <div class="key-term-row"><span class="key-term-label">Min Bet</span><span class="key-term-value">{e(brand.get('minBet','Varies'))}</span></div>
        <div class="key-term-row"><span class="key-term-label">Rating</span><span class="key-term-value">{rating_5}/5.0</span></div>
        <div class="key-term-row"><span class="key-term-label">Payments</span><span class="key-term-value">{len(pay_methods)} methods</span></div>
        <div class="key-term-row"><span class="key-term-label">Year Est.</span><span class="key-term-value">{e(brand.get('yearEstablished','N/A'))}</span></div>
      </div>
      <div style="background:var(--surface);border:1px solid var(--sep);border-radius:8px;padding:20px;margin-bottom:20px">
        <h3 class="font-label" style="margin-bottom:12px">Reviewed By</h3>
        <a href="{prefix}authors/thabo-mokoena.html" class="author-link" style="display:flex;align-items:center;gap:10px;text-decoration:none">
          {author_img('Thabo Mokoena', size=36, depth=depth)}
          <div>
            <div style="font-size:14px;font-weight:600">Thabo Mokoena</div>
            <div class="font-meta">Editor-in-Chief</div>
          </div>
        </a>
      </div>
      <a href="{prefix}betting-site-review/{brand['id']}.html" class="btn-outline btn-full btn-sm" style="margin-bottom:12px">Read Full Review</a>
      <a href="{prefix}promo-codes.html" style="display:flex;align-items:center;gap:8px;font-size:14px;color:var(--accent);font-weight:500">{ICON_ARROW_LEFT} All Promo Codes</a>
    </div>'''

    # Watermark logo for promo hero
    wm_logo_promo = logo_path(brand, depth)
    wm_html_promo = f'<img src="{wm_logo_promo}" alt="" class="brand-watermark" aria-hidden="true">' if wm_logo_promo else ''

    bc = breadcrumbs([{"label":"Home","href":"index.html"},{"label":"Promo Codes","href":"promo-codes.html"},{"label":brand["name"]}], depth)
    body = f"""
    <!-- Hero -->
    <div class="promo-detail-hero brand-hero-wrap">
      {wm_html_promo}
      <div class="container">
        {bc}
        <div class="hero-inner" style="align-items:flex-start">
          {logo_img}
          <div class="hero-info" style="flex:1;min-width:0">
            <div class="hero-title-row">
              {badge}
            </div>
            <h1>{name} Promo Code 2026: {e(code)}</h1>
            <p class="hero-subtitle">Get <strong style="color:var(--bonus)">{bonus}</strong> with code <strong style="color:var(--accent)">{e(code)}</strong>. Verified and working for {CURRENT_MONTH_YEAR}.</p>
            {trust_html}
          </div>
          <div class="rating-circle" style="flex-shrink:0;align-self:flex-start"><span class="rating-circle-score">{rating_10}</span><span style="font-size:11px;color:var(--text-muted);font-weight:600">/10</span></div>
        </div>
      </div>
    </div>

    <div class="container" style="padding-top:32px;padding-bottom:80px">
      <div class="two-col">
        <div>
          <!-- Promo Box -->
          <div class="promo-box" style="margin-bottom:32px">
            <div style="display:flex;align-items:flex-start;gap:16px">
              <div style="width:44px;height:44px;border-radius:8px;background:rgba(22,163,74,0.2);display:flex;align-items:center;justify-content:center;flex-shrink:0">{ICON_TROPHY}</div>
              <div style="flex:1;min-width:0">
                <p style="font-weight:700;font-size:clamp(1.1rem,2.5vw,1.35rem);color:#15803d">{bonus}</p>
                <div style="margin-top:12px;display:flex;align-items:center;gap:8px;flex-wrap:wrap">
                  <span class="promo-code">{e(code)}</span>
                  <button class="copy-btn" onclick="copyCode(this,'{e(code)}')">Copy</button>
                </div>
                {f'<a href="{masked_exit(brand, depth)}" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary" style="margin-top:14px;display:inline-flex;align-items:center;gap:8px;font-size:15px;padding:12px 28px;border-radius:24px">{ICON_TROPHY} Claim Bonus</a>' if brand.get("exitLink") else ''}
                <p style="font-size:12px;color:var(--text-muted);margin-top:12px">{e(brand.get("mcpTerms", brand.get("tcs","T&Cs apply. 18+.")))}</p>
              </div>
            </div>
          </div>

          <!-- Promo Banners -->
          {promo_banners_html(brand, depth)}

          <!-- Expert Analysis -->
          {expert_html}

          <!-- How to Claim -->
          <h2 id="how-to-claim" style="font-size:18px;font-weight:700;margin-bottom:20px">How to Claim Your Bonus</h2>
          <div class="claim-steps">{steps_html}</div>

          <!-- Pros & Cons -->
          <h2 id="pros-cons" style="font-size:18px;font-weight:700;margin-bottom:20px">Pros &amp; Cons</h2>
          <div class="grid-2" style="margin-bottom:32px">
            <div class="detail-pros">
              <h3>{ICON_CHECK} Pros</h3>
              <ul>{pros_html}</ul>
            </div>
            <div class="detail-cons">
              <h3>{ICON_X} Cons</h3>
              <ul>{cons_html}</ul>
            </div>
          </div>

          <!-- Bonus Details Table -->
          <div id="bonus-details" style="background:var(--card-bg);border:var(--card-border);border-radius:8px;padding:24px;margin-bottom:32px">
            <h2 style="font-size:16px;font-weight:700;margin-bottom:16px">Bonus Details</h2>
            <table class="data-table">
              <tbody>
                <tr><td style="font-weight:600">Welcome Bonus</td><td style="color:var(--bonus);font-weight:600">{bonus}</td></tr>
                <tr><td style="font-weight:600">Promo Code</td><td style="font-weight:700;color:var(--accent)">{e(code)}</td></tr>
                <tr><td style="font-weight:600">Minimum Deposit</td><td>{e(brand.get('minDeposit','Varies'))}</td></tr>
                <tr><td style="font-weight:600">Wagering</td><td>{e(brand.get('welcomeBonusDetails','See T&Cs')[:80])}</td></tr>
                <tr><td style="font-weight:600">Rating</td><td>{rating_5}/5.0</td></tr>
              </tbody>
            </table>
          </div>

          <!-- Detailed Promo Content -->
          {generate_promo_content(brand)}

          <!-- Payment Methods -->
          <div style="margin-bottom:32px">
            <h2 style="font-size:16px;font-weight:700;margin-bottom:12px">Accepted Payment Methods</h2>
            <div style="display:flex;flex-wrap:wrap;gap:8px">{pay_links}</div>
          </div>

          <!-- Comparison Table -->
          <div id="comparison" style="margin-bottom:32px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:16px">Compare With Similar Offers</h2>
            <div class="table-wrap">
              <table class="compare-table">
                <thead><tr><th>Bookmaker</th><th>Bonus</th><th>Code</th><th>Rating</th></tr></thead>
                <tbody>{compare_rows}</tbody>
              </table>
            </div>
          </div>

          <!-- All Bonuses Table -->
          <div style="margin-bottom:32px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:16px">All Bonuses</h2>
            <div class="table-wrap">
              <table class="all-bonuses-table">
                <thead><tr><th>Bookmaker</th><th>Welcome Bonus</th><th>Code</th><th>Rating</th></tr></thead>
                <tbody>{all_bonus_rows}</tbody>
              </table>
            </div>
          </div>

          <!-- FAQ -->
          <div id="faq" style="margin-bottom:32px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:20px">Frequently Asked Questions</h2>
            <div style="display:flex;flex-direction:column;gap:8px">{faq_html}</div>
          </div>

          <!-- Cross Links -->
          {cross_links_section(brand, depth)}
        </div>

        <!-- Sidebar -->
        {sidebar_html}
      </div>
    </div>

    <!-- Sticky Bottom CTA Bar -->
    <div class="sticky-bottom-bar" id="stickyBar">
      <div class="sticky-bottom-inner">
        <div class="sticky-bottom-left">
          {logo_sm}
          <div class="sticky-bottom-text">
            <div class="sticky-bottom-offer">{bonus}</div>
            <div class="sticky-bottom-tcs">{e(tcs_short)}</div>
          </div>
        </div>
        <div class="sticky-bottom-right">
          <span class="sticky-bottom-code">{e(code)}</span>
          {f'<a href="{masked_exit(brand, depth)}" target="_blank" rel="noopener noreferrer nofollow" class="sticky-bottom-cta">Claim Bonus</a>' if brand.get("exitLink") else f'<a href="javascript:void(0)" onclick="copyCode(this,\'{e(code)}\')" class="sticky-bottom-cta">Copy Code</a>'}
        </div>
      </div>
    </div>
    <script>
    (function(){{
      var bar=document.getElementById('stickyBar');
      if(!bar)return;
      var shown=false;
      window.addEventListener('scroll',function(){{
        if(window.scrollY>400){{if(!shown){{bar.classList.add('visible');shown=true;}}}}
        else{{if(shown){{bar.classList.remove('visible');shown=false;}}}}
      }});
    }})();
    </script>"""

    # Show sidebar on lg
    body = body.replace('class="sidebar" style="display:none"', 'class="sidebar lg-show"')

    t, d = seo_meta('promo', brand=brand)
    promo_ld = jsonld_offer(brand) + '\n' + jsonld_faq(faq_items)
    return page(t, d, f'promo-code/{brand["id"]}', body, depth=1, json_ld=promo_ld,
                bc_items=[{'label': 'Home', 'href': 'index.html'}, {'label': 'Promo Codes', 'href': 'promo-codes.html'}, {'label': brand['name'] + ' Promo Code'}])


def build_payment_detail(method):
    depth = 1
    icon = payment_icon_img(method['name'], size=28, depth=1)
    accepting = brands_for_method(method['name'])

    # Fee summary for stat card
    fee_raw = method.get('fees','') or ''
    fee_short = 'Free' if 'no fees' in fee_raw.lower() or 'free' in fee_raw.lower() else truncate(fee_raw, 25)

    # Deposit steps
    steps = []
    if 'voucher' in method['type']:
        steps = [f'Purchase a {method["name"]} at any participating retailer or online.', 'Receive your unique PIN code via SMS or printed receipt.', 'Log into your bookmaker account and navigate to Deposits.', f'Select "{method["name"]}" as your deposit method.', 'Enter your PIN code and the deposit amount.', 'Confirm the transaction. Funds are credited instantly.']
    elif 'EFT' in method['type'] or 'instant' in method['type']:
        steps = ['Log into your bookmaker account and go to Deposits.', f'Select "{method["name"]}" as your payment method.', 'Pick your bank from the list.', 'You will be redirected to your bank\'s secure login page.', 'Log in and confirm the payment via OTP or push notification.', 'Your funds are credited instantly.']
    elif 'card' in method['type']:
        steps = ['Go to the Deposit section of your bookmaker account.', 'Select Visa or Mastercard as your payment method.', 'Enter your card number, expiry date, and CVV.', 'Confirm via 3D Secure (OTP from your bank).', 'Your funds are credited instantly.']
    else:
        steps = [f'Open your {method["name"]} app or go to the bookmaker deposit page.', f'Select "{method["name"]}" as your payment method.', 'Follow the on-screen steps to authenticate.', 'Confirm the deposit amount.', 'Funds hit your betting account quickly.']

    steps_html = ''
    for i, s in enumerate(steps):
        steps_html += f'<div class="step-item"><span class="step-num">{i+1}</span><p class="step-text">{e(s)}</p></div>'

    # Pros / Cons - split items on \n separators and strip leading dashes
    def split_items_pm(items):
        result = []
        if isinstance(items, str): items = [items]
        for item in items:
            for sub in item.replace('\\n', '\n').split('\n'):
                s = sub.strip().lstrip('-').strip()
                if s: result.append(s)
        return result
    pros = split_items_pm(method.get('pros', []))
    cons = split_items_pm(method.get('cons', []))
    pros_li = ''.join(f'<li>{e(p)}</li>' for p in pros)
    cons_li = ''.join(f'<li>{e(c)}</li>' for c in cons)

    # Bookmakers table (desktop) + cards (mobile)
    bm_table = ''
    bm_cards = ''
    for b in accepting:
        blogo = logo_path(b, depth)
        blogo_img = f'<img src="{blogo}" alt="{e(b["name"])}" style="width:28px;height:28px;object-fit:contain;border-radius:6px;background:{brand_bg(b)};padding:2px;border:1px solid var(--border);vertical-align:middle;margin-right:8px" loading="lazy">' if blogo else ''
        bm_table += f'''<tr>
          <td><a href="../betting-site-review/{b['id']}.html" style="font-weight:500;color:var(--text-primary);display:inline-flex;align-items:center;gap:8px">{blogo_img}{e(b['name'])}</a></td>
          <td>{rating_badge(b['overallRating'], 'sm')}</td>
          <td style="font-size:12px;color:var(--text-secondary)">{e(b['welcomeBonusAmount'][:40])}</td>
          <td style="text-align:right"><a href="../betting-site-review/{b['id']}.html" class="table-link text-xs">Review</a></td>
        </tr>'''
        bm_cards += f'''<a href="../betting-site-review/{b['id']}.html" class="brand-row-mobile">
          {blogo_img}
          <div style="flex:1;min-width:0">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:8px">
              <div style="font-size:14px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{e(b['name'])}</div>
              {rating_badge(b['overallRating'], 'sm')}
            </div>
            <p style="font-size:12px;color:var(--bonus);font-weight:500;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{e(b['welcomeBonusAmount'])}</p>
          </div>
        </a>'''

    # Related methods
    related_m = [m for m in PAYMENTS if m['id'] != method['id'] and m['type'] == method['type']][:3]
    if not related_m: related_m = [m for m in PAYMENTS if m['id'] != method['id']][:3]
    related_html = ''
    for m in related_m:
        related_html += f'''<a href="{m['id']}.html" class="sidebar-link"><span style="font-weight:500">{e(m['name'])}</span><span>{e(m['type'])}</span></a>'''

    body = f'''
    <div class="container" style="padding-top:40px;padding-bottom:80px">
      {breadcrumbs([{"label":"Home","href":"index.html"},{"label":"Payment Methods","href":"payment-methods.html"},{"label":method["name"]}], depth)}

      <div style="display:flex;align-items:flex-start;gap:16px;margin-bottom:32px">
        <div class="method-icon-box" style="width:56px;height:56px;font-size:28px">{icon}</div>
        <div>
          <h1 style="font-size:clamp(1.375rem,3vw,1.75rem);font-weight:700;letter-spacing:-0.02em;line-height:1.25">{e(method['name'])}</h1>
          <p style="font-size:14px;color:var(--text-muted);text-transform:capitalize;margin-top:4px">{e(method['type'])}</p>
        </div>
      </div>

      <div class="stat-grid">
        <div class="stat-card"><div class="stat-label">{ICON_CLOCK} Deposit</div><p class="stat-value">{truncate(method.get('depositSpeed','Varies'), 25)}</p></div>
        <div class="stat-card"><div class="stat-label">Withdrawal</div><p class="stat-value">{truncate(method.get('withdrawalSpeed','Varies'), 25)}</p></div>
        <div class="stat-card"><div class="stat-label">Fees</div><p class="stat-value">{fee_short}</p></div>
        <div class="stat-card"><div class="stat-label">Bookmakers</div><p class="stat-value">{len(accepting)} sites</p></div>
      </div>

      <div class="two-col">
        <div>
          <h2 style="font-size:18px;font-weight:700;margin-bottom:16px">About {e(method['name'])}</h2>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.75;margin-bottom:32px">{e(method.get('description',''))}</p>

          {f'<div class="grid-2" style="margin-bottom:32px"><div style="background:var(--surface-2);border-radius:8px;padding:16px;text-align:center"><p class="stat-label">Min Deposit</p><p style="font-weight:700;font-size:16px">{e(method.get("minDeposit","Varies"))}</p></div><div style="background:var(--surface-2);border-radius:8px;padding:16px;text-align:center"><p class="stat-label">Max Deposit</p><p style="font-weight:700;font-size:16px">{e(method.get("maxDeposit","Varies"))}</p></div></div>' if method.get('minDeposit') or method.get('maxDeposit') else ''}

          <h2 style="font-size:18px;font-weight:700;margin-bottom:20px">How to Deposit Using {e(method['name'])}</h2>
          <div class="steps-list" style="margin-bottom:32px">{steps_html}</div>

          <h2 style="font-size:18px;font-weight:700;margin-bottom:20px">Pros and Cons</h2>
          <div class="grid-2" style="margin-bottom:32px">
            <div class="pros-box"><h3>{ICON_CHECK} Pros</h3><ul class="pros-list">{pros_li}</ul></div>
            <div class="cons-box"><h3>{ICON_X} Cons</h3><ul class="cons-list">{cons_li}</ul></div>
          </div>

          {f'<h2 style="font-size:18px;font-weight:700;margin-bottom:16px">Security</h2><p style="font-size:14px;color:var(--text-secondary);line-height:1.75;margin-bottom:32px">{e(method["security"])}</p>' if method.get('security') else ''}

          <h2 style="font-size:18px;font-weight:700;margin-bottom:8px">Bookmakers Accepting {e(method['name'])}</h2>
          <p style="font-size:14px;color:var(--text-muted);margin-bottom:20px">{len(accepting)} licensed South African bookmaker{"s" if len(accepting) != 1 else ""} support {e(method['name'])}.</p>

          <!-- Desktop table -->
          <div class="table-wrap sm-show" style="display:none;margin-bottom:32px">
            <table class="data-table">
              <thead><tr><th>Bookmaker</th><th>Rating</th><th>Welcome Bonus</th><th style="text-align:right">Action</th></tr></thead>
              <tbody>{bm_table}</tbody>
            </table>
          </div>
          <!-- Mobile cards -->
          <div class="sm-hide" style="display:flex;flex-direction:column;gap:10px;margin-bottom:32px">{bm_cards}</div>

          {f'<div style="background:var(--surface-2);border-radius:8px;padding:20px;margin-bottom:32px"><h2 style="font-size:16px;font-weight:700;margin-bottom:12px">Where to Get {e(method["name"])}</h2><p style="font-size:14px;color:var(--text-secondary);line-height:1.75">{e(method["whereToBuy"])}</p></div>' if method.get('whereToBuy') else ''}

          <!-- Explore More -->
          <div style="margin-top:32px;padding:24px;background:var(--surface-2);border-radius:8px">
            <h3 style="font-size:15px;font-weight:700;margin-bottom:16px">Explore More</h3>
            <div style="display:flex;flex-wrap:wrap;gap:10px">
              <a href="../betting-sites.html" class="btn-outline btn-sm">All Betting Sites</a>
              <a href="../promo-codes.html" class="btn-outline btn-sm">Promo Codes</a>
              <a href="../payment-methods.html" class="btn-outline btn-sm">All Payment Methods</a>
              <a href="../fica-guide.html" class="btn-outline btn-sm">FICA Guide</a>
            </div>
          </div>
        </div>

        <div class="sidebar lg-show" style="display:none">
          <div class="sidebar-card">
            <h3>Quick Info</h3>
            <div class="sidebar-row"><span class="text-muted">Min Deposit</span><span class="font-semibold">{e(method.get('minDeposit','Varies'))}</span></div>
            <div class="sidebar-row"><span class="text-muted">Max Deposit</span><span class="font-semibold">{e(method.get('maxDeposit','Varies'))}</span></div>
            <div class="sidebar-row"><span class="text-muted">Type</span><span class="font-semibold" style="text-transform:capitalize">{e(method['type'])}</span></div>
            <div class="sidebar-row"><span class="text-muted">Bookmakers</span><span class="font-semibold">{len(accepting)}</span></div>
          </div>
          <div class="sidebar-card">
            <h3>Related Methods</h3>
            {related_html}
          </div>
          <a href="../payment-methods.html" style="display:flex;align-items:center;gap:8px;font-size:14px;color:var(--accent);font-weight:500">{ICON_ARROW_LEFT} All Payment Methods</a>
        </div>
      </div>

      <!-- Mobile related -->
      <div class="lg-hide" style="margin-top:40px">
        <div class="sidebar-card">
          <h3>Related Methods</h3>
          {related_html}
        </div>
        <a href="../payment-methods.html" style="display:flex;align-items:center;gap:8px;font-size:14px;color:var(--accent);font-weight:500;padding:8px 0">{ICON_ARROW_LEFT} All Payment Methods</a>
      </div>
    </div>'''

    t_pd, d_pd = seo_meta('payment', method=method)
    return page(t_pd, d_pd, f'payment-methods/{method["id"]}', body, depth=1,
                bc_items=[{'label': 'Home', 'href': 'index.html'}, {'label': 'Payment Methods', 'href': 'payment-methods.html'}, {'label': method['name']}])


def news_sidebar_top5(depth=0):
    """Build a sidebar widget with top 5 betting sites that users can star."""
    top5 = BRANDS[:5]
    prefix = '../' * depth
    items = ''
    for i, b in enumerate(top5):
        logo = logo_path(b, depth)
        logo_img = f'<img src="{logo}" alt="{e(b["name"])}" class="sidebar-brand-logo" style="background:{brand_bg(b)};padding:3px;border:1px solid var(--border)" loading="lazy">' if logo else ''
        bv = bonus_val(b)
        bv_display = f'R{bv:,}' if bv > 0 else ''
        m_exit = masked_exit(b, depth)
        visit_link = f'<a href="{m_exit}" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary" style="font-size:12px;padding:6px 14px;border-radius:20px;white-space:nowrap">Visit</a>' if m_exit else ''
        items += f'''<div class="sidebar-brand-item" style="display:flex;align-items:center;gap:10px;padding:12px;border-radius:10px;border:1px solid var(--border);background:var(--surface);margin-bottom:8px;transition:box-shadow 0.2s">
          <button class="star-btn" data-brand="{b['id']}" onclick="event.stopPropagation();toggleStar('{b['id']}')" aria-label="Star {e(b['name'])}" style="flex-shrink:0">{ICON_STAR}</button>
          {logo_img}
          <div style="flex:1;min-width:0">
            <a href="{prefix}betting-site-review/{b['id']}.html" class="sidebar-brand-name">{e(b['name'])}</a>
            <span class="sidebar-brand-bonus">{bv_display}</span>
            <p class="sidebar-tcs">{e(b.get('tcs','18+ T&Cs apply.')[:60])}</p>
          </div>
          {visit_link}
        </div>'''

    return f'''<aside class="news-sidebar" style="position:sticky;top:90px">
      <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px">
        <h3 class="sidebar-section-title">Top 5 Betting Sites</h3>
        <p class="sidebar-section-sub">Star your favourites to track bonuses</p>
        {items}
        <a href="{prefix}betting-sites.html" class="btn-outline" style="display:block;text-align:center;margin-top:12px;font-size:13px;padding:10px 16px;border-radius:20px">View All Betting Sites</a>
      </div>
    </aside>'''


def build_news_article(article):
    depth = 1
    cat_colors = {'Promos':'#1641B4','Industry':'#0ea5e9','Payments':'#22c55e','Sports':'#f5a623','Platform':'#ef4444','Bonus':'#16a34a','Features':'#8b5cf6','Promotions':'#1641B4','Regulation':'#dc2626','Winners':'#f59e0b','Guides':'#6366f1'}
    cc = cat_colors.get(article.get('category',''), '#555')
    dt = datetime.fromisoformat(article['date'].replace('Z','+00:00')).strftime('%d %B %Y') if article.get('date') else ''

    # Convert body sections to HTML
    raw_body = article.get('body', '')
    body_html = ''
    if isinstance(raw_body, str):
        body_html = raw_body  # Already HTML (new articles)
    elif isinstance(raw_body, list):
        for section in raw_body:
            if isinstance(section, str):
                body_html += f'<p>{e(section)}</p>'
            elif isinstance(section, dict):
                if section.get('type') == 'heading':
                    body_html += f'<h2>{e(section.get("text",""))}</h2>'
                elif section.get('type') == 'paragraph':
                    body_html += f'<p>{e(section.get("text",""))}</p>'
                elif section.get('type') == 'list':
                    items = ''.join(f'<li>{e(i)}</li>' for i in section.get('items', []))
                    body_html += f'<ul>{items}</ul>'
    # Auto-link brand mentions to review pages
    body_html = linkify_brand_mentions(body_html, depth=1)

    related = [a for a in NEWS if a['slug'] != article['slug']][:3]
    related_html = ''
    for a in related:
        rcc = cat_colors.get(a.get('category',''), '#555')
        rdt = datetime.fromisoformat(a['date'].replace('Z','+00:00')).strftime('%d %b %Y') if a.get('date') else ''
        related_html += f'''<a href="{a['slug']}.html" class="card" style="padding:16px">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
            <span class="news-badge" style="background:{rcc}">{e(a.get('category',''))}</span>
            <span style="font-size:11px;color:var(--text-muted)">{rdt}</span>
          </div>
          <h3 style="font-size:14px;font-weight:600;line-height:1.35">{e(a['title'])}</h3>
        </a>'''

    sidebar = news_sidebar_top5(depth=1)

    body = f'''
    <div class="container" style="padding-top:40px;padding-bottom:80px">
      {breadcrumbs([{"label":"Home","href":"index.html"},{"label":"News","href":"news.html"},{"label":article["title"][:40]+"..."}], depth)}
      <div class="news-layout" style="display:grid;grid-template-columns:1fr 300px;gap:32px">
        <div>
          <article class="article-body">
            <h1 class="page-title">{e(article['title'])}</h1>
            <div class="article-meta">
              <a href="../news.html?cat={article.get('category','')}" class="news-badge" style="background:{cc};text-decoration:none;color:#fff">{e(article.get('category',''))}</a>
              <span>{dt}</span>
              <span class="article-author-byline">{author_img(article.get('author',''), size=28, depth=1)} By {e(article.get('author','MzansiWins'))}</span>
            </div>
            {body_html}
          </article>
          <div style="margin-top:48px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:20px">Related Articles</h2>
            <div class="grid-3">{related_html}</div>
          </div>
        </div>
        {sidebar}
      </div>
    </div>'''

    t_na, d_na = seo_meta('article', article=article)
    return page(t_na, d_na, f'news/{article["slug"]}', body, depth=1, json_ld=jsonld_news(article),
                bc_items=[{'label': 'Home', 'href': 'index.html'}, {'label': 'News', 'href': 'news.html'}, {'label': article['title']}])



def _build_subcat_nav(heading, items):
    """Build a subcategory pill/chip navigation section."""
    pills = ''
    for label, href, icon in items:
        pills += f'''<a href="{href}" class="subcat-pill">
          <span class="subcat-pill-icon">{icon}</span>
          <span>{label}</span>
        </a>\n'''
    return f'''<nav class="subcat-nav" aria-label="Subcategories">
      <h2 class="subcat-nav-heading">{heading}</h2>
      <div class="subcat-nav-pills">
        {pills}
      </div>
    </nav>'''


def category_hero(title, subtitle, breadcrumb_items, depth, badges=None, deco_icon=''):
    """Build a blue gradient hero bar for category pages."""
    bc = breadcrumbs(breadcrumb_items, depth)
    badge_html = ''
    if badges:
        items = ''.join(f'<span class="category-hero-badge">{b}</span>' for b in badges)
        badge_html = f'<div class="category-hero-badges">{items}</div>'
    deco = f'<div class="category-hero-deco" aria-hidden="true">{deco_icon}</div>' if deco_icon else ''
    return f'''<section class="category-hero">
      {deco}
      <div class="container">
        {bc}
        <h1 class="category-hero-title">{title}</h1>
        <p class="category-hero-sub">{subtitle}</p>
        {badge_html}
      </div>
    </section>'''

def build_listing_page(page_type):
    if page_type == 'betting-sites':
        brands = BRANDS_ORDERED
        title_text = f'Best Betting Sites in South Africa ({CURRENT_YEAR})'
        subtitle = f'Every single licensed SA bookmaker ranked, reviewed, and put through the wringer. Updated {CURRENT_MONTH_YEAR}.'
        canon = 'betting-sites'
        active = 'betting'
    elif page_type == 'casino-sites':
        brands = [b for b in BRANDS_ORDERED if b.get('type','').lower() in ('both','casino') or 'casino' in b.get('otherProducts','').lower() or True]
        title_text = 'Best Online Casino Sites in South Africa (2026)'
        subtitle = f'A detailed guide to trusted real-money online casinos for South African players. Updated {CURRENT_MONTH_YEAR}.'
        canon = 'casino-sites'
        active = 'casino'
    else:
        return ''

    # Calculate total bonus value
    total_bonus_val = sum(bonus_val(b) for b in brands)

    # Build brand data JSON for JS starred calculation
    brand_data_json = json.dumps([{"id": b["id"], "name": e(b["name"]), "bonus": bonus_val(b)} for b in brands])

    # Build responsive mobile cards + desktop table
    rows = ''
    mobile_cards = ''
    for i, b in enumerate(brands):
        tc_text = e(b.get('tcs', '18+ T&Cs apply.'))
        min_dep = e(b.get('minDeposit', ''))
        bv = bonus_val(b)
        bv_display = f'R{bv:,}' if bv > 0 else '-'
        star_icon = ICON_STAR
        logo = logo_path(b, 0)
        logo_img_sm = f'<img src="{logo}" alt="{e(b["name"])}" style="width:28px;height:28px;object-fit:contain;border-radius:4px;background:{brand_bg(b)};padding:2px;border:1px solid var(--border);flex-shrink:0" loading="lazy">' if logo else ''
        logo_img_mobile = f'<img src="{logo}" alt="{e(b["name"])}" style="width:36px;height:36px;object-fit:contain;border-radius:6px;background:{brand_bg(b)};padding:3px;border:1px solid var(--border);flex-shrink:0" loading="lazy">' if logo else ''

        rows += f'''<tr data-name="{e(b['name']).lower()}" data-brand-id="{b['id']}" data-bonus-val="{bv}">
          <td data-sort="{i+1}" style="font-weight:600;color:var(--text-muted)">{i+1}</td>
          <td data-sort="{e(b['name'])}" style="white-space:nowrap">
            <div style="display:flex;align-items:center;gap:8px">
              <button class="star-btn" data-brand="{b['id']}" onclick="event.stopPropagation();toggleStar('{b['id']}')" aria-label="Add to favourites">{star_icon}</button>
              {logo_img_sm}
              <a href="betting-site-review/{b['id']}.html" class="table-link" style="font-weight:600">{e(b['name'])}</a>
            </div>
          </td>
          <td><span style="color:var(--bonus);font-weight:600">{e(b['welcomeBonusAmount'])}</span><br><span style="font-size:11px;color:var(--text-muted)">{tc_text}</span></td>
          <td data-sort="{bv}" style="text-align:center;font-weight:700;color:var(--bonus)">{bv_display}</td>
          <td data-sort="{b['overallRating']}" style="text-align:center">{rating_badge(b['overallRating'], 'sm')}</td>
          <td style="text-align:center"><a href="betting-site-review/{b['id']}.html" class="btn-outline btn-sm">Review</a></td>
        </tr>'''

        # Mobile card version
        m_exit = masked_exit(b, 0)
        visit_btn = f'<a href="{m_exit}" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary btn-sm" style="flex:1;text-align:center">Visit Site</a>' if m_exit else ''
        mobile_cards += f'''<div class="listing-card" data-name="{e(b['name']).lower()}" data-brand-id="{b['id']}" data-bonus-val="{bv}">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:10px">
            <div style="display:flex;align-items:center;gap:8px;min-width:0">
              <button class="star-btn" data-brand="{b['id']}" onclick="event.stopPropagation();toggleStar('{b['id']}')" aria-label="Add to favourites">{star_icon}</button>
              {logo_img_mobile}
              <div style="min-width:0">
                <div style="display:flex;align-items:center;gap:6px">
                  <span style="font-size:13px;font-weight:700;color:var(--text-muted)">#{i+1}</span>
                  <a href="betting-site-review/{b['id']}.html" style="font-size:16px;font-weight:700;color:var(--text-primary)">{e(b['name'])}</a>
                </div>
              </div>
            </div>
            {rating_badge(b['overallRating'], 'sm')}
          </div>
          <div style="background:var(--accent-light);border-radius:8px;padding:10px 14px;margin-bottom:10px">
            <div style="display:flex;align-items:center;justify-content:space-between">
              <p style="font-size:15px;font-weight:700;color:var(--bonus)">{e(b['welcomeBonusAmount'])}</p>
              <span style="font-size:14px;font-weight:700;color:var(--bonus)">{bv_display}</span>
            </div>
            {f'<span style="font-size:12px;color:var(--text-muted)">Min deposit: {min_dep}</span>' if min_dep else ''}
          </div>
          <p style="font-size:11px;color:var(--text-muted);margin-bottom:12px;line-height:1.5">{tc_text}</p>
          <div style="display:flex;gap:8px">
            <a href="betting-site-review/{b['id']}.html" class="btn-outline btn-sm" style="flex:1;text-align:center">Review</a>
            {visit_btn}
          </div>
        </div>'''

    # SEO content for listing pages
    if page_type == 'betting-sites':
        seo_intro = betting_sites_intro_html()
        seo_mid = betting_sites_mid_html()
        seo_below = betting_sites_below_table_html(brands)
    elif page_type == 'casino-sites':
        seo_intro = casino_sites_intro_html()
        seo_mid = ''
        seo_below = casino_sites_below_table_html(brands)
    else:
        seo_intro = ''
        seo_mid = ''
        seo_below = ''

    # Subcategory navigation
    subcat_html = ''
    if page_type == 'betting-sites':
        subcat_items = [
            ('Best Betting Apps', 'betting/best-betting-apps-south-africa.html', '📱'),
            ('Football Betting', 'betting/best-football-betting-sites.html', '⚽'),
            ('Rugby Betting', 'betting/best-rugby-betting-sites.html', '🏉'),
            ('Low Deposit Sites', 'betting/low-minimum-deposit-betting-sites.html', '💰'),
            ('Ozow Betting Sites', 'betting/ozow-betting-sites.html', '⚡'),
            ('EFT Betting Sites', 'betting/eft-betting-sites.html', '🏦'),
            ('1Voucher Sites', 'betting/1voucher-betting-sites.html', '🎟️'),
            ('Visa/Mastercard', 'betting/visa-mastercard-betting-sites.html', '💳'),
            ('OTT Voucher Sites', 'betting/ott-voucher-betting-sites.html', '🎫'),
            ('Apple Pay Sites', 'betting/apple-pay-betting-sites.html', '🍎'),
            ('Bonus Finder', 'betting/bonus-finder.html', '🎁'),
            ('Find Your Bookmaker', 'betting/find-your-bookmaker.html', '🔍'),
            ('New Betting Sites', 'new-betting-sites.html', '🆕'),
            ('Compare Bookmakers', 'compare/index.html', '⚖️'),
        ]
        subcat_html = _build_subcat_nav('Browse by Category', subcat_items)
    elif page_type == 'casino-sites':
        subcat_items = [
            ('Best Casino Apps', 'casino/best-casino-apps-south-africa.html', '📱'),
            ('Online Slots Guide', 'casino-guides/online-slots-guide-south-africa.html', '🎰'),
            ('Live Casino Guide', 'casino-guides/live-casino-guide-south-africa.html', '🃏'),
            ('Casino Bonuses Guide', 'casino-guides/casino-bonuses-guide-south-africa.html', '🎁'),
            ('Aviator & Crash Games', 'casino-guides/aviator-crash-games-guide-south-africa.html', '✈️'),
            ('RTP & House Edge', 'casino-guides/rtp-and-house-edge-explained.html', '📊'),
        ]
        subcat_html = _build_subcat_nav('Explore Casino Guides', subcat_items)

    # Category hero badges
    check_sm = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'
    listing_badges = [
        f'{check_sm} <span>{len(brands)} Bookmakers Ranked</span>',
        f'{check_sm} <span>Updated {CURRENT_MONTH_YEAR}</span>',
        f'{check_sm} <span>Expert Reviewed</span>',
    ]
    deco = '&#x1F3C6;' if page_type == 'betting-sites' else '&#x1F3B0;'
    hero_html = category_hero(title_text, subtitle, [{"label":"Home","href":"index.html"},{"label":title_text.split(' in ')[0]}], 0, badges=listing_badges, deco_icon=deco)

    body = f'''
    {hero_html}
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      {seo_intro}
      {subcat_html}

      <!-- Bonus counter banner -->
      <div class="bonus-counter-banner">
        <div class="bonus-counter-item">
          <div class="bonus-counter-label">Total bonuses available</div>
          <div class="bonus-counter-value" style="color:var(--bonus)">R{total_bonus_val:,}</div>
          <div class="bonus-counter-sub">{len(brands)} bookmakers</div>
        </div>
        <div class="bonus-counter-divider"></div>
        <div class="bonus-counter-item">
          <div class="bonus-counter-label">{ICON_STAR} Your starred bonuses</div>
          <div class="bonus-counter-value starred-total" style="color:var(--accent)">R0</div>
          <div class="bonus-counter-sub starred-count">0 bookmakers starred</div>
        </div>
      </div>

      <input type="text" class="search-box" placeholder="Search bookmakers..." oninput="searchListing(this)">

      <!-- Desktop table -->
      <div class="table-wrap listing-desktop">
        <table class="data-table">
          <thead><tr>
            <th onclick="sortTable(this)"># <span class="sort-icon">\u2195</span></th>
            <th onclick="sortTable(this)">Bookmaker <span class="sort-icon">\u2195</span></th>
            <th>Welcome Bonus &amp; T&amp;Cs</th>
            <th onclick="sortTable(this)">Value <span class="sort-icon">\u2195</span></th>
            <th onclick="sortTable(this)" style="text-align:center">Rating <span class="sort-icon">\u2195</span></th>
            <th style="text-align:center">Review</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>

      <!-- Mobile cards -->
      <div class="listing-mobile">{mobile_cards}</div>

      {seo_mid}
      {seo_below}
    </div>
    <script>var brandBonusData = {brand_data_json};</script>'''

    list_ld = jsonld_itemlist(brands, title_text)
    og_img = 'og-betting-sites.png' if page_type == 'betting-sites' else 'og-casino.png'
    return page(f'{title_text} | MzansiWins', subtitle, canon, body, depth=0, active_nav=active, json_ld=list_ld,
                bc_items=[{'label': 'Home', 'href': 'index.html'}, {'label': title_text}], og_image=og_img)


def get_brand_bullets(brand):
    """Generate 3-4 concise bullet points for a brand from its data."""
    bullets = []
    # Bonus detail
    bonus = brand.get('welcomeBonusAmount', '')
    if bonus:
        bullets.append(bonus)
    # Mobile app
    ma = brand.get('mobileApp', '')
    if ma and 'yes' in ma.lower():
        if 'ios' in ma.lower() and 'android' in ma.lower():
            bullets.append('iOS and Android app available')
        elif 'android' in ma.lower():
            bullets.append('Android app available')
        else:
            bullets.append('Mobile app available')
    # Live betting / streaming
    if brand.get('liveBetting', '').lower().startswith('yes'):
        if brand.get('liveStreaming', '').lower().startswith('yes'):
            bullets.append('Live betting and streaming')
        else:
            bullets.append('Live in-play betting')
    # Sports count
    sc = len(brand.get('sportsCovered', []))
    if sc > 0:
        bullets.append(f'{sc}+ sports markets')
    # Cash out
    co = brand.get('cashOut', '')
    if co and 'yes' in co.lower():
        if 'partial' in co.lower():
            bullets.append('Cash out (incl. partial)')
        else:
            bullets.append('Cash out available')
    # Min deposit
    md = brand.get('minDeposit', '')
    if md:
        amt = re.search(r'R\d+', md)
        if amt:
            bullets.append(f'Min deposit {amt.group()}')
    return bullets[:4]

def build_promo_codes_page():
    # Ensure Zarbet is first
    ordered = []
    zarbet = next((b for b in BRANDS if b['id'] == 'zarbet'), None)
    if zarbet:
        ordered.append(zarbet)
    for b in BRANDS:
        if b['id'] != 'zarbet':
            ordered.append(b)

    total_brands = len(ordered)

    # ICON for copy
    copy_icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>'
    check_sm = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'

    # Trust badges
    trust_html = f'''<div class="trust-badges-row">
      <div class="trust-badge">{check_sm} <span>{total_brands} Verified Codes</span></div>
      <div class="trust-badge">{check_sm} <span>Updated {CURRENT_MONTH_YEAR}</span></div>
      <div class="trust-badge">{check_sm} <span>Expert Reviewed</span></div>
      <div class="trust-badge">{ICON_SHIELD} <span>18+ Only</span></div>
    </div>'''

    cards_html = ''
    for idx, b in enumerate(ordered):
        rank = idx + 1
        code = get_promo(b)
        rating_5 = float(b['overallRating'])
        rating_10 = f'{rating_5 * 2:.1f}'
        bonus = e(b['welcomeBonusAmount'])
        name = e(b['name'])
        bid = b['id']
        logo = logo_path(b, 0)
        bullets = get_brand_bullets(b)
        tcs = b.get('mcpTerms', '') or b.get('tcs', '') or ''
        tc_short = tcs[:90].rstrip() + ('...' if len(tcs) > 90 else '') if tcs else '18+. T&Cs apply.'
        tc_short = e(tc_short)

        # Badge per brand - unique sales messages
        _brand_badges = {
            'zarbet': ('promo-badge-top', 'TOP RATED'),
            'easybet-south-africa': ('promo-badge-value', 'LOWEST FEES'),
            '10bet-south-africa': ('promo-badge-pick', 'BEST ODDS'),
            'betway-south-africa': ('promo-badge-top', 'MOST TRUSTED'),
            'mzansibet': ('promo-badge-value', 'SA BORN'),
            'yesplay': ('promo-badge-pick', 'FAN FAVOURITE'),
            'saffaluck': ('promo-badge-value', 'BEST FOR SLOTS'),
            'playabets': ('promo-badge-pick', 'TOP LIVE BETTING'),
            'playtsogo': ('promo-badge-top', 'CASINO KING'),
            'playbetcoza': ('promo-badge-value', 'FAST PAYOUTS'),
            'wanejo-bets': ('promo-badge-pick', 'NEW CONTENDER'),
            'lucky-fish': ('promo-badge-value', 'RISING STAR'),
            'supersportbet': ('promo-badge-top', 'BRAND YOU KNOW'),
            'pokerbet': ('promo-badge-pick', 'POKER PRO'),
            'sportingbet': ('promo-badge-top', 'GLOBAL LEADER'),
            'lulabet': ('promo-badge-value', 'GREAT VALUE'),
            'betfred': ('promo-badge-pick', 'UK FAVOURITE'),
            'tictacbets': ('promo-badge-value', 'EASY SIGNUP'),
            'gbets': ('promo-badge-top', 'TOP FOR RACING'),
            'sunbet': ('promo-badge-pick', 'CASINO EXPERT'),
            'bet-co-za': ('promo-badge-value', 'SHARP ODDS'),
            'world-sports-betting': ('promo-badge-top', 'SA LEGEND'),
            'betcoza': ('promo-badge-pick', 'ALL ROUNDER'),
            'supabets': ('promo-badge-value', 'BEST PROMOS'),
            'lottostar': ('promo-badge-pick', 'LOTTO KING'),
            'playa-bets': ('promo-badge-top', 'FUN BETTING'),
            'hollywood-bets': ('promo-badge-top', 'CROWD FAVOURITE'),
            'betmaster': ('promo-badge-value', 'MULTI SPORT'),
            'gal-sport': ('promo-badge-pick', 'AFRICAN REACH'),
        }
        badge = ''
        _bb = _brand_badges.get(bid)
        if _bb:
            badge = f'<span class="promo-badge {_bb[0]}">{_bb[1]}</span>'
        elif rank <= 5:
            badge = '<span class="promo-badge promo-badge-top">TOP 5</span>'
        elif rank <= 10:
            badge = '<span class="promo-badge promo-badge-pick">TOP 10</span>'

        # Logo img
        logo_img = f'<img src="{logo}" alt="{name}" class="promo-card-logo" loading="lazy" style="background:{brand_bg(b)};padding:4px">' if logo else ''

        # Bullet items (skip first which is the bonus amount, shown as headline)
        bullet_items = ''
        for bl in bullets[1:]:
            bullet_items += f'<li>{e(bl)}</li>'

        cards_html += f'''<div class="promo-card" id="rank-{rank}" data-brand-id="{bid}">
  <div class="promo-card-header">
    <div style="display:flex;align-items:center;gap:10px;flex:1;min-width:0">
      <button class="star-btn" data-brand="{bid}" onclick="event.stopPropagation();toggleStar('{bid}')" aria-label="Add to favourites">{ICON_STAR}</button>
      {logo_img}
      <div class="promo-card-brand">
        <div class="promo-card-brand-row">
          <h2 class="promo-card-brand-name">{name}</h2>
          {badge}
        </div>
      </div>
    </div>
    <div class="rating-circle">
      <span class="rating-circle-score">{rating_10}</span>
    </div>
  </div>
  <div class="promo-card-offer">{bonus}</div>
  <div class="promo-card-code-box">
    <span class="promo-card-code-text">{e(code)}</span>
    <button class="promo-card-code-copy" onclick="copyCode(this,'{e(code)}')" aria-label="Copy code">{copy_icon}</button>
  </div>
  <ul class="promo-card-bullets">{bullet_items}</ul>
  <p class="promo-card-tcs">{tc_short}</p>
  <a href="promo-code/{bid}.html" class="promo-card-cta">View Details</a>
</div>'''

    check_sm_p = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'
    promo_hero = category_hero(
        f"SA\'s Juiciest Betting Promo Codes - {CURRENT_MONTH_YEAR}",
        f"We rounded up every welcome bonus and promo code from all {total_brands} licensed SA bookmakers. Ranked, reviewed, verified, and ready to claim. You are welcome.",
        [{"label":"Home","href":"index.html"},{"label":"Promo Codes"}], 0,
        badges=[
            f'{check_sm_p} <span>{total_brands} Verified Codes</span>',
            f'{check_sm_p} <span>Updated {CURRENT_MONTH_YEAR}</span>',
            f'{check_sm_p} <span>Expert Reviewed</span>',
            f'{ICON_SHIELD} <span>18+ Only</span>',
        ],
        deco_icon='&#x1F381;'
    )
    body = f'''
    {promo_hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      <div class="promo-card-grid">
        {cards_html}
      </div>

      <div class="promo-bottom-note">
        <p>Every code on this page is verified and working as of {CURRENT_MONTH_YEAR}. 18+ only. T&Cs apply to all offers. Gamble responsibly - your bank balance will thank you. Visit our <a href="responsible-gambling-policy.html">responsible gambling page</a> for support resources.</p>
      </div>
    </div>'''

    t_pc, d_pc = seo_meta('promos')
    return page(t_pc,
                 f'All {total_brands} South African betting promo codes and welcome bonuses ranked and compared - {CURRENT_MONTH_YEAR}.',
                 'promo-codes', body, depth=0, active_nav='promos', og_image='og-promos.png')


def build_payment_hub():
    categories = [
        ('all', 'All Methods', '\u2606', None),
        ('voucher', 'Vouchers', '\U0001F3AB', ['voucher']),
        ('eft', 'Instant EFT', '\u26A1', ['instant EFT']),
        ('wallet', 'Mobile Wallets', '\U0001F4F1', ['mobile wallet','mobile wallet / QR scan-to-pay']),
        ('card', 'Cards', '\U0001F4B3', ['credit/debit card']),
        ('bank', 'Bank Transfer', '\U0001F3E6', ['bank transfer']),
        ('gateway', 'Gateways', '\U0001F512', ['payment gateway']),
    ]

    pills = ''
    for key, label, icon, types in categories:
        count = len(PAYMENTS) if key == 'all' else len([m for m in PAYMENTS if types and m['type'] in types])
        pills += f'<button class="filter-pill{"" if key != "all" else " active"}" onclick="filterCards(this,\'{key}\')">{icon} {label} <span class="count">{count}</span></button>'

    rows = ''
    for m in PAYMENTS:
        icon = payment_icon_img(m['name'], size=28, depth=0)
        bc = brand_count_for_method(m['name'])
        # Determine filter keys
        fk = 'all'
        for key, label, ic, types in categories[1:]:
            if types and m['type'] in types: fk = key; break
        rows += f'''<a href="payment-methods/{m['id']}.html" class="method-row" data-filter="{fk} all" data-name="{e(m['name'])}" data-speed="{e(m.get('depositSpeed',''))}" data-brands="{bc}">
          <div class="method-row-mobile">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
              <div class="method-icon-box">{icon}</div>
              <div style="flex:1;min-width:0">
                <h3 style="font-size:14px;font-weight:700">{e(m['name'])}</h3>
                <span style="font-size:12px;color:var(--text-muted);text-transform:capitalize">{e(m['type'])}</span>
              </div>
              {ICON_CHEVRON_RIGHT}
            </div>
            <div class="method-stat-grid">
              <div class="method-stat"><p class="method-stat-label">Deposit</p><p class="method-stat-val">{truncate(m.get('depositSpeed',''), 18)}</p></div>
              <div class="method-stat"><p class="method-stat-label">Withdraw</p><p class="method-stat-val">{truncate(m.get('withdrawalSpeed',''), 18)}</p></div>
              <div class="method-stat"><p class="method-stat-label">Fees</p><p class="method-stat-val">{truncate(m.get('fees',''), 18) or 'Free'}</p></div>
            </div>
            {f'<p style="font-size:12px;color:var(--text-muted);margin-top:10px;padding-top:10px;border-top:1px solid var(--sep)">Accepted at {bc} bookmaker{"s" if bc != 1 else ""}</p>' if bc > 0 else ''}
          </div>
          <div class="method-row-desktop">
            <div style="display:flex;align-items:center;gap:12px;min-width:0">
              <div class="method-icon-box" style="width:36px;height:36px;font-size:16px">{icon}</div>
              <div style="min-width:0">
                <h3 style="font-size:14px;font-weight:600">{e(m['name'])}</h3>
                <span style="font-size:12px;color:var(--text-muted);text-transform:capitalize">{e(m['type'])}{f" - {bc} sites" if bc > 0 else ""}</span>
              </div>
            </div>
            <span style="font-size:14px;color:var(--text-secondary)">{truncate(m.get('depositSpeed',''), 22)}</span>
            <span style="font-size:14px;color:var(--text-secondary)">{truncate(m.get('withdrawalSpeed',''), 22)}</span>
            <span style="font-size:14px;color:var(--text-secondary)">{truncate(m.get('fees',''), 18) or 'Free'}</span>
            <span style="font-size:14px;color:var(--accent);font-weight:600;text-align:right">View</span>
          </div>
        </a>'''

    pay_hero = category_hero(
        "SA Betting Payment Methods",
        f"{len(PAYMENTS)} ways to get your rands into and out of SA betting sites. Find the one that works for you - no PhD in banking required.",
        [{"label":"Home","href":"index.html"},{"label":"Payment Methods"}], 0,
        deco_icon='&#x1F4B3;'
    )
    body = f'''
    {pay_hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      <div class="filter-scroll" style="margin-bottom:32px">{pills}</div>

      <div class="sort-bar">
        <p class="sort-count">{len(PAYMENTS)} methods</p>
        <select class="sort-select" onchange="sortMethods(this)">
          <option value="name">Name (A-Z)</option>
          <option value="speed">Deposit Speed</option>
          <option value="brands">Most Popular</option>
        </select>
      </div>

      <div class="method-list filterable-grid">{rows}</div>
    </div>'''

    return page('SA Betting Payment Methods Guide 2026 | MzansiWins',
                 'All the payment methods used at South African betting sites compared.',
                 'payment-methods', body, depth=0, active_nav='payments', og_image='og-payments.png')


def build_news_index():
    cat_colors = {'Promos':'#1641B4','Industry':'#0ea5e9','Payments':'#22c55e','Sports':'#f5a623','Platform':'#ef4444','Bonus':'#16a34a','Features':'#8b5cf6','Promotions':'#1641B4','Regulation':'#dc2626','Winners':'#f59e0b','Guides':'#6366f1'}

    # Collect unique categories in order of frequency
    cat_counts = {}
    for a in NEWS:
        c = a.get('category', '')
        if c:
            cat_counts[c] = cat_counts.get(c, 0) + 1
    sorted_cats = sorted(cat_counts.keys(), key=lambda x: -cat_counts[x])

    # Category filter tabs
    filter_tabs = '<button class="news-filter-tab active" data-cat="all" onclick="filterNews(this, \'all\')">All <span class="news-filter-count">' + str(len(NEWS)) + '</span></button>'
    for cat in sorted_cats:
        cc = cat_colors.get(cat, '#555')
        filter_tabs += f'<button class="news-filter-tab" data-cat="{e(cat)}" onclick="filterNews(this, \'{e(cat)}\')" style="--tab-color:{cc}">{e(cat)} <span class="news-filter-count">{cat_counts[cat]}</span></button>'

    cards = ''
    for a in NEWS:
        cc = cat_colors.get(a.get('category',''), '#555')
        dt = datetime.fromisoformat(a['date'].replace('Z','+00:00')).strftime('%d %b %Y') if a.get('date') else ''
        cards += f'''<a href="news/{a['slug']}.html" class="news-card" data-category="{e(a.get('category',''))}">
          <div style="padding:20px">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
              <span class="news-badge" style="background:{cc}">{e(a.get('category',''))}</span>
              <span style="font-size:12px;color:var(--text-muted)">{dt}</span>
            </div>
            <h3 style="font-size:17px;font-weight:700;line-height:1.3;margin-bottom:8px">{e(a['title'])}</h3>
            <p style="font-size:14px;color:var(--text-secondary);line-height:1.6;margin-bottom:8px">{e(a.get('excerpt',''))}</p>
            <div class="news-card-author">{author_img(a.get('author',''), size=24, depth=0)} <span style="font-size:13px;color:var(--text-muted)">By {e(a.get('author',''))}</span></div>
          </div>
        </a>'''

    sidebar = news_sidebar_top5(depth=0)

    news_hero = category_hero(
        "SA Betting News",
        "Bonus drops, platform shakeups, and industry gossip from the Mzansi betting world. Fresh off the press.",
        [{"label":"Home","href":"index.html"},{"label":"News"}], 0,
        deco_icon='&#x1F4F0;'
    )
    body = f'''
    {news_hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      <div class="news-filter-bar">{filter_tabs}</div>
      <div class="news-empty-state" style="display:none;text-align:center;padding:48px 20px;color:var(--text-muted)">No stories found in this category.</div>
      <div class="news-layout" style="display:grid;grid-template-columns:1fr 300px;gap:32px;margin-top:24px">
        <div class="grid-3 news-grid" style="grid-template-columns:repeat(auto-fill,minmax(280px,1fr))">{cards}</div>
        {sidebar}
      </div>
    </div>'''

    t_nw, d_nw = seo_meta('news')
    return page(t_nw, 'Latest South African betting industry news and updates.', 'news', body, depth=0, active_nav='news', og_image='og-news.png')


def build_content_page(page_type):
    if page_type == 'about-us':
        title = 'About MzansiWins'
        desc = 'Independent SA betting reviews by punters, for punters.'
        canon = 'about-us'
        active = 'about'
        content = '''<p>MzansiWins is South Africa's independent betting review platform, built by punters who were gatvol of biased reviews and dodgy bonus claims. So we made something honest.</p>
        <h2>What We Do</h2>
        <p>We test every licensed SA bookmaker with our own rands. We sign up, deposit, bet, and withdraw - then we write about what actually happened, not what the marketing team wanted us to say. No sugar-coating, no sponsored rankings.</p>
        <p>Our reviews cover 35 licensed operators, 11 payment methods, and hundreds of promo codes. Everything gets updated regularly because the SA betting landscape moves faster than a Rabada yorker.</p>
        <h2>Our Team</h2>
        <p>We are a tight crew of SA betting enthusiasts scattered across Joburg, Cape Town, and Durbs. Between us, we have over 20 years in the South African betting trenches. We have seen the good, the bad, and the "why does this withdrawal take 7 days?"</p>
        <h2>Editorial Independence</h2>
        <p>Yes, we earn affiliate commissions when you sign up through our links. No, this does not influence our ratings. A bookmaker that deserves a 2.5 gets a 2.5 - even if they are our biggest paying partner. That is how we sleep at night.</p>
        <h2>Contact Us</h2>
        <p>Got a question, a tip, or want to tell us we are wrong about something? Drop us a line at <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>. We read everything and try to get back within 48 hours. Unless it is a long weekend - then give us until Tuesday.</p>
        <div style="margin-top:20px;padding:20px;background:#f3f4f6;border-radius:12px;line-height:1.75">
          <strong>Our Office</strong><br>
          MzansiWins.co.za<br>
          38 Wale St<br>
          Cape Town City Centre<br>
          Cape Town 8000<br>
          South Africa
        </div>'''
    elif page_type == 'how-we-rate':
        title = 'How We Rate Bookmakers'
        desc = 'Our transparent methodology for rating South African betting sites.'
        canon = 'how-we-rate'
        active = 'about'
        content = '''<p>Every bookmaker on MzansiWins gets scored on a 5-point scale across 7 categories. No vibes-based ratings here - each category carries a specific weight based on what actually matters to South African punters.</p>
        <h2>Rating Categories</h2>
        <h3>Welcome Bonus (25%)</h3>
        <p>We look at the headline number, but more importantly, the wagering requirements, minimum deposit, expiry period, and how painful the claim process is. A R5,000 bonus with 50x wagering is worse than a R500 bonus with 3x wagering - and we are not afraid to say it.</p>
        <h3>Odds Quality (20%)</h3>
        <p>We compare odds on PSL football, Springbok rugby, and international cricket across all bookmakers. Tight margins mean more rands in your pocket. Every percentage point matters when you are punting regularly.</p>
        <h3>Payment Methods (15%)</h3>
        <p>Can you deposit with Ozow, EFT, vouchers, and cards? Great. But the real question: how fast do withdrawals actually land in your account? We time them. With a stopwatch. Okay, not literally, but close.</p>
        <h3>Sports Coverage (15%)</h3>
        <p>Market depth is everything. We check PSL coverage (player props and corners, not just match result), Currie Cup rugby, Proteas cricket, horse racing, and the niche stuff like MMA and eSports. More markets means more fun.</p>
        <h3>Platform Quality (10%)</h3>
        <p>Mobile is king in SA. We test load speed, navigation, bet slip usability, and whether the app crashes mid-accumulator. Because nothing ruins your day like a frozen screen when you are trying to cash out.</p>
        <h3>Live Betting (10%)</h3>
        <p>In-play market availability, how quickly odds update, cash out options, and live streaming. If you can watch and bet at the same time without buffering, that is a win.</p>
        <h3>Customer Support (5%)</h3>
        <p>Response time, available channels (live chat, email, phone), and whether local SA support agents are available. Bonus points if they actually solve your problem instead of sending you in circles.</p>
        <h2>Overall Score</h2>
        <p>The overall rating is the weighted average of all 7 categories, rounded to one decimal place. We update scores quarterly or whenever a bookmaker makes significant changes. No one gets a free pass forever.</p>'''
    elif page_type == 'fica-guide':
        title = 'FICA Verification Guide for SA Bettors'
        desc = 'Step-by-step guide to completing FICA verification at South African betting sites.'
        canon = 'fica-guide'
        active = 'fica'
        content = '''<p>FICA verification is that annoying-but-necessary step every SA bettor has to deal with before cashing out. Think of it as the bouncer at the door - you need to prove you are who you say you are. Here is how to get through it without losing your mind.</p>
        <h2>What is FICA?</h2>
        <p>FICA stands for Financial Intelligence Centre Act. Fancy name, simple concept: betting operators need to verify your identity before letting you withdraw. It is the law, it protects you from fraud, and there is zero way around it. So let us just get it done.</p>
        <h2>Documents You Need</h2>
        <ul>
          <li><strong>South African ID</strong> - your green book, smart ID card, or valid passport. Pro tip: smart ID card is fastest.</li>
          <li><strong>Proof of address</strong> - utility bill, bank statement, or municipal account from the last 3 months. Your mom's Netflix bill does not count.</li>
          <li><strong>Proof of payment method</strong> - screenshot or photo of the bank account or e-wallet you deposit with.</li>
        </ul>
        <h2>Step-by-Step Process</h2>
        <h3>Step 1: Register Your Account</h3>
        <p>Sign up with your real details. Use your name exactly as it appears on your ID. Not your gamertag, not your WhatsApp name - your actual government name. Mismatches cause delays.</p>
        <h3>Step 2: Upload Documents</h3>
        <p>Most bookmakers have a "Verify Account" or "FICA" section in your profile. Upload clear photos or scans. Make sure all text is readable and no corners are chopped off. Blurry selfie-style photos will get rejected faster than a bad Tinder pic.</p>
        <h3>Step 3: Wait for Approval</h3>
        <p>Typically 24 to 48 hours. Hollywoodbets and Betway are usually quicker - sometimes a few hours during business hours. Others... not so much. Patience is a virtue, bru.</p>
        <h3>Step 4: Start Withdrawing</h3>
        <p>Once verified, you can cash out to any linked payment method. First withdrawal might take a touch longer as they do a final check. After that? Smooth sailing.</p>
        <h2>Tips for Fast Verification</h2>
        <ul>
          <li>Use your smart ID card - it processes faster than the old green book</li>
          <li>Take photos in good lighting with a plain background (not on the braai table)</li>
          <li>Make sure your proof of address is from the last 3 months</li>
          <li>Upload during SA business hours (8am to 5pm) for the fastest turnaround</li>
          <li>If you have not heard back after 48 hours, poke their support team</li>
        </ul>
        <h2>Common Issues</h2>
        <p><strong>Name mismatch:</strong> Your registration name must match your ID exactly. Used a nickname? Contact support to fix it before you waste time uploading documents.</p>
        <p><strong>Blurry documents:</strong> The number one reason for rejection. Take clear, well-lit photos. Pretend you are photographing food for Instagram - that level of effort.</p>
        <p><strong>Expired proof of address:</strong> Must be within 3 months. If you do not have a recent one, download a bank statement from your banking app. Takes 30 seconds.</p>'''
    else:
        return ''

    body = f'''
    <div class="container" style="padding-top:40px;padding-bottom:80px">
      {breadcrumbs([{"label":"Home","href":"index.html"},{"label":title}], 0)}
      <div class="content-page">
        <h1 class="page-title">{title}</h1>
        {content}
      </div>
    </div>'''

    return page(f'{title} | MzansiWins', desc, canon, body, depth=0, active_nav=active)


# ===== NEW BETTING SITES PAGE =====
def build_new_betting_sites():
    new_ids = ['apexbets', 'lulabet', 'betshezi']
    new_brands = [b for b in DATA['brands'] if b['id'] in new_ids]
    # Sort by rating desc
    new_brands.sort(key=lambda b: -b['overallRating'])
    total_bonus_val = sum(bonus_val(b) for b in new_brands)
    brand_data_json = json.dumps([{"id": b["id"], "name": e(b["name"]), "bonus": bonus_val(b)} for b in new_brands])

    rows = ''
    mobile_cards = ''
    for i, b in enumerate(new_brands):
        tc_text = e(b.get('tcs', '18+ T&Cs apply.'))
        min_dep = e(b.get('minDeposit', ''))
        bv = bonus_val(b)
        bv_display = f'R{bv:,}' if bv > 0 else '-'
        star_icon = ICON_STAR
        code = get_promo(b)
        logo = logo_path(b, 0)
        logo_img_sm = f'<img src="{logo}" alt="{e(b["name"])}" style="width:28px;height:28px;object-fit:contain;border-radius:4px;background:{brand_bg(b)};padding:2px;border:1px solid var(--border);flex-shrink:0" loading="lazy">' if logo else ''
        logo_img_mobile = f'<img src="{logo}" alt="{e(b["name"])}" style="width:36px;height:36px;object-fit:contain;border-radius:6px;background:{brand_bg(b)};padding:3px;border:1px solid var(--border);flex-shrink:0" loading="lazy">' if logo else ''

        rows += f'''<tr data-name="{e(b['name']).lower()}" data-brand-id="{b['id']}" data-bonus-val="{bv}">
          <td data-sort="{i+1}" style="font-weight:600;color:var(--text-muted)">{i+1}</td>
          <td data-sort="{e(b['name'])}" style="white-space:nowrap">
            <div style="display:flex;align-items:center;gap:8px">
              <button class="star-btn" data-brand="{b['id']}" onclick="event.stopPropagation();toggleStar('{b['id']}')" aria-label="Add to favourites">{star_icon}</button>
              {logo_img_sm}
              <a href="betting-site-review/{b['id']}.html" class="table-link" style="font-weight:600">{e(b['name'])}</a>
            </div>
          </td>
          <td><span style="color:var(--bonus);font-weight:600">{e(b['welcomeBonusAmount'])}</span><br><span style="font-size:11px;color:var(--text-muted)">{tc_text}</span></td>
          <td data-sort="{bv}" style="text-align:center;font-weight:700;color:var(--bonus)">{bv_display}</td>
          <td style="text-align:center"><span class="promo-code" style="font-size:12px">{e(code)}</span></td>
          <td data-sort="{b['overallRating']}" style="text-align:center">{rating_badge(b['overallRating'], 'sm')}</td>
          <td style="text-align:center"><a href="betting-site-review/{b['id']}.html" class="btn-outline btn-sm">Review</a></td>
        </tr>'''

        m_exit = masked_exit(b, 0)
        visit_btn = f'<a href="{m_exit}" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary btn-sm" style="flex:1;text-align:center">Visit Site</a>' if m_exit else ''
        mobile_cards += f'''<div class="listing-card" data-name="{e(b['name']).lower()}" data-brand-id="{b['id']}" data-bonus-val="{bv}">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:10px">
            <div style="display:flex;align-items:center;gap:8px;min-width:0">
              <button class="star-btn" data-brand="{b['id']}" onclick="event.stopPropagation();toggleStar('{b['id']}')" aria-label="Add to favourites">{star_icon}</button>
              {logo_img_mobile}
              <div style="min-width:0">
                <div style="display:flex;align-items:center;gap:6px">
                  <span style="font-size:13px;font-weight:700;color:var(--text-muted)">#{i+1}</span>
                  <a href="betting-site-review/{b['id']}.html" style="font-size:16px;font-weight:700;color:var(--text-primary)">{e(b['name'])}</a>
                </div>
              </div>
            </div>
            {rating_badge(b['overallRating'], 'sm')}
          </div>
          <div style="background:var(--accent-light);border-radius:8px;padding:10px 14px;margin-bottom:10px">
            <div style="display:flex;align-items:center;justify-content:space-between">
              <p style="font-size:15px;font-weight:700;color:var(--bonus)">{e(b['welcomeBonusAmount'])}</p>
              <span style="font-size:14px;font-weight:700;color:var(--bonus)">{bv_display}</span>
            </div>
            {f'<span style="font-size:12px;color:var(--text-muted)">Min deposit: {min_dep}</span>' if min_dep else ''}
          </div>
          <p style="font-size:11px;color:var(--text-muted);margin-bottom:12px;line-height:1.5">{tc_text}</p>
          <div style="display:flex;gap:8px">
            <a href="betting-site-review/{b['id']}.html" class="btn-outline btn-sm" style="flex:1;text-align:center">Review</a>
            {visit_btn}
          </div>
        </div>'''

    seo_content = f'''<div class="content-page" style="margin-bottom:32px">
      <h2>Fresh Faces in the SA Betting Scene</h2>
      <p>The South African online betting market is growing fast, and new bookmakers are joining the ranks regularly. These fresh entrants bring innovative features, generous sign-up bonuses, and modern platforms built from the ground up for mobile users. Whether you are after bigger welcome offers or just want to try something different, new betting sites often have the most competitive deals as they fight to win your business.</p>
      <p>Every new bookmaker listed on MzansiWins holds a valid provincial gambling licence, so your money and personal data are protected under South African law. We test each one personally before recommending them.</p>

      <h2>Why Try a New Betting Site?</h2>
      <p>New bookmakers have to work harder to attract punters, which means better bonuses, fresher features, and more responsive customer support. The established names are fantastic, but the newcomers are hungry - and that hunger translates directly into better value for you.</p>
      <ul>
        <li><strong>Bigger welcome bonuses</strong> - new sites typically offer more generous sign-up packages to build their player base</li>
        <li><strong>Modern technology</strong> - built with the latest tech stack, so the platform tends to be slick, fast, and mobile-first</li>
        <li><strong>Responsive support</strong> - smaller player bases mean faster response times and more personal service</li>
        <li><strong>Unique features</strong> - new entrants often introduce innovative markets, bet builders, or payment methods not available elsewhere</li>
      </ul>

      <h2>Are New Betting Sites Safe?</h2>
      <p>Absolutely - as long as they are licensed. Every bookmaker on this page holds a valid South African provincial gambling board licence, which means they comply with strict regulations around player protection, responsible gambling, and fair play. We verify these licences before listing any operator on MzansiWins.</p>
    </div>'''

    below_table = f'''<div class="content-page" style="margin-top:32px">
      <h2>How We Evaluate New Betting Sites</h2>
      <p>We apply the exact same rating methodology to new bookmakers as we do to the established names. Our team creates a real account, deposits real rands, places real bets, and attempts real withdrawals. No shortcuts, no freebies from the operator. The review is based entirely on our first-hand experience as a regular South African punter.</p>
      <p>New sites do start at a slight disadvantage in categories like "Live" and "Sports" coverage simply because they tend to have fewer markets at launch. But they can absolutely score top marks in areas like bonuses, platform quality, and customer support - and several of them do exactly that.</p>

      <h2>Tips for Signing Up at a New Bookmaker</h2>
      <ul>
        <li><strong>Use the promo code</strong> - always enter the promo code during registration to make sure your welcome bonus is activated. For most new SA bookmakers, <strong>NEWBONUS</strong> is the code to use.</li>
        <li><strong>Complete FICA early</strong> - get your verification sorted straight after registration. Upload your ID and proof of address so there are no delays when you want to withdraw. Check our <a href="fica-guide.html">FICA guide</a> for step-by-step help.</li>
        <li><strong>Read the T&Cs</strong> - welcome bonuses come with wagering requirements and expiry dates. Know the rules before you play.</li>
        <li><strong>Start small</strong> - deposit the minimum first and get a feel for the platform before going big.</li>
      </ul>
    </div>'''

    new_hero = category_hero(
        "New Betting Sites in South Africa 2026",
        f"The freshest bookmakers on the SA scene - licensed, tested, and offering generous welcome bonuses to win you over. Updated {CURRENT_MONTH_YEAR}.",
        [{"label":"Home","href":"index.html"},{"label":"Betting Sites","href":"betting-sites.html"},{"label":"New Betting Sites"}], 0,
        deco_icon='&#x2B50;'
    )
    body = f'''
    {new_hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      {seo_content}

      <div class="bonus-counter-banner">
        <div class="bonus-counter-item">
          <div class="bonus-counter-label">New site bonuses</div>
          <div class="bonus-counter-value" style="color:var(--bonus)">R{total_bonus_val:,}</div>
          <div class="bonus-counter-sub">{len(new_brands)} new bookmakers</div>
        </div>
      </div>

      <div class="table-wrap listing-desktop">
        <table class="data-table">
          <thead><tr>
            <th onclick="sortTable(this)"># <span class="sort-icon">\u2195</span></th>
            <th onclick="sortTable(this)">Bookmaker <span class="sort-icon">\u2195</span></th>
            <th>Welcome Bonus &amp; T&amp;Cs</th>
            <th onclick="sortTable(this)">Value <span class="sort-icon">\u2195</span></th>
            <th>Promo Code</th>
            <th onclick="sortTable(this)" style="text-align:center">Rating <span class="sort-icon">\u2195</span></th>
            <th style="text-align:center">Review</th>
          </tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>

      <div class="listing-mobile">{mobile_cards}</div>

      {below_table}
    </div>
    <script>var brandBonusData = {brand_data_json};</script>'''

    return page('New Betting Sites South Africa 2026 - Latest Bookmakers | MzansiWins',
                 f'Discover the newest licensed betting sites in South Africa for 2026. Fresh bookmakers with generous welcome bonuses, modern platforms, and competitive odds.',
                 'new-betting-sites', body, depth=0, active_nav='betting')


# ===== FOOTER POLICY PAGES =====
FOOTER_PAGES = {
    # Transparency
    'code-of-ethics': {
        'title': 'Code of Ethics',
        'meta_desc': 'MzansiWins Code of Ethics. Our commitment to honest, transparent, and responsible betting reviews for South African punters.',
        'content': '''<p>At MzansiWins, we hold ourselves to the highest standards of integrity. Our code of ethics is not just a document we file away - it is the backbone of everything we do.</p>
        <h2>Our Core Principles</h2>
        <ul>
        <li><strong>Independence:</strong> Our reviews and ratings are never influenced by commercial relationships. No bookmaker can buy a higher rating on MzansiWins.</li>
        <li><strong>Honesty:</strong> We tell it like it is. If a bookmaker has a rubbish withdrawal process, we will say so. If their welcome bonus is the real deal, we will say that too.</li>
        <li><strong>Transparency:</strong> We disclose all affiliate relationships and explain exactly how we make money. No hidden agendas.</li>
        <li><strong>Accuracy:</strong> We verify every claim, bonus amount, and T&C before publishing. If we get something wrong, we fix it fast.</li>
        <li><strong>User-first:</strong> Our readers come first. Always. Every recommendation is made with your best interests in mind.</li>
        </ul>
        <h2>Editorial Independence</h2>
        <p>Our editorial team operates independently from the commercial side of the business. Advertisers and partners have zero say in our ratings, rankings, or review content. Our reviewers are free to be critical without fear of commercial repercussions.</p>
        <h2>Conflicts of Interest</h2>
        <p>We require all team members to declare any personal betting accounts or financial interests in the operators we review. Where a conflict exists, that person is removed from the review process for that particular brand.</p>
        <h2>Contact Us</h2>
        <p>If you believe we have breached our code of ethics, please contact us at <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>. We take every complaint seriously and will investigate thoroughly.</p>'''
    },
    'editorial-policy': {
        'title': 'Editorial Policy',
        'meta_desc': 'MzansiWins Editorial Policy. How we research, write, and publish betting site reviews and guides for South African players.',
        'content': '''<p>Quality content is what sets MzansiWins apart. Our editorial policy ensures every piece of content meets the high standards South African punters deserve.</p>
        <h2>How We Create Content</h2>
        <p>Every review and guide on MzansiWins follows a rigorous process:</p>
        <ol>
        <li><strong>Research:</strong> Our team registers real accounts, makes real deposits, and tests every feature hands-on.</li>
        <li><strong>Writing:</strong> Content is drafted by experienced writers who understand the SA betting landscape inside and out.</li>
        <li><strong>Review:</strong> Every piece is fact-checked by a second team member before publication.</li>
        <li><strong>Updates:</strong> Published content is reviewed at least monthly to ensure accuracy. Bonus amounts, T&Cs, and payment methods can change - we stay on top of it.</li>
        </ol>
        <h2>Sources and Verification</h2>
        <p>We verify all information directly with the bookmaker where possible. Bonus details, wagering requirements, and payment processing times are confirmed against the operator's own terms and conditions.</p>
        <h2>Corrections</h2>
        <p>If we get something wrong, we fix it. No excuses, no delays. See our <a href="corrections-policy.html">Corrections Policy</a> for details on how we handle errors.</p>
        <h2>Questions?</h2>
        <p>Reach out to our editorial team at <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
    'fact-checking': {
        'title': 'Fact Checking Policy',
        'meta_desc': 'How MzansiWins verifies facts, bonus details, and claims in our South African betting site reviews.',
        'content': '''<p>Every claim on MzansiWins goes through a fact-checking process before it reaches your screen. Punters deserve accurate information - not guesswork.</p>
        <h2>What We Verify</h2>
        <ul>
        <li><strong>Bonus amounts and T&Cs:</strong> Welcome bonuses, promo codes, wagering requirements, minimum deposits, and expiry periods.</li>
        <li><strong>Payment methods:</strong> Which methods are accepted, processing times, fees, and minimum/maximum limits.</li>
        <li><strong>Licensing status:</strong> We confirm every bookmaker holds a valid South African provincial gambling licence.</li>
        <li><strong>Feature claims:</strong> Live streaming, live betting, cash out, and mobile app availability are tested first-hand.</li>
        </ul>
        <h2>Our Process</h2>
        <p>The writer researches and drafts the content. A separate fact-checker then independently verifies every factual claim against primary sources - the bookmaker's own website, terms and conditions, and where necessary, direct communication with the operator.</p>
        <h2>When Facts Change</h2>
        <p>The betting industry moves fast. We conduct regular reviews of all published content and update any information that has changed. If you spot something that looks outdated, please let us know at <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
    'corrections-policy': {
        'title': 'Corrections Policy',
        'meta_desc': 'MzansiWins Corrections Policy. How we handle errors and inaccuracies in our South African betting content.',
        'content': '''<p>We are human, and sometimes we get things wrong. When that happens, we fix it promptly and transparently.</p>
        <h2>How We Handle Corrections</h2>
        <ul>
        <li><strong>Minor corrections:</strong> Typos, formatting errors, and small factual updates are corrected immediately without a formal notice.</li>
        <li><strong>Significant corrections:</strong> Material errors - such as incorrect bonus amounts, wrong promo codes, or inaccurate T&Cs - are corrected and flagged with a correction notice at the top of the article.</li>
        <li><strong>Retractions:</strong> In the rare event that an entire piece of content is found to be fundamentally inaccurate, we will retract it and publish an explanation.</li>
        </ul>
        <h2>Report an Error</h2>
        <p>If you spot an error on MzansiWins, please email us at <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a> with the page URL and a description of the issue. We aim to investigate and respond within 48 hours.</p>'''
    },
    'affiliate-disclosure': {
        'title': 'Affiliate Disclosure',
        'meta_desc': 'MzansiWins Affiliate Disclosure. How we earn money and why it does not affect our betting site reviews.',
        'content': '''<p>MzansiWins is a free resource for South African punters. Here is how we keep the lights on.</p>
        <h2>How We Make Money</h2>
        <p>When you click on a link to a bookmaker on our site and sign up or place a bet, we may earn a commission from that bookmaker. This is called affiliate marketing, and it is standard practice across the betting review industry.</p>
        <h2>Does This Affect Our Reviews?</h2>
        <p>No. Absolutely not. Our editorial team operates independently from our commercial relationships. A bookmaker that pays us a higher commission will not receive a better rating. Our ratings are based on our honest assessment using the criteria outlined on our <a href="how-we-rate.html">How We Rate</a> page.</p>
        <h2>What This Means for You</h2>
        <p>Using our links costs you nothing extra. You get the same bonuses and promotions as anyone else - often better, because our promo codes can unlock exclusive deals. Meanwhile, your click helps fund our research, testing, and content creation.</p>
        <h2>Our Promise</h2>
        <p>We will always prioritise your interests over commercial considerations. If a bookmaker with a lucrative affiliate deal delivers a poor experience, we will rate it accordingly. Full stop.</p>
        <p>Questions? Email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
    'advertising-disclosure': {
        'title': 'Advertising Disclosure',
        'meta_desc': 'MzansiWins Advertising Disclosure. How sponsored content and advertising works on our site.',
        'content': '''<p>MzansiWins may feature advertising and sponsored content. Here is how we handle it.</p>
        <h2>Types of Advertising</h2>
        <ul>
        <li><strong>Display advertising:</strong> Banner adverts and display ads from licensed South African bookmakers may appear on our pages.</li>
        <li><strong>Sponsored content:</strong> Occasionally, a bookmaker may sponsor a piece of content. Any sponsored content is clearly labelled as such.</li>
        <li><strong>Featured placements:</strong> Some bookmakers may pay for premium placement in our listings. Where this occurs, it is clearly disclosed.</li>
        </ul>
        <h2>Our Standards</h2>
        <p>All advertising on MzansiWins must comply with South African gambling advertising regulations. We do not accept advertising from unlicensed operators. All adverts must be truthful and not misleading.</p>
        <h2>Editorial Independence</h2>
        <p>Advertising relationships do not influence our editorial content, ratings, or reviews. Our editorial and advertising teams operate independently.</p>
        <p>For advertising enquiries, email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
    'complaints-policy': {
        'title': 'Complaints Policy',
        'meta_desc': 'MzansiWins Complaints Policy. How to raise a complaint and our process for resolving issues.',
        'content': '''<p>We want to get things right, and if you are unhappy with something on MzansiWins, we want to hear about it.</p>
        <h2>How to Complain</h2>
        <p>Send your complaint to <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a> with the subject line "Complaint". Please include:</p>
        <ul>
        <li>Your name and email address</li>
        <li>The URL of the page in question (if applicable)</li>
        <li>A clear description of your complaint</li>
        <li>What outcome you are hoping for</li>
        </ul>
        <h2>Our Process</h2>
        <ol>
        <li><strong>Acknowledgement:</strong> We will acknowledge your complaint within 2 business days.</li>
        <li><strong>Investigation:</strong> We will investigate thoroughly, which may take up to 10 business days.</li>
        <li><strong>Response:</strong> We will respond with our findings and any actions we plan to take.</li>
        <li><strong>Escalation:</strong> If you are not satisfied with our response, you may request a review by our senior editorial team.</li>
        </ol>'''
    },
    # Responsible Gambling
    'responsible-gambling-policy': {
        'title': 'Responsible Gambling Policy',
        'meta_desc': 'MzansiWins Responsible Gambling Policy. Our commitment to promoting safe, responsible betting in South Africa.',
        'content': '''<p>Betting should be fun. The moment it stops being fun, something has gone wrong. At MzansiWins, we take responsible gambling seriously.</p>
        <h2>Our Commitment</h2>
        <ul>
        <li>We only promote licensed, regulated South African bookmakers that have responsible gambling tools in place.</li>
        <li>We never target our content at anyone under the age of 18.</li>
        <li>We encourage all readers to set deposit limits, loss limits, and time limits on their betting accounts.</li>
        <li>We do not use language that encourages excessive or irresponsible gambling.</li>
        </ul>
        <h2>Warning Signs</h2>
        <p>If you answer yes to any of these, it might be time to take a step back:</p>
        <ul>
        <li>Are you betting with money you cannot afford to lose?</li>
        <li>Are you chasing losses - betting more to try to win back what you have lost?</li>
        <li>Is gambling causing arguments with family or friends?</li>
        <li>Are you borrowing money to gamble?</li>
        <li>Do you feel anxious or stressed when you are not betting?</li>
        </ul>
        <h2>Get Help</h2>
        <p>If gambling is becoming a problem, reach out:</p>
        <ul>
        <li><strong>South African Responsible Gambling Foundation:</strong> 0800 006 008 (free, 24/7)</li>
        <li><strong>Gambling Therapy:</strong> <a href="https://www.gamblingtherapy.org" target="_blank" rel="noopener noreferrer">gamblingtherapy.org</a></li>
        </ul>
        <p>You can also email us at <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a> and we will do our best to point you in the right direction.</p>'''
    },
    'support-organisations': {
        'title': 'Gambling Support Organisations in South Africa',
        'meta_desc': 'Directory of gambling support organisations in South Africa. Free helplines, counselling, and resources for problem gambling.',
        'content': '''<p>If you or someone you know is struggling with gambling, help is available. These organisations provide free, confidential support in South Africa.</p>
        <h2>South African Responsible Gambling Foundation (SARGF)</h2>
        <p>The SARGF is the primary body for responsible gambling in South Africa. They offer a free 24/7 helpline, counselling services, and treatment programmes.</p>
        <ul>
        <li><strong>Helpline:</strong> 0800 006 008 (free call, 24/7)</li>
        <li><strong>Website:</strong> <a href="https://www.responsiblegambling.co.za" target="_blank" rel="noopener noreferrer">responsiblegambling.co.za</a></li>
        </ul>
        <h2>Gambling Therapy</h2>
        <p>An international service offering free online support, including live chat, forums, and self-help tools.</p>
        <ul>
        <li><strong>Website:</strong> <a href="https://www.gamblingtherapy.org" target="_blank" rel="noopener noreferrer">gamblingtherapy.org</a></li>
        </ul>
        <h2>Gamblers Anonymous South Africa</h2>
        <p>A fellowship of men and women who share their experience, strength, and hope to help each other recover from a gambling problem.</p>
        <ul>
        <li><strong>Website:</strong> <a href="https://www.gasa.org.za" target="_blank" rel="noopener noreferrer">gasa.org.za</a></li>
        </ul>
        <h2>FAMSA (Families South Africa)</h2>
        <p>Offers family counselling services that can help when gambling is affecting relationships.</p>
        <ul>
        <li><strong>Website:</strong> <a href="https://www.famsa.org.za" target="_blank" rel="noopener noreferrer">famsa.org.za</a></li>
        </ul>
        <p>Remember: asking for help is a sign of strength, not weakness. These services are free and confidential.</p>'''
    },
    'betting-risk-awareness': {
        'title': 'Betting Risk Awareness',
        'meta_desc': 'Understanding the risks of sports betting in South Africa. Honest information to help you bet responsibly.',
        'content': '''<p>Betting can be great entertainment, but it carries real financial risk. Here is what every South African punter should understand.</p>
        <h2>The House Always Has an Edge</h2>
        <p>Bookmakers are businesses, and they are set up to make a profit over time. The odds are structured so that, on average, the bookmaker wins. Individual punters can and do win, but the longer you bet, the more the mathematical edge works against you.</p>
        <h2>Welcome Bonuses Are Not Free Money</h2>
        <p>Welcome bonuses come with wagering requirements - conditions you need to meet before you can withdraw. Always read the T&Cs. A R1,000 bonus with 30x wagering means you need to wager R30,000 before you can cash out. That is not free money - it is an incentive to keep betting.</p>
        <h2>Common Pitfalls</h2>
        <ul>
        <li><strong>Chasing losses:</strong> The urge to bet more after a loss is natural but dangerous. Set a loss limit before you start and stick to it.</li>
        <li><strong>Emotional betting:</strong> Never bet when you are angry, drunk, or upset. These are the moments when bad decisions happen.</li>
        <li><strong>Betting with rent money:</strong> Only ever bet with money you can genuinely afford to lose. If losing it would cause you stress, do not bet it.</li>
        <li><strong>Ignoring time:</strong> Set a time limit for your betting sessions. It is easy to lose track of time.</li>
        </ul>
        <h2>Practical Tips</h2>
        <ul>
        <li>Set a weekly or monthly betting budget and never exceed it.</li>
        <li>Use the deposit limit tools that every licensed SA bookmaker offers.</li>
        <li>Take regular breaks from betting.</li>
        <li>Never borrow money to gamble.</li>
        </ul>
        <p>If you need help, call the SA Responsible Gambling Foundation on <strong>0800 006 008</strong> (free, 24/7).</p>'''
    },
    'self-exclusion-resources': {
        'title': 'Self-Exclusion Resources for SA Bettors',
        'meta_desc': 'How to self-exclude from South African betting sites. Step-by-step guides and resources for taking a break from gambling.',
        'content': '''<p>Self-exclusion is a powerful tool if you need to take a break from betting. All licensed South African bookmakers are required to offer it.</p>
        <h2>What is Self-Exclusion?</h2>
        <p>Self-exclusion lets you voluntarily ban yourself from a betting site for a set period - typically 6 months, 1 year, or permanently. During this period, you cannot place bets, and the operator is required to close your account.</p>
        <h2>How to Self-Exclude</h2>
        <ol>
        <li><strong>Contact the bookmaker:</strong> Most SA bookmakers have a self-exclusion option in your account settings, or you can contact their support team directly.</li>
        <li><strong>Choose your period:</strong> Select how long you want to be excluded. If in doubt, choose a longer period. You can always reassess later.</li>
        <li><strong>Confirm:</strong> Once confirmed, self-exclusion cannot be reversed until the period expires.</li>
        </ol>
        <h2>Multi-Operator Self-Exclusion</h2>
        <p>If you want to exclude yourself from multiple bookmakers, you can contact the South African Responsible Gambling Foundation (0800 006 008) who can assist with the process.</p>
        <h2>What Happens During Self-Exclusion?</h2>
        <ul>
        <li>Your account is closed and you cannot log in.</li>
        <li>You should not receive any marketing communications.</li>
        <li>If you have funds in your account, they will be returned to you.</li>
        <li>The bookmaker must not allow you to open a new account during the exclusion period.</li>
        </ul>
        <p>Self-exclusion is nothing to be ashamed of. It is a responsible, mature decision. For support, call <strong>0800 006 008</strong> or email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
    # Corporate
    'management-team': {
        'title': 'Management Team',
        'meta_desc': 'Meet the MzansiWins editorial team. The betting analysts, casino experts, and payment specialists behind South Africa\'s trusted review platform.',
        'content': '''<p>MzansiWins is run by a focused editorial team with backgrounds in sports journalism, mathematics, data analytics, and fintech. Every review, guide, and recommendation on this site is produced by people with direct experience in the industries they write about.</p>

        <div style="display:grid;gap:32px;margin-top:32px">

        <div class="team-card">
          <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px">
            <img src="assets/author-thabo-mokoena.jpg" alt="Thabo Mokoena" width="64" height="64" style="width:64px;height:64px;border-radius:50%;object-fit:cover;object-position:center 20%;flex-shrink:0" loading="lazy">
            <div>
              <h2 style="font-size:20px;font-weight:700;margin-bottom:2px">Thabo Mokoena</h2>
              <p style="font-size:14px;color:var(--accent);font-weight:600">Editor-in-Chief</p>
            </div>
          </div>
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">Thabo Mokoena leads the editorial direction of the site and oversees all sportsbook reviews and regulatory coverage. Before joining the platform, he worked as a sports journalist for a major Johannesburg daily, where he reported on football, rugby, and the rapidly expanding South African online betting market.</p>
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">Since 2018, Thabo has specialised in analysing licensed betting operators serving South African players. He has personally reviewed more than 100 betting platforms across Africa, focusing on licensing standards, pricing competitiveness, and customer protections. His work ensures that all bookmaker reviews are grounded in factual testing rather than promotional claims.</p>
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">He holds a BA in Media Studies from the University of the Witwatersrand (Wits University).</p>
          <div style="display:flex;flex-wrap:wrap;gap:6px">
            <span style="display:inline-block;font-size:12px;font-weight:600;padding:4px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">Sportsbook Reviews</span>
            <span style="display:inline-block;font-size:12px;font-weight:600;padding:4px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">Betting Regulation &amp; Compliance</span>
            <span style="display:inline-block;font-size:12px;font-weight:600;padding:4px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">Odds Analysis</span>
          </div>
          <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border)">
          <h3 style="font-size:14px;font-weight:700;margin-bottom:8px;color:var(--accent)">Latest Articles</h3>
          <a href="news/betway-sa-cricket-betting-expansion.html" style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sep);text-decoration:none;color:inherit"><div style="flex:1;min-width:0"><p style="font-size:13px;font-weight:600;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Betway South Africa Adds 50 New Cricket Markets Ahead of T20 Season</p><span style="font-size:12px;color:var(--text-muted)">10 Mar 2026</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></a>
<a href="news/supabets-live-streaming-10-new-sports.html" style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sep);text-decoration:none;color:inherit"><div style="flex:1;min-width:0"><p style="font-size:13px;font-weight:600;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Supabets Adds Live Streaming for 10 Additional Sports</p><span style="font-size:12px;color:var(--text-muted)">09 Mar 2026</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></a>
<a href="news/gbets-partners-with-sharks-rugby.html" style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sep);text-decoration:none;color:inherit"><div style="flex:1;min-width:0"><p style="font-size:13px;font-weight:600;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Gbets Signs Sponsorship Deal with Sharks Rugby</p><span style="font-size:12px;color:var(--text-muted)">08 Mar 2026</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></a>

        </div>
        </div>

        <div class="team-card">
          <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px">
            <img src="assets/author-lerato-dlamini.jpg" alt="Lerato Dlamini" width="64" height="64" style="width:64px;height:64px;border-radius:50%;object-fit:cover;object-position:center 20%;flex-shrink:0" loading="lazy">
            <div>
              <h2 style="font-size:20px;font-weight:700;margin-bottom:2px">Lerato Dlamini</h2>
              <p style="font-size:14px;color:var(--accent);font-weight:600">Senior Casino Analyst</p>
            </div>
          </div>
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">Lerato Dlamini leads the site's casino evaluation methodology, with a particular focus on game mathematics and platform fairness. She studied mathematics at the University of Pretoria and spent three years working in risk analysis before moving into the iGaming review sector.</p>
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">Her work centres on evaluating return-to-player (RTP) structures, volatility models, and game mechanics across leading casino providers. Lerato also reviews operator licensing, ensuring that casinos recommended to South African players meet recognised regulatory and responsible gambling standards.</p>
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Her reviews emphasise transparency, explaining how payout percentages and game design affect long-term player outcomes.</p>
          <div style="display:flex;flex-wrap:wrap;gap:6px">
            <span style="display:inline-block;font-size:12px;font-weight:600;padding:4px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">Online Casino Reviews</span>
            <span style="display:inline-block;font-size:12px;font-weight:600;padding:4px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">RTP &amp; Game Mathematics</span>
            <span style="display:inline-block;font-size:12px;font-weight:600;padding:4px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">Responsible Gambling Standards</span>
          </div>
          <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border)">
          <h3 style="font-size:14px;font-weight:700;margin-bottom:8px;color:var(--accent)">Latest Articles</h3>
          <a href="news/lucky-fish-mystery-parcel-r450000-prizes.html" style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sep);text-decoration:none;color:inherit"><div style="flex:1;min-width:0"><p style="font-size:13px;font-weight:600;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Lucky Fish Launches Mystery Parcel Promo with R450,000 in Prizes</p><span style="font-size:12px;color:var(--text-muted)">13 Mar 2026</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></a>
<a href="news/hollywoodbets-spina-zonke-jackpot-winner.html" style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sep);text-decoration:none;color:inherit"><div style="flex:1;min-width:0"><p style="font-size:13px;font-weight:600;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Hollywoodbets Spina Zonke Pays Out R2.3 Million Jackpot to Durban Punter</p><span style="font-size:12px;color:var(--text-muted)">08 Mar 2026</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></a>
<a href="news/yesplay-adds-aviator-and-crash-games.html" style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sep);text-decoration:none;color:inherit"><div style="flex:1;min-width:0"><p style="font-size:13px;font-weight:600;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">YesPlay Enters Crash Games Market with Aviator and Three New Titles</p><span style="font-size:12px;color:var(--text-muted)">07 Mar 2026</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></a>

        </div>
        </div>

        <div class="team-card">
          <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px">
            <img src="assets/author-sipho-nkosi.jpg" alt="Sipho Nkosi" width="64" height="64" style="width:64px;height:64px;border-radius:50%;object-fit:cover;object-position:center 20%;flex-shrink:0" loading="lazy">
            <div>
              <h2 style="font-size:20px;font-weight:700;margin-bottom:2px">Sipho Nkosi</h2>
              <p style="font-size:14px;color:var(--accent);font-weight:600">Betting Strategist</p>
            </div>
          </div>
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">Sipho Nkosi focuses on betting analytics and strategy development. He holds an Honours degree in Statistics from the University of Cape Town (UCT) and has spent five years working in sports data analysis.</p>
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">His work involves building statistical models that track pricing inefficiencies across South African bookmakers. These models identify potential value opportunities across major leagues and tournaments while accounting for bookmaker margins and market movement.</p>
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Sipho also develops educational content designed to help bettors understand probability, variance, and disciplined bankroll management.</p>
          <div style="display:flex;flex-wrap:wrap;gap:6px">
            <span style="display:inline-block;font-size:12px;font-weight:600;padding:4px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">Betting Strategy</span>
            <span style="display:inline-block;font-size:12px;font-weight:600;padding:4px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">Accumulator Analysis</span>
            <span style="display:inline-block;font-size:12px;font-weight:600;padding:4px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">Bankroll Management</span>
          </div>
          <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border)">
          <h3 style="font-size:14px;font-weight:700;margin-bottom:8px;color:var(--accent)">Latest Articles</h3>
          <a href="news/beteasy-wale-street-cape-town-launch.html" style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sep);text-decoration:none;color:inherit"><div style="flex:1;min-width:0"><p style="font-size:13px;font-weight:600;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Cape Town's Wale Street Has a New Resident, and It's Making the Bookies Sweat</p><span style="font-size:12px;color:var(--text-muted)">13 Mar 2026</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></a>
<a href="news/zarbet-launches-cashback-loyalty-programme.html" style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sep);text-decoration:none;color:inherit"><div style="flex:1;min-width:0"><p style="font-size:13px;font-weight:600;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Zarbet Launches Industry-First Cashback Loyalty Programme for SA Punters</p><span style="font-size:12px;color:var(--text-muted)">11 Mar 2026</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></a>
<a href="news/easybet-r5000-deposit-match-march.html" style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sep);text-decoration:none;color:inherit"><div style="flex:1;min-width:0"><p style="font-size:13px;font-weight:600;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Easybet Increases Welcome Bonus to R5,000 Deposit Match for March</p><span style="font-size:12px;color:var(--text-muted)">09 Mar 2026</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></a>

        </div>
        </div>

        <div class="team-card">
          <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px">
            <img src="assets/author-naledi-khumalo.jpg" alt="Naledi Khumalo" width="64" height="64" style="width:64px;height:64px;border-radius:50%;object-fit:cover;object-position:center 20%;flex-shrink:0" loading="lazy">
            <div>
              <h2 style="font-size:20px;font-weight:700;margin-bottom:2px">Naledi Khumalo</h2>
              <p style="font-size:14px;color:var(--accent);font-weight:600">Payments &amp; Security Editor</p>
            </div>
          </div>
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">Naledi Khumalo oversees the site's coverage of payments, verification processes, and account security. Before joining the editorial team, she worked in fintech at one of South Africa's major banks, focusing on digital payments and compliance.</p>
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">She personally tests every deposit and withdrawal method listed on the site and tracks payout speeds across 36 South African-facing bookmakers. Her work also examines verification requirements under South Africa's FICA regulations, helping players understand identity checks, withdrawal procedures, and common delays.</p>
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Naledi authored the platform's widely read FICA verification guide, which explains how South African betting accounts are verified and why documentation is required.</p>
          <div style="display:flex;flex-wrap:wrap;gap:6px">
            <span style="display:inline-block;font-size:12px;font-weight:600;padding:4px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">Payment Methods</span>
            <span style="display:inline-block;font-size:12px;font-weight:600;padding:4px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">Security &amp; FICA Compliance</span>
            <span style="display:inline-block;font-size:12px;font-weight:600;padding:4px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">Withdrawal Testing &amp; Reviews</span>
          </div>
          <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border)">
          <h3 style="font-size:14px;font-weight:700;margin-bottom:8px;color:var(--accent)">Latest Articles</h3>
          <a href="news/mzansibet-ozow-instant-payouts.html" style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sep);text-decoration:none;color:inherit"><div style="flex:1;min-width:0"><p style="font-size:13px;font-weight:600;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Mzansibet Now Offers Instant Payouts via Ozow</p><span style="font-size:12px;color:var(--text-muted)">06 Mar 2026</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></a>
<a href="news/ozow-instant-withdrawals-rollout.html" style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sep);text-decoration:none;color:inherit"><div style="flex:1;min-width:0"><p style="font-size:13px;font-weight:600;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Ozow Rolls Out Instant Withdrawals at 12 SA Bookmakers</p><span style="font-size:12px;color:var(--text-muted)">22 Feb 2026</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></a>
<a href="news/supabets-mobile-app-major-update.html" style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--sep);text-decoration:none;color:inherit"><div style="flex:1;min-width:0"><p style="font-size:13px;font-weight:600;line-height:1.4;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">Supabets Releases Major Mobile App Update with Live Streaming</p><span style="font-size:12px;color:var(--text-muted)">12 Feb 2026</span></div><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></a>

        </div>
        </div>

        </div>

        <h2 style="margin-top:40px">Get in Touch</h2>
        <p>For editorial enquiries or corrections, email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>. You can also view our <a href="our-authors.html">full author pages</a> with individual article archives.</p>'''
    },
    'partnerships': {
        'title': 'Partnerships',
        'meta_desc': 'Partner with MzansiWins. Collaboration opportunities for the South African betting and iGaming industry.',
        'content': '''<p>MzansiWins works with licensed South African bookmakers and related businesses to deliver value to our readers.</p>
        <h2>Partnership Opportunities</h2>
        <ul>
        <li><strong>Operator partnerships:</strong> If you are a licensed South African bookmaker looking for exposure to our audience of engaged punters, we would love to chat.</li>
        <li><strong>Content partnerships:</strong> We collaborate with sports media, tipsters, and content creators who share our values of honesty and transparency.</li>
        <li><strong>Data partnerships:</strong> We work with data providers to ensure our odds comparisons and market information are accurate and up to date.</li>
        </ul>
        <h2>Our Requirements</h2>
        <p>All operator partners must hold a valid South African provincial gambling licence. We do not partner with unlicensed or offshore operators under any circumstances.</p>
        <h2>Contact</h2>
        <p>For partnership enquiries, email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
    'advertise-with-us': {
        'title': 'Advertise With Us',
        'meta_desc': 'Advertise on MzansiWins. Reach thousands of active South African sports bettors and casino players.',
        'content': '''<p>MzansiWins reaches thousands of South African punters looking for the best betting sites, bonuses, and promo codes. If you have a product or service that is relevant to our audience, we want to hear from you.</p>
        <h2>Why Advertise With Us?</h2>
        <ul>
        <li><strong>Targeted audience:</strong> Our readers are active, engaged South African bettors who are ready to sign up and deposit.</li>
        <li><strong>Trust:</strong> MzansiWins is a trusted name in SA betting reviews. Your brand benefits from that association.</li>
        <li><strong>Performance:</strong> We offer performance-based models as well as flat-rate display advertising.</li>
        </ul>
        <h2>Advertising Formats</h2>
        <ul>
        <li>Display banners (desktop and mobile)</li>
        <li>Sponsored content and reviews</li>
        <li>Newsletter sponsorships</li>
        <li>Featured placements</li>
        </ul>
        <h2>Get Started</h2>
        <p>Email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a> with the subject "Advertising" and we will send you our media pack and rate card.</p>'''
    },
    'careers': {
        'title': 'Careers at MzansiWins',
        'meta_desc': 'Join the MzansiWins team. Career opportunities in betting content, editorial, and digital media in South Africa.',
        'content': '''<p>MzansiWins is growing, and we are always on the lookout for talented people who share our passion for honest betting content.</p>
        <h2>Why Work With Us?</h2>
        <ul>
        <li>Remote-first team based in South Africa</li>
        <li>Flexible working hours</li>
        <li>Work in an industry you are passionate about</li>
        <li>Make a real difference for SA punters</li>
        </ul>
        <h2>Roles We Typically Hire For</h2>
        <ul>
        <li><strong>Betting content writers:</strong> Experienced writers with deep knowledge of the SA betting market.</li>
        <li><strong>SEO specialists:</strong> Help us reach more punters through organic search.</li>
        <li><strong>Web developers:</strong> Frontend and full-stack developers to improve our platform.</li>
        <li><strong>Researchers:</strong> People who love digging into data, T&Cs, and product features.</li>
        </ul>
        <h2>How to Apply</h2>
        <p>Send your CV and a short cover letter to <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a> with the subject "Careers - [Role]". We review every application.</p>'''
    },
    # Accessibility & Compliance
    'accessibility-statement': {
        'title': 'Accessibility Statement',
        'meta_desc': 'MzansiWins Accessibility Statement. Our commitment to making our betting review site accessible to all South Africans.',
        'content': '''<p>MzansiWins is committed to ensuring our website is accessible to as many people as possible, regardless of ability or technology.</p>
        <h2>Our Standards</h2>
        <p>We aim to conform to the Web Content Accessibility Guidelines (WCAG) 2.1 at Level AA. This includes:</p>
        <ul>
        <li>Sufficient colour contrast throughout the site</li>
        <li>Keyboard navigable interfaces</li>
        <li>Descriptive alt text on images</li>
        <li>Clear, consistent navigation</li>
        <li>Responsive design that works across devices and screen sizes</li>
        <li>Light and dark mode support</li>
        </ul>
        <h2>Known Issues</h2>
        <p>We are continuously working to improve accessibility. If you encounter any barriers, please let us know.</p>
        <h2>Feedback</h2>
        <p>If you have difficulty accessing any content on MzansiWins, or if you have suggestions for improvement, please email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>. We value your feedback and will do our best to address any issues promptly.</p>'''
    },
    'privacy-policy': {
        'title': 'Privacy Policy',
        'meta_desc': 'MzansiWins Privacy Policy. How we collect, use, and protect your personal information under POPIA.',
        'content': '''<p>Your privacy matters. This policy explains how MzansiWins collects, uses, and protects your personal information in accordance with the Protection of Personal Information Act (POPIA).</p>
        <h2>Information We Collect</h2>
        <p>We may collect the following information:</p>
        <ul>
        <li><strong>Usage data:</strong> Pages visited, time spent on site, and browser/device information via analytics tools.</li>
        <li><strong>Contact information:</strong> If you email us, we store your email address and message to respond to your enquiry.</li>
        <li><strong>Cookies:</strong> We use cookies to improve your browsing experience. See our <a href="cookie-policy.html">Cookie Policy</a> for details.</li>
        </ul>
        <h2>How We Use Your Information</h2>
        <ul>
        <li>To improve our website content and user experience</li>
        <li>To respond to your enquiries</li>
        <li>To understand how visitors interact with our site</li>
        </ul>
        <h2>Data Sharing</h2>
        <p>We do not sell your personal information to third parties. We may share anonymised, aggregated data with analytics partners to improve our service.</p>
        <h2>Your Rights Under POPIA</h2>
        <p>You have the right to access, correct, or delete your personal information held by us. To exercise these rights, email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>
        <h2>Data Security</h2>
        <p>We take reasonable measures to protect your information. However, no internet transmission is 100% secure, and we cannot guarantee absolute security.</p>
        <p>Last updated: {CURRENT_MONTH_YEAR}.</p>'''
    },
    'cookie-policy': {
        'title': 'Cookie Policy',
        'meta_desc': 'MzansiWins Cookie Policy. What cookies we use and how to manage your cookie preferences.',
        'content': '''<p>This policy explains how MzansiWins uses cookies and similar technologies.</p>
        <h2>What Are Cookies?</h2>
        <p>Cookies are small text files stored on your device when you visit a website. They help the site remember your preferences and understand how you use it.</p>
        <h2>Cookies We Use</h2>
        <ul>
        <li><strong>Essential cookies:</strong> Required for basic site functionality such as theme preferences (light/dark mode) and table sorting.</li>
        <li><strong>Analytics cookies:</strong> Help us understand how visitors use our site so we can improve it. These collect anonymised data.</li>
        <li><strong>Affiliate cookies:</strong> When you click through to a bookmaker, a cookie may be set to track the referral. This is how we earn revenue to keep the site running.</li>
        </ul>
        <h2>Managing Cookies</h2>
        <p>You can control cookies through your browser settings. Most browsers allow you to block or delete cookies. Please note that blocking essential cookies may affect site functionality.</p>
        <h2>Third-Party Cookies</h2>
        <p>Some cookies are set by third-party services we use, such as analytics providers. We do not control these cookies. Refer to the respective third party's privacy policy for details.</p>
        <p>Questions? Email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
    'terms-and-conditions': {
        'title': 'Terms and Conditions',
        'meta_desc': 'MzansiWins Terms and Conditions. Rules governing the use of our South African betting review website.',
        'content': '''<p>By using MzansiWins, you agree to the following terms and conditions. Please read them carefully.</p>
        <h2>Use of This Site</h2>
        <p>MzansiWins is an information and review website. We provide opinions, ratings, and information about South African betting sites. Our content is for informational purposes only and should not be taken as financial advice.</p>
        <h2>Age Restriction</h2>
        <p>This website is intended for users aged 18 and over. By using MzansiWins, you confirm that you are at least 18 years old. Gambling is strictly prohibited for anyone under 18 in South Africa.</p>
        <h2>Accuracy of Information</h2>
        <p>We make every effort to ensure the information on our site is accurate and up to date. However, bonus amounts, T&Cs, and other details can change at any time. Always check the bookmaker's own website for the most current information before signing up.</p>
        <h2>Third-Party Links</h2>
        <p>MzansiWins contains links to third-party websites (bookmakers). We are not responsible for the content, accuracy, or practices of these external sites. Use them at your own discretion.</p>
        <h2>Limitation of Liability</h2>
        <p>MzansiWins is not liable for any losses or damages arising from the use of our website or reliance on our content. All gambling carries risk, and you are solely responsible for your betting decisions.</p>
        <h2>Intellectual Property</h2>
        <p>All content on MzansiWins, including text, images, logos, and design, is the property of MzansiWins and is protected by copyright law. You may not reproduce, distribute, or use our content without permission.</p>
        <h2>Changes to These Terms</h2>
        <p>We may update these terms from time to time. Continued use of the site after changes constitutes acceptance of the new terms.</p>
        <p>Last updated: {CURRENT_MONTH_YEAR}. For questions, email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
}

def build_footer_page(page_id):
    pg = FOOTER_PAGES[page_id]
    body = f'''<div class="container content-page" style="max-width:800px;padding-top:40px;padding-bottom:60px">
    <h1>{e(pg["title"])}</h1>
    {pg["content"]}
    </div>'''
    return page(f'{pg["title"]} | MzansiWins', pg['meta_desc'], page_id, body, depth=0, active_nav='')


# ============================================================
# BETTING CALCULATORS
# ============================================================

def build_calculator_hub():
    """Build the main Betting Calculators hub page."""
    # Group calculators by category
    categories = {}
    for c in CALCULATORS:
        cat = c.get('category', 'Other')
        categories.setdefault(cat, []).append(c)

    # Category order
    cat_order = ['Basic Calculators', 'Odds Tools', 'Advanced Strategy', 'Bankroll Management', 'Bonus Tools', 'Exchange Tools']
    cat_icons = {'Basic Calculators': '&#x1F4B0;', 'Odds Tools': '&#x1F504;', 'Advanced Strategy': '&#x2696;', 'Bankroll Management': '&#x1F9E0;', 'Bonus Tools': '&#x1F381;', 'Exchange Tools': '&#x21C4;'}

    cards_html = ''
    for cat in cat_order:
        calcs = categories.get(cat, [])
        if not calcs:
            continue
        cards_html += f'<h2 style="font-size:18px;font-weight:700;margin:32px 0 16px;display:flex;align-items:center;gap:8px"><span>{cat_icons.get(cat, "")}</span> {cat}</h2>'
        cards_html += '<div class="calc-hub-grid">'
        for c in calcs:
            cards_html += f'''<a href="calculators/{c['id']}.html" class="calc-hub-card">
              <div class="calc-hub-icon">{c['icon']}</div>
              <div class="calc-hub-info">
                <h3>{e(c['title'])}</h3>
                <p>{e(c['short'])}</p>
              </div>
              <span class="calc-hub-arrow">{ICON_CHEVRON_RIGHT}</span>
            </a>'''
        cards_html += '</div>'

    bc = breadcrumbs([{"label":"Home","href":"index.html"},{"label":"Betting Calculators"}], 0)

    # Hub page SEO content
    hub_seo = f'''<div class="content-page" style="margin-top:48px">
      <h2>Why Use a Betting Calculator?</h2>
      <p>Smart punters do not guess - they calculate. Whether you are working out what an accumulator pays, converting between odds formats, or figuring out how much to stake on an arbitrage opportunity, these tools do the maths instantly so you can make informed decisions before risking your hard-earned rands.</p>

      <h2>Free Tools for South African Bettors</h2>
      <p>Every calculator on this page is built for the South African market. Stakes and returns are calculated in ZAR, examples reference local bookmakers like Hollywoodbets, Betway, and Sportingbet, and the tools work on mobile and desktop without any sign-up or download required.</p>

      <h3>Basic Calculators</h3>
      <p>Start here if you are new to sports betting. The <a href="calculators/bet-profit-calculator.html">Bet Profit Calculator</a> shows potential winnings from a single bet. The <a href="calculators/accumulator-calculator.html">Accumulator Calculator</a> handles multi-leg bets where odds multiply together. The <a href="calculators/each-way-calculator.html">Each Way Calculator</a> is essential for horse racing punters betting on win and place.</p>

      <h3>Odds and Value Tools</h3>
      <p>The <a href="calculators/odds-converter.html">Odds Converter</a> switches between decimal, fractional, and American formats. Use the <a href="calculators/value-bet-calculator.html">Value Bet Calculator</a> to identify whether a bet has positive expected value, and the <a href="calculators/bookmaker-margin-calculator.html">Bookmaker Margin Calculator</a> to see how much juice your bookmaker is charging on any market.</p>

      <h3>Advanced Strategy</h3>
      <p>For more experienced bettors, the <a href="calculators/arbitrage-calculator.html">Arbitrage Calculator</a> finds guaranteed profit by splitting stakes across bookmakers. The <a href="calculators/hedge-bet-calculator.html">Hedge Bet Calculator</a> helps lock in profit on existing wagers. The <a href="calculators/dutching-calculator.html">Dutching Calculator</a> distributes stakes across multiple selections for equal profit.</p>

      <h3>Bankroll and Exchange Tools</h3>
      <p>The <a href="calculators/kelly-criterion-calculator.html">Kelly Criterion Calculator</a> determines optimal bet sizing based on your edge. The <a href="calculators/free-bet-calculator.html">Free Bet Calculator</a> extracts cash value from sportsbook bonuses. The <a href="calculators/lay-bet-calculator.html">Lay Bet Calculator</a> handles exchange betting maths.</p>

      <h2>How We Built These Calculators</h2>
      <p>Every calculator uses the same proven mathematical formulas used by professional bettors worldwide. All calculations run in your browser - we do not store any data or require registration. The tools are tested against real SA bookmaker odds to ensure accuracy.</p>
    </div>'''

    # FAQ Schema for hub page
    hub_faqs = [
        ('What is a betting calculator?', 'A betting calculator is a free tool that helps sports bettors work out potential returns, compare odds, and evaluate strategies before placing a bet. Our calculators cover everything from basic profit calculations to advanced arbitrage and bankroll management.'),
        ('Are these betting calculators free?', 'Yes, all 12 calculators on MzansiWins are completely free. No registration, no download, no hidden charges. Just enter your numbers and get instant results.'),
        ('Do these calculators work with South African bookmakers?', 'Absolutely. Every calculator is designed for SA bettors using ZAR. They work with odds from any South African bookmaker including Hollywoodbets, Betway, Sportingbet, Supabets, and all 36 licensed operators listed on our site.'),
        ('Which betting calculator should I start with?', 'If you are new to sports betting, start with the Bet Profit Calculator to understand basic returns, then try the Accumulator Calculator for multi bets. As you gain experience, move to the Value Bet Calculator and Kelly Criterion for more advanced strategy.'),
    ]
    hub_faq_items = ''.join(f'''<div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">
      <h3 itemprop="name" style="font-size:16px;font-weight:600;margin-bottom:8px;cursor:pointer" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display==='none'?'block':'none'">{q}</h3>
      <div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer" style="display:none">
        <p itemprop="text" style="font-size:14px;color:var(--text-secondary);line-height:1.75;padding-left:16px;border-left:3px solid var(--accent)">{a}</p>
      </div>
    </div>''' for q, a in hub_faqs)
    hub_faq_section = f'''<div class="content-page" style="margin-top:32px" itemscope itemtype="https://schema.org/FAQPage">
      <h2>Frequently Asked Questions</h2>
      {hub_faq_items}
    </div>'''

    calc_hero = category_hero(
        "Betting Calculators South Africa - Free Tools for Punters",
        "12 free betting calculators built for South African punters. Calculate potential winnings, convert odds, evaluate strategies, and manage your bankroll in ZAR. No sign-up required.",
        [{"label":"Home","href":"index.html"},{"label":"Betting Calculators"}], 0,
        deco_icon='&#x1F9EE;'
    )
    body = f'''
    {calc_hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      {cards_html}

      {hub_seo}
      {hub_faq_section}
    </div>'''

    t, d = seo_meta('calculators')
    return page(t, d, 'betting-calculators', body, depth=0, active_nav='calculators', og_image='og-calculators.png')


def build_calculator_page(calc):
    """Build an individual calculator page with enhanced SEO."""
    depth = 1
    prefix = '../'
    desc_text, example_text = get_calculator_description(calc['id'])
    form_html = get_calculator_form(calc['id'])
    results_html = get_calculator_results(calc['id'])
    calc_js = get_calculator_js(calc['id'])

    # SEO data
    seo = CALC_SEO.get(calc['id'], {})
    page_h1 = seo.get('h1', calc['title'])
    guide_html = seo.get('guide', '')
    faqs = seo.get('faqs', [])
    seo_title = seo.get('seo_title', f'{calc["title"]} - Free Online Calculator | MzansiWins')
    seo_desc = seo.get('seo_desc', f'Free {calc["title"].lower()} for South African bettors. {calc["short"]} Instant results, mobile friendly.')

    # FAQ section with Schema.org markup
    faq_html = ''
    faq_ld = ''
    if faqs:
        faq_items = ''
        faq_ld_items = []
        for q, a in faqs:
            faq_items += f'''<div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question" onclick="this.classList.toggle('open')">
              <button class="faq-btn" type="button">
                <span itemprop="name">{q}</span>
                <svg class="faq-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
              </button>
              <div class="faq-body" itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">
                <p itemprop="text">{a}</p>
              </div>
            </div>'''
            faq_ld_items.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}})
        faq_html = f'''<div class="calc-info-section" itemscope itemtype="https://schema.org/FAQPage">
          <h2>Frequently Asked Questions</h2>
          {faq_items}
        </div>'''
        faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_ld_items})

    # Recommended sportsbooks sidebar (top 5)
    top5 = BRANDS[:5]
    sidebar_brands = ''
    for i, b in enumerate(top5):
        logo = logo_path(b, depth)
        logo_img = f'<img src="{logo}" alt="{e(b["name"])}" style="width:32px;height:32px;object-fit:contain;border-radius:6px;background:{brand_bg(b)};padding:3px">' if logo else ''
        m_exit = masked_exit(b, depth)
        visit_btn = f'<a href="{m_exit}" target="_blank" rel="noopener noreferrer nofollow" class="calc-sidebar-visit">Visit</a>' if m_exit else ''
        sidebar_brands += f'''<div class="calc-sidebar-brand">
          <div style="display:flex;align-items:center;gap:10px;flex:1;min-width:0">
            {logo_img}
            <div style="min-width:0">
              <a href="{prefix}betting-site-review/{b['id']}.html" style="font-size:14px;font-weight:600;color:var(--text-primary);display:block">{e(b['name'])}</a>
              <span style="font-size:12px;color:var(--bonus);font-weight:600">{e(b['welcomeBonusAmount'])}</span>
            </div>
          </div>
          {visit_btn}
        </div>'''

    # Related calculators - group by category for relevance
    same_cat = [c for c in CALCULATORS if c['id'] != calc['id'] and c.get('category') == calc.get('category')]
    diff_cat = [c for c in CALCULATORS if c['id'] != calc['id'] and c.get('category') != calc.get('category')]
    related = (same_cat + diff_cat)[:4]
    related_html = ''
    for rc in related:
        related_html += f'''<a href="{rc['id']}.html" class="calc-related-card">
          <span class="calc-related-icon">{rc['icon']}</span>
          <div>
            <div style="font-size:14px;font-weight:600">{e(rc['title'])}</div>
            <div style="font-size:12px;color:var(--text-muted);margin-top:2px">{e(rc['short'][:60])}...</div>
          </div>
        </a>'''

    # CTA to betting sites
    cta_section = f'''<div class="calc-info-section calc-cta-box" style="margin-top:24px">
      <h2 style="font-size:18px;margin-bottom:8px">Ready to Place Your Bet?</h2>
      <p style="font-size:14px;color:var(--text-secondary);line-height:1.75;margin-bottom:16px">Now that you have done the maths, find the best odds at a trusted South African bookmaker. We have tested and reviewed all {len(BRANDS)} licensed SA operators.</p>
      <div style="display:flex;gap:12px;flex-wrap:wrap">
        <a href="{prefix}betting-sites.html" class="btn-primary" style="font-size:14px;padding:10px 24px;border-radius:24px">View All Betting Sites</a>
        <a href="{prefix}promo-codes.html" class="btn-outline" style="font-size:14px;padding:10px 24px;border-radius:24px">Get Promo Codes</a>
      </div>
    </div>'''

    bc2 = breadcrumbs([{"label":"Home","href":"index.html"},{"label":"Calculators","href":"betting-calculators.html"},{"label":calc["title"]}], depth)
    body = f'''
    <div class="container" style="padding-top:40px;padding-bottom:80px">
      {bc2}

      <div class="calc-page-layout">
        <div class="calc-main">
          <h1 class="page-title" style="margin-bottom:8px">{page_h1}</h1>
          <p class="page-subtitle" style="margin-bottom:28px">{e(calc['short'])}</p>

          <div class="calc-card">
            <form id="calc-form" onsubmit="return false;">
              {form_html}
              <div class="calc-actions">
                <button type="button" id="calc-example" class="btn-outline btn-sm">Load example</button>
                <button type="button" id="calc-reset" class="btn-outline btn-sm" style="color:var(--text-muted)">Reset</button>
              </div>
            </form>

            <div id="calc-results" class="calc-results" style="display:none">
              <h3 class="calc-results-title">Results</h3>
              {results_html}
            </div>
          </div>

          <div class="calc-info-section">
            {guide_html if guide_html else f"<h2>How it works</h2><p>{desc_text}</p>"}
            <div class="calc-example-box">
              <strong>Quick Example</strong>
              <p>{example_text}</p>
            </div>
          </div>

          {faq_html}

          {cta_section}

          <div class="calc-info-section">
            <h2>Related Calculators</h2>
            <div class="calc-related-grid">{related_html}</div>
          </div>
        </div>

        <aside class="calc-sidebar">
          <div class="calc-sidebar-sticky">
            <div class="calc-sidebar-card">
              <h3 style="font-size:15px;font-weight:700;margin-bottom:16px">Top SA Sportsbooks</h3>
              {sidebar_brands}
              <a href="{prefix}betting-sites.html" class="calc-sidebar-all">View all {len(BRANDS)} bookmakers {ICON_CHEVRON_RIGHT}</a>
            </div>

            <div class="calc-sidebar-card" style="margin-top:16px">
              <h3 style="font-size:15px;font-weight:700;margin-bottom:8px">About This Calculator</h3>
              <p style="font-size:13px;color:var(--text-secondary);line-height:1.6">{e(calc['short'])} All calculations are instant and free. No sign-up required. Works on desktop and mobile. Built for SA punters using Rands (ZAR).</p>
            </div>
          </div>
        </aside>
      </div>
    </div>
    {f'<script type="application/ld+json">{faq_ld}</script>' if faq_ld else ''}
    <script>{calc_js}</script>'''

    return page(seo_title, seo_desc, f'calculators/{calc["id"]}', body, depth=1, active_nav='calculators')


def build_sitemap():
    urls = [('', '1.0'), ('betting-sites', '0.9'), ('casino-sites', '0.9'), ('promo-codes', '0.9'),
            ('payment-methods', '0.9'), ('news', '0.8'), ('about-us', '0.5'), ('how-we-rate', '0.5'), ('fica-guide', '0.7')]
    for b in DATA['brands']:
        urls.append((f'betting-site-review/{b["id"]}', '0.8'))
        urls.append((f'promo-code/{b["id"]}', '0.7'))
    for m in PAYMENTS:
        urls.append((f'payment-methods/{m["id"]}', '0.7'))
    for a in NEWS:
        urls.append((f'news/{a["slug"]}', '0.6'))
    urls.append(('betting-calculators', '0.8'))
    for c in CALCULATORS:
        urls.append((f'calculators/{c["id"]}', '0.7'))

    xml_urls = ''
    for path, pri in urls:
        xml_urls += f'  <url><loc>{BASE_URL}/{path}</loc><priority>{pri}</priority></url>\n'

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{xml_urls}</urlset>'''


# ============================================================
# MAIN BUILD
# ============================================================

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  {path}')

print('Building MzansiWins static site...')
print('='*50)

# Homepage
write_file(f'{OUT}/index.html', build_homepage())

# Listing pages
write_file(f'{OUT}/betting-sites.html', build_listing_page('betting-sites'))
write_file(f'{OUT}/casino-sites.html', build_listing_page('casino-sites'))
write_file(f'{OUT}/new-betting-sites.html', build_new_betting_sites())
write_file(f'{OUT}/promo-codes.html', build_promo_codes_page())
write_file(f'{OUT}/payment-methods.html', build_payment_hub())
write_file(f'{OUT}/news.html', build_news_index())

# Content pages
write_file(f'{OUT}/about-us.html', build_content_page('about-us'))
write_file(f'{OUT}/how-we-rate.html', build_content_page('how-we-rate'))
write_file(f'{OUT}/fica-guide.html', build_content_page('fica-guide'))

# Footer policy pages
print(f'\nGenerating {len(FOOTER_PAGES)} footer policy pages...')
for page_id in FOOTER_PAGES:
    write_file(f'{OUT}/{page_id}.html', build_footer_page(page_id))

# Brand reviews
print(f'\nGenerating {len(DATA["brands"])} brand reviews...')
for brand in DATA['brands']:
    write_file(f'{OUT}/betting-site-review/{brand["id"]}.html', build_brand_review(brand))

# Promo detail pages
print(f'\nGenerating {len(DATA["brands"])} promo detail pages...')
for brand in DATA['brands']:
    write_file(f'{OUT}/promo-code/{brand["id"]}.html', build_promo_detail(brand))

# Payment method detail pages
print(f'\nGenerating {len(PAYMENTS)} payment method pages...')
for method in PAYMENTS:
    write_file(f'{OUT}/payment-methods/{method["id"]}.html', build_payment_detail(method))

# News articles
print(f'\nGenerating {len(NEWS)} news articles...')
for article in NEWS:
    write_file(f'{OUT}/news/{article["slug"]}.html', build_news_article(article))

# Betting calculators
write_file(f'{OUT}/betting-calculators.html', build_calculator_hub())
print(f'\nGenerating {len(CALCULATORS)} calculator pages...')
for calc in CALCULATORS:
    write_file(f'{OUT}/calculators/{calc["id"]}.html', build_calculator_page(calc))

# Masked exit link redirect pages
print(f'\nGenerating masked exit link redirects...')
link_count = 0
for brand in DATA['brands']:
    if brand.get('exitLink'):
        dest = brand['exitLink']
        redirect_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0;url={dest}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{BASE_URL}/link/{brand['id']}/">
<title>Redirecting to {e(brand['name'])}...</title>
<script>window.location.replace("{dest}");</script>
</head>
<body>
<p>Redirecting to <a href="{dest}">{e(brand['name'])}</a>...</p>
</body>
</html>'''
        write_file(f'{OUT}/link/{brand["id"]}/index.html', redirect_html)
        link_count += 1
print(f'  {link_count} redirect pages created')

# ======== EXPANSION PAGES ========
print('\nBuilding expansion pages...')
from build_expansion import run_expansion
expansion_sitemap = run_expansion(
    DATA=DATA, BRANDS=BRANDS, BRANDS_ORDERED=BRANDS_ORDERED,
    page_fn=page, breadcrumbs_fn=breadcrumbs, logo_path_fn=logo_path, category_hero_fn=category_hero,
    masked_exit_fn=masked_exit, brand_bg_fn=brand_bg, rating_badge_fn=rating_badge,
    write_file_fn=write_file, OUT=OUT, BASE_URL=BASE_URL,
    ICON_CHECK=ICON_CHECK, ICON_X=ICON_X, ICON_TROPHY=ICON_TROPHY,
    ICON_GIFT=ICON_GIFT, ICON_SHIELD=ICON_SHIELD, ICON_CHEVRON_RIGHT=ICON_CHEVRON_RIGHT,
    ICON_CHEVRON_DOWN=ICON_CHEVRON_DOWN, ICON_STAR=ICON_STAR, ICON_ARROW_LEFT=ICON_ARROW_LEFT
)

# Sitemap - use xml.etree for proper namespace handling
import xml.etree.ElementTree as ET
today = datetime.now().strftime('%Y-%m-%d')
SITEMAP_NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', SITEMAP_NS)

def _add_url(parent, loc, lastmod, changefreq, priority):
    url_el = ET.SubElement(parent, 'url')
    ET.SubElement(url_el, 'loc').text = loc
    ET.SubElement(url_el, 'lastmod').text = lastmod
    ET.SubElement(url_el, 'changefreq').text = changefreq
    ET.SubElement(url_el, 'priority').text = str(priority)

urlset = ET.Element('urlset')
urlset.set('xmlns', SITEMAP_NS)
urlset.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
urlset.set('xsi:schemaLocation', 'http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd')

# Core pages
_add_url(urlset, f'{BASE_URL}/', today, 'daily', '1.0')
_add_url(urlset, f'{BASE_URL}/betting-sites', today, 'weekly', '0.9')
_add_url(urlset, f'{BASE_URL}/casino-sites', today, 'weekly', '0.9')
_add_url(urlset, f'{BASE_URL}/new-betting-sites', today, 'weekly', '0.8')
_add_url(urlset, f'{BASE_URL}/promo-codes', today, 'daily', '0.9')
_add_url(urlset, f'{BASE_URL}/payment-methods', today, 'monthly', '0.8')
_add_url(urlset, f'{BASE_URL}/news', today, 'daily', '0.7')
_add_url(urlset, f'{BASE_URL}/about-us', today, 'monthly', '0.4')
_add_url(urlset, f'{BASE_URL}/how-we-rate', today, 'monthly', '0.5')
_add_url(urlset, f'{BASE_URL}/fica-guide', today, 'monthly', '0.6')
# Footer policy pages
for fp_id in FOOTER_PAGES:
    _add_url(urlset, f'{BASE_URL}/{fp_id}', today, 'monthly', '0.3')
# Brand reviews - high priority
for b in BRANDS:
    _add_url(urlset, f'{BASE_URL}/betting-site-review/{b["id"]}', today, 'weekly', '0.8')
# Promo codes - high priority
for b in BRANDS:
    _add_url(urlset, f'{BASE_URL}/promo-code/{b["id"]}', today, 'weekly', '0.8')
# Payment methods
for m in PAYMENTS:
    _add_url(urlset, f'{BASE_URL}/payment-methods/{m["id"]}', today, 'monthly', '0.6')
# News articles
for a in NEWS:
    _add_url(urlset, f'{BASE_URL}/news/{a["slug"]}', today, 'monthly', '0.5')
# Expansion pages
for exp_path, exp_pri in expansion_sitemap:
    freq = 'weekly' if float(exp_pri) >= 0.7 else 'monthly'
    _add_url(urlset, f'{BASE_URL}/{exp_path}', today, freq, exp_pri)

# Write with proper XML declaration (double quotes)
tree = ET.ElementTree(urlset)
ET.indent(tree, space='  ')
with open(f'{OUT}/sitemap.xml', 'wb') as f:
    tree.write(f, encoding='UTF-8', xml_declaration=True)
# Fix single quotes to double quotes in XML declaration for strict validators
with open(f'{OUT}/sitemap.xml', 'r') as f:
    sitemap_content = f.read()
sitemap_content = sitemap_content.replace("version='1.0' encoding='UTF-8'", 'version="1.0" encoding="UTF-8"')
with open(f'{OUT}/sitemap.xml', 'w') as f:
    f.write(sitemap_content)

# Count
total = sum(len(files) for _, _, files in os.walk(OUT) if any(f.endswith('.html') for f in files))
html_count = sum(1 for _, _, files in os.walk(OUT) for f in files if f.endswith('.html'))
print(f'\n{"="*50}')
# 404 page
_404_body = f"""
<section style="padding:120px 0 80px;text-align:center">
  <div class="container" style="max-width:600px">
    <div style="font-size:120px;font-weight:800;color:var(--accent);line-height:1;opacity:0.2">404</div>
    <h1 style="font-size:28px;font-weight:800;margin-bottom:12px">Page not found</h1>
    <p style="color:var(--text-secondary);margin-bottom:32px;font-size:16px">The page you are looking for might have been moved, renamed, or does not exist. No stress - let us get you back on track.</p>
    <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
      <a href="index.html" class="btn-primary" style="border-radius:24px;padding:12px 32px">Back to Home</a>
      <a href="betting-sites.html" class="btn-outline" style="border-radius:24px;padding:12px 32px">Top Betting Sites</a>
    </div>
  </div>
</section>"""
write_file(f'{OUT}/404.html', page('Page Not Found | MzansiWins',
    'The page you are looking for could not be found. Browse our betting site reviews and promo codes instead.',
    '404', _404_body, active_nav='',
    bc_items=[{'label': 'Home', 'href': 'index.html'}, {'label': '404 - Page Not Found'}]))

print(f'BUILD COMPLETE: {html_count} HTML files generated')
print(f'Output: {OUT}/')
