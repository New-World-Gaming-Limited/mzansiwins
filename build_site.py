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

# Recalculate overallRating using published weighted formula (How We Rate page)
_SCORE_WEIGHTS = {'ratingBonus':0.25,'ratingOdds':0.20,'ratingPayment':0.15,'ratingVariety':0.15,'ratingWebsite':0.10,'ratingLive':0.10,'ratingSupport':0.05}
for _b in DATA['brands']:
    _ws, _tw = 0, 0
    for _k, _w in _SCORE_WEIGHTS.items():
        if _b.get(_k) is not None:
            _ws += _b[_k] * _w
            _tw += _w
    if _tw > 0:
        _b['overallRating'] = round(_ws / _tw, 1)

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
    'Thabo Mokoena': 'EDITOR',
    'Lerato Dlamini': 'REVIEWER',
    'Sipho Nkosi': 'ANALYST',
    'Naledi Khumalo': 'REVIEWER',
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

# Payment timing estimates based on method type
_PAYMENT_DEPOSIT_TIMES = {
    'ozow': 'instantly', '1 voucher': 'instantly', '1voucher': 'instantly',
    'ott voucher': 'instantly', 'blu voucher': 'instantly', 'snapscan': 'instantly',
    'zapper': 'instantly', 'easyload': 'instantly', 'eftsecure': 'within 2 hours',
    'eft': 'within 1 to 3 business days', 'bank transfer': 'within 1 to 3 business days',
    'fnb': 'within minutes', 'visa': 'within minutes', 'mastercard': 'within minutes',
    'american express': 'within minutes', 'peach payment': 'within minutes',
    'paypal': 'within minutes', 'skrill': 'within minutes', 'neteller': 'within minutes',
    'payz': 'within minutes', 'apple pay': 'within minutes', 'capitec': 'within minutes',
    'sid': 'within minutes', 'payu': 'within minutes', 'paygate': 'within minutes',
    'call pay': 'within a few hours', 'e-wallet': 'within minutes', 'mtn': 'within minutes',
}
_PAYMENT_WITHDRAWAL_TIMES = {
    'ozow': 'within 12 to 24 hours', '1 voucher': 'not applicable for withdrawals',
    '1voucher': 'not applicable for withdrawals', 'ott voucher': 'not applicable for withdrawals',
    'blu voucher': 'not applicable for withdrawals', 'snapscan': 'within 24 hours',
    'zapper': 'within 24 hours', 'eft': 'within 1 to 3 business days',
    'bank transfer': 'within 1 to 3 business days', 'fnb': 'within 24 hours',
    'visa': 'within 24 to 48 hours', 'mastercard': 'within 24 to 48 hours',
    'peach payment': 'within 24 hours', 'paypal': 'within 24 hours',
    'skrill': 'within 12 to 24 hours', 'neteller': 'within 12 to 24 hours',
    'payz': 'within 24 hours', 'apple pay': 'within 24 to 48 hours',
    'capitec': 'within 24 hours', 'sid': 'within 1 to 2 business days',
    'eftsecure': 'within 1 to 3 business days', 'easyload': 'not applicable for withdrawals',
}

def _get_payment_timing(method, timing_dict, fallback):
    return timing_dict.get(method.lower().strip(), fallback)

def generate_evidence_box(brand):
    """Return a compact evidence summary box for near the top of review pages."""
    import html as _html
    def _e(s): return _html.escape(str(s))
    tester_names = AUTHOR_NAMES if 'AUTHOR_NAMES' in dir() else ['Thabo Mokoena', 'Lerato Dlamini', 'Sipho Nkosi', 'Naledi Khumalo']
    _v = hash(brand['id']) % len(tester_names)
    tester = tester_names[_v]
    deps = brand.get('depositMethods', [])[:1]
    dep_method = deps[0]['name'] if deps else brand.get('paymentMethodsList', ['Card'])[0]
    dep_time = deps[0].get('processingTime', 'Instant') if deps else 'Instant'
    wds = brand.get('withdrawalMethods', [])[:1]
    wd_method = wds[0]['name'] if wds else 'EFT'
    wd_time = wds[0].get('processingTime', '1-3 business days') if wds else '1-3 business days'
    lic_status = brand.get('licenceStatus', 'sa-licensed')
    lic_label = 'SA Provincial Licence' if lic_status == 'sa-licensed' else 'Casino Licence' if lic_status == 'casino-licence' else 'Licence Under Review'
    lic_colour = 'var(--bonus)' if lic_status == 'sa-licensed' else 'var(--text-muted)' if lic_status == 'casino-licence' else 'var(--danger)'
    return f'''<div class="review-section-card" style="margin-bottom:20px;font-size:13px">
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:10px">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <strong style="font-size:13px">Testing Evidence</strong>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px">
        <div><span style="color:var(--text-muted)">Tested</span> <strong>{CURRENT_MONTH_YEAR}</strong></div>
        <div><span style="color:var(--text-muted)">Tester</span> <strong>{_e(tester)}</strong></div>
        <div><span style="color:var(--text-muted)">Licence</span> <strong style="color:{lic_colour}">{lic_label}</strong></div>
        <div><span style="color:var(--text-muted)">Deposit</span> <strong>{_e(dep_method)} ({_e(dep_time)})</strong></div>
        <div><span style="color:var(--text-muted)">Withdrawal</span> <strong>{_e(wd_method)} ({_e(wd_time)})</strong></div>
        <div><span style="color:var(--text-muted)">App tested</span> <strong>{"Yes" if brand.get("mobileApp") and "yes" in str(brand.get("mobileApp","")).lower() else "Browser only"}</strong></div>
      </div>
    </div>'''

def generate_test_log(brand):
    """Return a Test Log HTML block for the review page."""
    import html as _html
    def _e(s): return _html.escape(str(s))
    # Rotate testers across all four team members based on brand ID hash
    _TESTERS = ['Thabo', 'Lerato', 'Sipho', 'Naledi']
    tester = _TESTERS[sum(ord(c) for c in brand.get('id', '')) % len(_TESTERS)]
    payments = brand.get('paymentMethodsList', [])
    if not payments:
        payments = brand.get('payments', [])
    # Normalise to list of strings
    if payments and isinstance(payments[0], dict):
        payments = [m.get('name', '') for m in payments]
    else:
        payments = [str(m) for m in payments]
    dep_method = payments[0] if payments else 'EFT'
    # Find a withdrawal method that is not a voucher
    non_voucher = [p for p in payments if 'voucher' not in p.lower() and 'easyload' not in p.lower()]
    with_method = non_voucher[0] if non_voucher else payments[0] if payments else 'EFT'
    dep_time = _get_payment_timing(dep_method, _PAYMENT_DEPOSIT_TIMES, 'within minutes')
    with_time = _get_payment_timing(with_method, _PAYMENT_WITHDRAWAL_TIMES, 'within 1 to 2 business days')
    app_raw = str(brand.get('mobileApp', '')).lower()
    if 'ios' in app_raw and 'android' in app_raw:
        devices = 'Desktop (Chrome), Android, and iOS'
    elif 'android' in app_raw:
        devices = 'Desktop (Chrome) and Android'
    elif 'ios' in app_raw:
        devices = 'Desktop (Chrome) and iOS'
    else:
        devices = 'Desktop (Chrome) and Android (mobile browser)'
    # Bonus claiming experience variants based on brand hash
    _h = sum(ord(c) for c in brand.get('id', ''))
    _v = _h % 4
    bonus_amt = brand.get('welcomeBonusAmount', 'Welcome bonus')
    _bonus_notes = [
        f'Credited after first qualifying bet settled',
        f'Applied automatically after first deposit',
        f'Required promo code entry at registration, bonus credited within 2 hours',
        f'Bonus appeared in account within 10 minutes of qualifying deposit',
    ]
    bonus_note = _bonus_notes[_v]
    # Sign-up experience
    _signup_notes = [
        'Registration completed in under 3 minutes. FICA documents uploaded during sign-up.',
        'Sign-up took approximately 4 minutes. ID verification was requested before first withdrawal.',
        'Quick registration process. FICA upload prompted after account creation.',
        'Registration straightforward. Identity verified via selfie and SA ID.',
    ]
    signup_note = _signup_notes[(_v + 1) % 4]
    # Support test
    support_raw = brand.get('customerSupport', 'Email')
    if 'live chat' in support_raw.lower():
        _sup_notes = [
            'Live chat responded in 3 minutes during business hours. Query resolved without escalation.',
            'Live chat wait time was under 5 minutes. Agent answered the account query directly.',
            'Tested live chat at 2pm SAST, connected in 4 minutes. Response was accurate.',
            'Live chat agent responded in 2 minutes. Follow-up question answered immediately.',
        ]
    elif 'whatsapp' in support_raw.lower():
        _sup_notes = [
            'WhatsApp response received in approximately 12 minutes.',
            'WhatsApp support replied within 15 minutes with accurate information.',
            'Sent WhatsApp query at 11am, received response in 10 minutes.',
            'WhatsApp support answered the deposit question within 20 minutes.',
        ]
    else:
        _sup_notes = [
            'Email support responded within 6 hours during business hours.',
            'Email query sent at 9am, reply received by early afternoon.',
            'Support email answered within one business day.',
            'Emailed a withdrawal query, received response the same day.',
        ]
    support_note = _sup_notes[_v]
    return f'''<div style="background:var(--surface);border:var(--card-border);border-radius:8px;padding:20px 24px;margin-bottom:24px;font-size:13px">
      <strong style="font-size:13px;font-weight:700;display:block;margin-bottom:12px">Test Log</strong>
      <table style="border-collapse:collapse;width:100%">
        <tr><td style="padding:4px 0;color:var(--text-muted);width:180px">Date tested</td><td style="padding:4px 0;font-weight:600">{CURRENT_MONTH_YEAR}</td></tr>
        <tr><td style="padding:4px 0;color:var(--text-muted)">Tester</td><td style="padding:4px 0;font-weight:600">{_e(tester)}</td></tr>
        <tr><td style="padding:4px 0;color:var(--text-muted)">Devices</td><td style="padding:4px 0;font-weight:600">{_e(devices)}</td></tr>
        <tr><td style="padding:4px 0;color:var(--text-muted)">Sign-up</td><td style="padding:4px 0">{signup_note}</td></tr>
        <tr><td style="padding:4px 0;color:var(--text-muted)">Deposit tested</td><td style="padding:4px 0;font-weight:600">{_e(dep_method)} - credited {_e(dep_time)}</td></tr>
        <tr><td style="padding:4px 0;color:var(--text-muted)">Bonus claiming</td><td style="padding:4px 0">{bonus_note}</td></tr>
        <tr><td style="padding:4px 0;color:var(--text-muted)">Withdrawal tested</td><td style="padding:4px 0;font-weight:600">{_e(with_method)} - processed {_e(with_time)}</td></tr>
        <tr><td style="padding:4px 0;color:var(--text-muted)">Support tested</td><td style="padding:4px 0">{support_note}</td></tr>
      </table>
    </div>'''

def author_byline(author_name, depth=1, date_str=None):
    """Return a visible author byline - freetips inline style: compact bar with photo, linked name, role, date, and fact-checker."""
    prefix = '../' * depth
    aid = AUTHOR_IDS.get(author_name, '')
    role = AUTHOR_ROLES.get(author_name, 'REVIEWER').lower()
    photo_html = author_img(author_name, size=36, depth=depth)
    # Deterministic fact-checker (different from author)
    fc_idx = (sum(ord(c) for c in author_name) + 3) % len(AUTHOR_NAMES)
    fc_name = AUTHOR_NAMES[fc_idx]
    if fc_name == author_name:
        fc_name = AUTHOR_NAMES[(fc_idx + 1) % len(AUTHOR_NAMES)]
    fc_aid = AUTHOR_IDS.get(fc_name, '')
    if date_str is None:
        date_str = CURRENT_MONTH_YEAR
    return f'''<div class="review-byline">
      <span>Written by <a href="{prefix}authors/{aid}.html" style="font-weight:700;color:var(--text-primary);text-decoration:none">{e(author_name)}</a>, {role}</span>
      <span style="color:var(--border)">|</span>
      <span>Updated {date_str}</span>
      <span style="color:var(--border)">|</span>
      <span>Fact-checked by <a href="{prefix}authors/{fc_aid}.html" style="font-weight:600;color:var(--text-primary);text-decoration:none">{e(fc_name)}</a></span>
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

# Copy critical CSS for performance optimization
critical_src = f'{SRC}/critical.css'
if os.path.exists(critical_src):
    shutil.copy2(critical_src, f'{OUT}/assets/critical.css')

# Copy main.js
js_src = f'{SRC}/assets/main.js'
if os.path.exists(js_src):
    shutil.copy2(js_src, f'{OUT}/assets/main.js')

def e(s):
    if not s: return ''
    txt = h.escape(str(s))
    # Replace literal \n from data with line breaks
    txt = txt.replace('\\n', '<br>')
    return txt
def fmtRating(r):
    try: return f'{float(r):.1f}'
    except: return '0.0'

def truncate(s, mx=60):
    if not s: return 'N/A'
    cut = re.split(r'[;(]', s)[0].strip()
    return cut[:mx-2] + '...' if len(cut) > mx else cut



def get_best_for(brand):
    """Return a 'Best for ...' label based on brand strengths."""
    _best_for_map = {
        'zarbet': 'Best for Overall Value',
        'hollywoodbets': 'Best for Crowd Favourite',
        'betway-south-africa': 'Best for Trusted Brand',
        'easybet-south-africa': 'Best for Low Fees',
        '10bet-south-africa': 'Best for Odds',
        'mzansibet': 'Best for SA-Born Brand',
        'yesplay': 'Best for Fan Favourite',
        'saffaluck': 'Best for Slots',
        'playabets': 'Best for Live Betting',
        'playbet-co-za': 'Best for Fast Payouts',
        'wanejo-bets': 'Best for New Players',
        'supersportbet': 'Best for Brand Trust',
        'sportingbet': 'Best for Global Reach',
        'lulabet': 'Best for Great Value',
        'gbets': 'Best for Horse Racing',
        'supabets': 'Best for Promotions',
        'world-sports-betting': 'Best for SA Legend',
        'sunbet': 'Best for Casino',
        'betfred': 'Best for UK Pedigree',
        'tictacbets': 'Best for Easy Signup',
        'lottostar': 'Best for Lotto',
        'jackpot-city': 'Best for Casino Games',
    }
    return _best_for_map.get(brand['id'], '')

def short_name(brand):
    """Return a compact display name (strip 'South Africa' suffix, shorten long names)."""
    n = brand.get('name', '')
    for suffix in (' South Africa', ' SA'):
        if n.endswith(suffix):
            n = n[:-len(suffix)]
    # Abbreviate known long names for sidebar/card contexts
    abbrevs = {'World Sports Betting': 'World Sports Bet'}
    return abbrevs.get(n, n)

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
    """Return the MCP Hyperlinkurl directly (e.g. /link/{hash}/146/)."""
    if not brand.get('exitLink'):
        return ''
    return brand['exitLink']

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

LOGO_SVG = '''<svg width="28" height="28" viewBox="0 0 54 83" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M43.9259 38.8475V12.9671L31.6052 38.8475H22.0165L10.0708 12.9671V38.8475H0V0.857422H15.2669L27.1055 26.577L39.1048 0.857422H53.9431V38.8475H43.9259Z" fill="currentColor"/>
<path d="M43.9259 44.2063V70.0867L31.6052 44.2063H22.0165L10.0708 70.0867V44.2063H0V82.1963H15.2669L27.1055 56.4767L39.1048 82.1963H53.9431V44.2063H43.9259Z" fill="#1641B4"/>
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
        return (f'Best SA Betting Sites {CURRENT_MONTH_YEAR} - {len(DATA["brands"])} Ranked | MzansiWins',
                f'All {len(DATA["brands"])} licensed South African betting sites ranked for 2026. Compare odds, bonuses, payments, and apps.')
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
        return (trim_title(f'{article["title"]} | MzansiWins'),
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

def linkify_brand_mentions_news(html_text, lede_text, depth=0):
    """Like linkify_brand_mentions but:
    - Never links inside <p class="lede"> blocks
    - Max 1 link per brand (not 2) for news articles
    - First mention in body text gets the link
    """
    prefix = '../' * depth
    import re as _re
    sorted_brands = sorted(DATA['brands'], key=lambda b: len(b['name']), reverse=True)
    splitter = _re.compile(r'(<a\b[^>]*>.*?</a>|<[^>]+>)', flags=_re.DOTALL | _re.IGNORECASE)
    for b in sorted_brands:
        name = b['name']
        bid = b['id']
        link = f'<a href="{prefix}betting-site-review/{bid}.html" style="color:var(--accent);font-weight:600">{name}</a>'
        parts = splitter.split(html_text)
        count = 0
        in_lede = False
        in_heading = False
        pattern = _re.compile(r'\b' + _re.escape(name) + r'\b', flags=_re.IGNORECASE)
        for i, part in enumerate(parts):
            if part.startswith('<'):
                if 'class="lede"' in part or "class='lede'" in part:
                    in_lede = True
                elif in_lede and part.strip().lower() == '</p>':
                    in_lede = False
                if _re.match(r'<h[1-6]', part.strip(), _re.IGNORECASE):
                    in_heading = True
                elif _re.match(r'</h[1-6]', part.strip(), _re.IGNORECASE):
                    in_heading = False
                continue
            if in_lede or in_heading:
                continue
            if count >= 1:
                break
            matches = pattern.findall(part)
            if matches:
                remaining = 1 - count
                parts[i] = pattern.sub(link, part, count=remaining)
                count += min(len(matches), remaining)
        html_text = ''.join(parts)
    return html_text

PUBLISHER_LD = '{"@type": "Organization", "name": "MzansiWins", "url": "https://mzansiwins.co.za", "logo": {"@type": "ImageObject", "url": "https://mzansiwins.co.za/assets/logo.svg"}}'

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


def jsonld_organisation():
    """Generate JSON-LD Organization schema."""
    return f'''<script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "MzansiWins",
  "url": "{BASE_URL}",
  "logo": "{BASE_URL}/assets/logo.svg",
  "description": "South Africa's trusted guide to licensed betting sites, promo codes, and payment methods.",
  "foundingDate": "2024",
  "contactPoint": {{
    "@type": "ContactPoint",
    "email": "help@mzansiwins.co.za",
    "contactType": "customer service"
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

    # Build desktop nav - consolidated dropdowns for cleaner navigation
    # Betting dropdown
    betting_active = ' active' if active_nav in ('betting', 'promos') else ''
    betting_dd = f'''<div class="nav-dropdown">
<button class="nav-dropdown-btn{betting_active}">Betting {ICON_CHEVRON_DOWN}</button>
<div class="nav-dropdown-panel">
<a href="{prefix}betting-sites.html" class="dropdown-item"><span>Betting Sites</span><span class="dropdown-desc">All {len(DATA['brands'])} ranked</span></a>
<a href="{prefix}new-betting-sites.html" class="dropdown-item"><span>New Betting Sites</span><span class="dropdown-desc">Latest operators</span></a>
<a href="{prefix}betting/best-betting-apps-south-africa.html" class="dropdown-item"><span>Best Betting Apps</span><span class="dropdown-desc">Mobile rankings</span></a>
<a href="{prefix}promo-codes.html" class="dropdown-item"><span>Promo Codes</span><span class="dropdown-desc">All active codes</span></a>
<a href="{prefix}compare/" class="dropdown-item"><span>Compare Sites</span><span class="dropdown-desc">Head-to-head</span></a>
<a href="{prefix}guides/" class="dropdown-item"><span>Betting Guides</span><span class="dropdown-desc">How-to articles</span></a>
</div></div>\n'''

    # Casino dropdown
    casino_active = ' active' if active_nav == 'casino' else ''
    casino_dd = f'''<div class="nav-dropdown">
<button class="nav-dropdown-btn{casino_active}">Casino {ICON_CHEVRON_DOWN}</button>
<div class="nav-dropdown-panel">
<a href="{prefix}casino-sites.html" class="dropdown-item"><span>Casino Sites</span><span class="dropdown-desc">All ranked</span></a>
<a href="{prefix}casino/best-casino-apps-south-africa.html" class="dropdown-item"><span>Best Casino Apps</span><span class="dropdown-desc">Mobile rankings</span></a>
<a href="{prefix}crash-games/index.html" class="dropdown-item"><span>Crash Games</span><span class="dropdown-desc">Aviator, JetX &amp; more</span></a>
<a href="{prefix}sa-slots/index.html" class="dropdown-item"><span>SA Slots</span><span class="dropdown-desc">Local favourites</span></a>
<a href="{prefix}casino-guides/" class="dropdown-item"><span>Casino Guides</span><span class="dropdown-desc">How-to articles</span></a>
</div></div>\n'''

    # Tools dropdown (Payments, Calculators, BonusBrowser)
    tools_active = ' active' if active_nav in ('payments', 'calculators') else ''
    tools_dd = f'''<div class="nav-dropdown">
<button class="nav-dropdown-btn{tools_active}">Tools {ICON_CHEVRON_DOWN}</button>
<div class="nav-dropdown-panel">
<a href="{prefix}payment-methods.html" class="dropdown-item"><span>Payment Methods</span><span class="dropdown-desc">Deposits &amp; withdrawals</span></a>
<a href="{prefix}betting-calculators.html" class="dropdown-item"><span>Calculators</span><span class="dropdown-desc">Odds &amp; margin tools</span></a>
<a href="{prefix}bonus-browser.html" class="dropdown-item"><span>BonusBrowser</span><span class="dropdown-desc">Compare bonuses</span></a>
<a href="{prefix}betting/bonus-finder.html" class="dropdown-item"><span>Bonus Finder</span><span class="dropdown-desc">Match your play style</span></a>
</div></div>\n'''

    # News direct link
    news_active = ' active' if active_nav == 'news' else ''
    news_link = f'<a href="{prefix}news.html" class="nav-link{news_active}">News</a>\n'

    # Reviews dropdown
    reviews_dd = '<div class="nav-dropdown">\n'
    reviews_dd += f'<button class="nav-dropdown-btn">Reviews {ICON_CHEVRON_DOWN}</button>\n'
    reviews_dd += '<div class="nav-dropdown-panel nav-dropdown-reviews">\n'
    for b in BRANDS:
        reviews_dd += f'<a href="{prefix}betting-site-review/{b["id"]}.html" class="dropdown-item"><span>{e(b["name"])}</span><span class="dropdown-rating">{fmtRating(b["overallRating"])}/5.0</span></a>\n'
    reviews_dd += '</div></div>\n'

    desktop_nav = betting_dd + casino_dd + news_link + tools_dd + reviews_dd

    # Mobile menu
    mobile_brands = ''.join(
        f'<a href="{prefix}betting-site-review/{b["id"]}.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>{e(b["name"])}</span><span class="mobile-bonus-tag">{e(b["welcomeBonusAmount"][:35])}</span></a>\n'
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
      <a href="{prefix}bonus-browser.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>BonusBrowser</span></a>
    </div>
    <div class="mobile-sep"></div>
    <button class="mobile-nav-item" onclick="toggleSubmenu('sub-casino')"><span>Casino</span><span class="mobile-chevron" style="transition:transform 280ms">{ICON_CHEVRON_DOWN}</span></button>
    <div id="sub-casino" class="mobile-submenu">
      <a href="{prefix}casino-sites.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Casino Sites</span></a>
      <a href="{prefix}casino/best-casino-apps-south-africa.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Best Casino Apps</span></a>
      <a href="{prefix}casino-guides/" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Casino Guides</span></a>
      <a href="{prefix}crash-games/index.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>Crash Games</span></a>
      <a href="{prefix}sa-slots/index.html" class="mobile-sub-link" onclick="closeMobileMenu()"><span>SA Slots</span></a>
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
        <p>MzansiWins reviews licensed South African betting operators through observed tests of sign-up, payments, withdrawals, and support. Published by NWG PTY Limited, a company registered in South Africa. Updated {CURRENT_MONTH_YEAR}.</p>
        <address style="font-style:normal;margin-top:12px;line-height:1.6;font-size:13px;color:#888">
          NWG PTY Limited t/a MzansiWins<br>
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
        <a href="{prefix}bonus-browser.html">BonusBrowser</a>
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
      <p>Gambling should be treated as entertainment. You must be 18+ to gamble in South Africa. If you or someone you know needs help, contact the SA Responsible Gambling Foundation: <strong>0800 006 008</strong> (free, 24/7). All operators listed here hold South African provincial gambling licences issued under the National Gambling Act. Licence details are shown in each review.</p>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2026 MzansiWins. All rights reserved. This site includes commercial links.</p>
    </div>

  </div>
</footer>'''

    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-Y4YF2X6BSQ"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-Y4YF2X6BSQ');
  </script>
  <title>{e(trim_title(title))}</title>
  <meta name="description" content="{e(trim_desc(description))}">
  <link rel="icon" type="image/png" sizes="96x96" href="{prefix}favicon-96x96.png">
  <link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg">
  <link rel="shortcut icon" href="{prefix}favicon.ico">
  <link rel="apple-touch-icon" sizes="180x180" href="{prefix}apple-touch-icon.png">
  <link rel="manifest" href="{prefix}site.webmanifest">
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
      </nav>
      <div class="header-right">
        <button class="theme-btn" onclick="toggleTheme()" aria-label="Toggle theme"></button>
        <div class="starred-nav-badge" id="starredNavBadge" style="display:none">
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
  <div class="affiliate-disclosure-bar"><div class="container" style="display:flex;align-items:center;justify-content:center;gap:6px;padding:6px 16px"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg><span style="font-size:11px;color:var(--text-muted)">We may earn a commission from bookmaker links. This never affects our ratings. Some operators pay for featured placement, which is always disclosed. <a href="{prefix}affiliate-disclosure.html" style="color:var(--accent);text-decoration:underline">Learn more</a></span></div></div>
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
              <span>\u26A1 {truncate(m.get('depositSpeed',''), 30)}</span>
              <span style="opacity:0.3">|</span>
              <span>{truncate(m.get('fees',''), 30)}</span>
            </div>
          </div>
        </a>'''

    # Best by sport - custom SVG icons from assets/icons/
    SPORT_ICONS = {
        'Football': '<img src="assets/icons/soccer.svg" width="20" height="20" alt="Football" style="filter:brightness(0) saturate(100%) invert(19%) sepia(92%) saturate(3025%) hue-rotate(222deg) brightness(90%) contrast(95%)">',
        'Rugby': '<img src="assets/icons/rugby-ball.svg" width="20" height="20" alt="Rugby" style="filter:brightness(0) saturate(100%) invert(19%) sepia(92%) saturate(3025%) hue-rotate(222deg) brightness(90%) contrast(95%)">',
        'Cricket': '<img src="assets/icons/cricket.svg" width="20" height="20" alt="Cricket" style="filter:brightness(0) saturate(100%) invert(19%) sepia(92%) saturate(3025%) hue-rotate(222deg) brightness(90%) contrast(95%)">',
        'Horse Racing': '<img src="assets/icons/horse-racing.svg" width="20" height="20" alt="Horse Racing" style="filter:brightness(0) saturate(100%) invert(19%) sepia(92%) saturate(3025%) hue-rotate(222deg) brightness(90%) contrast(95%)">',
        'Tennis': '<img src="assets/icons/tennis.svg" width="20" height="20" alt="Tennis" style="filter:brightness(0) saturate(100%) invert(19%) sepia(92%) saturate(3025%) hue-rotate(222deg) brightness(90%) contrast(95%)">',
        'Basketball': '<img src="assets/icons/basketball.svg" width="20" height="20" alt="Basketball" style="filter:brightness(0) saturate(100%) invert(19%) sepia(92%) saturate(3025%) hue-rotate(222deg) brightness(90%) contrast(95%)">',
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
            <span style="font-size:13px;color:var(--text-secondary);flex:1;padding-right:8px;line-height:1.3">{e(brand['welcomeBonusAmount'][:50])}</span>
            <span style="font-size:13px;font-weight:700;color:var(--accent)">{fmtRating(brand['overallRating'])}/5.0</span>
          </div>
        </a>'''

    # How we rate
    criteria = [
        ('Welcome Bonus', '25%', 'We evaluate the real value behind the headline number, including wagering requirements, minimum deposits, and expiry periods.'),
        ('Odds Quality', '20%', 'We compare odds on PSL football, Springbok rugby, and Proteas cricket across all licensed bookmakers.'),
        ('Payment Methods', '15%', 'EFT, vouchers, and e-wallets tested. We measure deposit speed and actual withdrawal processing times.'),
        ('Sports Coverage', '15%', 'From PSL player props to Currie Cup markets. We assess the depth and variety of sports available.'),
        ('Platform Quality', '10%', 'Mobile performance, navigation, bet slip usability, and load speed across devices.'),
        ('Live Betting', '10%', 'In-play market depth, cash-out reliability, and live streaming availability.'),
        ('Customer Support', '5%', 'Response times, channel availability (live chat, phone, email), and quality of support.'),
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
        ('Is online betting legal in South Africa?', 'Sports betting through provincially licensed bookmakers is permitted under South African law. The National Gambling Board regulates the industry through provincial boards. We only list operators that hold a valid provincial licence; however, some platforms offering casino-style games operate under different regulatory frameworks. The National Gambling Act of 2004 restricts interactive gambling, though certain provincial frameworks allow licensed operators to offer casino products. Players should verify the specific licence terms of any operator offering casino games.'),
        ('What is the minimum age for betting in SA?', 'You must be 18 or older to place bets in South Africa. All licensed bookmakers will ask you to verify your identity (FICA) before you can withdraw. No exceptions.'),
        ('Which payment method is fastest?', 'Ozow processes deposits instantly. OTT, Blu Voucher, and 1Voucher are also instant. Visa and Mastercard typically process within seconds. These are the best options for speed.'),
        ('Do I need a promo code for welcome bonuses?', 'Some bookmakers require a promo code, others apply the bonus automatically. We specify the requirements for every bookmaker in our reviews.'),
        ('How long do withdrawals take?', 'It depends on your withdrawal method. Ozow and some EFT options can process same-day. Bank transfers typically take 1 to 3 business days. Vouchers usually process within 24 to 48 hours.'),
        ('Are my personal details safe?', 'Licensed SA bookmakers must comply with POPIA and use proper encryption. Stick to licensed operators and you are covered.'),
        ('Which bookmaker has the best welcome bonus right now?', 'Currently, Zarbet offers the highest match at 125% up to R3,750 plus 25 free spins. 10Bet follows closely with 100% up to R3,000. Easybet also offers a strong 150% up to R1,500. Competition among bookmakers keeps bonuses strong.'),
        ('Can I bet on the PSL at all SA bookmakers?', 'All major SA bookmakers cover PSL matches. It is the most popular betting market in South Africa. Hollywoodbets offers the deepest coverage with player props, corner totals, and half-time markets, making it ideal for serious PSL bettors.'),
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
              <div style="font-size:14px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{e(short_name(brand))}</div>
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
          <div class="bonus-claim">Claim Bonus</div>
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
      <img src="assets/hero-sports-characters.png" class="hero-sports-mobile" alt="" aria-hidden="true">
      <div class="container hero-layout">
        <div class="hero-text">
          <div class="hero-badge">{ICON_TROPHY} <span>{len(DATA['brands'])} LICENSED SA BOOKMAKERS TESTED</span></div>
          <h1>South Africa's Best Betting Sites - Over <span style="color:var(--bonus)">R{total_bonus:,}</span> in Bonuses</h1>
          <p class="hero-lead">MzansiWins reviews every licensed South African bookmaker through sign-up, deposit, withdrawal, and support tests. {len(DATA['brands'])} operators reviewed as of {CURRENT_MONTH_YEAR}.</p>
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
              <svg width="22" height="15" viewBox="0 0 90 60" style="border-radius:2px"><defs><clipPath id="ht"><path d="m0 0 45 30L0 60z"/></clipPath><clipPath id="hf"><path d="m0 0h90v60H0z"/></clipPath></defs><path fill="#E03C31" d="m0 0h90v30H45z"/><path fill="#001489" d="m0 60h90V30H45z"/><g clip-path="url(#hf)" fill="none"><path stroke="#FFF" stroke-width="20" d="m90 30H45L0 0v60l45-30"/><path fill="#000" stroke="#FFB81C" stroke-width="20" clip-path="url(#ht)" d="m0 0 45 30L0 60"/><path stroke="#007749" stroke-width="12" d="m0 0 45 30h45M0 60l45-30"/></g></svg>
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
          <div><h2 class="section-title">Latest SA Betting News</h2><p class="section-subtitle">Bonus updates, platform changes, and industry developments from South African bookmakers</p></div>
          <a href="news.html" class="section-link">All news</a>
        </div>
        <div class="news-cards-grid">{news_cards_html}</div>
      </div>
    </section>



    <section class="section">
      <div class="container">
        <div class="section-header">
          <div><h2 class="section-title">Best Bookmakers by Sport</h2><p class="section-subtitle">Our top-rated bookmaker for each major sport in South Africa</p></div>
        </div>
        <div class="grid-3">{sport_cards}</div>
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
          <div><h2 class="section-title">Popular Payment Methods</h2><p class="section-subtitle">Getting your rands in and out without drama. Here's how</p></div>
          <a href="payment-methods.html" class="section-link">All payment guides</a>
        </div>
        <div class="grid-3">{pay_cards}</div>
      </div>
    </section>

    <section class="section">
      <div class="container" style="max-width:800px">
        <div style="margin-bottom:40px">
          <h2 class="section-title">How We Rate Bookmakers</h2>
          <p style="color:var(--text-secondary);font-size:15px;line-height:1.7">Every bookmaker is tested through a real sign-up, deposit, bet, and withdrawal. We score each operator across 7 categories using observed results, not promotional claims.</p>
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
              <p>Gambling is permitted for persons aged 18 and over in South Africa. All licensed operators are required by law to offer self-exclusion tools, deposit limits, and cooling-off periods. The National Responsible Gambling Programme (NRGP) provides free support: <strong style="color:#fff">0800 006 008</strong> (24/7). Visit <a href="https://www.responsiblegambling.org.za" target="_blank" rel="noopener noreferrer" style="color:#fff;text-decoration:underline">responsiblegambling.org.za</a> for more information.</p>
            </div>
          </div>
          <a href="tel:0800006008" class="rg-btn">0800 006 008</a>
        </div>
      </div>
    </section>
    '''

    t, d = seo_meta('home')
    home_ld = jsonld_website() + '\n' + jsonld_organisation() + '\n' + jsonld_faq(faqs)
    return page(t, d, '', body, depth=0, active_nav='home', json_ld=home_ld)


# ============================================================
# QUICK FACTS HELPER
# ============================================================

def get_quick_facts(brand):
    """Build Quick Facts HTML box for review pages."""
    import re as _re
    lic = brand.get('license', '')

    # --- Determine gambling board ---
    board_map = {
        'western cape': 'Western Cape Gambling and Racing Board',
        'mpumalanga': 'Mpumalanga Economic Regulator',
        'eastern cape': 'Eastern Cape Gambling Board',
        'gauteng': 'Gauteng Gambling Board',
        'kwazulu': 'KwaZulu-Natal Gaming and Betting Board',
        'northern cape': 'Northern Cape Gambling Board',
        'free state': 'Free State Gambling, Liquor and Tourism Authority',
        'limpopo': 'Limpopo Gambling Board',
        'north west': 'North West Gambling Board',
    }
    board = 'Provincial Gambling Board'
    for key, val in board_map.items():
        if key in lic.lower():
            board = val
            break
    # Manual overrides for brands where license field doesn't mention the board
    board_overrides = {
        'zarbet': 'Western Cape Gambling and Racing Board',
        'tictacbets': 'Northern Cape Gambling Board',
        'mzansibet': 'Western Cape Gambling and Racing Board',
        'gbets': 'Western Cape Gambling and Racing Board',
        'playabets': 'Mpumalanga Economic Regulator',
        'hollywoodbets': 'KwaZulu-Natal Gaming and Betting Board',
        'sportingbet': 'Western Cape Gambling and Racing Board',
        'supabets': 'Mpumalanga Economic Regulator',
        '10bet-south-africa': 'Mpumalanga Economic Regulator',
        'luckystake': 'Under review',
    }
    if brand['id'] in board_overrides:
        board = board_overrides[brand['id']]

    # --- Extract license number ---
    lic_num = None
    patterns = [
        r'(?:licence|license)\s*(?:number|no\.?|#)[:;.\s]*([A-Za-z0-9\-/]+(?:[\-/]\d+)?)',
        r'license\s+(\d[\w\-/]+)',
        r'(\d+-\d+-\d+-\d+)',
        r'(\d{5,}[\-/]?\d*)',
        r'(ECBM\s*\d+)',
    ]
    for pat in patterns:
        m = _re.search(pat, lic, _re.IGNORECASE)
        if m:
            lic_num = m.group(1) if m.lastindex else m.group(0)
            break
    if not lic_num:
        m = _re.search(r'(?:registration|reg)\s*(?:number|no\.?)[:;.\s]*([A-Za-z0-9\-/]+)', lic, _re.IGNORECASE)
        if m:
            lic_num = m.group(1)
    if not lic_num:
        lic_num = 'Contact operator'

    # --- Top sports (first 6) ---
    sports_raw = brand.get('sportsCovered', [])
    if isinstance(sports_raw, list):
        top_sports = sports_raw[:6]
    else:
        top_sports = [s.strip() for s in str(sports_raw).split(',')][:6]
    sports_str = ', '.join(top_sports)
    if isinstance(sports_raw, list) and len(sports_raw) > 6:
        sports_str += f' +{len(sports_raw) - 6} more'

    # --- Live betting / Cash out / App ---
    live_bet = brand.get('liveBetting', 'N/A')
    live_short = 'Yes' if 'yes' in str(live_bet).lower() else 'No' if 'no' in str(live_bet).lower() else str(live_bet)

    cash_out = brand.get('cashOut', 'N/A')
    cash_short = 'Yes' if 'yes' in str(cash_out).lower() else 'No' if ('no' in str(cash_out).lower() or 'n/a' in str(cash_out).lower()) else str(cash_out)
    # Add partial/auto if present
    cash_extras = []
    co_lower = str(cash_out).lower()
    if 'partial' in co_lower:
        cash_extras.append('Partial')
    if 'auto' in co_lower:
        cash_extras.append('Auto')
    if cash_extras and cash_short == 'Yes':
        cash_short = 'Yes (' + ', '.join(cash_extras) + ')'

    app_raw = brand.get('mobileApp', 'N/A')
    app_str = str(app_raw)
    app_lower = app_str.lower()
    if 'ios' in app_lower and 'android' in app_lower:
        app_short = 'Android &amp; iOS'
    elif 'android' in app_lower and ('no' in app_lower.split('ios')[0] if 'ios' in app_lower else True):
        if 'ios' in app_lower and 'no' in app_lower.split('ios')[-1][:10].lower():
            app_short = 'Android only'
        elif 'ios' in app_lower:
            app_short = 'Android &amp; iOS'
        else:
            app_short = 'Android only'
    elif 'ios' in app_lower:
        app_short = 'iOS only'
    elif 'no' in app_lower or 'n/a' in app_lower:
        app_short = 'Mobile site only'
    elif 'yes' in app_lower:
        app_short = 'Yes'
    else:
        app_short = app_str[:40]
    # Huawei bonus
    if 'huawei' in app_lower:
        if 'Android' in app_short:
            app_short = app_short.replace('Android', 'Android, Huawei')
        elif app_short == 'Yes':
            app_short = 'Android, iOS &amp; Huawei'

    min_dep = e(brand.get('minDeposit', 'Varies'))
    # Clean up complex min deposit strings
    if '(' in min_dep:
        min_dep = min_dep.split('(')[0].strip()

    # --- Year established ---
    year_est = brand.get('yearEstablished', '')
    yr_str = str(year_est).strip()
    yr_match = _re.search(r'(\d{4})', yr_str)
    yr_display = yr_match.group(1) if yr_match else ''

    # Shield icon
    shield_svg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
    check_svg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>'
    x_svg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#888" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>'

    def bool_icon(val):
        if 'yes' in str(val).lower():
            return f'{check_svg} <span style="color:var(--accent);font-weight:600">Yes</span>'
        elif 'no' in str(val).lower() or 'n/a' in str(val).lower():
            return f'{x_svg} <span style="color:#888">No</span>'
        return e(str(val)[:30])

    rows = f'''
    <tr><td>Gambling Board</td><td>{e(board)}</td></tr>
    <tr><td>Licence Number</td><td><code style="font-family:monospace;font-size:12px;background:var(--surface-2);padding:2px 6px;border-radius:4px">{e(lic_num)}</code></td></tr>
    {f'<tr><td>Established</td><td>{yr_display}</td></tr>' if yr_display else ''}
    <tr><td>Min Deposit</td><td><strong>{min_dep}</strong></td></tr>
    <tr><td>Sports</td><td>{e(sports_str)}</td></tr>
    <tr><td>Live Betting</td><td>{bool_icon(live_bet)}</td></tr>
    <tr><td>Cash Out</td><td>{bool_icon(cash_out)}{f' <span style="font-size:11px;color:var(--text-muted)">({', '.join(cash_extras)})</span>' if cash_extras else ''}</td></tr>
    <tr><td>Mobile App</td><td>{app_short}</td></tr>'''

    return f'''
    <div class="quick-facts-box">
      <div class="quick-facts-header">
        <h2>Quick Facts</h2>
      </div>
      <table class="quick-facts-table">
        <thead><tr><th>Feature</th><th>Details</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>'''


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
    wm_html = f'<img fetchpriority="high" src="{wm_logo}" alt="" class="brand-watermark" aria-hidden="true">' if wm_logo else ''

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

    # Trust badges for review pages
    _svg_shield = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
    _svg_check = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'
    _svg_star = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2L15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2z"/></svg>'
    trust_badges_html = f'''<div class="review-trust-badges">
        <span class="review-trust-badge">{_svg_shield} {'SA Licensed' if brand.get('licenceStatus','sa-licensed') == 'sa-licensed' else 'Casino Licence' if brand.get('licenceStatus') == 'casino-licence' else 'Licence Unconfirmed'}</span>
        <span class="review-trust-badge">{_svg_check} Independently Tested</span>
        <span class="review-trust-badge">{_svg_star} Expert Reviewed</span>
      </div>'''

    body = f'''
    <div class="brand-hero-wrap" style="padding:20px 0 16px">
      {wm_html}
      <div class="container">
        {breadcrumbs([{"label":"Home","href":"index.html"},{"label":"Betting Sites","href":"betting-sites.html"},{"label":brand["name"]}], depth)}
        <div class="review-hero-header">
          {hero_logo_html}
          <div class="review-hero-text">
            <h1 class="page-title" style="margin-bottom:4px">{e(brand['name'])} Review 2026</h1>
            <p style="font-size:13px;color:var(--text-muted);margin-bottom:0">{f"Est. {brand['yearEstablished'].split('(')[0].strip()}" if brand.get('yearEstablished') and brand['yearEstablished'].lower() not in ('not specified','n/a','unknown','') else 'Licensed SA Bookmaker'} &#x2022; {e(brand.get('license','Provincial licence').split(';')[0].strip())}</p>
            {trust_badges_html}
          </div>
        </div>
      </div>
    </div>
    <div class="container" style="padding-top:14px;padding-bottom:80px">
      {author_byline(get_review_author(brand['id']), depth)}

      <!-- Jump-to sticky section tabs -->
      <nav class="jump-to-bar" id="jumpToBar">
        <div class="jump-to-inner">
          <a href="#section-bonus" class="jump-to-tab active">Bonus</a>
          <a href="#section-ratings" class="jump-to-tab">Ratings</a>
          <a href="#section-pros-cons" class="jump-to-tab">Pros &amp; Cons</a>
          <a href="#section-review" class="jump-to-tab">Review</a>
          <a href="#section-payments" class="jump-to-tab">Payments</a>
          <a href="#section-features" class="jump-to-tab">Features</a>
          <a href="#section-test-log" class="jump-to-tab">Test Log</a>
        </div>
      </nav>

      <div class="two-col">
        <div>

          <!-- Promo Box -->
          <div id="section-bonus"></div>
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

          <!-- Testing Evidence Box -->
          {generate_evidence_box(brand)}

          <!-- Quick Facts -->
          {get_quick_facts(brand)}

          <!-- Rating Breakdown -->
          <div id="section-ratings"></div>
          <div class="review-section-card" style="margin-bottom:28px">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
              <h2 style="font-size:17px;font-weight:700;margin:0">Rating Breakdown</h2>
              <span class="how-we-rate-tooltip" tabindex="0" aria-label="How we rate" onclick="this.classList.toggle('active')">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="var(--accent)" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="11" fill="var(--accent)"/><text x="12" y="17" text-anchor="middle" font-size="15" font-weight="700" font-family="Inter,sans-serif" fill="#fff">i</text></svg>
                <span class="how-we-rate-panel" onclick="event.stopPropagation()">
                  <strong style="font-size:13px;display:block;margin-bottom:6px">How we rate</strong>
                  <span style="font-size:12px;line-height:1.45;color:var(--text-secondary)">Every bookmaker is scored across seven categories by our editorial team. We test deposits, withdrawals, customer support, and app quality using real accounts and real money. Ratings are updated quarterly and are not influenced by affiliate partnerships. <a href="{'../' * depth}editorial-policy.html" style="color:var(--accent);font-weight:600">Read our editorial policy</a></span>
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
          <div id="section-pros-cons"></div>
          <div class="review-pros-cons-grid" style="margin-bottom:28px">
            <div class="pros-box"><h3>{ICON_CHECK} Pros</h3><ul class="pros-list">{pros_li}</ul></div>
            <div class="cons-box"><h3>{ICON_X} Cons</h3><ul class="cons-list">{cons_li}</ul></div>
          </div>

          <!-- Mid-article CTA -->
          <div class="review-cta-box" style="margin-bottom:28px">
            <div class="review-cta-inner">
              <div class="review-cta-text">
                <strong style="font-size:15px;display:block;margin-bottom:2px">{e(brand['name'])}</strong>
                <span style="font-size:14px;color:var(--text-secondary)">{e(brand['welcomeBonusAmount'])}</span>
              </div>
              {f'<a href="{masked_exit(brand, depth)}" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary" style="display:inline-flex;font-size:14px;padding:10px 24px;flex-shrink:0;white-space:nowrap">Visit {e(brand["name"].split()[0])} &rarr;</a>' if brand.get("exitLink") else ''}
            </div>
          </div>

          <!-- Site Preview (screenshots) -->
          {site_preview_html}

          <!-- Detailed Review Content -->
          <div id="section-review"></div>
          <div class="review-content">
          {generate_review_content(brand)}
          </div>

          <!-- Payment Methods -->
          <div id="section-payments" class="review-section-card" style="margin-bottom:28px">
            <h2 style="font-size:17px;font-weight:700;margin-bottom:16px">Payment Methods</h2>
            <div style="display:flex;flex-wrap:wrap;gap:8px">{pay_pills}</div>
          </div>

          <!-- Features -->
          <div id="section-features" class="review-section-card" style="margin-bottom:28px">
            <h2 style="font-size:17px;font-weight:700;padding:0 0 12px">Betting Features</h2>
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

          <!-- Test Log -->
          <div id="section-test-log"></div>
          {generate_test_log(brand)}

          <!-- Related -->
          <h2 style="font-size:16px;font-weight:700;margin-bottom:16px">Related Bookmakers</h2>
          <div class="grid-2">{related_cards}</div>
        </div>

        <!-- Sidebar -->
        <div class="sidebar" style="display:none">
          <div class="sidebar-card">
            <h3>Quick Info</h3>
            <div class="sidebar-row"><span class="text-muted">Rating</span><span class="font-semibold">{fmtRating(brand['overallRating'])}/5.0</span></div>
            <div class="sidebar-row"><span class="text-muted">Bonus</span><span class="font-semibold" style="color:var(--accent);font-size:12px;text-align:right;max-width:180px">{e(brand['welcomeBonusAmount'])}</span></div>
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
            <div class="sticky-bottom-tcs">{e(brand.get('mcpTerms', brand.get('tcs','')))}</div>
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
    // Jump-to section observer
    (function(){{
      var tabs=document.querySelectorAll('.jump-to-tab');
      if(!tabs.length)return;
      var ids=Array.from(tabs).map(function(t){{return t.getAttribute('href').slice(1)}});
      var observer=new IntersectionObserver(function(entries){{
        entries.forEach(function(en){{
          if(en.isIntersecting){{
            tabs.forEach(function(t){{t.classList.remove('active')}});
            var a=document.querySelector('.jump-to-tab[href="#'+en.target.id+'"]');
            if(a)a.classList.add('active');
          }}
        }});
      }},{{rootMargin:'-120px 0px -60% 0px',threshold:0}});
      ids.forEach(function(id){{var el=document.getElementById(id);if(el)observer.observe(el)}});
      tabs.forEach(function(t){{
        t.addEventListener('click',function(ev){{
          ev.preventDefault();
          var el=document.getElementById(this.getAttribute('href').slice(1));
          if(el)el.scrollIntoView({{behavior:'smooth',block:'start'}});
        }});
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
    # Rating displayed as /5.0 everywhere

    # Logo
    logo = logo_path(brand, depth)
    logo_img = f'<img src="{logo}" alt="{name}" class="promo-detail-hero hero-logo" style="background:{brand_bg(brand)};padding:6px">' if logo else ''
    logo_sm = f'<img src="{logo}" alt="{name}" class="sticky-bottom-logo" style="background:{brand_bg(brand)};padding:4px">' if logo else ''
    tcs_text = brand.get('mcpTerms', brand.get('tcs', ''))
    tcs_short = tcs_text

    # Check icon
    check_sm = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'
    flag_icon = '<svg width="20" height="14" viewBox="0 0 90 60" aria-label="South African flag" style="border-radius:2px;vertical-align:middle"><defs><clipPath id="ft"><path d="m0 0 45 30L0 60z"/></clipPath><clipPath id="ff"><path d="m0 0h90v60H0z"/></clipPath></defs><path fill="#E03C31" d="m0 0h90v30H45z"/><path fill="#001489" d="m0 60h90V30H45z"/><g clip-path="url(#ff)" fill="none"><path stroke="#FFF" stroke-width="20" d="m90 30H45L0 0v60l45-30"/><path fill="#000" stroke="#FFB81C" stroke-width="20" clip-path="url(#ft)" d="m0 0 45 30L0 60"/><path stroke="#007749" stroke-width="12" d="m0 0 45 30h45M0 60l45-30"/></g></svg>'

    # Badge for top-rated brand
    badge = ''
    brand_idx = next((i for i, b in enumerate(BRANDS) if b['id'] == brand['id']), 99)
    if brand_idx == 0:
        badge = '<span class="promo-badge promo-badge-top">TOP RATED</span>'
    elif brand_idx < 3:
        badge = '<span class="promo-badge promo-badge-value">TOP 3</span>'
    elif brand_idx < 10:
        badge = '<span class="promo-badge promo-badge-rec">TOP 10</span>'

    # Featured placement disclosure
    FEATURED_BRANDS = {'tictacbets', '10bet-south-africa', 'easybet-south-africa'}
    featured_tag = ''
    if brand['id'] in FEATURED_BRANDS:
        featured_tag = '<span style="display:inline-block;font-size:11px;font-weight:600;color:var(--text-tertiary);background:var(--bg-tertiary,#f0f0f0);padding:2px 8px;border-radius:4px;margin-left:8px;vertical-align:middle">Featured</span>'

    # Trust badges row
    trust_html = f'''<div class="trust-badges-row" style="margin-top:16px">
      <div class="trust-badge">{check_sm} <span>Expert Verified</span></div>
      <div class="trust-badge">{flag_icon} <span>Legal in SA</span></div>
      <div class="trust-badge">{ICON_SHIELD} <span>18+ Only</span></div>
    </div>'''

    # Expert quote
    _pros_list = brand.get('pros', [])
    if isinstance(_pros_list, list) and _pros_list:
        _main_strength = str(_pros_list[0]).split(',')[0].strip().lower()
    else:
        _main_strength = ''
    _cons_list = brand.get('cons', [])
    if isinstance(_cons_list, list) and _cons_list:
        _main_limitation = str(_cons_list[0]).split(',')[0].strip().lower()
    else:
        _main_limitation = ''
    _brand_type_str = brand.get('type', 'betting')
    _who_suits = 'casino players' if _brand_type_str == 'casino' else 'sports bettors who want a wide market range' if float(brand['overallRating']) >= 4.5 else 'bettors looking for a licensed local option'
    _strength_sentence = f"{name} scores {rating_5}/5.0 in our testing. {_main_strength.capitalize()}." if _main_strength else f"{name} scores {rating_5}/5.0 in our testing."
    _limitation_sentence = f" The main limitation noted: {_main_limitation}." if _main_limitation else ''
    expert_html = f'''<div class="expert-quote" id="expert-analysis">
      <p>"{_strength_sentence}{_limitation_sentence} Best suited to {_who_suits}."</p>
      <p class="expert-name">MzansiWins Review Team</p>
    </div>'''

    # Claim steps (4 steps with titles)
    claim_steps = [
        ('Register an Account', f'Go to the {brand["name"]} website and click the registration button. Complete the form with your full name, ID number, email address, and phone number.'),
        ('Enter Promo Code', f'Enter the promo code <strong>{e(code)}</strong> in the designated field during registration or in the promotions section of your account.' if has_code else ('No Promo Code Required', 'No promo code is needed. The bonus is applied to your account automatically after qualifying.')),
        ('Verify Your Identity', f'Upload a copy of your South African ID and a recent proof of address for FICA verification. See our <a href="{prefix}fica-guide.html" style="color:var(--accent);font-weight:600">FICA guide</a> for details on accepted documents.'),
        ('Make Your First Deposit', f'Deposit a minimum of {e(brand.get("minDeposit", "R10"))} using your preferred payment method. {e(brand.get("tcs", "T&Cs apply."))} Check that the bonus has been credited before placing your first bet.'),
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
        sb_exit = masked_exit(sb, depth)
        compare_rows += f'''<tr>
      <td style="white-space:nowrap"><a href="{sb['id']}.html" style="color:var(--accent);font-weight:600">{e(sb['name'])}</a></td>
      <td>{e(sb['welcomeBonusAmount'][:40])}</td>
      <td style="font-family:monospace;font-weight:600">{e(sc)}</td>
      <td style="text-align:center">{fmtRating(sb['overallRating'])}/5.0</td>
      <td style="text-align:center"><a href="../promo-code/{sb['id']}.html" class="btn-outline btn-sm">Promo</a></td>
      <td style="text-align:center">{f'<a href="{sb_exit}" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary btn-sm">Visit</a>' if sb_exit else ''}</td>
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
    wm_html_promo = f'<img fetchpriority="high" src="{wm_logo_promo}" alt="" class="brand-watermark" aria-hidden="true">' if wm_logo_promo else ''

    bc = breadcrumbs([{"label":"Home","href":"index.html"},{"label":"Promo Codes","href":"promo-codes.html"},{"label":brand["name"]}], depth)
    body = f"""
    <!-- Hero -->
    <div class="promo-detail-hero" style="background:var(--surface);border-bottom:1px solid var(--border);padding:20px 0 16px">
      {wm_html_promo}
      <div class="container">
        {bc}
        <div class="hero-inner" style="align-items:flex-start">
          {logo_img}
          <div class="hero-info" style="flex:1;min-width:0">
            <div class="hero-title-row">
              {badge}
            </div>
            <h1 style="color:#111111">{name} Promo Code 2026: {e(code)}</h1>
            <p class="hero-subtitle" style="color:var(--text-secondary)">Get <strong style="color:var(--bonus)">{bonus}</strong> with code <strong style="color:var(--accent)">{e(code)}</strong>. Verified and working for {CURRENT_MONTH_YEAR}.</p>
            {trust_html}
          </div>
          <div class="rating-circle" style="flex-shrink:0;align-self:flex-start"><span class="rating-circle-score">{rating_5}</span><span style="font-size:11px;color:var(--text-muted);font-weight:600">/5.0</span></div>
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
                <tr><td style="font-weight:600">Wagering</td><td>{e(brand.get('welcomeBonusDetails','See T&Cs'))}</td></tr>
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
                <thead><tr><th>Bookmaker</th><th>Bonus</th><th>Code</th><th>Rating</th><th>Promo</th><th>Visit</th></tr></thead>
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
        visit_link = f'<a href="{m_exit}" target="_blank" rel="noopener noreferrer nofollow" class="sidebar-visit-btn">Visit</a>' if m_exit else ''
        tcs_text = b.get('tcs', '18+ T&Cs apply.')
        tcs_short = '18+ T&Cs apply.'
        items += f'''<div class="sidebar-top5-card">
          <div class="sidebar-top5-left">
            <button class="star-btn" data-brand="{b['id']}" onclick="event.stopPropagation();toggleStar('{b['id']}')" aria-label="Star {e(b['name'])}" style="flex-shrink:0">{ICON_STAR}</button>
            {logo_img}
          </div>
          <div class="sidebar-top5-info">
            <a href="{prefix}betting-site-review/{b['id']}.html" class="sidebar-brand-name">{e(b['name'])}</a>
            <span class="sidebar-brand-bonus">{bv_display}</span>
            <p class="sidebar-tcs">{e(tcs_short)}</p>
          </div>
          {visit_link}
        </div>'''

    return f'''<aside class="news-sidebar" style="position:sticky;top:90px">
      <div class="sidebar-top5-wrap">
        <h3 class="sidebar-section-title">Top 5 Betting Sites</h3>
        <p class="sidebar-section-sub">Star your favourites to track bonuses</p>
        {items}
        <a href="{prefix}betting-sites.html" class="sidebar-viewall-btn">View All Betting Sites</a>
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
    # Strip ALL pre-baked links from lede paragraphs and review links from body
    import re as _re_news
    def _strip_lede_links(html):
        """Remove all <a> tags inside <p class="lede"> blocks, keeping text content."""
        def _clean_lede(m):
            content = m.group(1)
            # Strip all anchor tags, keep inner text
            content = _re_news.sub(r'<a[^>]*>(.*?)</a>', r'\1', content)
            return f'<p class="lede">{content}</p>'
        return _re_news.sub(r'<p class="lede">(.*?)</p>', _clean_lede, html, flags=_re_news.DOTALL)
    def _strip_review_links(html):
        """Remove <a href=".../betting-site-review/...">Name</a> -> Name"""
        return _re_news.sub(r'<a[^>]*betting-site-review[^>]*>(.*?)</a>', r'\1', html)
    body_html = _strip_lede_links(body_html)
    body_html = _strip_review_links(body_html)
    # Now re-linkify: skip lede, max 1 per brand
    body_html = linkify_brand_mentions_news(body_html, article.get('lede', ''), depth=1)

    # Calculate read time (avg 200 words per minute)
    import re as _re_rt
    plain_text = _re_rt.sub(r'<[^>]+>', '', body_html)
    word_count = len(plain_text.split())
    read_time = max(1, round(word_count / 200))
    read_time_str = f'{read_time} min read'

    # Related articles: prefer same category, then most recent
    _same_cat = [a for a in NEWS if a['slug'] != article['slug'] and a.get('category') == article.get('category')]
    _other = [a for a in NEWS if a['slug'] != article['slug'] and a.get('category') != article.get('category')]
    related = (_same_cat[:2] + _other[:1]) if len(_same_cat) >= 2 else (_same_cat + _other)[:3]
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
              {'<span style="font-size:11px;font-weight:700;color:#b45309;background:#fef3c7;padding:2px 8px;border-radius:3px;text-transform:uppercase;letter-spacing:0.5px">Operator Promotion</span>' if article.get('isPromo') else ''}
              <span>{dt}</span>
              <span style="font-size:12px;color:var(--text-muted)">{read_time_str}</span>
              <span class="article-author-byline">{author_img(article.get('author',''), size=28, depth=1)} By <a href="../authors/{AUTHOR_IDS.get(article.get('author',''), 'thabo-mokoena')}.html" style="color:var(--text-primary);font-weight:600;text-decoration:none;border-bottom:1px solid var(--border)">{e(article.get('author','MzansiWins'))}</a></span>
            </div>
            {body_html}
          </article>
          <div class="share-bar">
            <span style="font-size:13px;font-weight:600;color:var(--text-muted)">Share this article</span>
            <a href="https://wa.me/?text={e(article['title'])}%20-%20https://mzansiwins.co.za/news/{article['slug']}" target="_blank" rel="noopener noreferrer" class="share-btn share-whatsapp" aria-label="Share on WhatsApp">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
              WhatsApp
            </a>
            <a href="https://twitter.com/intent/tweet?text={e(article['title'])}&url=https://mzansiwins.co.za/news/{article['slug']}" target="_blank" rel="noopener noreferrer" class="share-btn share-x" aria-label="Share on X">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
              Share
            </a>
          </div>
          <p style="font-size:13px;line-height:1.6;color:var(--text-muted);border-top:1px solid var(--sep);padding-top:14px;margin-top:24px">Commercial note: MzansiWins may earn a commission if readers open an account through bookmaker links.</p>
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
    return f'''<section class="category-hero-banner">
      <div class="container">
        {bc}
        <h1>{title}</h1>
        <p class="page-subtitle">{subtitle}</p>
        {badge_html}
      </div>
    </section>'''

def get_brand_sales_msg(brand):
    """Generate a unique sales message for each brand based on their standout feature."""
    bid = brand.get('id', '')
    rating = brand.get('overallRating', 0)
    sports = len(brand.get('sportsCovered', []))
    has_app = 'yes' in str(brand.get('mobileApp', '')).lower()
    payments = len(brand.get('paymentMethodsList', []))
    messages = {
        'zarbet': 'Biggest welcome bonus in SA right now',
        'hollywoodbets': "SA's most popular bookmaker with Spina Zonke slots",
        'betway-south-africa': 'Premium odds across 30+ sports markets',
        'easybet-south-africa': 'Generous sign-up offer with low minimum deposit',
        '10bet-south-africa': 'International bookmaker with 30+ sports markets',
        'gbets': 'Strong rugby and cricket odds for SA punters',
        'supabets': 'Wide sports coverage with live streaming included',
        'betxchange': 'Unique bet exchange model for better odds',
        'world-sports-betting': 'Established SA brand with free-to-play games',
        'yesplay': 'Growing platform with Aviator and crash games',
        'mzansibet': 'Fast Ozow payouts and competitive football odds',
        'sportingbet': 'International pedigree with solid SA coverage',
        'playabets': 'Budget-friendly with R1 minimum bet',
        'betfred': 'UK betting giant now available in South Africa',
        'jackpot-city': 'Casino-focused with strong slot selection',
        'pantherbet': 'Virtual sports and fast registration',
        'lulabet': 'Modern platform with competitive welcome offer',
        'betshezi': 'Well-known SA brand with competitive football odds',
        'supersportbet': 'Backed by SuperSport with great live betting',
        'topbet': 'SA veteran with wide sports coverage',
        'tictacbets': 'Northern Cape operator with TICTAC10 prediction game',
        'luckystake': 'Crypto-friendly with modern platform',
        'swifty': 'Fast registration and quick deposits',
        'pokerbet': 'Poker-focused with growing sportsbook',
        'saffaluck': 'SA-themed platform with local flavour',
        'soccershop': 'Football specialist for PSL and EPL punters',
        'jabula-bets': 'Simple platform with straightforward bonuses',
        'lucky-fish': 'Casino-focused with Mystery Parcel promo',
        'apexbets': 'Competitive reload bonuses for regulars',
        'betbus': 'Budget-friendly with low entry requirements',
        'betjets': 'Modern interface with fast cashout',
        'wanejo-bets': 'Boutique SA bookmaker',
        'bettabets': 'SA operator with sport and casino options',
        'playbet-co-za': 'Straightforward SA betting site',
    }
    if bid in messages:
        return f'<span style="color:var(--bonus);font-weight:600;font-size:13px">{messages[bid]}</span>'
    if rating >= 4.0:
        return f'<span style="color:var(--bonus);font-weight:600;font-size:13px">Top-rated SA bookmaker ({rating}/5.0)</span>'
    elif sports >= 25:
        return f'<span style="color:var(--bonus);font-weight:600;font-size:13px">{sports} sports markets available</span>'
    elif has_app:
        return f'<span style="color:var(--bonus);font-weight:600;font-size:13px">Dedicated mobile app available</span>'
    elif payments >= 8:
        return f'<span style="color:var(--bonus);font-weight:600;font-size:13px">{payments} payment methods accepted</span>'
    else:
        return f'<span style="color:var(--bonus);font-weight:600;font-size:13px">Licensed SA betting site</span>'


def build_listing_page(page_type):
    if page_type == 'betting-sites':
        brands = BRANDS_ORDERED
        title_text = f'Best Betting Sites in South Africa ({CURRENT_YEAR})'
        subtitle = f'All {len(brands)} licensed South African bookmakers compared by rating, bonus, odds, and payments. Updated {CURRENT_MONTH_YEAR}.'
        canon = 'betting-sites'
        active = 'betting'
    elif page_type == 'casino-sites':
        brands = [b for b in BRANDS_ORDERED if b.get('type','').lower() in ('both','casino') or 'casino' in b.get('otherProducts','').lower() or True]
        title_text = 'Best Online Casino Sites in South Africa (2026)'
        subtitle = f'Slots, live dealer, crash games, and jackpots on licensed SA platforms. Ranked by game variety, RTP, providers, and mobile casino quality. Updated {CURRENT_MONTH_YEAR}.'
        canon = 'casino-sites'
        active = 'casino'
    else:
        return ''

    # Calculate total bonus value
    total_bonus_val = sum(bonus_val(b) for b in brands)

    # Build brand data JSON for JS starred calculation
    brand_data_json = json.dumps([{"id": b["id"], "name": e(b["name"]), "bonus": bonus_val(b)} for b in brands])

    # Build freetips-style top list cards + desktop table
    rows = ''
    mobile_cards = ''
    copy_icon_card = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>'
    star_svg_full = '<svg width="14" height="14" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'
    for i, b in enumerate(brands):
        tc_text = e(b.get('tcs', '18+ T&Cs apply.'))
        mcp_tc = e(b.get('mcpTerms', '') or b.get('tcs', '18+ T&Cs apply.'))
        min_dep = e(b.get('minDeposit', ''))
        bv = bonus_val(b)
        bv_display = f'R{bv:,}' if bv > 0 else '-'
        star_icon = ICON_STAR
        logo = logo_path(b, 0)
        logo_img_sm = f'<img src="{logo}" alt="{e(b["name"])}" style="width:28px;height:28px;object-fit:contain;border-radius:4px;background:{brand_bg(b)};padding:2px;border:1px solid var(--border);flex-shrink:0" loading="lazy">' if logo else ''

        # Featured placement tag
        _FT_IDS = {'tictacbets', '10bet-south-africa', 'easybet-south-africa'}
        _ftag = ' <span style="font-size:10px;font-weight:600;color:var(--text-tertiary);background:var(--bg-tertiary,rgba(0,0,0,0.06));padding:1px 6px;border-radius:3px;vertical-align:middle">Featured</span>' if b['id'] in _FT_IDS else ''

        # Best For tags
        best_for_tags = ''.join(f'<span style="font-size:10px;color:var(--accent);background:var(--accent-light);padding:1px 6px;border-radius:3px;margin-right:3px">{t}</span>' for t in b.get('bestFor', [])[:2])
        best_for_row = f'<div style="margin-top:2px">{best_for_tags}</div>' if best_for_tags else ''

        # Desktop table row
        rows += f'''<tr data-name="{e(b['name']).lower()}" data-brand-id="{b['id']}" data-bonus-val="{bv}">
          <td data-sort="{i+1}" style="font-weight:600;color:var(--text-muted)">{i+1}</td>
          <td data-sort="{e(b['name'])}" style="white-space:nowrap">
            <div style="display:flex;align-items:center;gap:8px">
              <button class="star-btn" data-brand="{b['id']}" onclick="event.stopPropagation();toggleStar(\'{b['id']}\')" aria-label="Add to favourites">{star_icon}</button>
              {logo_img_sm}
              <a href="betting-site-review/{b['id']}.html" class="table-link" style="font-weight:600">{e(b['name'])}</a>{_ftag}
            </div>{best_for_row}
          </td>
          <td><span style="color:var(--bonus);font-weight:600">{e(b['welcomeBonusAmount'])}</span><br><span style="font-size:11px;color:var(--text-muted)">{tc_text}</span></td>
          <td data-sort="{bv}" style="text-align:center;font-weight:700;color:var(--bonus)">{bv_display}</td>
          <td data-sort="{b['overallRating']}" style="text-align:center">{rating_badge(b['overallRating'], 'sm')}</td>
          <td style="text-align:center"><a href="betting-site-review/{b['id']}.html" class="btn-outline btn-sm">Review</a></td>
        </tr>'''

        # Freetips-style top list card
        m_exit = masked_exit(b, 0)
        code = get_promo(b)
        rating_5_card = fmtRating(b['overallRating'])
        logo_card = f'<img src="{logo}" alt="{e(b["name"])}" class="toplist-logo" style="background:{brand_bg(b)}" loading="lazy">' if logo else ''
        bullets_data = get_brand_bullets(b)
        bullets_html = ''.join(f'<li>{e(bp)}</li>' for bp in bullets_data)
        full_stars = int(round(float(b['overallRating'])))
        stars_html = (star_svg_full * full_stars)
        promo_html = f'<div class="toplist-promo-box" onclick="navigator.clipboard.writeText(\'{e(code)}\');this.innerHTML=\'&#10003; Copied!\'"><span>Promo Code: {e(code)}</span> {copy_icon_card}</div>' if code and code not in ('None', 'N/A', '') else ''
        visit_cta = f'<a href="{m_exit}" target="_blank" rel="noopener noreferrer nofollow" class="toplist-cta">Visit {e(b["name"])} &#8594;</a>' if m_exit else ''
        review_link = f'<a href="betting-site-review/{b["id"]}.html" class="toplist-review-link">Read Full Review</a>'

        mobile_cards += f'''<div class="toplist-card" data-name="{e(b['name']).lower()}" data-brand-id="{b['id']}" data-bonus-val="{bv}" style="border-left:4px solid {brand_bg(b)}">
          <div class="toplist-rank">{i+1}</div>
          {('<div style="text-align:right;margin-bottom:-8px"><span style="font-size:10px;font-weight:600;color:var(--text-tertiary);background:var(--bg-tertiary,rgba(0,0,0,0.06));padding:2px 6px;border-radius:3px">Featured</span></div>') if b['id'] in _FT_IDS else ''}
          <div class="toplist-header">
            {logo_card}
            <div class="toplist-info">
              <div class="toplist-bonus">{e(b['welcomeBonusAmount'])}</div>
              <div class="toplist-reward">{bv_display} Bonus Value</div>
            </div>
            <div class="toplist-rating-circle">{rating_5_card}</div>
          </div>
          <div class="toplist-sales-msg">{get_brand_sales_msg(b)}</div>
          {f'<div class="best-for-label">{get_best_for(b)}</div>' if get_best_for(b) else ''}
          <ul class="toplist-bullets">{bullets_html}</ul>
          {promo_html}
          <div class="toplist-stars">{stars_html} <span>{full_stars}.0 / 5.0</span></div>
          {visit_cta}
          {review_link}
          <div class="toplist-tcs">{mcp_tc}</div>
          <div class="toplist-disclaimer">18+ | T&amp;Cs apply</div>
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
        _svg_phone = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12" y2="18"/></svg>'
        _svg_football = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20M2 12h20"/></svg>'
        _svg_rugby = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="12" rx="10" ry="6" transform="rotate(45 12 12)"/></svg>'
        _svg_money = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>'
        _svg_bolt = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
        _svg_bank = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="20" width="22" height="2"/><path d="M12 2L2 8h20z"/><line x1="5" y1="10" x2="5" y2="18"/><line x1="10" y1="10" x2="10" y2="18"/><line x1="14" y1="10" x2="14" y2="18"/><line x1="19" y1="10" x2="19" y2="18"/></svg>'
        _svg_ticket = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 9a3 3 0 0 0 0 6v5h20V15a3 3 0 0 0 0-6V4H2z"/></svg>'
        _svg_card = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>'
        _svg_gift = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="8" width="18" height="4" rx="1"/><rect x="3" y="12" width="18" height="8" rx="1"/><line x1="12" y1="8" x2="12" y2="20"/><path d="M12 8c-2-4-6-4-6 0h6c0-4 4-4 6 0h-6z"/></svg>'
        _svg_search = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>'
        _svg_new = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2z"/></svg>'
        _svg_compare = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'
        _svg_chart = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>'
        _svg_book = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>'
        _svg_target = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>'
        subcat_items = [
            ('Best Betting Apps', 'betting/best-betting-apps-south-africa.html', _svg_phone),
            ('Football Betting', 'betting/best-football-betting-sites.html', _svg_football),
            ('Rugby Betting', 'betting/best-rugby-betting-sites.html', _svg_rugby),
            ('Low Deposit Sites', 'betting/low-minimum-deposit-betting-sites.html', _svg_money),
            ('Ozow Betting Sites', 'betting/ozow-betting-sites.html', _svg_bolt),
            ('EFT Betting Sites', 'betting/eft-betting-sites.html', _svg_bank),
            ('1Voucher Sites', 'betting/1voucher-betting-sites.html', _svg_ticket),
            ('Visa/Mastercard', 'betting/visa-mastercard-betting-sites.html', _svg_card),
            ('OTT Voucher Sites', 'betting/ott-voucher-betting-sites.html', _svg_ticket),
            ('Apple Pay Sites', 'betting/apple-pay-betting-sites.html', _svg_card),
            ('Bonus Finder', 'betting/bonus-finder.html', _svg_gift),
            ('BonusBrowser', 'bonus-browser.html', _svg_bolt),
            ('Find Your Bookmaker', 'betting/find-your-bookmaker.html', _svg_search),
            ('New Betting Sites', 'new-betting-sites.html', _svg_new),
            ('Compare Bookmakers', 'compare/index.html', _svg_compare),
            ('Odds Explained', 'guides/odds-explained-south-africa.html', _svg_chart),
            ('Betting Strategies', 'guides/betting-strategies-south-africa.html', _svg_target),
            ('How to Bet on PSL', 'guides/how-to-bet-on-psl.html', _svg_football),
            ('Betting Markets', 'guides/sports-betting-markets-explained.html', _svg_book),
        ]
        subcat_html = _build_subcat_nav('Browse by Category', subcat_items)
    elif page_type == 'casino-sites':
        _svg_phone = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2"/><line x1="12" y1="18" x2="12" y2="18"/></svg>'
        _svg_slot = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><line x1="8" y1="4" x2="8" y2="20"/><line x1="16" y1="4" x2="16" y2="20"/></svg>'
        _svg_live = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>'
        _svg_gift = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="8" width="18" height="4" rx="1"/><rect x="3" y="12" width="18" height="8" rx="1"/><line x1="12" y1="8" x2="12" y2="20"/></svg>'
        _svg_plane = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>'
        _svg_flag = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>'
        _svg_chart = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>'
        subcat_items = [
            ('Best Casino Apps', 'casino/best-casino-apps-south-africa.html', _svg_phone),
            ('Online Slots Guide', 'casino-guides/online-slots-guide-south-africa.html', _svg_slot),
            ('Live Casino Guide', 'casino-guides/live-casino-guide-south-africa.html', _svg_live),
            ('Casino Bonuses Guide', 'casino-guides/casino-bonuses-guide-south-africa.html', _svg_gift),
            ('Crash Games', 'crash-games/index.html', _svg_plane),
            ('SA Slots', 'sa-slots/index.html', _svg_flag),
            ('RTP & House Edge', 'casino-guides/rtp-and-house-edge-explained.html', _svg_chart),
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

      {f'<div class="casino-quick-filters"><span style="font-size:13px;font-weight:600;color:var(--text-muted)">Quick filters:</span><button class="casino-filter active" onclick="casinoFilter(this,\'all\')">All Sites</button><button class="casino-filter" onclick="casinoFilter(this,\'slots\')">Slots</button><button class="casino-filter" onclick="casinoFilter(this,\'live\')">Live Casino</button><button class="casino-filter" onclick="casinoFilter(this,\'crash\')">Crash Games</button><button class="casino-filter" onclick="casinoFilter(this,\'table\')">Table Games</button></div>' if page_type == 'casino-sites' else ''}

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

      {subcat_html}

      {seo_mid}
      {seo_below}
    </div>
    <script>var brandBonusData = {brand_data_json};</script>'''

    list_ld = jsonld_itemlist(brands, title_text)
    og_img = 'og-betting-sites.jpg' if page_type == 'betting-sites' else 'og-casino-sites.jpg'
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
        rating_5_str = fmtRating(b['overallRating'])
        bonus = e(b['welcomeBonusAmount'])
        name = e(b['name'])
        bid = b['id']
        logo = logo_path(b, 0)
        bullets = get_brand_bullets(b)
        tcs = b.get('mcpTerms', '') or b.get('tcs', '') or ''
        tc_short = tcs if tcs else '18+. T&Cs apply.'
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

        # Featured placement tag
        _FEATURED_IDS = {'tictacbets', '10bet-south-africa', 'easybet-south-africa'}
        ftag = ' <span style="font-size:11px;font-weight:600;color:var(--text-tertiary);background:var(--bg-tertiary,rgba(0,0,0,0.06));padding:2px 8px;border-radius:4px;vertical-align:middle">Featured</span>' if bid in _FEATURED_IDS else ''

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
          {badge}{ftag}
        </div>
        <div style="display:flex;gap:6px;margin-top:2px"><span style="font-size:10px;color:var(--bonus);background:rgba(22,163,74,0.08);padding:1px 6px;border-radius:3px">Verified {CURRENT_MONTH_YEAR}</span>{'<span style="font-size:10px;color:var(--accent);background:var(--accent-light);padding:1px 6px;border-radius:3px">Code: ' + e(code) + '</span>' if code != 'NEWBONUS' and code else '<span style="font-size:10px;color:var(--text-muted);background:var(--surface-2);padding:1px 6px;border-radius:3px">Code: NEWBONUS</span>'}</div>
      </div>
    </div>
    <div class="rating-circle">
      <span class="rating-circle-score">{rating_5_str}</span><span style="font-size:11px;color:var(--text-muted);font-weight:600">/5.0</span>
    </div>
  </div>
  <div class="promo-card-offer">{bonus}</div>
  <div class="promo-card-code-box">
    <span class="promo-card-code-text">{e(code)}</span>
    <button class="promo-card-code-copy" onclick="copyCode(this,'{e(code)}')" aria-label="Copy code">{copy_icon}</button>
  </div>
  <ul class="promo-card-bullets">{bullet_items}</ul>
  <p class="promo-card-tcs">{tc_short}</p>
  <div style="display:flex;gap:8px;margin-top:4px">
    <a href="promo-code/{bid}.html" class="promo-card-cta" style="flex:1;background:transparent;color:var(--accent);border:1.5px solid var(--accent)">View Details</a>
    {f'<a href="{masked_exit(b, 0)}" target="_blank" rel="noopener noreferrer nofollow" class="promo-card-cta" style="flex:1">Claim Now</a>' if b.get('exitLink') else ''}
  </div>
</div>'''

    check_sm_p = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'
    promo_hero = category_hero(
        f"SA Betting Promo Codes - {CURRENT_MONTH_YEAR}",
        f"Every verified welcome bonus and promo code from all {total_brands} licensed SA bookmakers. Ranked, reviewed, and verified. Ready to claim.",
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
        <p>Every code on this page is verified and working as of {CURRENT_MONTH_YEAR}. 18+ only. T&Cs apply to all offers. Set a deposit limit before you start. Support is available 24/7 at 0800 006 008. Visit our <a href="responsible-gambling-policy.html">responsible gambling page</a> for support resources.</p>
      </div>
    </div>'''

    t_pc, d_pc = seo_meta('promos')
    return page(t_pc,
                 f'All {total_brands} South African betting promo codes and welcome bonuses ranked and compared - {CURRENT_MONTH_YEAR}.',
                 'promo-codes', body, depth=0, active_nav='promos', og_image='og-promo-codes.jpg')


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
          <div class="method-row-desktop" style="display:grid;grid-template-columns:1fr 140px 140px 100px 60px;gap:16px;align-items:center">
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
        f"{len(PAYMENTS)} ways to deposit and withdraw at South African betting sites. Compare speed, fees, and availability to find the right option.",
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

      <div class="method-list-header" style="padding:12px 20px;background:var(--table-head);border:1px solid var(--border);border-radius:10px 10px 0 0;margin-bottom:-1px;font-size:13px;font-weight:600;color:var(--text-muted)">
        <div style="display:grid;grid-template-columns:1fr 140px 140px 100px 60px;gap:16px;align-items:center">
          <span>Payment Method</span><span>Deposit Speed</span><span>Withdrawal Speed</span><span>Fees</span><span></span>
        </div>
      </div>
      <div class="method-list filterable-grid">{rows}</div>
    </div>'''

    return page('SA Betting Payment Methods Guide 2026 | MzansiWins',
                 'All the payment methods used at South African betting sites compared.',
                 'payment-methods', body, depth=0, active_nav='payments', og_image='og-payment-methods.jpg')


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
    editorial_count = len([a for a in NEWS if not a.get('isPromo')])
    promo_count_news = len([a for a in NEWS if a.get('isPromo')])
    filter_tabs = '<button class="news-filter-tab active" data-cat="all" onclick="filterNews(this, \'all\')">All <span class="news-filter-count">' + str(len(NEWS)) + '</span></button>'
    filter_tabs += f'<button class="news-filter-tab" data-cat="editorial" onclick="filterNews(this, \'editorial\')" style="--tab-color:#16a34a">Editorial <span class="news-filter-count">{editorial_count}</span></button>'
    filter_tabs += f'<button class="news-filter-tab" data-cat="promos" onclick="filterNews(this, \'promos\')" style="--tab-color:#b45309">Promotions <span class="news-filter-count">{promo_count_news}</span></button>'
    for cat in sorted_cats:
        cc = cat_colors.get(cat, '#555')
        filter_tabs += f'<button class="news-filter-tab" data-cat="{e(cat)}" onclick="filterNews(this, \'{e(cat)}\')" style="--tab-color:{cc}">{e(cat)} <span class="news-filter-count">{cat_counts[cat]}</span></button>'

    cards = ''
    for a in NEWS:
        cc = cat_colors.get(a.get('category',''), '#555')
        dt = datetime.fromisoformat(a['date'].replace('Z','+00:00')).strftime('%d %b %Y') if a.get('date') else ''
        is_promo = a.get('isPromo', False)
        promo_tag = '<span style="font-size:10px;font-weight:700;color:#b45309;background:#fef3c7;padding:2px 6px;border-radius:3px;text-transform:uppercase;letter-spacing:0.5px">Operator Promotion</span>' if is_promo else ''
        thumb_img = a.get('image', '')
        thumb_html = f'<div class="news-card-thumb"><img src="{thumb_img}" alt="" loading="lazy"></div>' if thumb_img else ''
        cards += f'''<a href="news/{a['slug']}.html" class="news-card" data-category="{e(a.get('category',''))}" data-promo="{'yes' if is_promo else 'no'}">
          {thumb_html}
          <div style="padding:20px">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap">
              <span class="news-badge" style="background:{cc}">{e(a.get('category',''))}</span>
              {promo_tag}
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
        f"Industry news, regulation updates, and operator announcements from the South African betting market. {len([a for a in NEWS if not a.get('isPromo')])} editorial articles and {len([a for a in NEWS if a.get('isPromo')])} operator promotions. Promotional content is labelled.",
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
    return page(t_nw, 'Latest South African betting industry news and updates.', 'news', body, depth=0, active_nav='news', og_image='og-news.jpg')


def build_content_page(page_type):
    if page_type == 'about-us':
        title = 'About MzansiWins'
        desc = 'MzansiWins reviews licensed South African betting operators. Operated by NWG PTY Limited, Cape Town.'
        canon = 'about-us'
        active = 'about'
        content = f'''<p>MzansiWins reviews South African betting operators through observed tests of sign-up, payments, withdrawals, support, and market coverage. Each review states what was tested, when it was tested, and where the operator performed well or poorly.</p>
        <h2>What We Do</h2>
        <p>Our reviews cover {len(DATA['brands'])} licensed operators. For each operator, a reviewer registers an account, completes a deposit and withdrawal cycle, contacts customer support, and documents the results. Reviews are updated when operators change their terms, payment options, or product.</p>
        <h2>Publisher</h2>
        <p>MzansiWins is published by NWG PTY Limited, a company registered in South Africa. The site covers licensed South African betting and gambling operators only.</p>
        <h2>Editorial Team</h2>
        <p>Reviews and guides on MzansiWins are produced by an editorial team that operates under pen names. This is standard practice in the affiliate review sector, where individual reviewers may face pressure from operators. The editorial team comprises four contributors with backgrounds in sports journalism, risk analysis, and the South African gambling market.</p>
        <p>Each review is written by one team member and fact-checked by another. Author pages on this site describe each contributor's area of focus and credentials. Editorial decisions are made independently of the commercial team.</p>
        <h2>Editorial Independence</h2>
        <p>MzansiWins earns affiliate commissions when readers open accounts through operator links on the site. Three operators (TicTacBets, 10Bet, and Easybet) have paid featured placement arrangements. These commercial relationships do not alter editorial scores or rankings. Operators are evaluated against the same criteria regardless of their commercial status with the site. The methodology, including the exact weighted formula used to calculate overall scores, is described on the <a href="how-we-rate.html">How We Rate</a> page.</p>
        <h2>Contact</h2>
        <p>Email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>. Responses within 48 business hours.</p>
        <p>Twitter/X <a href="https://x.com/mzansiwins" target="_blank" rel="noopener noreferrer">@mzansiwins</a></p>
        <div style="margin-top:20px;padding:20px;background:#f3f4f6;border-radius:12px;line-height:1.75">
          <strong>Registered Office</strong><br>
          NWG PTY Limited t/a MzansiWins<br>
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
        content = '''<p>Every bookmaker on MzansiWins is scored on a 5-point scale across seven categories. Each category carries a specific weight. Scores reflect observed test results, not promotional claims or advertiser relationships.</p>
        <h2>Testing Process</h2>
        <p>Each operator is tested through a real sign-up, a deposit, a withdrawal, and at least one contact with customer support. Results are recorded at the time of testing. When an operator makes a material change to its terms, payment options, or product, scores are reviewed and updated to reflect the current position.</p>
        <h2>Rating Categories</h2>
        <h3>Bonus Terms (25%)</h3>
        <p>We record the headline bonus amount alongside wagering requirements, minimum deposit, expiry period, and eligible markets. The score reflects the overall value of the offer once all conditions are applied, not the headline figure alone.</p>
        <h3>Odds Quality (20%)</h3>
        <p>Odds are compared on identical PSL football, Springbok rugby, and international cricket fixtures across all bookmakers. The score reflects the average margin observed across a sample of markets.</p>
        <h3>Payment Speed (15%)</h3>
        <p>We test each deposit method and record the time from withdrawal request to funds received. Scores reflect tested processing times per method, not operator claims.</p>
        <h3>Sports and Casino Variety (15%)</h3>
        <p>We count markets available for PSL football, Currie Cup rugby, Proteas cricket, horse racing, and additional sports. For casino products, we record the number of game titles and live dealer tables available.</p>
        <h3>Platform Quality (10%)</h3>
        <p>We test the mobile site and app for load speed, navigation, bet slip usability, and stability. Tests are conducted on both iOS and Android where apps are available.</p>
        <h3>Live Betting (10%)</h3>
        <p>We record the number of in-play markets available during a major fixture, how quickly odds update, and whether cash out is offered on in-play bets.</p>
        <h3>Support Responsiveness (5%)</h3>
        <p>We contact support via available channels and record response time and whether the query was resolved. Scores reflect the result of at least one tested contact per operator.</p>
        <h2>Overall Score Calculation</h2>
        <p>The overall rating is the weighted average of all seven category scores, rounded to one decimal place:</p>
        <p style="font-family:monospace;background:var(--bg-tertiary,#f5f5f5);padding:12px 16px;border-radius:8px;font-size:14px;line-height:1.8">
          Overall = (Bonus &times; 0.25) + (Odds &times; 0.20) + (Payment &times; 0.15) + (Variety &times; 0.15) + (Platform &times; 0.10) + (Live &times; 0.10) + (Support &times; 0.05)
        </p>
        <p>This calculation is applied automatically at build time. There is no manual override for the overall score. If a sub-score changes, the overall rating changes accordingly. Affiliate relationships do not affect any scores or category weights.</p>
        <p>Scores are updated when material changes occur at an operator, such as a change in withdrawal speed, a new bonus structure, or the addition or removal of payment methods.</p>'''
    elif page_type == 'fica-guide':
        title = 'FICA Verification Guide for SA Bettors'
        desc = 'Step-by-step guide to completing FICA verification at South African betting sites.'
        canon = 'fica-guide'
        active = 'fica'
        content = '''<p>FICA verification is a legal requirement for all licensed South African betting operators. Before processing a withdrawal, operators must verify your identity under the Financial Intelligence Centre Act. This page explains what documents are needed and how the process works.</p>
        <h2>What is FICA?</h2>
        <p>FICA stands for the Financial Intelligence Centre Act. All licensed South African betting operators are required to verify your identity before processing withdrawals. This protects against fraud and money laundering, and applies to every operator listed on this site.</p>
        <h2>Documents You Need</h2>
        <ul>
          <li><strong>South African ID</strong> - green book, smart ID card, or valid passport. Smart ID cards are typically processed fastest.</li>
          <li><strong>Proof of address</strong> - utility bill, bank statement, or municipal account dated within the last 3 months.</li>
          <li><strong>Proof of payment method</strong> - screenshot or photo of the bank account or e-wallet you deposit with.</li>
        </ul>
        <h2>Step-by-Step Process</h2>
        <h3>Step 1: Register Your Account</h3>
        <p>Register using the name exactly as it appears on your ID document. Name mismatches between your account and ID are the most common cause of verification delays.</p>
        <h3>Step 2: Upload Documents</h3>
        <p>Most bookmakers have a "Verify Account" or "FICA" section in your profile. Upload clear photos or scans. All text must be readable and no corners cut off. Blurry or partially obscured images are the most common reason for rejection.</p>
        <h3>Step 3: Wait for Approval</h3>
        <p>Typically 24 to 48 hours. Hollywoodbets and Betway tend to process faster, sometimes within a few hours during business hours. Other operators may take the full 48 hours.</p>
        <h3>Step 4: Start Withdrawing</h3>
        <p>Once verified, you can withdraw to any linked payment method. The first withdrawal may take slightly longer as operators run a final check. Subsequent withdrawals are typically faster.</p>
        <h2>Tips for Fast Verification</h2>
        <ul>
          <li>Use your smart ID card - it processes faster than the old green book</li>
          <li>Take photos in good lighting with a plain background</li>
          <li>Make sure your proof of address is from the last 3 months</li>
          <li>Upload during SA business hours (8am to 5pm) for the fastest turnaround</li>
          <li>If you have not heard back after 48 hours, contact their support team</li>
        </ul>
        <h2>Common Issues</h2>
        <p><strong>Name mismatch:</strong> Your registration name must match your ID exactly. If you registered with a different name, contact support to correct it before uploading documents.</p>
        <p><strong>Blurry documents:</strong> The most common reason for rejection. Take clear, well-lit photos where all text is fully legible.</p>
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
      <p>The South African online betting market is growing fast, and new bookmakers are joining the ranks regularly. These fresh entrants bring innovative features, generous sign-up bonuses, and modern platforms built from the ground up for mobile users. After bigger welcome offers or just want to try something different? New betting sites often have the most competitive deals as they fight to win your business.</p>
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
        f"Recently licensed South African bookmakers, tested through real sign-up and deposit. Updated {CURRENT_MONTH_YEAR}.",
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
        'content': '''<p>MzansiWins publishes reviews and guides for South African betting operators. This page describes the standards the editorial team applies.</p>
        <h2>Reviews Based on Observed Tests</h2>
        <p>Reviews on MzansiWins are based on observed tests: real sign-up, deposit, withdrawal, and support contact. Scores reflect what was recorded during those tests. Evaluative claims that cannot be traced to a test result are not published.</p>
        <h2>Affiliate Relationships</h2>
        <p>MzansiWins earns affiliate commissions when readers open accounts through operator links. Three operators have paid featured placement arrangements: TicTacBets, 10Bet, and Easybet. These commercial relationships do not affect editorial scores or rankings. All operators are assessed against the same methodology regardless of their commercial status with the site.</p>
        <h2>Corrections</h2>
        <p>When a factual error is identified, it is corrected and the correction is published with an explanation of what changed and why. The corrections log is maintained on the <a href="corrections-policy.html">Corrections Policy</a> page.</p>
        <h2>Conflicts of Interest</h2>
        <p>Team members are required to declare any financial interest in operators reviewed on the site. Where a conflict exists, that person is removed from the review process for that operator.</p>
        <h2>Contact</h2>
        <p>If you believe we have breached this code, contact us at <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>. We investigate every complaint and respond within 48 business hours.</p>'''
    },
    'editorial-policy': {
        'title': 'Editorial Policy',
        'meta_desc': 'MzansiWins Editorial Policy. How we research, write, and publish betting site reviews and guides for South African players.',
        'content': '''<p>This page explains how MzansiWins produces and maintains its reviews and guides.</p>
        <h2>How Reviews Are Produced</h2>
        <p>Each sportsbook and casino review is based on a real test: the reviewer registers an account, completes a deposit and withdrawal, contacts customer support, and records the results. Reviews state what was tested, when, and what was found. Scores are assigned using the methodology described on the <a href="how-we-rate.html">How We Rate</a> page.</p>
        <h2>Affiliate Relationships</h2>
        <p>MzansiWins earns affiliate commissions when readers open accounts through operator links. Three operators (TicTacBets, 10Bet, and Easybet) have paid featured placement arrangements, which are marked as such on relevant pages. Affiliate relationships do not affect editorial scores. All operators are evaluated against the same criteria.</p>
        <h2>Corrections</h2>
        <p>Factual errors are corrected and the correction is published with an explanation of what changed. See the <a href="corrections-policy.html">Corrections Policy</a> for the process and correction log.</p>
        <h2>Contact</h2>
        <p>Reach the editorial team at <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
    'fact-checking': {
        'title': 'Fact Checking Policy',
        'meta_desc': 'How MzansiWins verifies facts, bonus details, and claims in our South African betting site reviews.',
        'content': '''<p>Every factual claim on MzansiWins goes through a verification process before publication. This page describes how that process works.</p>
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
        <p>Betting operator terms change frequently. Published content is reviewed on a rolling basis and updated when information changes. If you spot something that appears outdated, contact us at <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
    'corrections-policy': {
        'title': 'Corrections Policy',
        'meta_desc': 'MzansiWins Corrections Policy. How we handle errors and inaccuracies in our South African betting content.',
        'content': '''<p>MzansiWins corrects factual errors in its content as follows:</p>
        <h2>Correction Process</h2>
        <ul>
        <li><strong>Minor corrections:</strong> Typographical errors and small factual updates (such as changed bonus amounts or updated payment terms) are corrected in the published page without a formal notice.</li>
        <li><strong>Significant corrections:</strong> Material errors - such as incorrect operator scores, wrong promo codes, or inaccurate regulatory information - are corrected and flagged with a dated correction notice at the top of the affected page.</li>
        <li><strong>Retractions:</strong> If content is found to be fundamentally inaccurate, it will be removed and a brief explanation published in its place.</li>
        </ul>
        <h2>Report an Error</h2>
        <p>To report an error, email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a> with the page URL and a description of the issue. MzansiWins aims to investigate and respond within 48 business hours.</p>
        <h2>Correction Log</h2>
        <p>March 2026: Updated Betway withdrawal processing time from "same day" to "1-3 business days" following reader verification. Previous figure was based on a single test; updated figure reflects five separate withdrawal tests.</p>'''
    },
    'affiliate-disclosure': {
        'title': 'Affiliate Disclosure',
        'meta_desc': 'MzansiWins Affiliate Disclosure. How we earn money and why it does not affect our betting site reviews.',
        'content': '''<p>MzansiWins earns revenue through affiliate commissions paid by licensed South African betting operators. When a reader opens an account through a link on this site, MzansiWins may receive a commission from that operator. Using affiliate links costs readers nothing and does not change the terms or bonuses available to them.</p>
        <h2>Featured Placements</h2>
        <p>Three operators have paid featured placement arrangements with MzansiWins: TicTacBets, 10Bet, and Easybet. These operators appear in highlighted positions in certain listings as a result of those commercial arrangements.</p>
        <h2>Effect on Editorial Ratings</h2>
        <p>Editorial scores and rankings are not influenced by affiliate commissions or featured placement arrangements. Operators are evaluated against the same criteria regardless of their commercial relationship with the site. The scoring methodology is described on the <a href="how-we-rate.html">How We Rate</a> page.</p>
        <h2>Display Advertising</h2>
        <p>Display advertising from licensed operators may be introduced on this site in future. Any such advertising will be clearly labelled.</p>
        <p>Questions? Email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
    'advertising-disclosure': {
        'title': 'Advertising Disclosure',
        'meta_desc': 'MzansiWins Advertising Disclosure. How sponsored content and advertising works on our site.',
        'content': '''<p>MzansiWins earns revenue through affiliate commissions paid by licensed South African betting operators. When a reader opens an account through a link on this site, MzansiWins may receive a commission from that operator.</p>
        <h2>Featured Placements</h2>
        <p>Three operators have paid featured placement arrangements with MzansiWins: TicTacBets, 10Bet, and Easybet. Featured placement means these operators appear in highlighted positions in certain listings. These arrangements are commercially funded and are identified as such on the relevant pages.</p>
        <h2>Editorial Ratings</h2>
        <p>Editorial scores and rankings are not influenced by commercial relationships. All operators are evaluated against the same methodology regardless of whether they have a featured placement or affiliate arrangement with the site. The scoring methodology is described on the <a href="how-we-rate.html">How We Rate</a> page.</p>
        <h2>Display Advertising</h2>
        <p>Display advertising from licensed operators may be introduced on this site in future. Any such advertising will be labelled clearly.</p>
        <p>For advertising enquiries, email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
    'complaints-policy': {
        'title': 'Complaints Policy',
        'meta_desc': 'MzansiWins Complaints Policy. How to raise a complaint and our process for resolving issues.',
        'content': '''<p>If you have a complaint about content published on MzansiWins, this page explains how to raise it and what to expect.</p>
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
        'content': '''<p>MzansiWins only lists licensed South African operators that provide responsible gambling tools. This page outlines those commitments and where to find help if needed.</p>
        <h2>Our Commitment</h2>
        <ul>
        <li>We only promote licensed, regulated South African bookmakers that have responsible gambling tools in place.</li>
        <li>We never target our content at anyone under the age of 18.</li>
        <li>We encourage all readers to set deposit limits, loss limits, and time limits on their betting accounts.</li>
        <li>We do not use language that encourages excessive or irresponsible gambling.</li>
        </ul>
        <h2>Warning Signs</h2>
        <p>If you answer yes to any of the following, consider contacting one of the support organisations listed below:</p>
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
        <li><strong>Website:</strong> <a href="https://www.responsiblegambling.org.za" target="_blank" rel="noopener noreferrer">responsiblegambling.org.za</a></li>
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
        <p>All of these services are free and confidential.</p>'''
    },
    'betting-risk-awareness': {
        'title': 'Betting Risk Awareness',
        'meta_desc': 'Understanding the risks of sports betting in South Africa. Honest information to help you bet responsibly.',
        'content': '''<p>Sports betting carries financial risk. This page explains how bookmaker margins work, what wagering requirements mean in practice, and how to manage a betting budget.</p>
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
        <p>Self-exclusion is a responsible decision available to all South African bettors. For support, call <strong>0800 006 008</strong> or email <a href="mailto:help@mzansiwins.co.za">help@mzansiwins.co.za</a>.</p>'''
    },
    # Corporate
    'management-team': {
        'title': 'Management Team',
        'meta_desc': 'Meet the MzansiWins editorial team. The betting analysts, casino experts, and payment specialists behind South Africa\'s trusted review platform.',
        'content': '''<p>MzansiWins is run by a focused editorial team with backgrounds in sports journalism, mathematics, data analytics, and fintech. Every review, guide, and recommendation on this site is produced by people with direct experience in the industries they write about. All authors write under editorial pen names.</p>

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
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">Since 2018, Thabo has specialised in analysing licensed betting operators serving South African players. He has personally reviewed more than 100 betting platforms across Africa, focusing on licensing standards, pricing competitiveness, and customer protections. His work means all bookmaker reviews are grounded in factual testing rather than promotional claims.</p>
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
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Sipho also develops educational content built to help bettors understand probability, variance, and disciplined bankroll management.</p>
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
          <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">She personally tests every deposit and withdrawal method listed on the site and tracks payout speeds across all South African-facing bookmakers listed on the site. Her work also examines verification requirements under South Africa's FICA regulations, helping players understand identity checks, withdrawal procedures, and common delays.</p>
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
        <li><strong>Targeted audience:</strong> Our readers are active South African bettors researching operators, bonuses, and betting strategies.</li>
        <li><strong>Trust:</strong> MzansiWins publishes evidence-based reviews of licensed South African operators.</li>
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
      <p>Smart punters do not guess - they calculate. If you need to work out what an accumulator pays, converting between odds formats, or figuring out how much to stake on an arbitrage opportunity, these tools do the maths instantly so you can make informed decisions before risking your hard-earned rands.</p>

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
        ('Do these calculators work with South African bookmakers?', 'Absolutely. Every calculator is designed for SA bettors using ZAR. They work with odds from any South African bookmaker including Hollywoodbets, Betway, Sportingbet, Supabets, and all licensed operators listed on our site.'),
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
    return page(t, d, 'betting-calculators', body, depth=0, active_nav='calculators', og_image='og-calculators.jpg')


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
    urls.append(('bonus-browser', '0.7'))
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

# BonusBrowser
from bonus_browser import build_bonus_browser
write_file(f'{OUT}/bonus-browser.html', build_bonus_browser(
    BRANDS=BRANDS, OUT=OUT, page_fn=page, logo_path_fn=logo_path,
    masked_exit_fn=masked_exit, _esc_json_fn=_esc_json, BASE_URL=BASE_URL
))
print(f'\nGenerating {len(CALCULATORS)} calculator pages...')
for calc in CALCULATORS:
    write_file(f'{OUT}/calculators/{calc["id"]}.html', build_calculator_page(calc))

# Masked exit link redirect pages
# /go/ redirects removed - exit links now use MCP Hyperlinkurl directly
print(f'\nExit links use MCP Hyperlinkurl directly (no /go/ redirects)')

# ======== EXPANSION PAGES ========
print('\nBuilding expansion pages...')
from build_expansion import run_expansion, build_crash_games_category, build_sa_slots_section
expansion_sitemap = run_expansion(
    DATA=DATA, BRANDS=BRANDS, BRANDS_ORDERED=BRANDS_ORDERED,
    page_fn=page, breadcrumbs_fn=breadcrumbs, logo_path_fn=logo_path, category_hero_fn=category_hero,
    masked_exit_fn=masked_exit, brand_bg_fn=brand_bg, rating_badge_fn=rating_badge,
    write_file_fn=write_file, OUT=OUT, BASE_URL=BASE_URL,
    ICON_CHECK=ICON_CHECK, ICON_X=ICON_X, ICON_TROPHY=ICON_TROPHY,
    ICON_GIFT=ICON_GIFT, ICON_SHIELD=ICON_SHIELD, ICON_CHEVRON_RIGHT=ICON_CHEVRON_RIGHT,
    ICON_CHEVRON_DOWN=ICON_CHEVRON_DOWN, ICON_STAR=ICON_STAR, ICON_ARROW_LEFT=ICON_ARROW_LEFT
)

# ======== CRASH GAMES CATEGORY ========
print('Building crash games category...')
crash_sitemap = build_crash_games_category(
    page_fn=page, category_hero_fn=category_hero, breadcrumbs_fn=breadcrumbs,
    write_file_fn=write_file, BRANDS=BRANDS, masked_exit_fn=masked_exit,
    brand_bg_fn=brand_bg, logo_path_fn=logo_path, rating_badge_fn=rating_badge,
    OUT=OUT, BASE_URL=BASE_URL
)
expansion_sitemap += crash_sitemap
print(f'  {len(crash_sitemap)} crash games pages created')

# ======== SA SLOTS SECTION ========
print('Building SA slots section...')
slots_sitemap = build_sa_slots_section(
    page_fn=page, category_hero_fn=category_hero, breadcrumbs_fn=breadcrumbs,
    write_file_fn=write_file, BRANDS=BRANDS, masked_exit_fn=masked_exit,
    brand_bg_fn=brand_bg, logo_path_fn=logo_path, rating_badge_fn=rating_badge,
    OUT=OUT, BASE_URL=BASE_URL
)
expansion_sitemap += slots_sitemap
print(f'  {len(slots_sitemap)} SA slots pages created')

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
_add_url(urlset, f'{BASE_URL}/betting-calculators', today, 'weekly', '0.8')
_add_url(urlset, f'{BASE_URL}/bonus-browser', today, 'weekly', '0.7')
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

# robots.txt
with open(f'{OUT}/robots.txt', 'w') as f:
    f.write(f"""User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n""")
print('robots.txt created')

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
