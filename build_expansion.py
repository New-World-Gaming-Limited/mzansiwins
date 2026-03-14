"""
MzansiWins Site Expansion - New Category Pages
Generates: sport pages, comparison pages, payment-by-method pages, guides,
quiz, bonus finder, author pages, and casino equivalents.
Called from build_site.py after the main build.
"""
import json, os, random
from html import escape as _e

def e(s):
    return _e(str(s)) if s else ''

# ---------------------------------------------------------------------------
# DATA
# ---------------------------------------------------------------------------
with open(os.path.join(os.path.dirname(__file__), 'site_expansion_data.json')) as f:
    EXPANSION = json.load(f)

AUTHORS = EXPANSION['authors']
AUTHORS_MAP = {a['id']: a for a in AUTHORS}

# Author photo mapping
AUTHOR_PHOTOS = {
    'Thabo Mokoena': 'author-thabo-mokoena.jpg',
    'Lerato Dlamini': 'author-lerato-dlamini.jpg',
    'Sipho Nkosi': 'author-sipho-nkosi.jpg',
    'Naledi Khumalo': 'author-naledi-khumalo.jpg',
}
AUTHOR_NAMES_LIST = ['Thabo Mokoena', 'Sipho Nkosi', 'Lerato Dlamini', 'Naledi Khumalo']
def get_review_author(brand_id):
    idx = sum(ord(c) for c in brand_id) % len(AUTHOR_NAMES_LIST)
    return AUTHOR_NAMES_LIST[idx]
def author_img_tag(name, size=80, depth=0):
    prefix = '../' * depth
    photo = AUTHOR_PHOTOS.get(name)
    if photo:
        return f'<img src="{prefix}assets/{photo}" alt="{e(name)}" width="{size}" height="{size}" style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;object-position:center 20%;flex-shrink:0" loading="lazy">'
    initials = ''.join(w[0] for w in name.split()[:2]).upper() if name else 'MW'
    return f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:#1641B4;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:{max(size//3,12)}px;flex-shrink:0">{initials}</div>'
BETTING_GUIDES = EXPANSION['betting_guides']
CASINO_GUIDES = EXPANSION['casino_guides']
COMPARISONS_BETTING = EXPANSION['comparisons_betting']
COMPARISONS_CASINO = EXPANSION['comparisons_casino']
PAYMENT_METHOD_PAGES_DATA = EXPANSION['payment_method_pages']


def run_expansion(DATA, BRANDS, BRANDS_ORDERED, page_fn, breadcrumbs_fn, logo_path_fn,
                  masked_exit_fn, brand_bg_fn, rating_badge_fn, write_file_fn,
                  OUT, BASE_URL, ICON_CHECK, ICON_X, ICON_TROPHY, ICON_GIFT,
                  ICON_SHIELD, ICON_CHEVRON_RIGHT, ICON_CHEVRON_DOWN, ICON_STAR,
                  ICON_ARROW_LEFT, category_hero_fn=None, news_sidebar_top5_fn=None):
    """Build all expansion pages. Returns list of (url_path, priority) for sitemap."""
    sitemap_entries = []
    os.makedirs(f'{OUT}/betting', exist_ok=True)
    os.makedirs(f'{OUT}/casino', exist_ok=True)
    os.makedirs(f'{OUT}/guides', exist_ok=True)
    os.makedirs(f'{OUT}/casino-guides', exist_ok=True)
    os.makedirs(f'{OUT}/compare', exist_ok=True)
    os.makedirs(f'{OUT}/authors', exist_ok=True)

    # Helper: category hero
    category_hero = category_hero_fn

    # Helper: brand lookup
    brands_map = {b['id']: b for b in DATA['brands']}

    def bc(items, depth=0):
        return breadcrumbs_fn(items, depth)

    def logo(brand, depth=0):
        return logo_path_fn(brand, depth)

    def exit_link(brand, depth=0):
        return masked_exit_fn(brand, depth)

    def bg(brand):
        return brand_bg_fn(brand)

    def badge(r, size=''):
        return rating_badge_fn(r, size)

    # Helper: top N brands filtered
    def top_brands_for(filter_fn, n=5):
        return sorted([b for b in DATA['brands'] if filter_fn(b)],
                      key=lambda b: b['overallRating'], reverse=True)[:n]

    # Helper: brand card for listing
    def brand_card_html(brand, depth, rank=None):
        lp = logo(brand, depth)
        logo_img = f'<img src="{lp}" alt="{e(brand["name"])}" style="width:48px;height:48px;object-fit:contain;border-radius:10px;background:{bg(brand)};padding:4px">' if lp else ''
        ex = exit_link(brand, depth)
        visit_btn = f'<a href="{ex}" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary" style="font-size:13px;padding:10px 22px;border-radius:24px;white-space:nowrap">Visit Site</a>' if ex else ''
        rank_badge = f'<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:var(--accent);color:#fff;font-size:13px;font-weight:700;flex-shrink:0">#{rank}</span>' if rank else ''
        # Pros (first 2)
        pros = brand.get('pros', [])[:2]
        pros_html = ''.join(f'<li style="font-size:13px;line-height:1.6;color:var(--text-secondary);margin-bottom:4px;padding-left:18px;position:relative"><span style="position:absolute;left:0;color:#16a34a">&#10003;</span>{e(p)}</li>' for p in pros)
        prefix = '../' * depth
        return f'''<div class="expansion-brand-card" style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:24px;margin-bottom:16px">
          <div style="display:flex;align-items:flex-start;gap:16px;flex-wrap:wrap">
            <div style="display:flex;align-items:center;gap:12px;flex:1;min-width:200px">
              {rank_badge}
              {logo_img}
              <div style="min-width:0">
                <a href="{prefix}betting-site-review/{brand['id']}.html" style="font-size:18px;font-weight:700;color:var(--text-primary);text-decoration:none">{e(brand['name'])}</a>
                <div style="margin-top:4px">{badge(brand['overallRating'], 'sm')}</div>
              </div>
            </div>
            <div style="text-align:right;flex-shrink:0">
              <div style="font-size:15px;font-weight:700;color:var(--bonus);margin-bottom:6px">{e(brand['welcomeBonusAmount'])}</div>
              <div style="display:flex;align-items:center;gap:6px;justify-content:flex-end;margin-bottom:10px">
                <span style="font-family:monospace;font-size:12px;font-weight:700;padding:4px 10px;background:#FFF8E7;border:1.5px dashed #d4a843;border-radius:6px">{e(brand['promoCode'])}</span>
              </div>
              {visit_btn}
            </div>
          </div>
          <ul style="margin-top:14px;padding:0;list-style:none">{pros_html}</ul>
          <p style="font-size:12px;color:var(--text-muted);margin-top:10px">{e(brand.get('tcs','18+ T&Cs apply.'))}</p>
        </div>'''

    # Helper: full-width brand card for subcategory pages (inspired by UK casino comparison layout)
    def brand_card_fullwidth_html(brand, depth, rank=None, sport_detail=None):
        lp = logo(brand, depth)
        logo_img = f'<img src="{lp}" alt="{e(brand["name"])}" style="width:64px;height:64px;object-fit:contain;border-radius:12px;background:{bg(brand)};padding:4px;border:1px solid var(--border)">' if lp else ''
        ex = exit_link(brand, depth)
        prefix = '../' * depth
        review_url = f'{prefix}betting-site-review/{brand["id"]}.html'
        promo_url = f'{prefix}promo-code/{brand["id"]}.html'
        promo = e(brand.get('promoCode', 'NEWBONUS'))
        bonus_text = e(brand.get('welcomeBonusAmount', ''))
        rating = brand.get('overallRating', 4.0)
        rating_fmt = f'{rating:.1f}'
        tcs = e(brand.get('tcs', '18+. New customers only. T&Cs apply.'))
        min_dep = e(brand.get('minDeposit', 'R20'))

        # Stars SVG
        full_stars = int(rating)
        half_star = 1 if (rating - full_stars) >= 0.3 else 0
        stars_svg = ''.join('<svg width="14" height="14" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>' for _ in range(full_stars))
        if half_star:
            stars_svg += '<svg width="14" height="14" viewBox="0 0 24 24" fill="#f59e0b" stroke="#f59e0b" stroke-width="1" opacity="0.5"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>'

        # Brand-specific sales messages per category
        def _brand_msgs(b, cat):
            sc = len(b.get('sportsCovered', []))
            has_stream = b.get('liveStreaming', '').lower().startswith('yes')
            has_live = b.get('liveBetting', '').lower().startswith('yes')
            co = b.get('cashOut', '')
            has_partial_co = 'partial' in co.lower()
            has_co = 'yes' in co.lower()
            ma = b.get('mobileApp', '')
            has_ios = 'ios' in ma.lower()
            has_android = 'android' in ma.lower()
            has_app = ma.lower().startswith('yes')
            r_odds = b.get('ratingOdds', 0)
            r_var = b.get('ratingVariety', 0)
            r_live = b.get('ratingLive', 0)
            other = b.get('otherProducts', '')
            has_casino = 'casino' in other.lower()
            bname = b.get('name', '')

            if cat == 'football':
                pool = []
                # Odds quality differentiator
                if r_odds >= 4.5:
                    pool.append(f'Top-rated football odds among SA bookmakers')
                elif r_odds >= 4.0:
                    pool.append(f'Competitive PSL &amp; Premier League odds')
                else:
                    pool.append(f'PSL, Premier League &amp; Champions League markets')
                # Market depth
                if r_var >= 4.5:
                    pool.append(f'{sc}+ sports with deep football market coverage')
                elif sc >= 25:
                    pool.append(f'Extensive football coverage across {sc}+ sports')
                else:
                    pool.append(f'Football markets including PSL and European leagues')
                # Live/streaming
                if has_stream and has_live:
                    pool.append(f'Live streaming &amp; in-play betting on football')
                elif has_live and has_co:
                    pool.append(f'In-play football betting with cash-out')
                elif has_live:
                    pool.append(f'Live in-play betting on football matches')
                else:
                    pool.append(f'Pre-match football betting with strong odds')
                # Unique differentiator
                if has_partial_co:
                    pool.append(f'Partial cash-out on football multi-bets')
                elif has_casino:
                    pool.append(f'Football betting plus casino games under one roof')
                elif has_app and has_ios:
                    pool.append(f'Bet on football via iOS &amp; Android app')
                elif has_app:
                    pool.append(f'Mobile app for football betting on the go')
                else:
                    pool.append(f'Build custom football accumulators')
                return pool[:4]

            elif cat == 'rugby':
                pool = []
                if r_odds >= 4.5:
                    pool.append(f'Best-in-class rugby odds for Springbok matches')
                elif r_odds >= 4.0:
                    pool.append(f'Sharp odds on URC, Currie Cup &amp; Test rugby')
                else:
                    pool.append(f'Springbok Tests, URC &amp; Currie Cup markets')
                if r_var >= 4.5:
                    pool.append(f'Deep rugby markets - try scorer, handicaps &amp; more')
                elif sc >= 25:
                    pool.append(f'Covers {sc}+ sports including niche rugby comps')
                else:
                    pool.append(f'Try scorer, handicap &amp; total points markets')
                if has_stream and has_live:
                    pool.append(f'Watch &amp; bet live on rugby with streaming')
                elif has_live and has_partial_co:
                    pool.append(f'Live rugby betting with partial cash-out')
                elif has_live:
                    pool.append(f'In-play rugby betting with real-time odds')
                else:
                    pool.append(f'Pre-match rugby markets for every round')
                if has_partial_co:
                    pool.append(f'Partial cash-out mid-match on rugby bets')
                elif has_app and has_ios:
                    pool.append(f'Bet on the Boks via iOS &amp; Android app')
                elif has_app:
                    pool.append(f'Mobile app ready for matchday rugby betting')
                elif has_casino:
                    pool.append(f'Rugby betting plus casino entertainment')
                else:
                    pool.append(f'Specials for Boks, Stormers &amp; Bulls fixtures')
                return pool[:4]

            elif cat == 'apps':
                pool = []
                if has_ios and has_android:
                    pool.append(f'Native iOS &amp; Android app available')
                elif has_android:
                    pool.append(f'Android app (APK download from site)')
                else:
                    pool.append(f'Mobile-optimised site with app-like experience')
                if has_stream:
                    pool.append(f'Live streaming built into the mobile app')
                elif has_live:
                    pool.append(f'Full live betting with real-time odds on mobile')
                else:
                    pool.append(f'Pre-match betting optimised for mobile')
                if has_partial_co:
                    pool.append(f'Cash out (including partial) from the app')
                elif has_co:
                    pool.append(f'One-tap cash-out on open bets')
                else:
                    pool.append(f'Fast loading on SA mobile networks')
                # Unique per brand
                if 'ozow' in ' '.join(b.get('paymentMethodsList', [])).lower():
                    pool.append(f'Ozow &amp; EFT deposits directly in-app')
                elif r_odds >= 4.5:
                    pool.append(f'Top-rated odds - compare on the go')
                elif sc >= 25:
                    pool.append(f'{sc}+ sports markets at your fingertips')
                else:
                    pool.append(f'Quick deposits via EFT &amp; vouchers')
                return pool[:4]

            elif cat == 'low-deposit':
                pool = []
                pool.append(f'Minimum deposit from as low as {min_dep}')
                if bonus_text:
                    pool.append(f'{bonus_text}')
                else:
                    pool.append(f'Welcome bonus available on first deposit')
                if has_live and has_co:
                    pool.append(f'Live betting &amp; cash-out even on small stakes')
                elif has_live:
                    pool.append(f'Full live betting access from {min_dep}')
                else:
                    pool.append(f'All markets accessible from {min_dep}')
                if has_app:
                    pool.append(f'Mobile app for quick low-value deposits')
                elif sc >= 20:
                    pool.append(f'{sc}+ sports markets with no stake restrictions')
                else:
                    pool.append(f'No reduced odds for small stakes')
                return pool[:4]

            elif cat == 'ozow':
                pool = [
                    f'Instant Ozow deposits in under 30 seconds',
                ]
                if has_co:
                    pool.append(f'Cash out winnings quickly after Ozow deposit')
                else:
                    pool.append(f'No card details needed - bank-level security')
                if bonus_text:
                    pool.append(f'{bonus_text} with Ozow deposit')
                else:
                    pool.append(f'Full bonus eligibility via Ozow')
                pool.append(f'Works with FNB, Absa, Nedbank &amp; Standard Bank')
                return pool[:4]

            elif cat == 'eft':
                pool = [
                    f'EFT deposits via all major SA banks',
                ]
                if bonus_text:
                    pool.append(f'{bonus_text} with EFT deposit')
                else:
                    pool.append(f'No third-party fees on EFT transfers')
                if has_co:
                    pool.append(f'EFT withdrawals plus cash-out on open bets')
                else:
                    pool.append(f'EFT withdrawals within 24-48 hours')
                if has_app:
                    pool.append(f'Initiate EFT deposits from the mobile app')
                else:
                    pool.append(f'Secure banking with South African banks only')
                return pool[:4]

            elif cat == 'voucher':
                pool = [
                    f'1Voucher deposits accepted instantly',
                ]
                if bonus_text:
                    pool.append(f'{bonus_text} when depositing via 1Voucher')
                else:
                    pool.append(f'No bank account needed to deposit')
                if sc >= 20:
                    pool.append(f'Access {sc}+ sports markets with voucher deposit')
                else:
                    pool.append(f'Full platform access from a voucher deposit')
                if has_live:
                    pool.append(f'Live betting available after voucher top-up')
                else:
                    pool.append(f'Privacy-friendly - no banking details shared')
                return pool[:4]

            elif cat == 'visa':
                pool = [
                    f'Visa &amp; Mastercard deposits processed instantly',
                ]
                if has_co:
                    pool.append(f'Fast card withdrawals with cash-out support')
                else:
                    pool.append(f'Card withdrawals back to same card')
                if bonus_text:
                    pool.append(f'{bonus_text} on card deposit')
                else:
                    pool.append(f'3D Secure authentication for safety')
                pool.append(f'Supports debit, credit &amp; prepaid cards')
                return pool[:4]

            elif cat == 'ott':
                pool = [
                    f'OTT Voucher deposits in seconds',
                ]
                if bonus_text:
                    pool.append(f'{bonus_text} with OTT top-up')
                else:
                    pool.append(f'Buy OTT at Shoprite, Checkers &amp; Pick n Pay')
                if has_live:
                    pool.append(f'Jump straight into live betting after OTT deposit')
                else:
                    pool.append(f'No bank details needed to fund your account')
                pool.append(f'Available in denominations from R10 to R3,000')
                return pool[:4]

            elif cat == 'apple-pay':
                pool = [
                    f'Apple Pay deposits with Face ID or Touch ID',
                ]
                if bonus_text:
                    pool.append(f'{bonus_text} via Apple Pay deposit')
                else:
                    pool.append(f'Instant processing - no card numbers to type')
                if has_stream:
                    pool.append(f'Deposit &amp; watch live streams in seconds')
                else:
                    pool.append(f'Secure tokenised payments via Wallet app')
                pool.append(f'Works with all major SA bank cards in Wallet')
                return pool[:4]

            # Default fallback
            return [
                f'Licensed SA bookmaker - fully regulated',
                f'{bonus_text}' if bonus_text else 'Competitive welcome bonus',
                f'Fast deposits &amp; withdrawals',
                f'Mobile-friendly with live betting',
            ]

        msgs = _brand_msgs(brand, sport_detail)[:4]
        msgs_html = ''.join(f'<li style="font-size:13px;line-height:1.6;color:var(--text-secondary);padding:3px 0;padding-left:20px;position:relative"><span style="position:absolute;left:0;color:var(--accent)">&#10003;</span>{m}</li>' for m in msgs)

        rank_html = f'<div style="font-size:28px;font-weight:800;color:var(--text-muted);flex-shrink:0;min-width:44px;text-align:center">#{rank}</div>' if rank else ''

        visit_btn = f'<a href="{ex}" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary" style="display:block;text-align:center;font-size:14px;font-weight:700;padding:12px 28px;border-radius:24px;white-space:nowrap;margin-bottom:10px">Visit Site</a>' if ex else ''

        return f'''<div class="subcat-brand-card" style="background:var(--surface);border:var(--card-border);border-left:4px solid var(--accent);border-radius:12px;padding:24px 28px;margin-bottom:20px">
          <div style="display:flex;align-items:flex-start;gap:20px;flex-wrap:wrap">
            <div style="display:flex;align-items:center;gap:16px;flex-shrink:0">
              {rank_html}
              {logo_img}
            </div>
            <div style="flex:1;min-width:220px">
              <a href="{review_url}" style="font-size:20px;font-weight:800;color:var(--text-primary);text-decoration:none;display:block;margin-bottom:2px">{e(brand['name'])}</a>
              <div style="font-size:16px;font-weight:700;color:var(--bonus);margin-bottom:8px">{bonus_text}</div>
              <ul style="margin:0;padding:0;list-style:none">{msgs_html}</ul>
            </div>
            <div style="display:flex;flex-direction:column;align-items:center;gap:6px;flex-shrink:0;min-width:160px">
              <div style="display:flex;align-items:center;gap:2px;margin-bottom:2px">{stars_svg}</div>
              <div style="font-size:16px;font-weight:800;color:var(--text-primary)">{rating_fmt}/5.0</div>
              {visit_btn}
              <div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center">
                <a href="{review_url}" style="font-size:12px;font-weight:600;color:var(--accent);text-decoration:none;padding:5px 14px;border:1.5px solid var(--accent);border-radius:20px;white-space:nowrap">Read Review</a>
                <a href="{promo_url}" style="font-size:12px;font-weight:600;color:var(--accent);text-decoration:none;padding:5px 14px;border:1.5px solid var(--accent);border-radius:20px;white-space:nowrap">Promo Code</a>
              </div>
            </div>
          </div>
          <p style="font-size:11px;color:var(--text-muted);margin-top:14px;padding-top:12px;border-top:1px solid var(--sep);line-height:1.5">{tcs} Promo code: {promo}. Min deposit: {min_dep}. 18+. <a href="{prefix}responsible-gambling-policy.html" style="color:var(--text-muted);text-decoration:underline">T&amp;Cs apply</a>. GambleAware.co.za</p>
        </div>'''

    # Helper: sidebar with top 5 brands
    def sidebar_top5(depth):
        top5 = BRANDS[:5]
        items = ''
        for b in top5:
            lp = logo(b, depth)
            logo_img = f'<img src="{lp}" alt="{e(b["name"])}" style="width:28px;height:28px;object-fit:contain;border-radius:6px;background:{bg(b)};padding:2px">' if lp else ''
            prefix = '../' * depth
            items += f'''<div style="display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--sep)">
              {logo_img}
              <div style="flex:1;min-width:0">
                <a href="{prefix}betting-site-review/{b['id']}.html" style="font-size:13px;font-weight:600;color:var(--text-primary)">{e(b['name'])}</a>
                <div style="font-size:11px;color:var(--bonus)">{e(b['welcomeBonusAmount'][:40])}</div>
              </div>
            </div>'''
        prefix = '../' * depth
        return f'''<aside class="expansion-sidebar lg-show" style="position:sticky;top:80px">
          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:20px">
            <h3 style="font-size:15px;font-weight:700;margin-bottom:12px">Top SA Bookmakers</h3>
            {items}
            <a href="{prefix}betting-sites.html" style="display:block;text-align:center;margin-top:12px;font-size:13px;font-weight:600;color:var(--accent)">View all {len(BRANDS)} bookmakers {ICON_CHEVRON_RIGHT}</a>
          </div>
        </aside>'''

    # Helper: breadcrumb JSON-LD
    def bc_jsonld(items):
        ld_items = []
        for i, item in enumerate(items):
            entry = {"@type": "ListItem", "position": i + 1, "name": item["label"]}
            if item.get("href"):
                entry["item"] = f'{BASE_URL}/{item["href"]}'
            ld_items.append(entry)
        return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ld_items})

    # Helper: internal link CTA block
    def internal_links_block(depth, category='betting'):
        prefix = '../' * depth
        if category == 'betting':
            return f'''<div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:24px;margin-top:32px">
              <h2 style="font-size:17px;font-weight:700;margin-bottom:14px">Explore More Betting Content</h2>
              <div style="display:flex;flex-wrap:wrap;gap:8px">
                <a href="{prefix}betting-sites.html" class="btn-outline btn-sm">All Betting Sites</a>
                <a href="{prefix}promo-codes.html" class="btn-outline btn-sm">Promo Codes</a>
                <a href="{prefix}betting/best-betting-apps-south-africa.html" class="btn-outline btn-sm">Best Betting Apps</a>
                <a href="{prefix}betting/low-minimum-deposit-betting-sites.html" class="btn-outline btn-sm">Low Deposit Sites</a>
                <a href="{prefix}guides/" class="btn-outline btn-sm">Betting Guides</a>
                <a href="{prefix}betting/bonus-finder.html" class="btn-outline btn-sm">Bonus Finder</a>
                <a href="{prefix}compare/" class="btn-outline btn-sm">Compare Sites</a>
                <a href="{prefix}betting-calculators.html" class="btn-outline btn-sm">Calculators</a>
              </div>
            </div>'''
        else:
            return f'''<div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:24px;margin-top:32px">
              <h2 style="font-size:17px;font-weight:700;margin-bottom:14px">Explore More Casino Content</h2>
              <div style="display:flex;flex-wrap:wrap;gap:8px">
                <a href="{prefix}casino-sites.html" class="btn-outline btn-sm">All Casino Sites</a>
                <a href="{prefix}promo-codes.html" class="btn-outline btn-sm">Casino Bonuses</a>
                <a href="{prefix}casino-guides/" class="btn-outline btn-sm">Casino Guides</a>
                <a href="{prefix}casino/best-casino-apps-south-africa.html" class="btn-outline btn-sm">Casino Apps</a>
                <a href="{prefix}betting-calculators.html" class="btn-outline btn-sm">Calculators</a>
              </div>
            </div>'''

    # ====================================================================
    # 1. AUTHOR PAGES
    # ====================================================================
    print('  Building author pages...')
    # Authors index page
    authors_cards = ''
    for author in AUTHORS:
        avatar_html = author_img_tag(author['name'], size=80, depth=0)
        expertise_tags = ''.join(f'<span style="display:inline-block;font-size:11px;font-weight:600;padding:4px 10px;background:var(--accent-light);color:var(--accent);border-radius:20px">{e(exp)}</span>' for exp in author.get('expertise', []))
        authors_cards += f'''<a href="authors/{author['id']}.html" style="text-decoration:none;color:inherit" class="card" >
          <div style="display:flex;align-items:center;gap:20px;padding:24px">
            {avatar_html}
            <div>
              <h2 style="font-size:18px;font-weight:700;margin-bottom:4px">{e(author['name'])}</h2>
              <p style="font-size:14px;color:var(--accent);font-weight:600;margin-bottom:8px">{e(author['role'])}</p>
              <p style="font-size:14px;color:var(--text-secondary);line-height:1.6;margin-bottom:10px">{e(author['bio'][:150])}...</p>
              <div style="display:flex;flex-wrap:wrap;gap:6px">{expertise_tags}</div>
            </div>
          </div>
        </a>'''

    bc_items = [{"label": "Home", "href": "index.html"}, {"label": "About Us", "href": "about-us.html"}, {"label": "Our Authors"}]
    body = f'''
    <div class="container" style="padding-top:40px;padding-bottom:80px">
      {bc(bc_items, 0)}
      <script type="application/ld+json">{bc_jsonld(bc_items)}</script>
      <h1 class="page-title">Meet the MzansiWins Team</h1>
      <p class="page-subtitle" style="margin-bottom:32px">The people behind your trusted SA betting and casino reviews. Real expertise, no fluff.</p>
      <div style="display:grid;gap:16px">{authors_cards}</div>
    </div>'''
    write_file_fn(f'{OUT}/our-authors.html',
                  page_fn('Our Authors - Meet the MzansiWins Review Team', 'Meet the expert team behind MzansiWins. Our authors bring years of experience in SA betting, casino analysis, payments, and responsible gambling.', 'our-authors', body, depth=0, active_nav=''))
    sitemap_entries.append(('our-authors', '0.5'))

    # Individual author pages
    for author in AUTHORS:
        avatar_html = author_img_tag(author['name'], size=100, depth=1)
        expertise_tags = ''.join(f'<span style="display:inline-block;font-size:12px;font-weight:600;padding:5px 12px;background:var(--accent-light);color:var(--accent);border-radius:20px">{e(exp)}</span>' for exp in author.get('expertise', []))
        # Find articles by this author
        all_guides = BETTING_GUIDES + CASINO_GUIDES
        author_guides = [g for g in all_guides if g.get('author') == author['id']]
        guides_html = ''
        if author_guides:
            guides_list = ''
            for g in author_guides:
                folder = 'guides' if g in BETTING_GUIDES else 'casino-guides'
                gid = g['id']
                gtitle = g['title']
                guides_list += f'<li style="margin-bottom:8px"><a href="../{folder}/{gid}.html" style="font-size:14px;color:var(--accent);font-weight:500">{e(gtitle)}</a></li>'
            author_name_escaped = e(author['name'])
            guides_html = f'<h2 style="font-size:17px;font-weight:700;margin-top:32px;margin-bottom:12px">Articles by {author_name_escaped}</h2><ul style="padding-left:20px">{guides_list}</ul>'

        # Find brands reviewed by this author
        author_brands = [b for b in BRANDS if get_review_author(b['id']) == author['name']]
        reviews_html = ''
        if author_brands:
            reviews_list = ''
            for b in author_brands:
                logo_html = ''
                lp = logo_path_fn(b, 1)
                if lp:
                    logo_html = f'<img src="{lp}" alt="{e(b["name"])}" style="width:24px;height:24px;border-radius:6px;object-fit:contain;border:1px solid var(--border);background:{brand_bg_fn(b)};padding:2px" loading="lazy">'
                reviews_list += f'<li style="margin-bottom:10px"><a href="../betting-site-review/{b["id"]}.html" style="display:inline-flex;align-items:center;gap:8px;font-size:14px;color:var(--accent);font-weight:500">{logo_html}{e(b["name"])} Review</a></li>'
            reviews_html = f'<h2 style="font-size:17px;font-weight:700;margin-top:32px;margin-bottom:12px">Reviews by {e(author["name"])}</h2><ul style="list-style:none;padding-left:0">{reviews_list}</ul>'

        bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Our Authors", "href": "our-authors.html"}, {"label": author['name']}]
        bc_jsonld_str = bc_jsonld([{"label": "Home", "href": "index.html"}, {"label": "Our Authors", "href": "our-authors.html"}, {"label": author['name'], "href": f"authors/{author['id']}.html"}])
        body = f'''
        <div class="container" style="padding-top:40px;padding-bottom:80px">
          {bc(bc_items, 1)}
          <script type="application/ld+json">{bc_jsonld_str}</script>
          <div style="display:flex;align-items:flex-start;gap:28px;flex-wrap:wrap;margin-bottom:32px">
            {avatar_html}
            <div style="flex:1;min-width:200px">
              <h1 class="page-title" style="margin-bottom:4px">{e(author['name'])}</h1>
              <p style="font-size:16px;color:var(--accent);font-weight:600;margin-bottom:12px">{e(author['role'])}</p>
              <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px">{expertise_tags}</div>
            </div>
          </div>
          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-bottom:24px">
            <h2 style="font-size:17px;font-weight:700;margin-bottom:12px">About {e(author['name'].split()[0])}</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">{e(author['bio'])}</p>
          </div>
          {guides_html}
          {reviews_html}
          <div style="margin-top:32px"><a href="../our-authors.html" style="display:inline-flex;align-items:center;gap:6px;font-size:14px;color:var(--accent);font-weight:500">{ICON_ARROW_LEFT} All Authors</a></div>
        </div>'''
        write_file_fn(f'{OUT}/authors/{author["id"]}.html',
                      page_fn(f'{author["name"]} - {author["role"]} | MzansiWins', f'{author["name"]} is {author["role"]} at MzansiWins. {author["bio"][:120]}', f'authors/{author["id"]}', body, depth=1, active_nav=''))
        sitemap_entries.append((f'authors/{author["id"]}', '0.4'))
    print(f'    {len(AUTHORS)} author pages + index')

    # ====================================================================
    # 2. SPORT-SPECIFIC PAGES (Betting)
    # ====================================================================
    print('  Building sport-specific pages...')
    # Cross-linking helper for subcategory pages
    def subcat_crosslinks(depth, category='betting', current_page=''):
        prefix = '../' * depth
        if category == 'betting':
            links = [
                ('betting-sites.html', 'All Betting Sites'),
                ('betting/best-rugby-betting-sites.html', 'Rugby Betting'),
                ('betting/best-football-betting-sites.html', 'Football Betting'),
                ('betting/best-betting-apps-south-africa.html', 'Best Betting Apps'),
                ('betting/low-minimum-deposit-betting-sites.html', 'Low Deposit Sites'),
                ('promo-codes.html', 'Promo Codes'),
                ('betting/bonus-finder.html', 'Bonus Finder'),
                ('compare/', 'Compare Sites'),
                ('guides/', 'Betting Guides'),
                ('casino-sites.html', 'Casino Sites'),
            ]
        else:
            links = [
                ('casino-sites.html', 'All Casino Sites'),
                ('casino/best-casino-apps-south-africa.html', 'Casino Apps'),
                ('casino-guides/', 'Casino Guides'),
                ('promo-codes.html', 'Promo Codes'),
                ('betting-sites.html', 'Betting Sites'),
                ('betting/bonus-finder.html', 'Bonus Finder'),
                ('compare/', 'Compare Sites'),
            ]
        pills = ''
        for href, label in links:
            if current_page and current_page in href:
                continue
            pills += f'<a href="{prefix}{href}" class="btn-outline btn-sm">{label}</a>'
        return f'''<div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:24px;margin-top:32px">
              <h2 style="font-size:17px;font-weight:700;margin-bottom:14px">Related Pages</h2>
              <div style="display:flex;flex-wrap:wrap;gap:8px">{pills}</div>
            </div>'''

    sport_pages = [
        {
            "id": "best-rugby-betting-sites",
            "sport": "Rugby",
            "title": "Best Rugby Betting Sites South Africa 2026",
            "seo_title": "Best Rugby Betting Sites South Africa 2026 - Top 5 Picks",
            "seo_desc": "Find the best rugby betting sites in South Africa for 2026. Springboks, URC, Currie Cup - our experts rank the top 5 SA bookmakers for rugby betting.",
            "h1": "Best Rugby Betting Sites in South Africa",
            "intro": "Whether you are backing the Springboks in a Test series or placing a punt on the URC, you need a bookmaker that takes rugby seriously. We have tested all 36 licensed SA betting sites and ranked the top 5 for rugby betting based on odds quality, live betting coverage, market depth, and bonuses.",
            "filter": lambda b: 'Rugby' in b.get('sportsCovered', []),
            "guide_link": "how-to-bet-on-rugby-south-africa",
            "sport_detail": "rugby",
            "extended_content": '''<div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:32px">
                <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">What to Look for in a Rugby Betting Site</h2>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">The best rugby betting sites offer far more than just match winner. Look for markets like first try scorer, handicap betting, total points over/under, half-time/full-time, and penalty count. For Test matches and big URC fixtures, top bookmakers like Zarbet and Betway also offer player props and team specials.</p>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">South Africa is a rugby-mad nation, and your bookmaker should reflect that. The best sites cover Springbok Tests, the United Rugby Championship, Currie Cup, and the Rugby Championship with deep markets. Some even offer specials for the British and Irish Lions tours and the Rugby World Cup qualifiers.</p>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Live betting is where rugby gets truly exciting. Momentum shifts happen constantly in rugby - a yellow card, a dominant scrum, or a breakaway try can flip the match. The sites we rank highest offer real-time odds updates with minimal lag, cash-out options mid-game, and a wide spread of in-play markets including next scoring method and next try scorer.</p>
                <h3 style="font-size:16px;font-weight:600;margin-bottom:8px">Popular Rugby Betting Markets in SA</h3>
                <ul style="padding-left:20px;margin-bottom:16px">
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Match Result</strong> - The classic home/away/draw. Simple and straightforward.</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Handicap Betting</strong> - Level the playing field between mismatched teams. Popular for Springbok Tests against lower-ranked sides.</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>First Try Scorer</strong> - Pick who crosses the line first. Wingers like Cheslin Kolbe are always popular picks.</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Total Points Over/Under</strong> - Will the combined score go above or below a set number? Great for matches with clear attacking styles.</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Winning Margin</strong> - Predict how close the final score will be. Pays better than a straight match result bet.</li>
                </ul>
                <h3 style="font-size:16px;font-weight:600;margin-bottom:8px">Our Top Tip</h3>
                <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:16px;background:var(--accent-light);border-radius:8px;border-left:3px solid var(--accent)">Rugby is a physical game with plenty of momentum swings. Live betting markets during the second half can offer great value, especially when a team is trailing but has the set-piece advantage. Also keep an eye on weather conditions - rain makes handling errors more likely and favours the under on total points.</p>
              </div>
              <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:24px">
                <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">How We Rank Rugby Betting Sites</h2>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Our rankings are not random. We evaluate each SA bookmaker on five core criteria, weighted specifically for rugby betting. A site might have the best welcome bonus in the country, but if their rugby odds are consistently poor and their live markets lag behind, they will not make our top 5.</p>
                <ul style="padding-left:0;list-style:none">
                  <li style="padding:8px 0;padding-left:24px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent);font-weight:700">1.</span><strong>Rugby Odds Quality</strong> - We compare odds across all SA bookmakers for every major Test match and URC round</li>
                  <li style="padding:8px 0;padding-left:24px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent);font-weight:700">2.</span><strong>Market Depth</strong> - How many rugby markets per fixture? Do they cover Currie Cup or just Tests?</li>
                  <li style="padding:8px 0;padding-left:24px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent);font-weight:700">3.</span><strong>Live Betting</strong> - Real-time in-play coverage with fast odds updates and cash-out options</li>
                  <li style="padding:8px 0;padding-left:24px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent);font-weight:700">4.</span><strong>Welcome Bonus</strong> - The best sign-up offers for new rugby punters</li>
                  <li style="padding:8px 0;padding-left:24px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent);font-weight:700">5.</span><strong>Payouts</strong> - Fast withdrawals when your Springbok bet comes in</li>
                </ul>
              </div>
              <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:24px">
                <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Rugby Betting Calendar - Key Dates for SA Punters</h2>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">South African rugby runs almost year-round. The Currie Cup kicks off in January and runs through to the final in June. The URC season stretches from September through to the knockouts in June. Springbok Tests are scattered across mid-year (incoming tours) and end-of-year (November tours to Europe). Then you have the Rugby Championship from August to September. For punters, this means there is almost always a rugby match worth betting on.</p>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">Make sure your chosen bookmaker covers all these competitions, not just the Springbok fixtures. A site that only offers odds on Test matches is leaving money on the table for dedicated rugby punters who follow the domestic season closely.</p>
              </div>''',
        },
        {
            "id": "best-football-betting-sites",
            "sport": "Football",
            "title": "Best Football Betting Sites South Africa 2026",
            "seo_title": "Best Football Betting Sites South Africa 2026 - Top 5 Picks",
            "seo_desc": "The best football betting sites in South Africa for 2026. PSL, Premier League, Champions League - top 5 SA bookmakers ranked for football betting.",
            "h1": "Best Football Betting Sites in South Africa",
            "intro": "Football is the most popular sport to bet on in South Africa, and every bookmaker knows it. From the PSL to the English Premier League, the competition between SA betting sites for football punters is fierce. We have evaluated odds, market depth, live streaming, and bonuses to bring you the top 5.",
            "filter": lambda b: 'Football' in b.get('sportsCovered', []),
            "guide_link": "how-to-bet-on-football-south-africa",
            "sport_detail": "football",
            "extended_content": '''<div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:32px">
                <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">What to Look for in a Football Betting Site</h2>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">The top football betting sites offer hundreds of markets per match - from match result and both teams to score to Asian handicaps, corner betting, and goalscorer markets. For big leagues like the Premier League and Champions League, expect 200+ markets per fixture at sites like 10Bet and Betway.</p>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">For South African punters, the PSL is where it starts. The DStv Premiership and Nedbank Cup are the bread and butter of local football betting. But the real test of a good betting site is how they handle the international leagues. English Premier League, La Liga, Serie A, Bundesliga, Champions League, and even the MLS - the best SA bookmakers cover them all with competitive odds and deep markets.</p>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Live streaming is a big differentiator. Some SA bookmakers like Betway offer live streaming of select football matches, which means you can watch and bet at the same time. This is especially valuable for European fixtures that you might not get on regular South African TV. If live streaming matters to you, check our individual reviews for which sites offer it.</p>
                <h3 style="font-size:16px;font-weight:600;margin-bottom:8px">Popular Football Betting Markets</h3>
                <ul style="padding-left:20px;margin-bottom:16px">
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Match Result (1X2)</strong> - The simplest bet. Pick home win, away win, or draw.</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Both Teams to Score (BTTS)</strong> - Will both sides find the net? Great for matches between attacking teams.</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Over/Under Goals</strong> - Predict whether the total goals will be above or below 2.5 (the most popular line).</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Anytime Goalscorer</strong> - Pick a player to score at any point in the match. Combines well in multi-bets.</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Asian Handicap</strong> - Eliminates the draw and gives one team a head start. Tighter margins mean better value for serious punters.</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Correct Score</strong> - High risk, high reward. Predict the exact final score for big payouts.</li>
                </ul>
                <h3 style="font-size:16px;font-weight:600;margin-bottom:8px">Our Top Tip</h3>
                <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:16px;background:var(--accent-light);border-radius:8px;border-left:3px solid var(--accent)">The PSL often has inflated odds on draws. South African football is unpredictable, and bookmakers sometimes overreact to recent form. Look for value on the draw market, especially in derbies. Also consider building accumulators from different leagues to avoid correlation risk.</p>
              </div>
              <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:24px">
                <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">How We Rank Football Betting Sites</h2>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">We do not just look at who has the flashiest homepage. Our ranking process for football betting sites focuses on what actually matters to punters who bet on football regularly. We compare odds on identical PSL and Premier League fixtures across every SA bookmaker, and the differences can be significant. Over a season, those margins add up.</p>
                <ul style="padding-left:0;list-style:none">
                  <li style="padding:8px 0;padding-left:24px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent);font-weight:700">1.</span><strong>Football Odds Quality</strong> - We compare odds on PSL and Premier League fixtures weekly across all SA bookmakers</li>
                  <li style="padding:8px 0;padding-left:24px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent);font-weight:700">2.</span><strong>Market Depth</strong> - How many football markets per match? Do they cover lower leagues?</li>
                  <li style="padding:8px 0;padding-left:24px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent);font-weight:700">3.</span><strong>Live Betting &amp; Streaming</strong> - In-play coverage, cash-out, and live match streaming</li>
                  <li style="padding:8px 0;padding-left:24px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent);font-weight:700">4.</span><strong>Welcome Bonus</strong> - The best sign-up offers for football punters</li>
                  <li style="padding:8px 0;padding-left:24px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent);font-weight:700">5.</span><strong>Payouts</strong> - Fast withdrawals when your accumulator hits</li>
                </ul>
              </div>
              <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:24px">
                <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Football Betting Calendar for SA Punters</h2>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">The beauty of football betting is that the calendar is packed year-round. The PSL season runs from August to May, overlapping nicely with the European seasons. The Premier League, La Liga, and Serie A all kick off in August and wrap up in May or June. The Champions League and Europa League add midweek action from September through to the finals in May and June.</p>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">During the off-season, there are still international friendlies, pre-season tournaments, and summer leagues to keep you busy. The AFCON qualifiers and World Cup qualifiers also provide excellent betting opportunities for Bafana Bafana supporters. Smart punters open accounts at multiple bookmakers to always get the best odds on any given fixture.</p>
              </div>''',
        }
    ]

    for sp in sport_pages:
        top5 = top_brands_for(sp['filter'], 5)
        cards = ''
        for i, b in enumerate(top5, 1):
            cards += brand_card_fullwidth_html(b, 1, rank=i, sport_detail=sp.get('sport_detail'))
        bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Betting Sites", "href": "betting-sites.html"}, {"label": sp['title'].split(' South Africa')[0]}]
        sport_deco = {'football': '&#x26BD;', 'rugby': '&#x1F3C9;'}
        hero_html = category_hero(sp['h1'], sp['intro'], bc_items, 1, deco_icon=sport_deco.get(sp.get('sport',''), ''))
        body = f'''
        {hero_html}
        <div class="container" style="padding-top:32px;padding-bottom:80px;max-width:900px">
          {cards}
          {sp['extended_content']}
          <div style="margin-top:24px"><a href="../guides/{sp['guide_link']}.html" class="btn-outline" style="font-size:14px;padding:10px 24px;border-radius:24px">Read Our {e(sp['sport'])} Betting Guide {ICON_CHEVRON_RIGHT}</a></div>
          {subcat_crosslinks(1, 'betting', sp['id'])}
        </div>'''
        write_file_fn(f'{OUT}/betting/{sp["id"]}.html',
                      page_fn(sp['seo_title'], sp['seo_desc'], f'betting/{sp["id"]}', body, depth=1, active_nav='betting'))
        sitemap_entries.append((f'betting/{sp["id"]}', '0.8'))

    # ====================================================================
    # 3. BEST BETTING APPS PAGE
    # ====================================================================
    print('  Building best betting apps page...')
    app_brands = sorted([b for b in DATA['brands'] if b.get('mobileApp','').lower().startswith('yes')],
                        key=lambda b: b['overallRating'], reverse=True)[:10]
    app_cards = ''
    for i, b in enumerate(app_brands, 1):
        app_cards += brand_card_fullwidth_html(b, 1, rank=i, sport_detail='apps')
    bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Betting Sites", "href": "betting-sites.html"}, {"label": "Best Betting Apps"}]
    apps_hero = category_hero('Best Betting Apps in South Africa 2026', f'Not every SA bookmaker has a proper mobile app. We have tested them all and ranked the top {len(app_brands)} betting apps available on iOS and Android in South Africa.', bc_items, 1, deco_icon='&#x1F4F1;')
    body = f'''
    {apps_hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px;max-width:900px">
      {app_cards}
          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:32px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">What Makes a Great Betting App?</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">A great betting app in South Africa needs to do more than just shrink the desktop site onto a smaller screen. The best apps offer smooth navigation, fast loading on South African mobile networks, push notifications for live bets, and easy deposit and withdrawal options including Ozow and EFT.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">We tested each app on both Wi-Fi and mobile data (including slower 3G connections that are still common in many parts of SA). Load times matter when you are trying to place a live bet before the odds shift. The apps that made our top list load core betting pages in under three seconds on LTE and handle in-play betting without freezing or crashing.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Security is another factor we weigh heavily. The best betting apps support biometric login (fingerprint or Face ID), two-factor authentication, and encrypted connections. You are trusting these apps with your banking details and personal information, so security cannot be an afterthought.</p>
            <h3 style="font-size:16px;font-weight:600;margin-bottom:8px">Native App vs Mobile Site</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">Some bookmakers offer dedicated apps from the App Store or Google Play, while others have mobile-optimised websites. Both can work well, but native apps tend to offer faster performance, biometric login, and push notifications for your bets. If a bookmaker only has a mobile site, that is not necessarily a deal-breaker - just check that it runs smoothly on your device.</p>
          </div>
          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:24px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">How to Download Betting Apps in SA</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px"><strong>iOS (iPhone/iPad):</strong> Most SA betting apps are available on the Apple App Store. Search for the bookmaker name and download directly. Apple requires all gambling apps to be geo-restricted, so you will need a South African Apple ID or be physically in SA to find them.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px"><strong>Android:</strong> Google Play does not always list gambling apps for South Africa. Most bookmakers offer an APK download from their website instead. You will need to enable "Install from unknown sources" in your phone settings. This sounds dodgy, but it is standard practice - just make sure you are downloading from the official bookmaker website and not a random link.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px"><strong>Huawei:</strong> Some bookmakers like betbus, Jackpot City, and Supersportbet are available on Huawei AppGallery. Huawei users can also sideload APKs the same way as other Android devices.</p>
          </div>
          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:24px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Key Features to Look For</h2>
            <ul style="padding-left:20px;margin-bottom:16px">
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Live Betting</strong> - The app should support in-play betting with real-time odds updates. Slow refresh rates mean you miss value.</li>
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Push Notifications</strong> - Get alerts for bet results, promotions, and live match events without opening the app.</li>
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Quick Deposits</strong> - One-tap deposits via Ozow, EFT, or saved card details. The fewer taps, the better.</li>
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Cash Out</strong> - Settle bets early directly from the app. Essential for live betting on the go.</li>
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Bet Builder</strong> - Create custom multi-bets within a single match. The best apps make this intuitive on mobile.</li>
            </ul>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">If you are serious about mobile betting, it is worth having two or three apps installed from different bookmakers. This lets you compare odds on the fly and always grab the best price. Check our <a href="../compare/" style="color:var(--accent);text-decoration:underline">head-to-head comparisons</a> to see how the top apps stack up against each other.</p>
          </div>
          <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:8px">
            <a href="../betting-sites.html" class="btn-outline" style="font-size:14px;padding:10px 24px;border-radius:24px">All Betting Sites</a>
            <a href="../promo-codes.html" class="btn-outline" style="font-size:14px;padding:10px 24px;border-radius:24px">Promo Codes</a>
          </div>
      {subcat_crosslinks(1, 'betting', 'best-betting-apps')}
    </div>'''
    write_file_fn(f'{OUT}/betting/best-betting-apps-south-africa.html',
                  page_fn('Best Betting Apps South Africa 2026 - Top 10 Mobile Apps', 'The best betting apps in South Africa for 2026. Download top-rated iOS and Android betting apps from licensed SA bookmakers. Expert-tested and ranked.', 'betting/best-betting-apps-south-africa', body, depth=1, active_nav='betting'))
    sitemap_entries.append(('betting/best-betting-apps-south-africa', '0.8'))

    # ====================================================================
    # 4. LOW MINIMUM DEPOSIT PAGE
    # ====================================================================
    print('  Building low minimum deposit page...')
    def parse_min_dep(brand):
        md = brand.get('minDeposit', 'R50')
        try:
            return int(''.join(c for c in md.split('(')[0] if c.isdigit()))
        except:
            return 50
    low_dep = sorted(DATA['brands'], key=lambda b: (parse_min_dep(b), -b['overallRating']))
    low_dep_r10 = [b for b in low_dep if parse_min_dep(b) <= 10][:10]
    cards = ''
    for i, b in enumerate(low_dep_r10, 1):
        cards += brand_card_html(b, 1, rank=i)
    bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Betting Sites", "href": "betting-sites.html"}, {"label": "Low Minimum Deposit"}]
    lowdep_hero = category_hero('Low Minimum Deposit Betting Sites South Africa', 'You do not need a fat wallet to start betting. These SA bookmakers let you deposit as little as R1 to R10, so you can try the platform without risking much.', bc_items, 1, deco_icon='&#x1F4B0;')
    body = f'''
    {lowdep_hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px;max-width:900px">
          {cards}
          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:32px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Why Low Deposit Sites Matter</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">A low minimum deposit means you can test a new bookmaker with minimal risk. Some sites like YesPlay allow R1 deposits, while others like Betway and Mzansibet start at R10. This is perfect for beginners who want to learn the ropes without committing serious cash.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Keep in mind that bonus eligibility often requires a higher deposit. Always check the T&Cs - a site might accept R5 deposits but require R50 to qualify for the welcome bonus. We flag these details in each of our <a href="../betting-sites.html" style="color:var(--accent);text-decoration:underline">individual betting site reviews</a> so you know exactly what to expect before you sign up.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Low deposit sites are also great for testing different bookmakers before committing to one. You can open accounts at three or four sites, deposit R10 at each, and see which platform feels right for your betting style. The navigation, odds presentation, and cash-out features all vary between sites, and there is no substitute for hands-on experience.</p>
          </div>
          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:24px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">How to Make the Most of a Small Deposit</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Starting with a small deposit does not mean you cannot win. Here are some tips for stretching your rands further:</p>
            <ul style="padding-left:20px;margin-bottom:16px">
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Stick to single bets first.</strong> Multi-bets are tempting because the potential payout is huge, but the probability of winning drops sharply with each leg. Build your bankroll with singles before going for the big accas.</li>
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Use your welcome bonus wisely.</strong> Most sites offer a match bonus on your first deposit. If you deposit R10 and get a R10 bonus, you have R20 to play with. Read the wagering requirements on our <a href="../promo-codes.html" style="color:var(--accent);text-decoration:underline">promo codes page</a> before claiming.</li>
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Shop for the best odds.</strong> Even small differences in odds add up over time. Use our <a href="../compare/" style="color:var(--accent);text-decoration:underline">comparison tool</a> to find which bookmaker offers the best price on your chosen bet.</li>
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Set a loss limit.</strong> Decide beforehand how much you are willing to lose and stick to it. This is not just responsible gambling advice - it is smart bankroll management.</li>
            </ul>
          </div>
          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:24px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Deposit Methods for Small Amounts</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Not every payment method works well for small deposits. Bank EFTs sometimes have minimum transfer amounts, and credit card fees can eat into a tiny deposit. For low-value deposits, we recommend Ozow (instant EFT with no minimums at most sites), 1VOUCHER, and airtime top-up where available. Check our <a href="../payment-methods.html" style="color:var(--accent);text-decoration:underline">payment methods hub</a> for a full breakdown of which methods work best for different deposit amounts.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">Some bookmakers also accept cryptocurrency for deposits, which can be useful for small amounts since there are no bank processing fees. However, crypto availability varies between sites and you will need to check the minimum deposit in BTC or ETH equivalent.</p>
          </div>
          <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:8px">
            <a href="../betting-sites.html" class="btn-outline" style="font-size:14px;padding:10px 24px;border-radius:24px">All Betting Sites</a>
            <a href="../guides/" class="btn-outline" style="font-size:14px;padding:10px 24px;border-radius:24px">Betting Guides</a>
          </div>
          {subcat_crosslinks(1, 'betting', 'low-minimum')}
    </div>'''
    write_file_fn(f'{OUT}/betting/low-minimum-deposit-betting-sites.html',
                  page_fn('Low Minimum Deposit Betting Sites SA 2026 - From R1', 'Find the best low minimum deposit betting sites in South Africa. Deposit as little as R1 at licensed SA bookmakers. Top picks for budget-friendly betting.', 'betting/low-minimum-deposit-betting-sites', body, depth=1, active_nav='betting'))
    sitemap_entries.append(('betting/low-minimum-deposit-betting-sites', '0.8'))

    # ====================================================================
    # 5. PAYMENT METHOD PAGES
    # ====================================================================
    print('  Building payment method pages...')
    for pm in PAYMENT_METHOD_PAGES_DATA:
        matching = sorted([b for b in DATA['brands'] if any(k in b.get('paymentMethodsList', []) for k in pm['filter_keys'])],
                          key=lambda b: b['overallRating'], reverse=True)[:10]
        cards = ''
        for i, b in enumerate(matching, 1):
            cards += brand_card_html(b, 1, rank=i)
        bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Betting Sites", "href": "betting-sites.html"}, {"label": f"{pm['method']} Sites"}]
        pm_hero = category_hero(f'{pm["title"]} 2026', f'We found {len(matching)} licensed SA betting sites that accept {pm["method"]}. Here are the top picks, ranked by our experts.', bc_items, 1, deco_icon='&#x1F4B3;')
        body = f'''
        {pm_hero}
        <div class="container" style="padding-top:32px;padding-bottom:80px;max-width:900px">
              {cards}
              <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:32px">
                <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Using {e(pm['method'])} at SA Betting Sites</h2>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Deposits via {e(pm['method'])} are typically instant and free at South African bookmakers. This is one of the most popular payment methods among SA punters because of its speed and convenience. You will not need to wait for bank processing times or deal with complicated verification steps just to fund your betting account.</p>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">When it comes to withdrawals, the picture is slightly different. Not every bookmaker that accepts {e(pm['method'])} deposits will also process withdrawals via the same method. In those cases, you will typically need to withdraw via bank EFT, which takes 24 to 48 hours at most SA betting sites. We note the withdrawal options in each of our <a href="../betting-sites.html" style="color:var(--accent);text-decoration:underline">individual site reviews</a>.</p>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Minimum deposit amounts vary between bookmakers. Some sites accept deposits as low as R1 via certain methods, while others set the floor at R10 or R50. If budget is a concern, check our <a href="low-minimum-deposit-betting-sites.html" style="color:var(--accent);text-decoration:underline">low minimum deposit page</a> for the most affordable options.</p>
              </div>
              <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:24px">
                <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">How to Deposit with {e(pm['method'])}</h2>
                <ol style="padding-left:20px;margin-bottom:16px">
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:6px 0"><strong>Sign up or log in</strong> to your chosen bookmaker. If you are new, grab a <a href="../promo-codes.html" style="color:var(--accent);text-decoration:underline">promo code</a> before registering to maximise your welcome bonus.</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:6px 0"><strong>Navigate to the deposit section</strong> - usually found under "My Account" or via a prominent "Deposit" button.</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:6px 0"><strong>Select {e(pm['method'])}</strong> from the available payment options.</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:6px 0"><strong>Enter your deposit amount</strong> and follow the on-screen instructions to complete the transaction.</li>
                  <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:6px 0"><strong>Funds should appear instantly</strong> in your betting account, ready to use.</li>
                </ol>
                <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:16px;background:var(--accent-light);border-radius:8px;border-left:3px solid var(--accent)">Pro tip: Always deposit from a method registered in your own name. SA bookmakers are required by law to verify your identity (FICA), and deposits from third-party accounts can trigger delays or even account suspension.</p>
              </div>
              <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:24px">
                <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Safety and Security</h2>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">All the bookmakers listed on MzansiWins are licensed by one or more of South Africa's provincial gambling boards. This means your deposits are processed through regulated, secure channels. We only recommend sites that use SSL encryption for all financial transactions.</p>
                <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">If you have any issues with a deposit or withdrawal at a licensed SA bookmaker, you can lodge a complaint with the relevant provincial gambling board. We cover the dispute resolution process in our <a href="../guides/" style="color:var(--accent);text-decoration:underline">betting guides</a> section.</p>
              </div>
              <div style="margin-top:16px"><a href="../payment-methods.html" class="btn-outline" style="font-size:14px;padding:10px 24px;border-radius:24px">All Payment Methods {ICON_CHEVRON_RIGHT}</a></div>
              {subcat_crosslinks(1, 'betting', pm['id'])}
        </div>'''
        write_file_fn(f'{OUT}/betting/{pm["id"]}.html',
                      page_fn(f'{pm["title"]} 2026 - Top {len(matching)} Sites', f'Best betting sites accepting {pm["method"]} in South Africa. {len(matching)} licensed bookmakers compared. Instant deposits, fast withdrawals.', f'betting/{pm["id"]}', body, depth=1, active_nav='betting'))
        sitemap_entries.append((f'betting/{pm["id"]}', '0.7'))

    # ====================================================================
    # 6. COMPARISON HUB + INDIVIDUAL COMPARISONS
    # ====================================================================
    print('  Building comparison pages...')
    # Comparison hub
    comp_links = ''
    for pair in COMPARISONS_BETTING:
        b1, b2 = brands_map.get(pair[0]), brands_map.get(pair[1])
        if not b1 or not b2: continue
        comp_links += f'''<a href="{pair[0]}-vs-{pair[1]}.html" class="card" style="padding:18px;display:flex;align-items:center;gap:16px">
          <div style="display:flex;align-items:center;gap:8px;flex:1;min-width:0">
            <span style="font-size:15px;font-weight:600">{e(b1['name'])}</span>
            <span style="font-size:13px;color:var(--text-muted);font-weight:700">vs</span>
            <span style="font-size:15px;font-weight:600">{e(b2['name'])}</span>
          </div>
          <span style="font-size:13px;color:var(--accent);font-weight:500">Compare {ICON_CHEVRON_RIGHT}</span>
        </a>'''
    for pair in COMPARISONS_CASINO:
        b1, b2 = brands_map.get(pair[0]), brands_map.get(pair[1])
        if not b1 or not b2: continue
        comp_links += f'''<a href="{pair[0]}-vs-{pair[1]}.html" class="card" style="padding:18px;display:flex;align-items:center;gap:16px">
          <div style="display:flex;align-items:center;gap:8px;flex:1;min-width:0">
            <span style="font-size:15px;font-weight:600">{e(b1['name'])}</span>
            <span style="font-size:13px;color:var(--text-muted);font-weight:700">vs</span>
            <span style="font-size:15px;font-weight:600">{e(b2['name'])}</span>
          </div>
          <span style="font-size:13px;color:var(--accent);font-weight:500">Compare {ICON_CHEVRON_RIGHT}</span>
        </a>'''
    bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Betting Sites", "href": "betting-sites.html"}, {"label": "Compare"}]
    body = f'''
    <div class="container" style="padding-top:40px;padding-bottom:80px">
      {bc(bc_items, 1)}
      <script type="application/ld+json">{bc_jsonld(bc_items)}</script>
      <h1 class="page-title">Compare SA Betting Sites Head-to-Head</h1>
      <p class="page-subtitle" style="margin-bottom:32px">Can not decide between two bookmakers? Our side-by-side comparisons break down the differences in odds, bonuses, payments, and features.</p>
      <div style="display:grid;gap:10px">{comp_links}</div>
      {internal_links_block(1, 'betting')}
    </div>'''
    write_file_fn(f'{OUT}/compare/index.html',
                  page_fn('Compare SA Betting Sites 2026 - Head-to-Head Reviews', 'Compare South African betting sites side by side. Head-to-head reviews of odds, bonuses, payments, and features for all top SA bookmakers.', 'compare', body, depth=1, active_nav='betting'))
    sitemap_entries.append(('compare', '0.7'))

    # Individual comparison pages
    all_comparisons = COMPARISONS_BETTING + COMPARISONS_CASINO
    for pair in all_comparisons:
        b1, b2 = brands_map.get(pair[0]), brands_map.get(pair[1])
        if not b1 or not b2: continue
        # Comparison table
        def comp_row(label, val1, val2):
            return f'<tr><td style="font-weight:600;font-size:14px;padding:12px 16px;width:30%">{label}</td><td style="font-size:14px;padding:12px 16px;text-align:center">{val1}</td><td style="font-size:14px;padding:12px 16px;text-align:center">{val2}</td></tr>'
        rows = ''
        rows += comp_row('Overall Rating', f'<strong>{b1["overallRating"]}/5.0</strong>', f'<strong>{b2["overallRating"]}/5.0</strong>')
        rows += comp_row('Welcome Bonus', f'<span style="color:var(--bonus);font-weight:600">{e(b1["welcomeBonusAmount"])}</span>', f'<span style="color:var(--bonus);font-weight:600">{e(b2["welcomeBonusAmount"])}</span>')
        rows += comp_row('Promo Code', e(b1['promoCode']), e(b2['promoCode']))
        rows += comp_row('Min Deposit', e(b1.get('minDeposit','N/A')), e(b2.get('minDeposit','N/A')))
        rows += comp_row('Sports', f'{len(b1.get("sportsCovered",[]))}', f'{len(b2.get("sportsCovered",[]))}')
        rows += comp_row('Live Betting', e(b1.get('liveBetting','N/A')), e(b2.get('liveBetting','N/A')))
        rows += comp_row('Live Streaming', e(b1.get('liveStreaming','N/A')), e(b2.get('liveStreaming','N/A')))
        rows += comp_row('Cash Out', e(b1.get('cashOut','N/A')), e(b2.get('cashOut','N/A')))
        rows += comp_row('Mobile App', e(b1.get('mobileApp','N/A')[:30]), e(b2.get('mobileApp','N/A')[:30]))
        rows += comp_row('Payments', f'{len(b1.get("paymentMethodsList",[]))} methods', f'{len(b2.get("paymentMethodsList",[]))} methods')
        rows += comp_row('License', e(b1.get('license','N/A')), e(b2.get('license','N/A')))

        # Determine winner
        if b1['overallRating'] > b2['overallRating']:
            verdict = f'{e(b1["name"])} edges ahead with a higher overall rating of {b1["overallRating"]}/5.0 compared to {b2["overallRating"]}/5.0. However, {e(b2["name"])} may still be the better choice depending on your priorities.'
        elif b2['overallRating'] > b1['overallRating']:
            verdict = f'{e(b2["name"])} has the edge with a {b2["overallRating"]}/5.0 rating vs {b1["overallRating"]}/5.0. That said, {e(b1["name"])} holds its own in specific areas and may suit your betting style better.'
        else:
            verdict = f'These two are neck and neck with identical {b1["overallRating"]}/5.0 ratings. Your choice comes down to which bonus, payment methods, and features matter most to you.'

        l1, l2 = logo(b1, 1), logo(b2, 1)
        logo1 = f'<img src="{l1}" alt="{e(b1["name"])}" style="width:48px;height:48px;object-fit:contain;border-radius:10px;background:{bg(b1)};padding:4px">' if l1 else ''
        logo2 = f'<img src="{l2}" alt="{e(b2["name"])}" style="width:48px;height:48px;object-fit:contain;border-radius:10px;background:{bg(b2)};padding:4px">' if l2 else ''

        bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Compare", "href": "compare/index.html"}, {"label": f"{b1['name']} vs {b2['name']}"}]
        body = f'''
        <div class="container" style="padding-top:40px;padding-bottom:80px">
          {bc(bc_items, 1)}
          <script type="application/ld+json">{bc_jsonld(bc_items)}</script>
          <h1 class="page-title">{e(b1['name'])} vs {e(b2['name'])} - Which is Better in 2026?</h1>
          <p class="page-subtitle" style="margin-bottom:32px">A detailed head-to-head comparison of two popular SA betting sites.</p>

          <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:16px;margin-bottom:32px;align-items:stretch">
            <div class="compare-brand-header" style="background:{bg(b1)};border-radius:12px;padding:24px;display:flex;flex-direction:column;align-items:center;justify-content:center">
              {logo1}
              <div class="brand-name" style="font-size:16px;font-weight:700;margin-top:8px;color:#fff">{e(b1['name'])}</div>
              <div class="brand-rating" style="font-size:14px;font-weight:600;color:rgba(255,255,255,0.9)">{b1['overallRating']}/5.0</div>
            </div>
            <div style="display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800;color:var(--text-muted)">VS</div>
            <div class="compare-brand-header" style="background:{bg(b2)};border-radius:12px;padding:24px;display:flex;flex-direction:column;align-items:center;justify-content:center">
              {logo2}
              <div class="brand-name" style="font-size:16px;font-weight:700;margin-top:8px;color:#fff">{e(b2['name'])}</div>
              <div class="brand-rating" style="font-size:14px;font-weight:600;color:rgba(255,255,255,0.9)">{b2['overallRating']}/5.0</div>
            </div>
          </div>

          <div style="overflow-x:auto;margin-bottom:32px">
            <table class="data-table compare-table" style="width:100%;table-layout:fixed">
              <thead><tr>
                <th style="text-align:left;padding:14px 16px;width:30%">Feature</th>
                <th style="text-align:center;padding:14px 16px;width:35%"><div style="display:flex;align-items:center;justify-content:center;gap:8px">{f'<img src="{l1}" alt="" style="width:24px;height:24px;object-fit:contain;border-radius:6px;background:{bg(b1)};padding:2px">' if l1 else ''}{e(b1['name'])}</div></th>
                <th style="text-align:center;padding:14px 16px;width:35%"><div style="display:flex;align-items:center;justify-content:center;gap:8px">{f'<img src="{l2}" alt="" style="width:24px;height:24px;object-fit:contain;border-radius:6px;background:{bg(b2)};padding:2px">' if l2 else ''}{e(b2['name'])}</div></th>
              </tr></thead>
              <tbody>{rows}</tbody>
            </table>
          </div>

          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-bottom:24px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Our Verdict</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">{verdict}</p>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px">
            <a href="../betting-site-review/{b1['id']}.html" class="btn-primary" style="text-align:center;border-radius:24px;padding:14px 20px;font-size:14px">Read {e(b1['name'])} Review</a>
            <a href="../betting-site-review/{b2['id']}.html" class="btn-outline" style="text-align:center;border-radius:24px;padding:14px 20px;font-size:14px">Read {e(b2['name'])} Review</a>
          </div>
          {internal_links_block(1, 'betting')}
        </div>'''
        slug = f'{pair[0]}-vs-{pair[1]}'
        write_file_fn(f'{OUT}/compare/{slug}.html',
                      page_fn(f'{b1["name"]} vs {b2["name"]} 2026 - Which SA Betting Site is Better?', f'Compare {b1["name"]} and {b2["name"]} side by side. Odds, bonuses, payments, features - find which SA betting site is better for you.', f'compare/{slug}', body, depth=1, active_nav='betting'))
        sitemap_entries.append((f'compare/{slug}', '0.6'))

    # ====================================================================
    # 7. BETTING GUIDES HUB + INDIVIDUAL GUIDES
    # ====================================================================
    print('  Building betting guides...')
    guide_icons = {
        'football': '\u26BD', 'rugby': '\U0001F3C9', 'acca': '\U0001F4CA',
        'money': '\U0001F4B0', 'live': '\u26A1', 'odds': '\U0001F4CA',
        'cashout': '\U0001F4B8', 'bonus': '\U0001F381', 'horse': '\U0001F3C7',
        'shield': '\U0001F6E1\uFE0F', 'slots': '\U0001F3B0', 'crash': '\U0001F680'
    }
    # Guides index
    guides_grid = ''
    for g in BETTING_GUIDES:
        icon = guide_icons.get(g.get('icon', ''), '\U0001F4D6')
        author = AUTHORS_MAP.get(g.get('author', ''), {})
        guides_grid += f'''<a href="{g['id']}.html" class="card" style="padding:20px;display:flex;align-items:flex-start;gap:16px;text-decoration:none;color:inherit">
          <span style="font-size:28px;flex-shrink:0">{icon}</span>
          <div>
            <h2 style="font-size:16px;font-weight:700;margin-bottom:4px">{e(g['title'])}</h2>
            <p style="font-size:13px;color:var(--text-secondary);line-height:1.5;margin-bottom:6px">{e(g['short'])}</p>
            <div style="display:flex;align-items:center;gap:6px">{author_img_tag(author.get('name',''), size=20, depth=1)} <span style="font-size:12px;color:var(--text-muted)">By {e(author.get('name','MzansiWins'))}</span></div>
          </div>
        </a>'''
    bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Betting Sites", "href": "betting-sites.html"}, {"label": "Betting Guides"}]
    guides_hub_hero = category_hero('Betting Guides for South African Punters', 'Whether you are a first-time punter or looking to sharpen your strategy, our guides cover everything from the basics to advanced betting techniques. Written by SA betting experts.', bc_items, 1, deco_icon='&#x1F4D6;')
    body = f'''
    {guides_hub_hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      <div style="display:grid;gap:12px">{guides_grid}</div>
      {internal_links_block(1, 'betting')}
    </div>'''
    write_file_fn(f'{OUT}/guides/index.html',
                  page_fn('Betting Guides South Africa 2026 - Learn to Bet Smarter', 'Free betting guides for South African punters. Football, rugby, accumulators, odds, bankroll management and more. Expert tips from the MzansiWins team.', 'guides', body, depth=1, active_nav='betting'))
    sitemap_entries.append(('guides', '0.7'))

    # Individual guide pages - full content
    guide_content = _generate_guide_content(BETTING_GUIDES, 'betting', DATA, BRANDS, brands_map)
    for g in BETTING_GUIDES:
        content = guide_content.get(g['id'], '')
        icon = guide_icons.get(g.get('icon', ''), '\U0001F4D6')
        author = AUTHORS_MAP.get(g.get('author', ''), {})
        author_badge = f'''<div style="display:flex;align-items:center;gap:10px;margin-bottom:24px">
          {author_img_tag(author.get('name',''), size=36, depth=1)}
          <div>
            <a href="../authors/{author.get('id','')}.html" style="font-size:14px;font-weight:600;color:var(--text-primary)">{e(author.get('name','MzansiWins'))}</a>
            <div style="font-size:12px;color:var(--text-muted)">{e(author.get('role',''))}</div>
          </div>
        </div>'''
        # Related guides
        other_guides = [og for og in BETTING_GUIDES if og['id'] != g['id']][:3]
        related = ''
        for og in other_guides:
            oicon = guide_icons.get(og.get('icon', ''), '\U0001F4D6')
            related += f'<a href="{og["id"]}.html" class="card" style="padding:14px;display:flex;align-items:center;gap:12px;text-decoration:none;color:inherit"><span style="font-size:20px">{oicon}</span><span style="font-size:14px;font-weight:600">{e(og["title"])}</span></a>'

        bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Betting Guides", "href": "guides/index.html"}, {"label": g['title']}]
        bc_jsonld_str = bc_jsonld([{"label":"Home","href":"index.html"},{"label":"Betting Guides","href":"guides/index.html"},{"label":g["title"],"href":f"guides/{g['id']}.html"}])
        guide_hero = category_hero(g['title'], g['short'], bc_items, 1, deco_icon=icon)
        body = f'''
        {guide_hero}
        <div class="container" style="padding-top:32px;padding-bottom:80px;max-width:900px">
              {author_badge}
              <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px">
                {content}
              </div>
              <div style="background:var(--accent-light);border-radius:12px;padding:24px;margin-top:24px">
                <h2 style="font-size:17px;font-weight:700;margin-bottom:8px">Ready to Start Betting?</h2>
                <p style="font-size:14px;color:var(--text-secondary);line-height:1.75;margin-bottom:14px">Put what you have learned into practice at a trusted SA bookmaker.</p>
                <div style="display:flex;gap:10px;flex-wrap:wrap">
                  <a href="../betting-sites.html" class="btn-primary" style="font-size:14px;padding:10px 22px;border-radius:24px">View Top Bookmakers</a>
                  <a href="../promo-codes.html" class="btn-outline" style="font-size:14px;padding:10px 22px;border-radius:24px">Get Promo Codes</a>
                </div>
              </div>
              <div style="margin-top:24px">
                <h2 style="font-size:17px;font-weight:700;margin-bottom:12px">More Guides</h2>
                <div style="display:grid;gap:8px">{related}</div>
              </div>
              {internal_links_block(1, 'betting')}
        </div>'''
        write_file_fn(f'{OUT}/guides/{g["id"]}.html',
                      page_fn(g['seo_title'], g['seo_desc'], f'guides/{g["id"]}', body, depth=1, active_nav='betting'))
        sitemap_entries.append((f'guides/{g["id"]}', '0.6'))

    # ====================================================================
    # 8. QUIZ PAGE - What Betting Site is Right for Me?
    # ====================================================================
    print('  Building betting quiz page...')
    bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Betting Sites", "href": "betting-sites.html"}, {"label": "Find Your Bookmaker"}]
    quiz_brands_json = json.dumps([{
        'id': b['id'], 'name': b['name'], 'rating': b['overallRating'],
        'bonus': b['welcomeBonusAmount'], 'code': b['promoCode'],
        'minDep': b.get('minDeposit','R50'), 'sports': b.get('sportsCovered',[]),
        'app': b.get('mobileApp','No'), 'live': b.get('liveBetting','No'),
        'streaming': b.get('liveStreaming','No'), 'cashOut': b.get('cashOut','No'),
        'payments': b.get('paymentMethodsList',[]),
        'casino': 'Casino' in b.get('otherProducts','') or b.get('type') in ('casino','both'),
        'tcs': b.get('tcs','18+ T&Cs apply.'),
        'logo': logo_path_fn(b, 1), 'bgColor': b.get('baseColour', '#1641B4')
    } for b in BRANDS[:20]])

    body = f'''
    <div class="container" style="padding-top:40px;padding-bottom:80px">
      {bc(bc_items, 1)}
      <script type="application/ld+json">{bc_jsonld(bc_items)}</script>
      <div style="max-width:680px;margin:0 auto">
        <h1 class="page-title" style="text-align:center">Which Betting Site is Right for You?</h1>
        <p class="page-subtitle" style="text-align:center;margin-bottom:32px">Answer 5 quick questions and we will match you with the best SA bookmaker for your style.</p>

        <div id="quiz-container">
          <div id="quiz-progress" style="display:flex;gap:6px;margin-bottom:24px"></div>
          <div id="quiz-question" style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:32px;min-height:300px"></div>
        </div>
        <div id="quiz-result" style="display:none"></div>
      </div>
      {internal_links_block(1, 'betting')}
    </div>
    <script>
    const QUIZ_BRANDS = {quiz_brands_json};
    const questions = [
      {{q: "What do you mainly want to bet on?", opts: [
        {{label: "Football (PSL, EPL, Champions League)", val: "football"}},
        {{label: "Rugby (Springboks, URC, Currie Cup)", val: "rugby"}},
        {{label: "Multiple sports - I like variety", val: "multi"}},
        {{label: "Casino games, slots, and Aviator", val: "casino"}}
      ]}},
      {{q: "What is your typical budget per month?", opts: [
        {{label: "Under R100 - I want to keep it light", val: "low"}},
        {{label: "R100 - R500 - Casual punter", val: "mid"}},
        {{label: "R500+ - I take it seriously", val: "high"}}
      ]}},
      {{q: "Which feature matters most to you?", opts: [
        {{label: "Big welcome bonus", val: "bonus"}},
        {{label: "Best odds and markets", val: "odds"}},
        {{label: "Live betting and streaming", val: "live"}},
        {{label: "Fast withdrawals", val: "payout"}}
      ]}},
      {{q: "Do you want a mobile app?", opts: [
        {{label: "Yes, I bet mostly on my phone", val: "app"}},
        {{label: "No, mobile site is fine", val: "noapp"}}
      ]}},
      {{q: "Which payment method do you prefer?", opts: [
        {{label: "Ozow / Instant EFT", val: "ozow"}},
        {{label: "Vouchers (1Voucher, OTT, Blu)", val: "voucher"}},
        {{label: "Card (Visa/Mastercard)", val: "card"}},
        {{label: "I do not mind", val: "any"}}
      ]}}
    ];
    let step = 0, answers = [];
    function renderQ() {{
      const pg = document.getElementById('quiz-progress');
      pg.innerHTML = questions.map((_,i) => '<div style="flex:1;height:4px;border-radius:2px;background:'+(i<=step?'var(--accent)':'var(--border)')+'"></div>').join('');
      const c = document.getElementById('quiz-question');
      const q = questions[step];
      c.innerHTML = '<h2 style="font-size:20px;font-weight:700;margin-bottom:20px">'+q.q+'</h2>' +
        q.opts.map(o => '<button onclick="answer(\\''+o.val+'\\')\" style="display:block;width:100%;text-align:left;padding:16px 20px;margin-bottom:10px;background:var(--bg);border:var(--card-border);border-radius:10px;cursor:pointer;font-size:15px;font-family:inherit;color:var(--text-primary);transition:all 150ms" onmouseover="this.style.borderColor=\\'var(--accent)\\'" onmouseout="this.style.borderColor=\\'\\'">'+o.label+'</button>').join('');
    }}
    function answer(val) {{
      answers.push(val);
      step++;
      if (step < questions.length) {{ renderQ(); return; }}
      showResult();
    }}
    function showResult() {{
      document.getElementById('quiz-container').style.display='none';
      let scored = QUIZ_BRANDS.map(b => {{
        let s = b.rating * 10;
        if (answers[0]==='football' && b.sports.includes('Football')) s += 10;
        if (answers[0]==='rugby' && b.sports.includes('Rugby')) s += 10;
        if (answers[0]==='multi' && b.sports.length > 20) s += 10;
        if (answers[0]==='casino' && b.casino) s += 15;
        if (answers[1]==='low') {{ let d=parseInt(b.minDep.replace(/[^0-9]/g,'')); if(d<=10) s+=10; }}
        if (answers[1]==='high') s += 5;
        if (answers[2]==='bonus') s += 5;
        if (answers[2]==='live' && b.live==='Yes') s += 10;
        if (answers[2]==='live' && b.streaming!=='No') s += 5;
        if (answers[3]==='app' && b.app.toLowerCase().startsWith('yes')) s += 10;
        if (answers[4]==='ozow' && b.payments.includes('Ozow')) s += 5;
        if (answers[4]==='voucher' && b.payments.some(p=>p.includes('oucher'))) s += 5;
        if (answers[4]==='card' && b.payments.includes('Visa')) s += 5;
        return {{...b, score: s}};
      }});
      scored.sort((a,b) => b.score - a.score);
      let top3 = scored.slice(0,3);
      let html = '<div style="text-align:center;margin-bottom:24px"><h2 style="font-size:24px;font-weight:800">Your Top Matches</h2><p style="color:var(--text-secondary)">Based on your answers, these bookmakers suit you best.</p></div>';
      top3.forEach((b,i) => {{
        var logoHtml = b.logo ? '<img src="'+b.logo+'" alt="'+b.name+'" style="width:48px;height:48px;border-radius:10px;object-fit:contain;border:1px solid var(--border);padding:4px;background:'+b.bgColor+';flex-shrink:0">' : '';
        html += '<div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:24px;margin-bottom:12px">' +
          '<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">' +
          '<div style="display:flex;align-items:center;gap:12px">' + logoHtml +
          '<div><div style="display:flex;align-items:center;gap:8px;margin-bottom:2px"><span style="display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;background:var(--accent);color:#fff;font-size:12px;font-weight:700">#'+(i+1)+'</span>' +
          '<span style="font-size:18px;font-weight:700">'+b.name+'</span></div>' +
          '<span style="font-size:14px;color:var(--accent);font-weight:600">'+b.rating+'/5.0</span></div></div>' +
          '<div style="text-align:right"><div style="font-size:15px;font-weight:700;color:var(--bonus);margin-bottom:4px">'+b.bonus+'</div>' +
          '<span style="font-family:monospace;font-size:12px;padding:3px 8px;background:#FFF8E7;border:1.5px dashed #d4a843;border-radius:4px">'+b.code+'</span></div></div>' +
          '<p style="font-size:12px;color:var(--text-muted);margin-top:10px">'+b.tcs+'</p>' +
          '<div style="display:flex;gap:10px;margin-top:12px">' +
          '<a href="../betting-site-review/'+b.id+'.html" class="btn-primary" style="font-size:13px;padding:10px 20px;border-radius:24px">Read Review</a>' +
          '<a href="../promo-code/'+b.id+'.html" class="btn-outline" style="font-size:13px;padding:10px 20px;border-radius:24px">Get Promo Code</a></div></div>';
      }});
      html += '<button onclick="restart()" style="display:block;margin:20px auto;padding:12px 28px;border-radius:24px;border:1px solid var(--border);background:var(--surface);cursor:pointer;font-size:14px;font-weight:600;font-family:inherit;color:var(--accent)">Retake Quiz</button>';
      document.getElementById('quiz-result').innerHTML = html;
      document.getElementById('quiz-result').style.display = 'block';
    }}
    function restart() {{
      step=0; answers=[];
      document.getElementById('quiz-container').style.display='block';
      document.getElementById('quiz-result').style.display='none';
      renderQ();
    }}
    renderQ();
    </script>'''
    write_file_fn(f'{OUT}/betting/find-your-bookmaker.html',
                  page_fn('Find Your Perfect Betting Site - SA Quiz 2026 | MzansiWins', 'Not sure which SA betting site to join? Take our 30-second quiz to find the best bookmaker for your betting style, budget, and preferences.', 'betting/find-your-bookmaker', body, depth=1, active_nav='betting'))
    sitemap_entries.append(('betting/find-your-bookmaker', '0.7'))

    # ====================================================================
    # 9. BONUS FINDER PAGE
    # ====================================================================
    print('  Building bonus finder page...')
    bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Betting Sites", "href": "betting-sites.html"}, {"label": "Bonus Finder"}]
    bonus_data_json = json.dumps([{
        'id': b['id'], 'name': b['name'], 'rating': b['overallRating'],
        'bonus': b['welcomeBonusAmount'], 'code': b['promoCode'],
        'tcs': b.get('tcs', '18+ T&Cs apply.'),
        'type': b.get('type', 'betting'),
        'casino': 'Casino' in b.get('otherProducts', '') or b.get('type') in ('casino', 'both'),
        'minDep': b.get('minDeposit', 'R50')
    } for b in BRANDS])

    body = f'''
    <div class="container" style="padding-top:40px;padding-bottom:80px">
      {bc(bc_items, 1)}
      <script type="application/ld+json">{bc_jsonld(bc_items)}</script>
      <h1 class="page-title">SA Betting Bonus Finder</h1>
      <p class="page-subtitle" style="margin-bottom:24px">Filter and compare welcome bonuses from all {len(BRANDS)} licensed South African bookmakers. Find the perfect bonus for you.</p>

      <div style="display:flex;gap:12px;margin-bottom:24px;flex-wrap:wrap">
        <select id="bf-type" onchange="filterBonuses()" style="padding:10px 16px;border:1px solid var(--border);border-radius:8px;background:var(--bg);font-size:14px;font-family:inherit;color:var(--text-primary)">
          <option value="all">All Types</option>
          <option value="betting">Sports Betting</option>
          <option value="casino">Casino</option>
        </select>
        <select id="bf-sort" onchange="filterBonuses()" style="padding:10px 16px;border:1px solid var(--border);border-radius:8px;background:var(--bg);font-size:14px;font-family:inherit;color:var(--text-primary)">
          <option value="rating">Sort: Top Rated</option>
          <option value="name">Sort: A-Z</option>
        </select>
        <input type="text" id="bf-search" onkeyup="filterBonuses()" placeholder="Search bookmaker..." style="padding:10px 16px;border:1px solid var(--border);border-radius:8px;background:var(--bg);font-size:14px;font-family:inherit;color:var(--text-primary);flex:1;min-width:180px">
      </div>
      <div id="bf-results"></div>
      <p id="bf-count" style="font-size:13px;color:var(--text-muted);margin-top:12px"></p>
      {internal_links_block(1, 'betting')}
    </div>
    <script>
    const BF_BRANDS = {bonus_data_json};
    function filterBonuses() {{
      const type = document.getElementById('bf-type').value;
      const sort = document.getElementById('bf-sort').value;
      const search = document.getElementById('bf-search').value.toLowerCase();
      let filtered = BF_BRANDS.filter(b => {{
        if (type==='casino' && !b.casino) return false;
        if (type==='betting' && b.type==='casino') return false;
        if (search && !b.name.toLowerCase().includes(search)) return false;
        return true;
      }});
      if (sort==='name') filtered.sort((a,b) => a.name.localeCompare(b.name));
      else filtered.sort((a,b) => b.rating - a.rating);

      let html = '';
      filtered.forEach((b,i) => {{
        html += '<div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:20px;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">' +
          '<div style="flex:1;min-width:200px"><div style="display:flex;align-items:center;gap:8px"><span style="font-size:16px;font-weight:700">'+b.name+'</span><span style="font-size:13px;color:var(--accent);font-weight:600">'+b.rating+'/5.0</span></div>' +
          '<div style="font-size:15px;font-weight:700;color:var(--bonus);margin-top:4px">'+b.bonus+'</div>' +
          '<p style="font-size:12px;color:var(--text-muted);margin-top:4px">'+b.tcs+'</p></div>' +
          '<div style="display:flex;align-items:center;gap:8px;flex-shrink:0">' +
          '<span style="font-family:monospace;font-size:12px;font-weight:700;padding:5px 12px;background:#FFF8E7;border:1.5px dashed #d4a843;border-radius:6px">'+b.code+'</span>' +
          '<a href="../promo-code/'+b.id+'.html" class="btn-primary" style="font-size:13px;padding:10px 20px;border-radius:24px;white-space:nowrap">Get Bonus</a></div></div>';
      }});
      document.getElementById('bf-results').innerHTML = html;
      document.getElementById('bf-count').textContent = 'Showing ' + filtered.length + ' of ' + BF_BRANDS.length + ' bookmakers';
    }}
    filterBonuses();
    </script>'''
    write_file_fn(f'{OUT}/betting/bonus-finder.html',
                  page_fn('SA Betting Bonus Finder 2026 - Compare All Welcome Bonuses', f'Compare welcome bonuses from all {len(BRANDS)} licensed SA betting sites. Filter by type, search by name, and find the best sign-up offer for you.', 'betting/bonus-finder', body, depth=1, active_nav='betting'))
    sitemap_entries.append(('betting/bonus-finder', '0.8'))

    # ====================================================================
    # 10. CASINO EQUIVALENTS
    # ====================================================================
    print('  Building casino category pages...')
    casino_brands = sorted([b for b in DATA['brands'] if 'Casino' in b.get('otherProducts', '') or b.get('type') in ('casino', 'both')],
                           key=lambda b: b['overallRating'], reverse=True)

    # Best Casino Apps
    casino_app_brands = [b for b in casino_brands if b.get('mobileApp','').lower().startswith('yes')][:8]
    cards = ''
    for i, b in enumerate(casino_app_brands, 1):
        cards += brand_card_html(b, 1, rank=i)
    bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Casino Sites", "href": "casino-sites.html"}, {"label": "Best Casino Apps"}]
    casino_apps_hero = category_hero('Best Casino Apps in South Africa 2026', 'Play slots, live casino, and table games on the go. We have tested the top SA casino apps for iOS and Android.', bc_items, 1, deco_icon='&#x1F3B0;')
    body = f'''
    {casino_apps_hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px;max-width:900px">
          {cards}
          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:32px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">What Makes a Good Casino App?</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">The best casino apps load games quickly, support touch-optimised controls for slots and table games, and offer the same promotions as the desktop site. Look for apps that support live dealer games on mobile - not all do. A smooth, lag-free experience is non-negotiable when real money is on the line.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Game selection on mobile is the first thing we check. Some casino apps only carry a fraction of their desktop game library. The best ones, like PlayTsogo and SaffaLuck, bring 90% or more of their full catalogue to mobile. This includes popular slot providers like Pragmatic Play, NetEnt, and Microgaming, plus live dealer tables from Evolution Gaming.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Touch controls matter more than you think for table games. Placing chips on a roulette layout or managing your blackjack hand on a small screen needs to feel natural. The top-rated apps in our list have invested in mobile-specific UI that makes gameplay intuitive rather than frustrating.</p>
          </div>
          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:24px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Casino App Features We Test</h2>
            <ul style="padding-left:20px;margin-bottom:16px">
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Game Loading Speed</strong> - Slots and table games should load in under five seconds on LTE. We test on mid-range Android devices, not just flagships.</li>
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Live Dealer Quality</strong> - HD streaming of live casino tables without buffering. The best apps offer portrait mode for live dealers, which is perfect for one-handed play.</li>
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Game Library Size</strong> - How many of the desktop games are available on mobile? We count and compare.</li>
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Bonuses on Mobile</strong> - Can you claim and use bonuses from the app? Some sites restrict certain promotions to desktop only.</li>
              <li style="font-size:14px;line-height:1.75;color:var(--text-secondary);padding:4px 0"><strong>Banking</strong> - Deposits and withdrawals from within the app. Support for Ozow, EFT, and other SA payment methods.</li>
            </ul>
          </div>
          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:24px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">How to Download Casino Apps in South Africa</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px"><strong>iOS:</strong> Most SA casino apps are available on the App Store. Search for the brand name and look for the official app from the verified publisher. Apple is strict about gambling apps, so any app you find in the store is legitimate.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px"><strong>Android:</strong> Google Play has loosened its policy on gambling apps in South Africa, but not all casino apps are listed. If you cannot find it on Play Store, visit the casino website directly and download the APK. Enable "Install from unknown sources" in your settings first.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px"><strong>Mobile Browser:</strong> If you prefer not to install anything, most SA online casinos work perfectly in your mobile browser. Chrome, Safari, and Samsung Internet all support HTML5 casino games without any plugins.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">Looking for casino bonuses to use on your mobile? Check our <a href="../promo-codes.html" style="color:var(--accent);text-decoration:underline">promo codes page</a> for the latest welcome offers. If you also enjoy sports betting, take a look at our <a href="best-betting-apps-south-africa.html" style="color:var(--accent);text-decoration:underline">best betting apps</a> guide for the sports side of things.</p>
          </div>
          <div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:8px">
            <a href="../casino-sites.html" class="btn-outline" style="font-size:14px;padding:10px 24px;border-radius:24px">All Casino Sites</a>
            <a href="../casino-guides/" class="btn-outline" style="font-size:14px;padding:10px 24px;border-radius:24px">Casino Guides</a>
          </div>
          {subcat_crosslinks(1, 'casino', 'casino-apps')}
    </div>'''
    write_file_fn(f'{OUT}/casino/best-casino-apps-south-africa.html',
                  page_fn('Best Casino Apps South Africa 2026 - Top Mobile Casino Apps', 'The best casino apps in South Africa for 2026. Play slots, live casino, and table games on iOS and Android. Expert-tested SA casino apps.', 'casino/best-casino-apps-south-africa', body, depth=1, active_nav='casino'))
    sitemap_entries.append(('casino/best-casino-apps-south-africa', '0.8'))

    # Casino Guides Hub
    cguide_grid = ''
    for g in CASINO_GUIDES:
        icon = guide_icons.get(g.get('icon', ''), '\U0001F4D6')
        author = AUTHORS_MAP.get(g.get('author', ''), {})
        cguide_grid += f'''<a href="{g['id']}.html" class="card" style="padding:20px;display:flex;align-items:flex-start;gap:16px;text-decoration:none;color:inherit">
          <span style="font-size:28px;flex-shrink:0">{icon}</span>
          <div>
            <h2 style="font-size:16px;font-weight:700;margin-bottom:4px">{e(g['title'])}</h2>
            <p style="font-size:13px;color:var(--text-secondary);line-height:1.5;margin-bottom:6px">{e(g['short'])}</p>
            <div style="display:flex;align-items:center;gap:6px">{author_img_tag(author.get('name',''), size=20, depth=1)} <span style="font-size:12px;color:var(--text-muted)">By {e(author.get('name','MzansiWins'))}</span></div>
          </div>
        </a>'''
    bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Casino Sites", "href": "casino-sites.html"}, {"label": "Casino Guides"}]
    cguides_hub_hero = category_hero('Casino Guides for South African Players', 'From online slots to live dealer games, our guides help you play smarter at licensed SA casinos.', bc_items, 1, deco_icon='&#x1F3B0;')
    body = f'''
    {cguides_hub_hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      <div style="display:grid;gap:12px">{cguide_grid}</div>
      {internal_links_block(1, 'casino')}
    </div>'''
    write_file_fn(f'{OUT}/casino-guides/index.html',
                  page_fn('Casino Guides South Africa 2026 - Slots, Live Casino & More', 'Free casino guides for South African players. Slots, live casino, bonuses, RTP explained. Expert tips from the MzansiWins team.', 'casino-guides', body, depth=1, active_nav='casino'))
    sitemap_entries.append(('casino-guides', '0.7'))

    # Individual casino guide pages
    cguide_content = _generate_guide_content(CASINO_GUIDES, 'casino', DATA, BRANDS, brands_map)
    for g in CASINO_GUIDES:
        content = cguide_content.get(g['id'], '')
        icon = guide_icons.get(g.get('icon', ''), '\U0001F4D6')
        author = AUTHORS_MAP.get(g.get('author', ''), {})
        author_badge = f'''<div style="display:flex;align-items:center;gap:10px;margin-bottom:24px">
          {author_img_tag(author.get('name',''), size=36, depth=1)}
          <div>
            <a href="../authors/{author.get('id','')}.html" style="font-size:14px;font-weight:600;color:var(--text-primary)">{e(author.get('name','MzansiWins'))}</a>
            <div style="font-size:12px;color:var(--text-muted)">{e(author.get('role',''))}</div>
          </div>
        </div>'''
        other = [og for og in CASINO_GUIDES if og['id'] != g['id']][:3]
        related = ''
        for og in other:
            oicon = guide_icons.get(og.get('icon', ''), '\U0001F4D6')
            related += f'<a href="{og["id"]}.html" class="card" style="padding:14px;display:flex;align-items:center;gap:12px;text-decoration:none;color:inherit"><span style="font-size:20px">{oicon}</span><span style="font-size:14px;font-weight:600">{e(og["title"])}</span></a>'
        bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Casino Guides", "href": "casino-guides/index.html"}, {"label": g['title']}]
        bc_jsonld_str = bc_jsonld([{"label":"Home","href":"index.html"},{"label":"Casino Guides","href":"casino-guides/index.html"},{"label":g["title"],"href":f"casino-guides/{g['id']}.html"}])
        cguide_hero = category_hero(g['title'], g['short'], bc_items, 1, deco_icon=icon)
        body = f'''
        {cguide_hero}
        <div class="container" style="padding-top:32px;padding-bottom:80px;max-width:900px">
              {author_badge}
              <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px">
                {content}
              </div>
              <div style="background:var(--accent-light);border-radius:12px;padding:24px;margin-top:24px">
                <h2 style="font-size:17px;font-weight:700;margin-bottom:8px">Ready to Play?</h2>
                <p style="font-size:14px;color:var(--text-secondary);line-height:1.75;margin-bottom:14px">Find the best SA casino for your game.</p>
                <div style="display:flex;gap:10px;flex-wrap:wrap">
                  <a href="../casino-sites.html" class="btn-primary" style="font-size:14px;padding:10px 22px;border-radius:24px">View Top Casinos</a>
                  <a href="../promo-codes.html" class="btn-outline" style="font-size:14px;padding:10px 22px;border-radius:24px">Get Promo Codes</a>
                </div>
              </div>
              <div style="margin-top:24px">
                <h2 style="font-size:17px;font-weight:700;margin-bottom:12px">More Casino Guides</h2>
                <div style="display:grid;gap:8px">{related}</div>
              </div>
              {internal_links_block(1, 'casino')}
        </div>'''
        write_file_fn(f'{OUT}/casino-guides/{g["id"]}.html',
                      page_fn(g['seo_title'], g['seo_desc'], f'casino-guides/{g["id"]}', body, depth=1, active_nav='casino'))
        sitemap_entries.append((f'casino-guides/{g["id"]}', '0.6'))

    print(f'  Expansion complete: {len(sitemap_entries)} new pages')
    return sitemap_entries


# ---------------------------------------------------------------------------
# Guide content generator
# ---------------------------------------------------------------------------
def _generate_guide_content(guides, category, DATA, BRANDS, brands_map):
    """Generate article HTML content for each guide."""
    content = {}
    top3 = [b['name'] for b in BRANDS[:3]]

    for g in guides:
        gid = g['id']
        # Build content based on guide ID
        if gid == 'how-to-bet-on-football-south-africa':
            content[gid] = f'''
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Getting Started with Football Betting</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Football is the most popular sport to bet on in South Africa, and for good reason. Between the PSL, English Premier League, Champions League, and international tournaments, there is always a match to bet on. Here is everything you need to know to start betting on football at SA bookmakers.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Choosing the Right Bookmaker</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Not all SA bookmakers are equal when it comes to football. Look for sites that offer competitive odds on PSL matches, a wide range of markets (especially for big European leagues), and live in-play betting. {top3[0]}, {top3[1]}, and {top3[2]} consistently rank highest for football coverage.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Popular Football Betting Markets</h3>
            <ul style="padding-left:0;list-style:none;margin-bottom:16px">
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Match Result (1X2)</strong> - Back the home team, away team, or draw</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Both Teams to Score (BTTS)</strong> - Will both sides find the net?</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Over/Under Goals</strong> - Bet on total goals in the match (2.5 is most common)</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>First Goalscorer</strong> - Pick who scores first at bigger odds</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Handicap Betting</strong> - Level the playing field with virtual goal advantages</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Correct Score</strong> - High risk, high reward. Predict the exact final score</li>
            </ul>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">PSL Betting Tips</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">The Premier Soccer League is unpredictable, which is part of what makes it exciting. Home advantage is significant in the PSL - teams like Kaizer Chiefs and Orlando Pirates rarely lose at home. Watch out for derby matches where form goes out the window, and consider the draw market which hits more often than you might expect.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Live Football Betting</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">In-play betting lets you react to what is happening on the pitch. If a strong team goes 1-0 down early, you can often get inflated odds on them to come back. Most SA bookmakers offer live betting for major football leagues, with odds updating in real time.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Football Betting Mistakes to Avoid</h3>
            <ul style="padding-left:0;list-style:none;margin-bottom:16px">
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:#dc2626">&#10007;</span>Betting on your favourite team every week (bias clouds judgement)</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:#dc2626">&#10007;</span>Chasing losses with bigger bets after a bad weekend</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:#dc2626">&#10007;</span>Ignoring team news - injuries and suspensions matter</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:#dc2626">&#10007;</span>Loading 10+ legs into accumulators (the maths is not on your side)</li>
            </ul>'''
        elif gid == 'how-to-bet-on-rugby-south-africa':
            content[gid] = f'''
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Rugby Betting in South Africa</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">South Africa is a rugby nation through and through. From the Springboks' World Cup campaigns to the United Rugby Championship and Currie Cup, there is always an opportunity to back the green and gold - or find value elsewhere.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Key Rugby Betting Markets</h3>
            <ul style="padding-left:0;list-style:none;margin-bottom:16px">
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Match Winner</strong> - Back the team to win outright</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Handicap</strong> - The bookmaker gives one team a points head start</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Total Points Over/Under</strong> - Bet on whether the combined score goes over or under a set number</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>First Try Scorer</strong> - Popular in Test matches at juicy odds</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Winning Margin</strong> - Predict the margin of victory within a range</li>
            </ul>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Springbok Test Match Betting</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">The Springboks draw massive betting volumes. Home advantage at Loftus or Ellis Park is significant - the Boks rarely lose at home. For the Rugby Championship and touring series, look at handicap markets where the bookmaker sets a points spread. The Boks often cover big handicaps against tier-two nations.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">URC and Currie Cup Tips</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">The United Rugby Championship features SA franchises against Irish, Welsh, Scottish, and Italian teams. SA teams have home advantage at altitude which significantly affects kicking accuracy. The Currie Cup is more unpredictable - development players and rotation make it harder to call. Stick to the bigger fixtures and avoid heavy accas in domestic rugby.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Best Bookmakers for Rugby</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">{top3[0]}, {top3[1]}, and {top3[2]} offer the deepest rugby markets among SA bookmakers. Look for sites that provide player prop bets for Test matches - these offer some of the best value if you know the game well.</p>'''
        else:
            # Generic guide content template
            title = g['title']
            short = g['short']
            content[gid] = f'''
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">{e(title)}</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">{e(short)} This guide breaks down everything South African punters need to know, from the basics to more advanced strategies. Whether you are completely new to betting or looking to level up your game, we have got you covered.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Why This Matters for SA Punters</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">South Africa's betting market has grown massively in recent years, with over 36 licensed operators competing for your business. Understanding the fundamentals gives you an edge - not just over the bookmakers, but over other punters who bet on gut feeling alone. Knowledge is your best tool.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Getting Started</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">First, make sure you are signed up with a licensed South African bookmaker. We recommend starting with {top3[0]} or {top3[1]} for the best combination of odds, bonuses, and user experience. Once you have an account, take time to explore the platform before placing your first bet.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Key Tips</h3>
            <ul style="padding-left:0;list-style:none;margin-bottom:16px">
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Start small and learn the ropes before increasing your stakes</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Compare odds across multiple SA bookmakers before placing a bet</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Set a monthly budget and never bet more than you can afford to lose</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Use the welcome bonus to your advantage, but always read the T&Cs</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Keep records of your bets to track what works and what does not</li>
            </ul>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Common Mistakes to Avoid</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">The biggest mistake new punters make is chasing losses. If you have had a bad run, take a break. The bookmakers will still be there tomorrow. Also avoid putting too many legs in your accumulators - the maths works against you exponentially with each additional selection.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Recommended Bookmakers</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">For the best experience, we recommend {top3[0]}, {top3[1]}, and {top3[2]}. All three are licensed, well-established, and offer competitive odds across a wide range of markets. Check our individual reviews for detailed breakdowns.</p>'''

    return content
