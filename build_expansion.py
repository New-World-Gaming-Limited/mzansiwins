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
        # Pros & Cons (first 2 each)
        pros = brand.get('pros', [])[:2]
        cons = brand.get('cons', [])[:2]
        pros_html = ''.join(f'<li style="font-size:13px;line-height:1.6;color:var(--text-secondary);margin-bottom:4px;padding-left:18px;position:relative"><span style="position:absolute;left:0;color:#16a34a">&#10003;</span>{e(p)}</li>' for p in pros)
        cons_html = ''.join(f'<li style="font-size:13px;line-height:1.6;color:var(--text-secondary);margin-bottom:4px;padding-left:18px;position:relative"><span style="position:absolute;left:0;color:#ef4444">&#10007;</span>{e(c)}</li>' for c in cons)
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
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px">
            <ul style="padding:0;list-style:none;margin:0">{pros_html}</ul>
            <ul style="padding:0;list-style:none;margin:0">{cons_html}</ul>
          </div>
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
      <p class="page-subtitle" style="margin-bottom:32px">The editorial team behind MzansiWins operator reviews and guides.</p>
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
                      page_fn(f'{author["name"]} - {author["role"]} | MzansiWins', (lambda d: d[:157]+'...' if len(d)>160 else d)(f'{author["name"]} is {author["role"]} at MzansiWins. {author["bio"][:110]}'), f'authors/{author["id"]}', body, depth=1, active_nav=''))
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
            "intro": "Backing the Springboks in a Test series or placing a punt on the URC? You need a bookmaker that takes rugby seriously. We have tested all licensed SA betting sites and ranked the top 5 for rugby betting based on odds quality, live betting coverage, market depth, and bonuses.",
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
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px"><strong>Android:</strong> Google Play does not always list gambling apps for South Africa. Most bookmakers offer an APK download from their website instead. If the app is not on Play Store, download the APK directly from the bookmaker's official website. Android will prompt you to allow installation from that source.</p>
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
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Starting with a small deposit doesn't mean you can't win. A few tips for stretching your rands further:</p>
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
        pm_hero = category_hero(f'{pm["title"]} 2026', f'We found {len(matching)} licensed SA betting sites that accept {pm["method"]}. These are the top picks, ranked by our experts.', bc_items, 1, deco_icon='&#x1F4B3;')
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
    def _comp_card(pair):
        b1, b2 = brands_map.get(pair[0]), brands_map.get(pair[1])
        if not b1 or not b2: return ''
        l1 = logo_path_fn(b1, 1) if logo_path_fn else ''
        l2 = logo_path_fn(b2, 1) if logo_path_fn else ''
        bg1, bg2 = brand_bg_fn(b1), brand_bg_fn(b2)
        img1 = f'<img src="{l1}" alt="{e(b1["name"])}" style="width:32px;height:32px;object-fit:contain;border-radius:6px;background:{bg1};padding:3px">' if l1 else ''
        img2 = f'<img src="{l2}" alt="{e(b2["name"])}" style="width:32px;height:32px;object-fit:contain;border-radius:6px;background:{bg2};padding:3px">' if l2 else ''
        r1 = f'{b1["overallRating"]:.1f}'
        r2 = f'{b2["overallRating"]:.1f}'
        return f'''<a href="{pair[0]}-vs-{pair[1]}.html" class="card" style="padding:16px;display:flex;align-items:center;gap:12px;text-decoration:none">
          <div style="display:flex;align-items:center;gap:8px;flex:1;min-width:0">
            {img1}<div><span style="font-size:14px;font-weight:600;display:block">{e(b1['name'])}</span><span style="font-size:12px;color:var(--accent)">{r1}/5.0</span></div>
          </div>
          <span style="font-size:12px;color:var(--text-muted);font-weight:700;flex-shrink:0">vs</span>
          <div style="display:flex;align-items:center;gap:8px;flex:1;min-width:0">
            {img2}<div><span style="font-size:14px;font-weight:600;display:block">{e(b2['name'])}</span><span style="font-size:12px;color:var(--accent)">{r2}/5.0</span></div>
          </div>
          <span style="font-size:13px;color:var(--accent);font-weight:500;flex-shrink:0">Compare {ICON_CHEVRON_RIGHT}</span>
        </a>'''
    for pair in COMPARISONS_BETTING:
        comp_links += _comp_card(pair)
    for pair in COMPARISONS_CASINO:
        comp_links += _comp_card(pair)
    bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Betting Sites", "href": "betting-sites.html"}, {"label": "Compare"}]
    body = f'''
    <div class="container" style="padding-top:40px;padding-bottom:80px">
      {bc(bc_items, 1)}
      <script type="application/ld+json">{bc_jsonld(bc_items)}</script>
      <h1 class="page-title">Compare SA Betting Sites Head-to-Head</h1>
      <p class="page-subtitle" style="margin-bottom:32px">Can't decide between two bookmakers? Our side-by-side comparisons break down the differences in odds, bonuses, payments, and features.</p>
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
        rows += comp_row('Mobile App', e(b1.get('mobileApp','N/A')), e(b2.get('mobileApp','N/A')))
        rows += comp_row('Payments', f'{len(b1.get("paymentMethodsList",[]))} methods', f'{len(b2.get("paymentMethodsList",[]))} methods')
        rows += comp_row('License', e(b1.get('license','N/A')), e(b2.get('license','N/A')))

        # Determine winner
        if b1['overallRating'] > b2['overallRating']:
            verdict = f'{e(b1["name"])} edges ahead with a higher overall rating of {b1["overallRating"]}/5.0 compared to {b2["overallRating"]}/5.0. However, {e(b2["name"])} may still be the better choice depending on your priorities.'
        elif b2['overallRating'] > b1['overallRating']:
            verdict = f'{e(b2["name"])} has the edge with a {b2["overallRating"]}/5.0 rating vs {b1["overallRating"]}/5.0. That said, {e(b1["name"])} holds its own in specific areas and may suit your betting style better.'
        else:
            verdict = f'These two are neck and neck with identical {b1["overallRating"]}/5.0 ratings. Your choice comes down to which bonus, payment methods, and features matter most to you.'

        # Best for / watch out for summaries
        def _first_pro(b):
            p = b.get('pros', [])
            if isinstance(p, list) and p:
                return str(p[0])[:120]
            if isinstance(p, str) and p.strip():
                return p.strip()[:120]
            return f'Overall rating {b["overallRating"]}/5.0'
        def _first_con(b):
            c = b.get('cons', [])
            if isinstance(c, list) and c:
                return str(c[0])[:120]
            if isinstance(c, str) and c.strip():
                return c.strip()[:120]
            return 'Check terms and conditions before depositing'
        best_for_1 = _first_pro(b1)
        best_for_2 = _first_pro(b2)
        watch_out_1 = _first_con(b1)
        watch_out_2 = _first_con(b2)
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
            <a href="../go/{b1['id']}/" target="_blank" rel="noopener noreferrer nofollow" class="compare-brand-header exit-link" style="background:{bg(b1)};border-radius:12px;padding:24px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none;transition:transform 0.15s ease,box-shadow 0.15s ease" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 20px rgba(0,0,0,0.25)'" onmouseout="this.style.transform='';this.style.boxShadow=''">
              {logo1}
              <div class="brand-name" style="font-size:16px;font-weight:700;margin-top:8px;color:#fff">{e(b1['name'])}</div>
              <div class="brand-rating" style="font-size:14px;font-weight:600;color:rgba(255,255,255,0.9)">{b1['overallRating']}/5.0</div>
              <span style="margin-top:10px;font-size:12px;font-weight:600;color:rgba(255,255,255,0.85);background:rgba(255,255,255,0.15);padding:4px 14px;border-radius:20px">Visit Site &#8594;</span>
            </a>
            <div style="display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800;color:var(--text-muted)">VS</div>
            <a href="../go/{b2['id']}/" target="_blank" rel="noopener noreferrer nofollow" class="compare-brand-header exit-link" style="background:{bg(b2)};border-radius:12px;padding:24px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-decoration:none;transition:transform 0.15s ease,box-shadow 0.15s ease" onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 20px rgba(0,0,0,0.25)'" onmouseout="this.style.transform='';this.style.boxShadow=''">
              {logo2}
              <div class="brand-name" style="font-size:16px;font-weight:700;margin-top:8px;color:#fff">{e(b2['name'])}</div>
              <div class="brand-rating" style="font-size:14px;font-weight:600;color:rgba(255,255,255,0.9)">{b2['overallRating']}/5.0</div>
              <span style="margin-top:10px;font-size:12px;font-weight:600;color:rgba(255,255,255,0.85);background:rgba(255,255,255,0.15);padding:4px 14px;border-radius:20px">Visit Site &#8594;</span>
            </a>
          </div>

          <div style="overflow-x:auto;margin-bottom:32px">
            <table class="data-table compare-table" style="width:100%;table-layout:fixed;border-collapse:separate;border-spacing:0">
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
            <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:20px">
              <h3 style="font-size:15px;font-weight:700;margin-bottom:8px">Best for: {e(b1['name'])}</h3>
              <p style="font-size:14px;line-height:1.6;color:var(--text-secondary)">{e(best_for_1)}</p>
              <h3 style="font-size:15px;font-weight:700;margin-top:14px;margin-bottom:8px">Watch out for</h3>
              <p style="font-size:14px;line-height:1.6;color:var(--text-secondary)">{e(watch_out_1)}</p>
            </div>
            <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:20px">
              <h3 style="font-size:15px;font-weight:700;margin-bottom:8px">Best for: {e(b2['name'])}</h3>
              <p style="font-size:14px;line-height:1.6;color:var(--text-secondary)">{e(best_for_2)}</p>
              <h3 style="font-size:15px;font-weight:700;margin-top:14px;margin-bottom:8px">Watch out for</h3>
              <p style="font-size:14px;line-height:1.6;color:var(--text-secondary)">{e(watch_out_2)}</p>
            </div>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
            <a href="../betting-site-review/{b1['id']}.html" class="btn-primary" style="text-align:center;border-radius:24px;padding:14px 20px;font-size:14px">Read {e(b1['name'])} Review</a>
            <a href="../betting-site-review/{b2['id']}.html" class="btn-primary" style="text-align:center;border-radius:24px;padding:14px 20px;font-size:14px">Read {e(b2['name'])} Review</a>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px">
            <a href="../promo-code/{b1['id']}.html" class="btn-outline" style="text-align:center;border-radius:24px;padding:14px 20px;font-size:14px">{e(b1['name'])} Promo Code</a>
            <a href="../promo-code/{b2['id']}.html" class="btn-outline" style="text-align:center;border-radius:24px;padding:14px 20px;font-size:14px">{e(b2['name'])} Promo Code</a>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px">
            <a href="../go/{b1['id']}/" target="_blank" rel="noopener noreferrer nofollow" class="exit-link" style="text-align:center;border-radius:24px;padding:14px 20px;font-size:14px;font-weight:700;background:var(--bonus);color:#fff;display:block">Visit {e(b1['name'])} &#8594;</a>
            <a href="../go/{b2['id']}/" target="_blank" rel="noopener noreferrer nofollow" class="exit-link" style="text-align:center;border-radius:24px;padding:14px 20px;font-size:14px;font-weight:700;background:var(--bonus);color:#fff;display:block">Visit {e(b2['name'])} &#8594;</a>
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
    guides_hub_hero = category_hero('Betting Guides for South African Punters', 'Guides covering payment methods, operator selection, regulatory requirements, and betting markets for South African players.', bc_items, 1, deco_icon='&#x1F4D6;')
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
    # Prioritise genuine casino brands (type=casino), then type=both, then sportsbooks with casino
    _casino_first = [b for b in casino_brands if b.get('type') == 'casino' and b.get('mobileApp','').lower().startswith('yes')]
    _both_brands = [b for b in casino_brands if b.get('type') == 'both' and b.get('mobileApp','').lower().startswith('yes')]
    _sports_with_casino = [b for b in casino_brands if b.get('type') not in ('casino','both') and b.get('mobileApp','').lower().startswith('yes')]
    casino_app_brands = (_casino_first + _both_brands + _sports_with_casino)[:8]
    cards = ''
    for i, b in enumerate(casino_app_brands, 1):
        cards += brand_card_html(b, 1, rank=i)
    bc_items = [{"label": "Home", "href": "index.html"}, {"label": "Casino Sites", "href": "casino-sites.html"}, {"label": "Best Casino Apps"}]
    casino_apps_hero = category_hero('Best Casino Apps in South Africa 2026', 'Mobile apps for slots, live casino, and table games. This list includes dedicated casino apps and sportsbook apps that carry substantial casino sections.', bc_items, 1, deco_icon='&#x1F3B0;')
    body = f'''
    {casino_apps_hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px;max-width:900px">
          {cards}
          <div style="background:var(--surface);border:var(--card-border);border-radius:12px;padding:28px;margin-top:32px">
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">What Makes a Good Casino App?</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">The best casino apps load games quickly, support touch-optimised controls for slots and table games, and offer the same promotions as the desktop site. Look for apps that support live dealer games on mobile - not all do. A smooth, lag-free experience is non-negotiable when real money is on the line.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Game selection on mobile is the first thing we check. Some casino apps only carry a fraction of their desktop game library. The best ones, like SaffaLuck and Hollywoodbets, bring 90% or more of their full catalogue to mobile. This includes popular slot providers like Pragmatic Play, NetEnt, and Microgaming, plus live dealer tables from Evolution Gaming.</p>
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
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px"><strong>iOS:</strong> Most SA casino apps are available on the App Store. Search for the brand name and download only from the operator's verified App Store listing.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px"><strong>Android:</strong> Google Play has loosened its policy on gambling apps in South Africa, but not all casino apps are listed. If the app is not on Play Store, download the APK directly from the operator's official website. Android will prompt you to allow installation from that source.</p>
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
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Football is the most bet-on sport in South Africa. This guide covers how to choose a licensed bookmaker for football, which markets are available on PSL and European leagues, and how live betting works at SA-facing operators.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Choosing the Right Bookmaker</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Not all SA bookmakers are equal for football. Look for sites that offer competitive odds on PSL matches, plenty of markets (especially for big European leagues), and live in-play betting. {top3[0]}, {top3[1]}, and {top3[2]} consistently rank highest for football coverage.</p>

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
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">South Africa has one of the most active rugby betting markets in the world. From the Springboks' World Cup campaigns to the United Rugby Championship and Currie Cup, there is always an opportunity to back the green and gold - or find value elsewhere.</p>

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
        elif gid == 'aviator-crash-games-guide-south-africa':
            content[gid] = f'''
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">What Are Crash Games?</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Crash games are a category of fast-paced casino games where a multiplier rises from 1.00x and can "crash" at any moment. Your job is to cash out before the crash. The longer you wait, the higher the potential payout - but if the game crashes before you cash out, you lose your stake. It is simple, quick, and has become one of the most popular game types at South African online casinos.</p>

            <h2 style="font-size:18px;font-weight:700;margin-top:32px;margin-bottom:16px">Popular Crash Games in South Africa</h2>

            <div style="background:var(--surface-2);border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid var(--accent)">
              <h3 style="font-size:16px;font-weight:700;margin-bottom:8px">&#9992;&#65039; Aviator (Spribe)</h3>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);margin-bottom:8px">The game that started the crash game craze in South Africa. A plane takes off and the multiplier climbs. Cash out before the plane flies away. Aviator uses a provably fair algorithm so every round can be independently verified. Available at most licensed SA bookmakers including {top3[0]}, {top3[1]}, and {top3[2]}.</p>
              <p style="font-size:13px;color:var(--text-muted)"><strong>Provider:</strong> Spribe &bull; <strong>Min bet:</strong> R1 &bull; <strong>Max multiplier:</strong> 100x+ &bull; <strong>RTP:</strong> 97%</p>
            </div>

            <div style="background:var(--surface-2);border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid var(--accent)">
              <h3 style="font-size:16px;font-weight:700;margin-bottom:8px">&#128640; JetX (SmartSoft Gaming)</h3>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);margin-bottom:8px">JetX features a rocket that flies higher as the multiplier climbs. The gameplay is similar to Aviator but with a different visual style and the ability to place up to three simultaneous bets. Popular at SA sites for its smooth interface and fast rounds.</p>
              <p style="font-size:13px;color:var(--text-muted)"><strong>Provider:</strong> SmartSoft Gaming &bull; <strong>Min bet:</strong> R1 &bull; <strong>Max multiplier:</strong> unlimited &bull; <strong>RTP:</strong> 97%</p>
            </div>

            <div style="background:var(--surface-2);border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid var(--accent)">
              <h3 style="font-size:16px;font-weight:700;margin-bottom:8px">&#128125; Spaceman (Pragmatic Play)</h3>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);margin-bottom:8px">Spaceman puts an astronaut on screen and lets you watch the multiplier climb as he floats through space. It offers a 50% partial cash-out feature, letting you lock in some profit while keeping the rest in play. This makes it more strategic than some other crash games.</p>
              <p style="font-size:13px;color:var(--text-muted)"><strong>Provider:</strong> Pragmatic Play &bull; <strong>Min bet:</strong> R1 &bull; <strong>Max multiplier:</strong> 5,000x &bull; <strong>RTP:</strong> 96.5%</p>
            </div>

            <div style="background:var(--surface-2);border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid #dc2626">
              <h3 style="font-size:16px;font-weight:700;margin-bottom:8px">&#9992;&#65039; Red Baron (Evolution)</h3>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);margin-bottom:8px">The newest addition to the SA crash games market, Red Baron from Evolution features a vintage biplane theme. Like other crash games the multiplier rises as the Red Baron flies - cash out before the plane disappears. Evolution is one of the biggest names in live casino, and their move into crash games signals how popular the category has become.</p>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);margin-bottom:8px">Red Baron is currently available at <a href="../betting-site-review/betxchange.html" style="color:var(--accent);font-weight:600">betXchange</a>, with a live promotion running until 29 March 2026 where R2 bets earn entries into a R200,000 shopping voucher lucky draw.</p>
              <p style="font-size:13px;color:var(--text-muted)"><strong>Provider:</strong> Evolution &bull; <strong>Min bet:</strong> R2 &bull; <strong>Type:</strong> Crash/Multiplier</p>
            </div>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">How Crash Games Work</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Every crash game follows the same core mechanic: a multiplier starts at 1.00x and rises. It can crash at any point - sometimes at 1.01x, sometimes at 50x or higher. You decide when to cash out. If you cash out at 3.00x on a R10 bet, you get R30 back. If the game crashes before you press the button, you lose your R10.</p>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Most crash games use a provably fair algorithm, which means you can verify after each round that the outcome was not manipulated. This transparency is one reason crash games have become so popular - players can check the maths themselves.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Strategies for Crash Games</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">No strategy can guarantee wins, but some approaches help manage your bankroll:</p>
            <ul style="padding-left:0;list-style:none;margin-bottom:16px">
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Low multiplier grind</strong> - Cash out consistently at 1.5x-2.0x for frequent small wins</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Auto cash-out</strong> - Set an automatic cash-out target to remove emotion from the decision</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Split bets</strong> - Place two smaller bets: cash one out early for safety, let the other ride for a higher multiplier</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span><strong>Session limits</strong> - Set a loss limit and stop-win target before you start playing</li>
            </ul>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Where to Play Crash Games in SA</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Most licensed South African betting sites now offer at least one crash game. Aviator is the most widely available, but JetX, Spaceman, and Red Baron are growing fast. Check our <a href="../casino-sites.html" style="color:var(--accent);font-weight:600">casino sites</a> page for the full list of licensed operators, or browse <a href="../promo-codes.html" style="color:var(--accent);font-weight:600">promo codes</a> for welcome bonuses you can use on crash games.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Responsible Play</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">Crash games are fast and can be addictive. The speed of rounds means you can go through your bankroll quickly if you are not careful. Always set limits, use the auto cash-out feature, and never chase losses. If you need help, visit our <a href="../responsible-gambling-policy.html" style="color:var(--accent);font-weight:600">responsible gambling</a> page for SA support resources.</p>'''
        elif gid == 'odds-explained-south-africa':
            h2s = 'style="font-size:18px;font-weight:700;margin-bottom:12px"'
            h3s = 'style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px"'
            ps = 'style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px"'
            li_s = 'style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"'
            bullet = '<span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>'
            xmark = '<span style="position:absolute;left:0;color:#dc2626">&#10007;</span>'
            uls = 'style="padding-left:0;list-style:none;margin-bottom:16px"'
            tbl = 'style="width:100%;border-collapse:collapse;font-size:14px;margin-bottom:20px"'
            ths = 'style="text-align:left;padding:10px 14px;background:var(--accent);color:#fff;font-size:13px;font-weight:600"'
            tds = 'style="padding:10px 14px;border-bottom:1px solid var(--border);color:var(--text-secondary)"'
            tip_box = 'style="background:var(--surface-2);border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid var(--accent)"'
            content[gid] = f'''
            <h2 {h2s}>Understanding Betting Odds</h2>
            <p {ps}>Betting odds tell you two things: how likely a bookmaker thinks an outcome is, and how much you stand to win if your bet is successful. Every bet you place at a South African bookmaker uses odds to calculate your potential return. Understanding them is the single most important skill in sports betting.</p>

            <h3 {h3s}>Decimal Odds (Standard in South Africa)</h3>
            <p {ps}>South African bookmakers display odds in decimal format by default. Decimal odds show your total return per R1 wagered, including your original stake. For example, odds of 2.50 mean a R100 bet returns R250 (R150 profit + R100 stake). The calculation is simple: Stake x Odds = Total Return.</p>
            <table {tbl}>
              <thead><tr><th {ths}>Odds</th><th {ths}>R100 Stake</th><th {ths}>Total Return</th><th {ths}>Profit</th><th {ths}>Implied Probability</th></tr></thead>
              <tbody>
                <tr><td {tds}>1.20</td><td {tds}>R100</td><td {tds}>R120</td><td {tds}>R20</td><td {tds}>83.3% (strong favourite)</td></tr>
                <tr><td {tds}>1.50</td><td {tds}>R100</td><td {tds}>R150</td><td {tds}>R50</td><td {tds}>66.7%</td></tr>
                <tr><td {tds}>2.00</td><td {tds}>R100</td><td {tds}>R200</td><td {tds}>R100</td><td {tds}>50.0% (even chance)</td></tr>
                <tr><td {tds}>3.00</td><td {tds}>R100</td><td {tds}>R300</td><td {tds}>R200</td><td {tds}>33.3%</td></tr>
                <tr><td {tds}>5.00</td><td {tds}>R100</td><td {tds}>R500</td><td {tds}>R400</td><td {tds}>20.0%</td></tr>
                <tr><td {tds}>10.00</td><td {tds}>R100</td><td {tds}>R1,000</td><td {tds}>R900</td><td {tds}>10.0% (outsider)</td></tr>
                <tr><td {tds}>51.00</td><td {tds}>R100</td><td {tds}>R5,100</td><td {tds}>R5,000</td><td {tds}>2.0% (long shot)</td></tr>
              </tbody>
            </table>

            <h3 {h3s}>Fractional Odds (UK Style)</h3>
            <p {ps}>You may see fractional odds on international sites or in horse racing. Fractional odds show profit relative to stake. Odds of 3/1 (spoken "three to one") mean you win R3 for every R1 staked. To convert fractional to decimal: divide the fraction and add 1. So 3/1 = 3.0 + 1 = 4.00 decimal.</p>
            <table {tbl}>
              <thead><tr><th {ths}>Fractional</th><th {ths}>Decimal</th><th {ths}>Meaning</th></tr></thead>
              <tbody>
                <tr><td {tds}>1/5</td><td {tds}>1.20</td><td {tds}>Win R1 for every R5 staked (heavy favourite)</td></tr>
                <tr><td {tds}>1/2</td><td {tds}>1.50</td><td {tds}>Win R1 for every R2 staked</td></tr>
                <tr><td {tds}>Evens (1/1)</td><td {tds}>2.00</td><td {tds}>Win R1 for every R1 staked</td></tr>
                <tr><td {tds}>2/1</td><td {tds}>3.00</td><td {tds}>Win R2 for every R1 staked</td></tr>
                <tr><td {tds}>5/1</td><td {tds}>6.00</td><td {tds}>Win R5 for every R1 staked</td></tr>
                <tr><td {tds}>10/1</td><td {tds}>11.00</td><td {tds}>Win R10 for every R1 staked</td></tr>
              </tbody>
            </table>

            <h3 {h3s}>American Odds (Moneyline)</h3>
            <p {ps}>American odds use + and - symbols. A minus sign (e.g. -150) shows how much you need to stake to win R100. A plus sign (e.g. +200) shows how much you win from a R100 stake. You will mainly see these on American sports. Most SA bookmakers let you switch display format in your account settings.</p>

            <h3 {h3s}>Implied Probability: The Key Concept</h3>
            <p {ps}>Every set of odds implies a probability. The formula is: Implied Probability = 1 / Decimal Odds x 100. Odds of 2.00 imply a 50% chance (1/2.00 = 0.50). This matters because the bookmaker adds a margin (called "overround" or "vig") to every market. If the true probability of an outcome is 50%, the bookmaker might price it at 1.90 instead of 2.00 - that difference is their profit margin.</p>

            <div {tip_box}>
              <h4 style="font-size:15px;font-weight:700;margin-bottom:6px">&#128161; Worked Example: PSL Match</h4>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);margin-bottom:8px">Orlando Pirates vs Kaizer Chiefs. Odds: Pirates 1.80 | Draw 3.40 | Chiefs 4.50</p>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);margin-bottom:4px">Implied probabilities: Pirates 55.6% + Draw 29.4% + Chiefs 22.2% = <strong>107.2%</strong></p>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary)">The total exceeds 100% by 7.2% - that is the bookmaker margin. A lower margin means better value for punters. Compare margins across SA bookmakers to find the best odds.</p>
            </div>

            <h3 {h3s}>How Bookmakers Set Odds</h3>
            <p {ps}>Bookmakers employ teams of traders and algorithms to set odds. They start with statistical models based on team form, head-to-head records, injuries, and other data. Then they adjust based on where the money is flowing. If too many punters back one outcome, the odds shorten to balance the book.</p>

            <h3 {h3s}>Finding Value in the Odds</h3>
            <p {ps}>Value betting is the foundation of profitable long-term betting. A bet has value when the probability you assign to an outcome is higher than what the odds imply. If you believe Orlando Pirates have a 60% chance of winning but the odds imply only 50%, that is a value bet.</p>
            <ul {uls}>
              <li {li_s}>{bullet}<strong>Step 1:</strong> Estimate the probability based on your research</li>
              <li {li_s}>{bullet}<strong>Step 2:</strong> Calculate the implied probability from the bookmaker odds</li>
              <li {li_s}>{bullet}<strong>Step 3:</strong> If your estimate is higher, place the bet</li>
              <li {li_s}>{bullet}<strong>Step 4:</strong> Keep detailed records to track if your estimates are accurate</li>
            </ul>

            <h3 {h3s}>Odds Movement and Line Shopping</h3>
            <p {ps}>Odds are not fixed - they move based on market conditions. Line shopping (comparing odds across bookmakers) is one of the easiest ways to increase your returns. The difference between odds of 2.00 and 2.10 might seem small, but over 100 bets of R100 each, that is an extra R1,000 in returns.</p>

            <h3 {h3s}>Common Odds Mistakes</h3>
            <ul {uls}>
              <li {li_s}>{xmark}Assuming shorter odds always win (they do not - upsets happen)</li>
              <li {li_s}>{xmark}Ignoring the bookmaker margin when comparing value</li>
              <li {li_s}>{xmark}Betting on long shots for the thrill without considering probability</li>
              <li {li_s}>{xmark}Not comparing odds across different SA bookmakers before placing a bet</li>
            </ul>

            <h3 {h3s}>Recommended Bookmakers for Best Odds</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">For consistently competitive odds on South African sports, we recommend {top3[0]}, {top3[1]}, and {top3[2]}. Check our <a href="../betting-sites.html" style="color:var(--accent);font-weight:600">betting sites comparison</a> for a full breakdown of which bookmakers offer the best odds by sport.</p>'''

        elif gid == 'betting-strategies-south-africa':
            h2s = 'style="font-size:18px;font-weight:700;margin-bottom:12px"'
            h3s = 'style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px"'
            ps = 'style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px"'
            li_s = 'style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"'
            bullet = '<span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>'
            xmark = '<span style="position:absolute;left:0;color:#dc2626">&#10007;</span>'
            uls = 'style="padding-left:0;list-style:none;margin-bottom:16px"'
            tbl = 'style="width:100%;border-collapse:collapse;font-size:14px;margin-bottom:20px"'
            ths = 'style="text-align:left;padding:10px 14px;background:var(--accent);color:#fff;font-size:13px;font-weight:600"'
            tds = 'style="padding:10px 14px;border-bottom:1px solid var(--border);color:var(--text-secondary)"'
            tip_box = 'style="background:var(--surface-2);border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid var(--accent)"'
            content[gid] = f'''
            <h2 {h2s}>Betting Strategies That Work for SA Punters</h2>
            <p {ps}>There is no magic formula that guarantees profit from betting. Anyone who tells you otherwise is selling something. But there are proven strategies that tilt the odds in your favour over time. This guide covers approaches used by successful South African punters - from basic bankroll management to advanced staking systems.</p>

            <h3 {h3s}>1. Value Betting</h3>
            <p {ps}>Value betting is the single most important concept in profitable sports betting. A value bet exists when the bookmaker odds overestimate the probability of an outcome not happening. In other words, the odds are higher than they should be.</p>
            <div {tip_box}>
              <h4 style="font-size:15px;font-weight:700;margin-bottom:6px">&#128161; Example</h4>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary)">Mamelodi Sundowns at home to Stellenbosch. You believe Sundowns have a 70% chance of winning. The bookmaker offers odds of 1.55 (implying 64.5%). Since your estimate (70%) exceeds the implied probability (64.5%), this is a value bet.</p>
            </div>

            <h3 {h3s}>2. Bankroll Management</h3>
            <p {ps}>Your bankroll is the total amount you have set aside specifically for betting. It should be money you can afford to lose completely. The most common approach is the percentage method: never bet more than 1-5% of your bankroll on a single bet.</p>
            <table {tbl}>
              <thead><tr><th {ths}>Bankroll Size</th><th {ths}>Conservative (1%)</th><th {ths}>Moderate (2%)</th><th {ths}>Aggressive (5%)</th></tr></thead>
              <tbody>
                <tr><td {tds}>R1,000</td><td {tds}>R10 per bet</td><td {tds}>R20 per bet</td><td {tds}>R50 per bet</td></tr>
                <tr><td {tds}>R5,000</td><td {tds}>R50 per bet</td><td {tds}>R100 per bet</td><td {tds}>R250 per bet</td></tr>
                <tr><td {tds}>R10,000</td><td {tds}>R100 per bet</td><td {tds}>R200 per bet</td><td {tds}>R500 per bet</td></tr>
              </tbody>
            </table>

            <h3 {h3s}>3. Specialisation</h3>
            <p {ps}>The best bettors specialise. Instead of betting on every sport and every league, pick one or two areas and become an expert. If you follow the PSL religiously, you probably know more about Polokwane City home form than most bookmaker traders do. That knowledge is your edge.</p>

            <h3 {h3s}>4. Staking Plans</h3>
            <ul {uls}>
              <li {li_s}>{bullet}<strong>Flat staking</strong> - Same amount on every bet regardless of confidence. Simple and effective. Best for beginners.</li>
              <li {li_s}>{bullet}<strong>Proportional staking</strong> - Bet a fixed percentage of your current bankroll. Bets grow when you win, shrink when you lose.</li>
              <li {li_s}>{bullet}<strong>Kelly Criterion</strong> - A mathematical formula for optimal stake based on your edge: Stake = (bp - q) / b. Most use quarter or half Kelly to reduce variance.</li>
              <li {li_s}>{bullet}<strong>Level confidence</strong> - Assign 1-5 star ratings to bets. 1-star = 1% bankroll, 5-star = 5% bankroll.</li>
            </ul>

            <h3 {h3s}>5. Line Shopping</h3>
            <p {ps}>Different SA bookmakers offer different odds on the same event. Checking 3-4 bookmakers before placing a bet takes 30 seconds and can increase your long-term returns by 10-15%. Keep accounts with at least three of the top SA bookmakers: {top3[0]}, {top3[1]}, and {top3[2]}.</p>

            <h3 {h3s}>6. Record Keeping</h3>
            <p {ps}>If you do not track your bets, you cannot improve. At minimum, record: date, event, market, odds, stake, result, and profit/loss.</p>
            <div {tip_box}>
              <h4 style="font-size:15px;font-weight:700;margin-bottom:6px">&#128202; Key Metrics to Track</h4>
              <ul style="padding-left:0;list-style:none;margin:0">
                <li {li_s}>{bullet}<strong>ROI</strong> - Total profit / total staked x 100. Anything above 5% long-term is excellent.</li>
                <li {li_s}>{bullet}<strong>Strike rate</strong> - Percentage of bets that win. A 40% strike rate at average odds of 3.00 is very profitable.</li>
                <li {li_s}>{bullet}<strong>Yield</strong> - Profit per bet as a percentage. A 10% yield means R10 profit per R100 bet on average.</li>
              </ul>
            </div>

            <h3 {h3s}>7. In-Play Betting Strategy</h3>
            <p {ps}>Live betting offers opportunities that pre-match markets miss. Watch for: early goals that inflate odds on the losing team to come back, red cards that shift the dynamic, and late-game scenarios where bookmakers overreact. The key is to watch the match rather than betting blind on in-play stats.</p>

            <h3 {h3s}>Strategies to Avoid</h3>
            <ul {uls}>
              <li {li_s}>{xmark}<strong>Martingale</strong> - Doubling your stake after every loss. Mathematically flawed and will eventually destroy your bankroll.</li>
              <li {li_s}>{xmark}<strong>Paid betting systems</strong> - If someone had a guaranteed profitable system, they would not sell it for R500.</li>
              <li {li_s}>{xmark}<strong>Chasing losses</strong> - Increasing stakes to recover previous losses. The maths is against you.</li>
              <li {li_s}>{xmark}<strong>Following tipsters blindly</strong> - Most tipsters cherry-pick their results. Track their actual performance first.</li>
            </ul>

            <h3 {h3s}>Long-Term Mindset</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">Profitable betting is a marathon, not a sprint. Even the best strategies go through losing streaks. What matters is making good decisions consistently. Set realistic expectations: a 5-10% return on investment is what professional bettors target.</p>'''

        elif gid == 'how-to-bet-on-psl':
            h2s = 'style="font-size:18px;font-weight:700;margin-bottom:12px"'
            h3s = 'style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px"'
            ps = 'style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px"'
            li_s = 'style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"'
            bullet = '<span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>'
            check = '<span style="position:absolute;left:0;color:#16a34a">&#10003;</span>'
            uls = 'style="padding-left:0;list-style:none;margin-bottom:16px"'
            tbl = 'style="width:100%;border-collapse:collapse;font-size:14px;margin-bottom:20px"'
            ths = 'style="text-align:left;padding:10px 14px;background:var(--accent);color:#fff;font-size:13px;font-weight:600"'
            tds = 'style="padding:10px 14px;border-bottom:1px solid var(--border);color:var(--text-secondary)"'
            tip_box = 'style="background:var(--surface-2);border-radius:12px;padding:20px;margin-bottom:16px;border-left:4px solid var(--accent)"'
            content[gid] = f'''
            <h2 {h2s}>The Definitive Guide to Betting on the PSL</h2>
            <p {ps}>The Betway Premiership (Premier Soccer League) is the highest division of South African football and one of the most bet-on leagues in Africa. With 16 teams competing across a 30-match season from August to May, there are over 240 league matches per season to bet on. This guide breaks down the key stats and betting angles using real data from the 2025/2026 season.</p>

            <h3 {h3s}>2025/2026 Season Overview</h3>
            <p {ps}>The 2025/2026 Betway Premiership season has been one of the most competitive in recent memory, with a fierce title race between two of South Africa's biggest clubs. As of March 2026:</p>
            <table {tbl}>
              <thead><tr><th {ths}>Pos</th><th {ths}>Team</th><th {ths}>P</th><th {ths}>W</th><th {ths}>D</th><th {ths}>L</th><th {ths}>GF</th><th {ths}>GA</th><th {ths}>GD</th><th {ths}>Pts</th></tr></thead>
              <tbody>
                <tr><td {tds}><strong>1</strong></td><td {tds}><strong>Orlando Pirates</strong></td><td {tds}>21</td><td {tds}>15</td><td {tds}>3</td><td {tds}>3</td><td {tds}>34</td><td {tds}>9</td><td {tds}>+25</td><td {tds}><strong>48</strong></td></tr>
                <tr><td {tds}><strong>2</strong></td><td {tds}><strong>Mamelodi Sundowns</strong></td><td {tds}>20</td><td {tds}>14</td><td {tds}>5</td><td {tds}>1</td><td {tds}>34</td><td {tds}>10</td><td {tds}>+24</td><td {tds}><strong>47</strong></td></tr>
                <tr><td {tds}>3</td><td {tds}>Sekhukhune United</td><td {tds}>21</td><td {tds}>9</td><td {tds}>7</td><td {tds}>5</td><td {tds}>21</td><td {tds}>14</td><td {tds}>+7</td><td {tds}>34</td></tr>
                <tr><td {tds}>4</td><td {tds}>AmaZulu FC</td><td {tds}>21</td><td {tds}>10</td><td {tds}>4</td><td {tds}>7</td><td {tds}>21</td><td {tds}>19</td><td {tds}>+2</td><td {tds}>34</td></tr>
                <tr><td {tds}>5</td><td {tds}>Durban City FC</td><td {tds}>20</td><td {tds}>9</td><td {tds}>5</td><td {tds}>6</td><td {tds}>19</td><td {tds}>14</td><td {tds}>+5</td><td {tds}>32</td></tr>
                <tr><td {tds}>6</td><td {tds}>Kaizer Chiefs</td><td {tds}>18</td><td {tds}>8</td><td {tds}>6</td><td {tds}>4</td><td {tds}>16</td><td {tds}>12</td><td {tds}>+4</td><td {tds}>30</td></tr>
                <tr><td {tds}>7</td><td {tds}>Polokwane City</td><td {tds}>20</td><td {tds}>7</td><td {tds}>8</td><td {tds}>5</td><td {tds}>16</td><td {tds}>13</td><td {tds}>+3</td><td {tds}>29</td></tr>
              </tbody>
            </table>

            <h3 {h3s}>The Title Race: Pirates vs Sundowns</h3>
            <p {ps}>Orlando Pirates lead with 48 points from 21 matches, with Mamelodi Sundowns just one point behind on 47 from 20 matches (with a game in hand). Pirates have the league's best defence (just 9 goals conceded). Sundowns remain unbeaten away and have dropped only one match all season.</p>

            <div {tip_box}>
              <h4 style="font-size:15px;font-weight:700;margin-bottom:6px">&#9917; Betting Angle: Title Outright Market</h4>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary)">With Sundowns having a game in hand, the outright title market is essentially a coin flip. Look for value in the "winning margin" market. Historically, Sundowns are strong finishers, winning 7 of their last 8 titles.</p>
            </div>

            <h3 {h3s}>Top Scorers 2025/2026</h3>
            <table {tbl}>
              <thead><tr><th {ths}>Player</th><th {ths}>Team</th><th {ths}>Goals</th><th {ths}>Matches</th><th {ths}>Goals/Match</th></tr></thead>
              <tbody>
                <tr><td {tds}><strong>J. Dion</strong></td><td {tds}>Golden Arrows</td><td {tds}>12</td><td {tds}>18</td><td {tds}>0.67</td></tr>
                <tr><td {tds}><strong>I. Rayners</strong></td><td {tds}>Mamelodi Sundowns</td><td {tds}>10</td><td {tds}>16</td><td {tds}>0.63</td></tr>
                <tr><td {tds}>B. Grobler</td><td {tds}>Sekhukhune United</td><td {tds}>8</td><td {tds}>19</td><td {tds}>0.42</td></tr>
                <tr><td {tds}>L. Phili</td><td {tds}>Stellenbosch FC</td><td {tds}>7</td><td {tds}>17</td><td {tds}>0.41</td></tr>
                <tr><td {tds}>P. Maswanganyi</td><td {tds}>Orlando Pirates</td><td {tds}>6</td><td {tds}>17</td><td {tds}>0.35</td></tr>
              </tbody>
            </table>

            <h3 {h3s}>Understanding PSL Teams</h3>

            <div {tip_box}>
              <h4 style="font-size:15px;font-weight:700;margin-bottom:6px">&#128640; Orlando Pirates</h4>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary)">The Buccaneers have a 71% win rate (15W, 3D, 3L). Their defence concedes just 0.43 goals per match. <strong>Betting angle:</strong> Pirates under 1.5 goals conceded has hit in over 80% of matches. "Pirates to win to nil" offers consistent value at home.</p>
            </div>

            <div {tip_box}>
              <h4 style="font-size:15px;font-weight:700;margin-bottom:6px">&#9728;&#65039; Mamelodi Sundowns</h4>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary)">The defending champions have only lost once this season. Loftus Versfeld remains a fortress. <strong>Betting angle:</strong> Sundowns Double Chance (win or draw) has hit in 19 of 20 matches. Their games tend to have fewer goals - Under 2.5 is profitable.</p>
            </div>

            <div {tip_box}>
              <h4 style="font-size:15px;font-weight:700;margin-bottom:6px">&#128293; Kaizer Chiefs</h4>
              <p style="font-size:14px;line-height:1.75;color:var(--text-secondary)">Amakhosi sit 6th with 30 points from 18 matches, still within reach of the top 4. Chiefs are the most backed team by SA punters which often means shorter odds than warranted. <strong>Betting angle:</strong> Look for value fading Chiefs away. Their draw rate (33%) suggests BTTS is worth considering.</p>
            </div>

            <h3 {h3s}>Relegation Battle</h3>
            <p {ps}>Magesi FC (14 points from 20 matches), Orbit College (18 points), and Marumo Gallants (18 points) are in serious danger. The relegation market is often overlooked and can offer excellent value.</p>

            <h3 {h3s}>PSL Betting Markets</h3>
            <table {tbl}>
              <thead><tr><th {ths}>Market</th><th {ths}>Description</th><th {ths}>Best For</th></tr></thead>
              <tbody>
                <tr><td {tds}><strong>1X2</strong></td><td {tds}>Home win, draw, or away win</td><td {tds}>Straightforward bets</td></tr>
                <tr><td {tds}><strong>Double Chance</strong></td><td {tds}>Cover two of three outcomes</td><td {tds}>Safer bets at lower odds</td></tr>
                <tr><td {tds}><strong>Over/Under 2.5</strong></td><td {tds}>Will there be 3+ goals?</td><td {tds}>PSL averages 2.3 goals/match</td></tr>
                <tr><td {tds}><strong>BTTS</strong></td><td {tds}>Will both sides score?</td><td {tds}>BTTS hits ~50% in PSL</td></tr>
                <tr><td {tds}><strong>Asian Handicap</strong></td><td {tds}>Virtual goal head start</td><td {tds}>Eliminating the draw</td></tr>
                <tr><td {tds}><strong>Correct Score</strong></td><td {tds}>Predict the exact final score</td><td {tds}>High odds, low probability</td></tr>
                <tr><td {tds}><strong>Goalscorer</strong></td><td {tds}>Which player scores?</td><td {tds}>Top scorer markets</td></tr>
                <tr><td {tds}><strong>Corners</strong></td><td {tds}>Total corners in the match</td><td {tds}>Niche market with value</td></tr>
              </tbody>
            </table>

            <h3 {h3s}>PSL-Specific Betting Tips</h3>
            <ul {uls}>
              <li {li_s}>{check}<strong>Home advantage is real</strong> - Home teams win approximately 44% of PSL matches. Travel distances in SA are significant.</li>
              <li {li_s}>{check}<strong>The draw is undervalued</strong> - Draws occur in roughly 26% of PSL matches, often at odds of 3.00+. That is value.</li>
              <li {li_s}>{check}<strong>Under 2.5 goals is profitable</strong> - The PSL averages around 2.3 goals per match.</li>
              <li {li_s}>{check}<strong>Follow team news</strong> - Player suspensions and injuries have an outsized impact in the PSL. Squads are thinner.</li>
              <li {li_s}>{check}<strong>Midweek matches favour big clubs</strong> - Smaller clubs with thinner squads struggle with fixture congestion.</li>
              <li {li_s}>{check}<strong>Derby matches are unpredictable</strong> - Soweto Derby (Chiefs vs Pirates) and the Tshwane Derby often produce shock results.</li>
            </ul>

            <h3 {h3s}>Key Fixtures to Watch</h3>
            <ul {uls}>
              <li {li_s}>{bullet}<strong>Pirates vs Sundowns</strong> - The biggest match of the season. The winner likely takes the title.</li>
              <li {li_s}>{bullet}<strong>Chiefs vs Pirates (Soweto Derby)</strong> - The biggest derby in African football. Form goes out the window.</li>
              <li {li_s}>{bullet}<strong>Bottom 3 clashes</strong> - Magesi, Orbit College, and Gallants playing each other - motivation is at 100%.</li>
            </ul>

            <h3 {h3s}>Where to Bet on the PSL</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">All licensed SA bookmakers cover the PSL. {top3[0]}, {top3[1]}, and {top3[2]} typically offer the best odds and deepest markets. For welcome bonuses, check our <a href="../promo-codes.html" style="color:var(--accent);font-weight:600">promo codes page</a>. Remember to bet responsibly.</p>'''

        elif gid == 'sports-betting-markets-explained':
            h2s = 'style="font-size:18px;font-weight:700;margin-bottom:12px"'
            h3s = 'style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px"'
            ps = 'style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px"'
            li_s = 'style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"'
            bullet = '<span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>'
            uls = 'style="padding-left:0;list-style:none;margin-bottom:16px"'
            tbl = 'style="width:100%;border-collapse:collapse;font-size:14px;margin-bottom:20px"'
            ths = 'style="text-align:left;padding:10px 14px;background:var(--accent);color:#fff;font-size:13px;font-weight:600"'
            tds = 'style="padding:10px 14px;border-bottom:1px solid var(--border);color:var(--text-secondary)"'
            content[gid] = f'''
            <h2 {h2s}>Sports Betting Markets Explained</h2>
            <p {ps}>A betting market is a specific outcome you can bet on within a sporting event. A single football match might have 100+ markets available. Understanding the main markets is essential for finding value. This guide explains every major market available at South African bookmakers.</p>

            <h3 {h3s}>Match Result (1X2)</h3>
            <p {ps}>The most basic market. You back the home team to win (1), the draw (X), or the away team to win (2). In PSL football, the draw is undervalued - it occurs in about 26% of matches but is rarely the public's first choice.</p>

            <h3 {h3s}>Double Chance</h3>
            <p {ps}>Double Chance lets you cover two of three outcomes: 1X (home or draw), X2 (away or draw), or 12 (either team wins). Odds are lower because your chance of winning is around 66%. For example, backing Mamelodi Sundowns Double Chance (1X) this season would have won 95% of the time.</p>

            <h3 {h3s}>Over/Under Goals</h3>
            <p {ps}>You bet on whether the total goals will be over or under a specified line. The most common is 2.5 goals.</p>
            <table {tbl}>
              <thead><tr><th {ths}>Line</th><th {ths}>Over Wins If</th><th {ths}>Under Wins If</th><th {ths}>PSL Hit Rate (Over)</th></tr></thead>
              <tbody>
                <tr><td {tds}>0.5</td><td {tds}>1+ goals</td><td {tds}>0 goals</td><td {tds}>~92%</td></tr>
                <tr><td {tds}>1.5</td><td {tds}>2+ goals</td><td {tds}>0-1 goals</td><td {tds}>~68%</td></tr>
                <tr><td {tds}>2.5</td><td {tds}>3+ goals</td><td {tds}>0-2 goals</td><td {tds}>~45%</td></tr>
                <tr><td {tds}>3.5</td><td {tds}>4+ goals</td><td {tds}>0-3 goals</td><td {tds}>~25%</td></tr>
                <tr><td {tds}>4.5</td><td {tds}>5+ goals</td><td {tds}>0-4 goals</td><td {tds}>~12%</td></tr>
              </tbody>
            </table>

            <h3 {h3s}>Both Teams to Score (BTTS)</h3>
            <p {ps}>A simple yes/no market: will both teams score at least one goal? BTTS Yes hits roughly 50% of the time in the PSL. It is popular because it keeps you invested for the full 90 minutes.</p>

            <h3 {h3s}>Handicap Betting (Asian and European)</h3>
            <p {ps}>Handicap betting gives one team a virtual advantage. If you bet Orlando Pirates -1.5, they need to win by 2+ goals. If you bet Orbit College +1.5, they need to win, draw, or lose by just one goal. Asian Handicaps use quarter-goal increments to eliminate dead-heat scenarios.</p>

            <h3 {h3s}>Goalscorer Markets</h3>
            <ul {uls}>
              <li {li_s}>{bullet}<strong>First Goalscorer</strong> - Highest odds. Your player must score the first goal.</li>
              <li {li_s}>{bullet}<strong>Last Goalscorer</strong> - Similar but less popular. Often slightly better value.</li>
              <li {li_s}>{bullet}<strong>Anytime Goalscorer</strong> - Your player scores at any point. Lower odds, higher hit rate.</li>
              <li {li_s}>{bullet}<strong>2+ Goals</strong> - Your player scores two or more. Good odds on prolific strikers like Iqraam Rayners or J. Dion.</li>
            </ul>

            <h3 {h3s}>Correct Score</h3>
            <p {ps}>Predict the exact final score. High-risk, high-reward. Odds range from 5.00 for common scores (1-0, 1-1) to 100+ for unusual results. In the PSL, the most common scorelines are 1-0, 1-1, and 2-1. Some punters place small stakes across 3-4 likely scorelines.</p>

            <h3 {h3s}>Corners, Cards, and Specials</h3>
            <ul {uls}>
              <li {li_s}>{bullet}<strong>Total Corners Over/Under</strong> - Usually set around 9.5-10.5 for PSL matches</li>
              <li {li_s}>{bullet}<strong>Total Cards Over/Under</strong> - PSL matches tend to be physical; over 3.5 cards is common</li>
              <li {li_s}>{bullet}<strong>Half-time/Full-time</strong> - Predict the result at both half-time and full-time</li>
              <li {li_s}>{bullet}<strong>Winning margin</strong> - By how many goals will the winning team win?</li>
            </ul>

            <h3 {h3s}>Accumulator Markets</h3>
            <p {ps}>An accumulator (acca) combines multiple selections into one bet. All must win to pay out. The odds multiply: three 2.00 selections become 8.00. While returns are exciting, the probability drops fast. A 4-fold acca at 50% per leg has only a 6.25% chance of winning. Stick to doubles and trebles.</p>

            <h3 {h3s}>Outright and Futures Markets</h3>
            <ul {uls}>
              <li {li_s}>{bullet}<strong>League Winner</strong> - Who wins the Betway Premiership?</li>
              <li {li_s}>{bullet}<strong>Top Goalscorer</strong> - Who finishes as the season top scorer?</li>
              <li {li_s}>{bullet}<strong>Relegation</strong> - Which team(s) will be relegated?</li>
              <li {li_s}>{bullet}<strong>Top 4 Finish</strong> - Will a specific team finish in the top 4?</li>
            </ul>
            <p {ps}>Outright markets offer the best value early in the season before the picture becomes clear.</p>

            <h3 {h3s}>Live (In-Play) Markets</h3>
            <p {ps}>In-play markets are available once a match kicks off. Odds update in real time. Popular live markets include: next goal, match result, total goals, and next corner. In-play betting requires discipline - the speed can lead to impulsive decisions.</p>

            <h3 {h3s}>Which Markets Are Best for Beginners?</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">Start with Match Result, Over/Under 2.5, and BTTS. These are easy to understand and have competitive odds. As you gain experience, explore Asian Handicaps and goalscorer markets. For the best odds, compare {top3[0]}, {top3[1]}, and {top3[2]} before placing your bets.</p>'''


        elif gid == 'online-slots-guide-south-africa':
            content[gid] = '''
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Choosing an Online Slot at a Licensed SA Casino</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">This guide helps you decide which slot to play based on RTP, volatility, free-spin terms, and max-cashout limits. Those four figures determine whether a slot suits your bankroll and session goals, and they vary significantly across titles available at South African platforms.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">RTP: What the Number Means in Practice</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">RTP (return to player) is the theoretical percentage of total wagers a slot pays back over millions of rounds. A slot with 96% RTP returns R96 per R100 wagered on average, with the house keeping R4. Higher RTP narrows the house edge but does not guarantee individual session results. Slots between 96% and 97% RTP are considered above average. Anything below 94% represents a steeper edge against the player.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Volatility: Low, Medium, and High</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Volatility describes how a slot distributes its payouts. Low-volatility slots pay out frequently but in smaller amounts, which suits players who want longer sessions on a fixed deposit. High-volatility slots pay less often but can produce large single wins. Medium volatility sits between the two. Volatility is not listed on every game page but providers like Pragmatic Play and Habanero publish it in their PAR sheets.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Free-Spin Terms: What Counts and What Does Not</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">When a platform awards free spins, the terms determine their actual value. Key factors: the wagering requirement (how many times you must bet the winnings before withdrawal), the spin value (fixed coin size versus your last bet size), which games are eligible, and the expiry window. Free spins with a 30x wagering requirement on a low-RTP slot are worth far less than spins with a 5x requirement on a 96%+ RTP title.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Max-Cashout Limits</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Many slot bonuses and free-spin offers carry a max-cashout cap, typically between R500 and R5,000. This means that even if you hit a large win during the bonus round, your withdrawable amount is capped. Check this limit before accepting a free-spin bonus, particularly on high-volatility slots where a single feature can exceed that ceiling.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Choosing by User Type</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Casual players on a fixed session budget: choose low-volatility slots with RTP above 95% and avoid high-cap slots where a large stake is needed to trigger features. Players who want feature-heavy gameplay with bigger potential wins: look for medium-to-high volatility with RTP above 96%, and check whether the base-game hit frequency is high enough to sustain the bankroll during dry spells. Bonus hunters: prioritise the wagering requirement and expiry window over headline bonus size.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Common Mistakes</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">Choosing a slot based on visual theme alone without checking RTP. Claiming free spins without reading the cashout cap. Playing a high-volatility slot with a session budget too small to reach the feature consistently. Confusing the displayed RTP with a guaranteed return per session.</p>'''

        else:
            # Generic guide content template
            title = g['title']
            short = g['short']
            content[gid] = f'''
            <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">{e(title)}</h2>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">{e(short)} This guide covers the specific factors South African players need to weigh, including local payment methods, provincial licensing, and platform differences observed during our testing.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">What This Decision Involves</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">South Africa has more than 30 licensed operators. Each one structures its markets, bonuses, and payment flows differently. The guides on this site are written to point out where those differences are material, not to describe what every punter already knows.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">What to Check Before Choosing a Platform</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Confirm the operator holds a valid provincial gambling licence. Check the minimum deposit and whether the payment methods you use are supported for both deposits and withdrawals. Review the welcome bonus terms, specifically the wagering requirement and expiry period, before claiming. See our <a href="../betting-sites.html" style="color:var(--accent);font-weight:600">betting sites comparison</a> for tested ratings across all SA operators.</p>

            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Local Factors That Matter</h3>
            <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">FICA verification is required by all licensed operators before withdrawals are permitted. Most SA platforms support Ozow, Instant EFT, and bank cards. Withdrawal approval times vary by operator; our tested figures are on each individual review page.</p>'''

    return content


# ============================================
# CRASH GAMES CATEGORY & SA SLOTS SECTION
# ============================================

def build_crash_games_category(page_fn, category_hero_fn, breadcrumbs_fn, write_file_fn,
                                BRANDS, masked_exit_fn, brand_bg_fn, logo_path_fn,
                                rating_badge_fn, OUT, BASE_URL):
    """Build crash games category page with sub-page links."""
    os.makedirs(f'{OUT}/crash-games', exist_ok=True)

    # Crash games data
    crash_games = [
        {
            'id': 'aviator',
            'name': 'Aviator',
            'provider': 'Spribe',
            'description': 'The original crash game. Watch the plane fly and cash out before it disappears. Provably fair with RTP of 97%.',
            'rtp': '97%',
            'icon': '✈️',
        },
        {
            'id': 'jetx',
            'name': 'JetX',
            'provider': 'SmartSoft Gaming',
            'description': 'A rocket launches and the multiplier climbs. Three simultaneous bets possible. Multiplier can reach 25,000x.',
            'rtp': '97%',
            'icon': '🚀',
        },
        {
            'id': 'spaceman',
            'name': 'Spaceman',
            'provider': 'Pragmatic Play',
            'description': 'An astronaut floats through space as the multiplier rises. Features 50% partial cash-out for strategic play.',
            'rtp': '96.5%',
            'icon': '🧑‍🚀',
        },
        {
            'id': 'red-baron',
            'name': 'Red Baron',
            'provider': 'Evolution',
            'description': 'Vintage biplane theme from Evolution Gaming. The newest crash game in the SA market with smooth animations.',
            'rtp': '96.36%',
            'icon': '🔴',
        },
    ]

    # Build game cards
    game_cards = ''
    for g in crash_games:
        game_cards += f"""<a href="{g['id']}.html" class="card" style="padding:24px;display:flex;flex-direction:column;gap:12px;min-height:220px">
          <div style="font-size:40px;line-height:1">{g['icon']}</div>
          <h3 style="font-size:18px;font-weight:700">{e(g['name'])}</h3>
          <p style="font-size:13px;color:var(--text-muted)">by {e(g['provider'])} &middot; RTP: {g['rtp']}</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.6;flex:1">{e(g['description'])}</p>
          <span style="font-size:13px;color:var(--accent);font-weight:600">Read Full Guide &rarr;</span>
        </a>"""

    # Top bookmakers for crash games
    top_crash = BRANDS[:5]
    bookie_cards = ''
    for i, b in enumerate(top_crash):
        logo = logo_path_fn(b, 1)
        logo_html = f'<img src="{logo}" alt="{e(b["name"])}" style="width:32px;height:32px;object-fit:contain;border-radius:6px;background:{brand_bg_fn(b)};padding:2px;border:1px solid var(--border)" loading="lazy">' if logo else ''
        exit_link = masked_exit_fn(b, 1)
        bookie_cards += f"""<div class="card" style="padding:16px;display:flex;align-items:center;gap:12px">
          <span style="font-size:14px;font-weight:700;color:var(--text-muted)">#{i+1}</span>
          {logo_html}
          <div style="flex:1;min-width:0">
            <div style="font-size:14px;font-weight:600">{e(b['name'])}</div>
            <div style="font-size:12px;color:var(--bonus);font-weight:500">{e(b.get('welcomeBonusAmount',''))}</div>
          </div>
          {f'<a href="{exit_link}" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary btn-sm">Play</a>' if exit_link else ''}
        </div>"""

    hero = category_hero_fn(
        'Crash Games in South Africa',
        'The complete guide to Aviator, JetX, Spaceman, Red Baron, and other crash games available at SA betting sites.',
        [{"label": "Home", "href": "index.html"}, {"label": "Casino", "href": "casino-sites.html"}, {"label": "Crash Games"}], 1,
        deco_icon='&#x2708;'
    )

    body = f"""
    {hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      <div style="max-width:760px;margin-bottom:32px">
        <p style="font-size:16px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">Crash games are the fastest-growing casino game category in South Africa. Instead of spinning reels or playing cards, you watch a multiplier rise and decide when to cash out. Simple concept, high adrenaline.</p>
        <p style="font-size:16px;line-height:1.75;color:var(--text-secondary)">All crash games listed below are available at licensed SA bookmakers. Explore our detailed guides for each game, or find the best bookmakers to play them.</p>
      </div>

      <h2 style="font-size:20px;font-weight:700;margin-bottom:20px">Popular Crash Games</h2>
      <div class="grid-2" style="margin-bottom:40px">{game_cards}</div>

      <h2 style="font-size:20px;font-weight:700;margin-bottom:20px">Best SA Bookmakers for Crash Games</h2>
      <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:40px;max-width:600px">{bookie_cards}</div>

      <div style="background:var(--card-bg);border:1px solid var(--border);border-radius:12px;padding:24px;max-width:760px">
        <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">How Crash Games Work</h2>
        <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">Every crash game follows the same core mechanic: a multiplier starts at 1.00x and rises. It can crash at any moment, sometimes at 1.01x, sometimes above 100x. You decide when to cash out. If you cash out at 3.00x on a R10 bet, you receive R30. If the game crashes before you press the button, you lose your stake.</p>
        <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">Most crash games use a provably fair algorithm, meaning you can verify after each round that the outcome was not manipulated. This transparency is one reason crash games have become so popular.</p>
        <p style="font-size:14px;line-height:1.75;color:var(--text-secondary)">For detailed strategy tips and game-specific guides, click on any crash game above. 18+ only. Gamble responsibly.</p>
      </div>

      <div style="margin-top:32px">
        <a href="../casino-guides/aviator-crash-games-guide-south-africa.html" style="color:var(--accent);font-weight:600;font-size:14px">Read our in-depth Crash Games Guide &rarr;</a>
      </div>
    </div>"""

    cat_page = page_fn('Crash Games South Africa - Aviator, JetX, Spaceman, Red Baron | MzansiWins',
                       'Complete guide to crash games in SA. Play Aviator, JetX, Spaceman, Red Baron at licensed bookmakers.',
                       'crash-games', body, depth=1, active_nav='casino')
    write_file_fn(f'{OUT}/crash-games/index.html', cat_page)

    # Build individual crash game sub-pages
    for g in crash_games:
        _build_crash_game_subpage(g, crash_games, page_fn, breadcrumbs_fn, write_file_fn,
                                  BRANDS, masked_exit_fn, brand_bg_fn, logo_path_fn,
                                  rating_badge_fn, OUT, BASE_URL)

    return [('crash-games', 0.8)] + [(f'crash-games/{g["id"]}', 0.7) for g in crash_games]


def _build_crash_game_subpage(game, all_games, page_fn, breadcrumbs_fn, write_file_fn,
                               BRANDS, masked_exit_fn, brand_bg_fn, logo_path_fn,
                               rating_badge_fn, OUT, BASE_URL):
    """Build individual crash game page."""
    bc = breadcrumbs_fn([
        {"label": "Home", "href": "index.html"},
        {"label": "Casino", "href": "casino-sites.html"},
        {"label": "Crash Games", "href": "crash-games/index.html"},
        {"label": game['name']}
    ], 1)

    # Content varies by game
    extra_content = {
        'aviator': """
            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Aviator Strategy Tips</h3>
            <ul style="list-style:none;padding:0;margin-bottom:16px">
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Consider using auto-cashout at lower multipliers (1.5x-2x) for consistent small wins</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>The provably fair system means no pattern exists. Each round is independent</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Use the two-bet feature: one safe low cashout, one risky high target</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Set a loss limit before you start playing and stick to it</li>
            </ul>""",
        'jetx': """
            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">JetX Features</h3>
            <ul style="list-style:none;padding:0;margin-bottom:16px">
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Place up to 3 simultaneous bets per round for different strategies</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Maximum multiplier of 25,000x with massive theoretical max payouts</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Galaxy jackpot feature adds extra winning potential</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Provably fair. You can verify each round result independently</li>
            </ul>""",
        'spaceman': """
            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Spaceman Unique Features</h3>
            <ul style="list-style:none;padding:0;margin-bottom:16px">
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>50% partial cash-out lets you lock in some profit while keeping the rest active</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>From Pragmatic Play, one of the world's biggest game providers</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Clean space theme with smooth animations</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Available at most licensed SA betting sites</li>
            </ul>""",
        'red-baron': """
            <h3 style="font-size:16px;font-weight:600;margin-top:24px;margin-bottom:8px">Red Baron Details</h3>
            <ul style="list-style:none;padding:0;margin-bottom:16px">
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>From Evolution, the world leader in live casino games</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>Vintage World War I biplane theme with excellent production quality</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>One of the newest crash games available in SA</li>
              <li style="padding:6px 0;padding-left:20px;position:relative;font-size:14px;line-height:1.75;color:var(--text-secondary)"><span style="position:absolute;left:0;color:var(--accent)">&#8226;</span>RTP of 96.36%, which is standard for crash games</li>
            </ul>""",
    }

    top5 = BRANDS[:5]
    bookies_html = ''
    for i, b in enumerate(top5):
        logo = logo_path_fn(b, 1)
        logo_html = f'<img src="{logo}" alt="{e(b["name"])}" style="width:28px;height:28px;object-fit:contain;border-radius:4px;background:{brand_bg_fn(b)};padding:2px;border:1px solid var(--border)" loading="lazy">' if logo else ''
        exit_link = masked_exit_fn(b, 1)
        bookies_html += f"""<tr>
          <td style="white-space:nowrap"><div style="display:flex;align-items:center;gap:8px">{logo_html} <a href="../betting-site-review/{b['id']}.html" style="color:var(--accent);font-weight:600">{e(b['name'])}</a></div></td>
          <td style="color:var(--bonus);font-weight:600;font-size:13px">{e(b.get('welcomeBonusAmount',''))}</td>
          <td style="text-align:center">{rating_badge_fn(b['overallRating'], 'sm')}</td>
          <td style="text-align:center">{f'<a href="{exit_link}" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary btn-sm">Play</a>' if exit_link else ''}</td>
        </tr>"""

    # Related games
    related = [g2 for g2 in all_games if g2['id'] != game['id']]
    related_html = ''
    for r in related:
        related_html += f'<a href="{r["id"]}.html" class="card" style="padding:16px;display:flex;align-items:center;gap:12px"><span style="font-size:24px">{r["icon"]}</span><div><div style="font-size:14px;font-weight:600">{e(r["name"])}</div><div style="font-size:12px;color:var(--text-muted)">by {e(r["provider"])}</div></div></a>'

    body = f"""
    <div style="background:var(--surface-2);padding:40px 0 32px;border-bottom:1px solid var(--border)">
      <div class="container">
        {bc}
        <div style="display:flex;align-items:center;gap:16px;margin-top:16px">
          <span style="font-size:48px">{game['icon']}</span>
          <div>
            <h1 style="font-size:clamp(1.5rem, 4vw, 2rem);font-weight:800;letter-spacing:-0.02em">{game['name']} Guide South Africa</h1>
            <p style="font-size:14px;color:var(--text-muted)">by {e(game['provider'])} &middot; RTP: {game['rtp']}</p>
          </div>
        </div>
      </div>
    </div>
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      <div style="max-width:760px">
        <p style="font-size:16px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">{e(game['description'])}</p>

        {extra_content.get(game['id'], '')}

        <h2 style="font-size:18px;font-weight:700;margin-top:32px;margin-bottom:16px">Best SA Bookmakers for {game['name']}</h2>
        <div class="table-wrap">
          <table class="compare-table">
            <thead><tr><th>Bookmaker</th><th>Welcome Bonus</th><th>Rating</th><th>Play</th></tr></thead>
            <tbody>{bookies_html}</tbody>
          </table>
        </div>

        <h2 style="font-size:18px;font-weight:700;margin-top:32px;margin-bottom:16px">Other Crash Games</h2>
        <div style="display:flex;flex-direction:column;gap:8px;margin-bottom:32px">{related_html}</div>

        <div style="background:var(--accent-light);border-radius:10px;padding:20px;margin-top:24px">
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.6"><strong>Responsible gambling:</strong> Crash games are entertainment, not a guaranteed way to make money. Set limits, never chase losses, and contact the SA Responsible Gambling Foundation on 0800 006 008 if you need help. 18+ only.</p>
        </div>
      </div>
    </div>"""

    pg = page_fn(f'{game["name"]} Crash Game SA - Play at Licensed Bookmakers | MzansiWins',
                 f'Complete guide to {game["name"]} crash game in South Africa. RTP, strategy tips, and best bookmakers.',
                 f'crash-games/{game["id"]}', body, depth=1, active_nav='casino')
    write_file_fn(f'{OUT}/crash-games/{game["id"]}.html', pg)


def build_sa_slots_section(page_fn, category_hero_fn, breadcrumbs_fn, write_file_fn,
                            BRANDS, masked_exit_fn, brand_bg_fn, logo_path_fn,
                            rating_badge_fn, OUT, BASE_URL):
    """Build SA Slots category page and individual game pages."""
    os.makedirs(f'{OUT}/sa-slots', exist_ok=True)

    sa_slots = [
        {
            'id': 'amakhosi-cash',
            'name': 'Amakhosi Cash',
            'tagline': 'Kaizer Chiefs Megaways',
            'provider': 'Red Tiger',
            'image': 'slot-amakhosi-cash.jpg',
            'rtp': '95.72%',
            'volatility': 'Medium-High',
            'reels': '6 + horizontal reel',
            'rows': 'Up to 7 per reel',
            'paylines': 'Up to 117,649 ways',
            'min_bet': 'R0.50',
            'max_bet': 'R500',
            'max_win': '117,649 ways to win',
            'bonus_features': 'Megaways, Chain Reactions, Free Spins, Multipliers, Win Exchange',
            'jackpot': 'No',
            'availability': 'SuperSportBET exclusive',
            'casino_ids': ['supersportbet'],
            'author': 'Lerato Dlamini',
            'features': ['Megaways mechanic', 'Chain Reactions (cascading wins)', 'Progressive multiplier Free Spins', 'Win Exchange feature', 'Up to 117,649 ways to win'],
            'intro': """Football and slots rarely collide in a way that feels properly local. Amakhosi Cash pulls it off. Developed by Red Tiger and launched exclusively on SuperSportBET, the game is built around the colours and identity of Kaizer Chiefs.

For South African players, that makes a difference. Instead of generic football imagery, Amakhosi Cash leans heavily into the culture of Chiefs supporters. The soundtrack echoes the noise of the stands, while the gold and black colour scheme mirrors matchday at FNB Stadium.

Under the surface it is also a serious slot, using Megaways mechanics, cascading wins, and Red Tiger's Win Exchange feature to create multiple layers of gameplay.""",
            'body_sections': [
                ('Theme and Design', """Amakhosi Cash is unmistakably built for Chiefs supporters. The visual design revolves around the club's colours and symbols.

High-value icons include:
<ul class="slot-symbol-list">
<li>Stadium symbol representing the energy of matchday</li>
<li>Kaizer Chiefs crest, the main premium symbol</li>
<li>Goalkeeper gloves, crown, and football in the mid-tier pay range</li>
</ul>

Lower-value symbols follow the traditional slot format with stylised letters and numbers (A, K, Q, J and 10).

The presentation is loud, celebratory and clearly aimed at fans who follow South African football. It plays less like a standard casino slot and more like a branded entertainment product built around the club's identity."""),
                ('Gameplay Mechanics', """At its core, Amakhosi Cash uses the Megaways system, meaning the number of possible win combinations changes with every spin. Depending on the symbol layout, players can have anything from a few thousand to 117,649 potential ways to win.

Two additional mechanics shape the gameplay:

<strong>Chain Reactions</strong>
When a winning combination lands, the winning symbols disappear and new symbols drop down to fill the gaps. Additional wins can trigger on the same spin. This cascading system creates the potential for multiple wins in quick succession.

<strong>Wild Symbols</strong>
Wilds appear on the middle reels and substitute for any regular paying symbol. They always count as the symbol that produces the longest winning combination, which increases the chances of extending winning chains."""),
                ('Free Spins Feature', """The main bonus round begins when three scatter symbols land.

<table class="slot-table"><thead><tr><th>Scatters</th><th>Reward</th></tr></thead><tbody>
<tr><td>3 scatters</td><td>10 Free Spins</td></tr>
<tr><td>Each additional scatter</td><td>+5 extra spins</td></tr>
</tbody></table>

During the feature, the game introduces a progressive multiplier system. The round begins with a x1 multiplier, and every win increases it by +1, up to x20. Importantly, the multiplier does not reset during the round, which means a strong run of cascading wins can escalate quickly."""),
                ('Win Exchange Feature', """One of the more distinctive elements in the slot is Red Tiger's Win Exchange mechanic. Instead of automatically collecting certain wins, players can exchange them for bonus opportunities.

<table class="slot-table"><thead><tr><th>Win Size</th><th>Player Option</th></tr></thead><tbody>
<tr><td>60x stake or more</td><td>Direct exchange for Free Spins</td></tr>
<tr><td>20x - 60x stake</td><td>Gamble the win on the Win Exchange wheel</td></tr>
</tbody></table>

The feature introduces a small strategic decision. Conservative players will bank wins, while risk-takers may push for the bonus round."""),
            ],
            'review_summary': """Amakhosi Cash is one of the few properly localised slots for South Africa. Instead of a generic football theme, it draws directly from the culture surrounding Kaizer Chiefs and their supporters.

The gameplay delivers solid mechanics: Megaways volatility, cascading Chain Reactions, a growing Free Spins multiplier, and Red Tiger's Win Exchange feature.

For Chiefs fans it is an obvious novelty play. For regular slot players, it remains a technically strong release with plenty of volatility and bonus potential. SuperSportBET has clearly aimed to create club-specific casino content, and Amakhosi Cash shows how that idea can work in practice.""",
            'faqs': [
                ('Where can I play Amakhosi Cash?', 'Amakhosi Cash is exclusive to SuperSportBET. It was created specifically for their Sta Player campaign and is not available at other online casinos.'),
                ('What is the RTP of Amakhosi Cash?', 'The return to player rate is 95.72%, which sits slightly below the industry average. The medium-high volatility compensates with larger potential wins.'),
                ('Does Amakhosi Cash have a progressive jackpot?', 'No. The slot uses a Megaways system with cascading wins and multipliers rather than a progressive jackpot mechanic.'),
                ('What is the Win Exchange feature?', 'Win Exchange allows players to trade wins of 20x stake or more for Free Spins opportunities instead of collecting the payout directly. It is a Red Tiger proprietary feature.'),
            ],
        },
        {
            'id': 'jack-parow',
            'name': 'Jack Parow: Heeltyd Speeltyd',
            'tagline': 'Afrikaans rapper-themed slot',
            'provider': 'ZARbet Signature Range',
            'image': 'slot-jack-parow.jpg',
            'rtp': '96.15%',
            'volatility': 'Medium-High',
            'reels': '5',
            'rows': '3',
            'paylines': '25',
            'min_bet': 'R0.20',
            'max_bet': 'R200',
            'max_win': '12,255 coins',
            'bonus_features': 'Wilds, Triple Wild multiplier, Free Spins, Retriggers',
            'jackpot': 'No',
            'availability': 'ZARbet exclusive',
            'casino_ids': ['zarbet'],
            'author': 'Lerato Dlamini',
            'features': ['Triple Wild on reel 3 triples wins', 'Free Spins with retriggers', '25 paylines', 'Scatter pays anywhere', 'Cape Town music theme'],
            'intro': """South African casino games rarely lean this heavily into local culture. Jack Parow: Heeltyd Speeltyd does exactly that. Built as part of the Signature Range from ZARbet, the slot takes inspiration from Afrikaans rap star Jack Parow.

The result is a music-themed slot that trades traditional casino imagery for caps, microphones, and street-style visuals associated with the artist. It is clearly designed for a South African audience, particularly players familiar with Parow's Cape Town roots in Bellville.

Underneath the cultural references sits a fairly straightforward video slot with Free Spins, Wild multipliers, and a top payout of 12,255 coins.""",
            'body_sections': [
                ('Theme and Design', """Heeltyd Speeltyd is unapologetically local. The reels feature symbols drawn from the visual language of Parow's music and live performances.

Higher-value icons include:
<ul class="slot-symbol-list">
<li>Baseball caps</li>
<li>Sunglasses</li>
<li>Microphones</li>
<li>Jewellery and stage accessories</li>
</ul>

Lower-value symbols follow the usual slot structure, using stylised playing-card letters. The visual design leans towards bright colours, neon accents, and graffiti-style typography. Combined with the soundtrack, the presentation resembles a small Cape Town music festival rather than a traditional casino environment."""),
                ('Gameplay Overview', """The core gameplay is simple and accessible. Choose your stake between R0.20 and R200 per spin, spin the reels, and match symbols from left to right across the paylines. Only the highest win per payline is paid on each spin, although scatter symbols can trigger additional payouts. This structure makes the slot easy to follow even for casual players."""),
                ('Wild and Triple Wild Symbols', """Two Wild mechanics drive the base game.

The standard Wild symbol substitutes for all regular symbols except the Scatter. Its main purpose is to complete winning combinations.

The more interesting mechanic is the Triple Wild:

<table class="slot-table"><thead><tr><th>Feature</th><th>Effect</th></tr></thead><tbody>
<tr><td>Reel position</td><td>Appears only on reel 3</td></tr>
<tr><td>Multiplier</td><td>Triples any win it contributes to</td></tr>
</tbody></table>

Because the symbol multiplies the final payout, it can turn a moderate win into a significantly larger one."""),
                ('Free Spins Feature', """The primary bonus round is triggered by Scatter symbols.

<table class="slot-table"><thead><tr><th>Scatter Symbols</th><th>Free Spins Awarded</th></tr></thead><tbody>
<tr><td>3 Scatters</td><td>7 Free Spins</td></tr>
<tr><td>4 Scatters</td><td>10 Free Spins</td></tr>
<tr><td>5 Scatters</td><td>14 Free Spins</td></tr>
</tbody></table>

Spins use the same stake and paylines as the triggering spin. Free Spins can retrigger during the feature, and Wild symbols remain active, increasing the chance of larger combinations. The ability to retrigger means the bonus round can extend significantly if Scatters continue to appear."""),
            ],
            'review_summary': """Jack Parow: Heeltyd Speeltyd is an unusual release in the online slot market. Instead of relying on generic themes such as ancient Egypt or mythology, it centres on a recognisable South African cultural figure.

The mechanics are straightforward: 25 paylines, a Triple Wild multiplier, and Free Spins with retriggers. What sets the game apart is the local identity. It clearly targets South African players who recognise Jack Parow's brand and the Cape Town music scene that inspired the slot.

For players looking for a casino game with a distinctly South African feel, Heeltyd Speeltyd delivers something different from the typical international slot catalogue.""",
            'faqs': [
                ('Where can I play Jack Parow Heeltyd Speeltyd?', 'The slot is part of ZARbet\'s Signature Range and is exclusive to ZARbet. It cannot be found at other online casinos.'),
                ('What is the RTP?', 'The return to player rate is 96.15%, which is slightly above the industry average for online slots.'),
                ('What is the Triple Wild?', 'The Triple Wild appears only on reel 3 and triples any win it contributes to. It is the main mechanic for generating larger payouts in the base game.'),
                ('Can Free Spins retrigger?', 'Yes. Additional Scatter symbols during the Free Spins round can retrigger the feature, extending the bonus round.'),
            ],
        },
        {
            'id': 'isibaya-queens',
            'name': 'Isibaya Queens',
            'tagline': 'African heritage high-volatility slot',
            'provider': 'Habanero',
            'image': 'slot-isibaya-queens.jpg',
            'rtp': 'Not yet confirmed',
            'volatility': 'High',
            'reels': '5',
            'rows': '3',
            'paylines': '25',
            'min_bet': 'Varies by casino',
            'max_bet': 'Varies by casino',
            'max_win': '10,151x stake',
            'bonus_features': 'Butterfly Feature, Free Games Choice, Wilds, Buy Feature, Jackpot Race',
            'jackpot': 'Yes (Jackpot Race)',
            'availability': 'ApexBets (rolling out to more SA casinos)',
            'casino_ids': ['apexbets'],
            'author': 'Lerato Dlamini',
            'features': ['Butterfly Feature (expanding reels)', 'Choice-based Free Games with multipliers', 'Wild payouts up to 5,000x stake', 'Jackpot Race progressive prizes', 'Super Bet and Buy Feature'],
            'intro': """African themes occasionally appear in online slots, but few attempt to build a narrative around cultural symbolism and female leadership. Isibaya Queens, developed by Habanero, takes a proper crack at it.

Released on 27 January 2026, the slot combines African-inspired artwork with high-volatility mechanics. The game runs on a traditional five-reel layout but introduces expanding reels, a choice-driven Free Games feature, and a maximum win potential of 10,151x the stake.

Early availability has been limited, with the slot appearing first at operators such as ApexBets while gradually rolling out across other South African casinos.""",
            'body_sections': [
                ('Theme and Cultural Inspiration', """The slot centres on African heritage and leadership, represented through a series of regal female characters appearing on the reels.

Visual elements include:
<ul class="slot-symbol-list">
<li>Colourful African patterns</li>
<li>Regal character portraits</li>
<li>Tribal geometric symbols</li>
<li>The Protea flower, which acts as the Scatter symbol</li>
</ul>

The use of the Protea is particularly notable. As the national flower of South Africa, it adds a distinctly local reference to the game's visual identity. The name Isibaya itself comes from the Zulu language and traditionally refers to a cattle enclosure or communal homestead space associated with heritage and community."""),
                ('Symbols and Paytable', """The highest-paying icons are the four queen portraits. Landing five matching symbols can produce payouts between 300x and 600x stake. These symbols also play a role in triggering the Butterfly Feature.

The remaining icons consist of geometric tribal designs. While smaller in payout, they contribute to wins more frequently.

The Wild substitutes for all regular symbols except the Scatter:

<table class="slot-table"><thead><tr><th>Feature</th><th>Details</th></tr></thead><tbody>
<tr><td>Reel Positions</td><td>Appears on reels 2 and 4</td></tr>
<tr><td>Maximum Wild Win</td><td>5,000x stake</td></tr>
</tbody></table>"""),
                ('Butterfly Feature', """The Butterfly Feature is the slot's primary base-game mechanic.

When three or more premium symbols appear consecutively from the leftmost reel, a butterfly lands on one of the qualifying symbols. That symbol expands to fill the entire reel. Matching symbols can continue expanding across additional reels.

The feature effectively increases the number of active symbol positions, which raises the probability of larger combinations."""),
                ('Free Games Feature', """Once three Protea scatters appear, players enter a choice-based bonus round. They must select one of three Free Game options:

<table class="slot-table"><thead><tr><th>Option</th><th>Free Spins</th><th>Multiplier</th></tr></thead><tbody>
<tr><td>High Risk</td><td>5 spins</td><td>10x multiplier</td></tr>
<tr><td>Balanced</td><td>8 spins</td><td>5x multiplier</td></tr>
<tr><td>Low Risk</td><td>15 spins</td><td>3x multiplier</td></tr>
</tbody></table>

During Free Games, Wild symbols can appear on all reels. Each additional scatter adds +1 extra spin, and all wins are multiplied by the chosen multiplier. This structure allows players to adjust volatility according to their preference."""),
                ('Super Bet, Buy Feature and Jackpot Race', """Activating Super Bet increases the cost of each spin but improves Free Games trigger probability, adjusts Free Games options, and increases Wild frequency during bonus rounds.

Players can also purchase direct entry into the Free Games feature using the Buy Feature, bypassing the base game entirely.

The slot also participates in Habanero's Jackpot Race system. This progressive prize can trigger randomly after any spin, pays independently of symbol combinations, and adds directly to the player's balance."""),
            ],
            'review_summary': """Isibaya Queens is designed as a high-volatility feature-driven slot with strong visual identity.

Its main gameplay highlights include expanding reels via the Butterfly Feature, choice-based Free Games with multipliers, Wild payouts up to 5,000x stake, and Jackpot Race progressive prizes.

While the mechanics are typical of modern video slots, the presentation distinguishes the game by drawing on African cultural themes and symbolism. For players looking for a slot with higher volatility and bonus-focused gameplay, Isibaya Queens offers a feature set that can produce significant payouts during the Free Games round.""",
            'faqs': [
                ('Where can I play Isibaya Queens?', 'At launch, Isibaya Queens has appeared at ApexBets. It is expected to gradually appear across other South African casinos such as Hollywoodbets, Lucky Fish, YesPlay, and Jackpot City.'),
                ('What is the Butterfly Feature?', 'When three or more premium symbols appear from the leftmost reel, a butterfly expands the qualifying symbol to fill the entire reel, increasing win potential.'),
                ('Can I choose my Free Games volatility?', 'Yes. Players select from three options: High Risk (5 spins at 10x), Balanced (8 spins at 5x), or Low Risk (15 spins at 3x).'),
                ('Does Isibaya Queens have a progressive jackpot?', 'Yes. The slot participates in Habanero\'s Jackpot Race system, which can trigger randomly after any spin.'),
            ],
        },
        {
            'id': 'liefde',
            'name': 'Liefde',
            'tagline': 'Liefde by die Dam festival theme',
            'provider': 'ZARbet Signature Range',
            'image': 'slot-liefde.jpg',
            'rtp': '~96%',
            'volatility': 'Medium-High',
            'reels': '5',
            'rows': '3',
            'paylines': '25',
            'min_bet': 'R0.20',
            'max_bet': 'R500',
            'max_win': '7,900 coins',
            'bonus_features': 'Choose the Love Bonus, Free Spins, Expanding Wilds',
            'jackpot': 'No',
            'availability': 'ZARbet exclusive',
            'casino_ids': ['zarbet'],
            'author': 'Lerato Dlamini',
            'features': ['Expanding Wild Yeti symbol', 'Choose the Love interactive bonus', 'Free Spins with expanding wilds', '25 paylines', 'Festival theme'],
            'intro': """Few casino games try to capture the atmosphere of a South African music festival. Liefde attempts exactly that. Developed as part of the Signature Range from ZARbet, the slot draws inspiration from the popular festival Liefde by die Dam.

The theme centres on the relaxed energy of summer concerts. Think picnic blankets, guitars, sunset crowds, and the social atmosphere typical of outdoor music events in Johannesburg or Cape Town. The game translates that mood into a five-reel slot built around Free Spins, expanding wilds, and an interactive bonus feature.

With a maximum win of around 7,900 coins, the game focuses more on entertainment and accessible gameplay than extreme volatility.""",
            'body_sections': [
                ('Theme and Presentation', """Liefde leans heavily into a South African festival aesthetic. The design uses bright colours and playful icons intended to evoke music, friendship, and summer gatherings.

Typical symbols include:
<ul class="slot-symbol-list">
<li>Musical notes</li>
<li>Hearts</li>
<li>Festival-themed icons</li>
<li>Colourful decorative symbols</li>
</ul>

The presentation is deliberately light and cheerful, mirroring the atmosphere associated with the Liefde by die Dam event."""),
                ('Wild Symbol: The Yeti', """One of the more unusual elements in the slot is the Yeti Wild symbol.

During the base game, the Wild substitutes for any symbol except the Scatter and helps complete winning combinations across paylines.

During the Free Spins feature, the Yeti transforms into an Expanding Wild, covering entire reels and increasing the probability of large combinations."""),
                ('Free Spins Feature', """Landing Love Scatter symbols activates the Free Spins bonus round.

<table class="slot-table"><thead><tr><th>Scatter Symbols</th><th>Free Spins Awarded</th></tr></thead><tbody>
<tr><td>3 Symbols</td><td>3 Free Spins</td></tr>
<tr><td>4 Symbols</td><td>6 Free Spins</td></tr>
<tr><td>5 Symbols</td><td>9 Free Spins</td></tr>
</tbody></table>

During the bonus round, the Expanding Wild Yeti becomes active. Entire reels can be covered with wild symbols, and winning combinations can increase significantly when multiple expanding wild reels appear.

The Love Scatter also pays independently:

<table class="slot-table"><thead><tr><th>Scatter Symbols</th><th>Payout</th></tr></thead><tbody>
<tr><td>3 Symbols</td><td>75 coins</td></tr>
<tr><td>4 Symbols</td><td>200 coins</td></tr>
<tr><td>5 Symbols</td><td>1,000 coins</td></tr>
</tbody></table>"""),
                ('Choose the Love Bonus Game', """A distinctive element of the slot is the Choose the Love bonus feature. When triggered, players select from several heart icons on screen. Each heart contains one of the following rewards: additional Free Spins or win multipliers.

The feature introduces a small interactive element that breaks up the standard reel gameplay."""),
            ],
            'review_summary': """Liefde is designed as a feel-good slot rather than a high-volatility powerhouse. The mechanics are familiar, but the theme is deliberately local.

Key elements include a traditional 25-payline slot format, expanding wild reels during Free Spins, scatter payouts and bonus rounds, and an interactive heart-picking bonus game.

The main appeal lies in its South African identity, particularly for players who recognise the music festival that inspired the slot. For players looking for a relaxed, culturally themed slot with straightforward mechanics, Liefde provides a distinctive alternative to the usual international casino catalogue.""",
            'faqs': [
                ('Where can I play Liefde?', 'Liefde is part of the ZARbet Signature Range and is exclusive to ZARbet.'),
                ('What is the Choose the Love feature?', 'An interactive pick-and-reveal bonus where players select heart icons to reveal Free Spins or multipliers.'),
                ('What is the Expanding Wild?', 'During Free Spins, the Yeti Wild symbol expands to cover entire reels, significantly increasing win potential.'),
                ('Are there other games in the ZARbet Signature Range?', 'Yes. The range includes Jack Parow: Heeltyd Speeltyd and Big Game, all built around South African themes.'),
            ],
        },
        {
            'id': 'babalas',
            'name': 'Babalas',
            'tagline': 'SA pub-themed cluster pays slot',
            'provider': 'Game On Studios',
            'image': 'slot-babalas.jpg',
            'rtp': '96.55%',
            'volatility': 'Medium',
            'reels': '6',
            'rows': '5',
            'paylines': 'Pays Anywhere',
            'min_bet': 'R0.20',
            'max_bet': 'R2,400',
            'max_win': '7,150.85x stake',
            'bonus_features': 'Cascades, Multiplier Symbols, Free Spins, Stake Boost, Buy Feature',
            'jackpot': 'No',
            'availability': 'Hollywoodbets, Lucky Fish',
            'casino_ids': ['hollywoodbets', 'lucky-fish'],
            'author': 'Lerato Dlamini',
            'features': ['Cluster pays (8+ symbols anywhere)', 'Cascading wins', 'Multipliers up to 500x', 'Retriggerable Free Spins', 'Stake Boost and Buy Feature'],
            'intro': """Anyone who has experienced a late night celebration in South Africa will recognise the word "babalas." It is the familiar morning-after feeling following a lively night out. The slot Babalas takes that idea and turns it into a colourful pub-themed casino game.

Developed by Game On Studios, the game recreates the atmosphere of a busy local tavern with drinks, neon happy-hour signs, and a light-hearted mascot raising a beer. Behind the playful theme sits a modern slot structure built around cascades, multipliers, and retriggerable Free Spins.

The game is currently available to South African players on platforms such as Hollywoodbets and Lucky Fish.""",
            'body_sections': [
                ('Theme and Presentation', """Babalas is built around the familiar setting of a neighbourhood bar. The reels display drinks, glasses, and pub-style visuals that evoke a relaxed Friday night atmosphere.

Higher-value symbols include:
<ul class="slot-symbol-list">
<li>The Babalas mascot, the top-paying symbol</li>
<li>Beer pints</li>
<li>Wine glasses</li>
<li>Whiskey glasses and premium shots</li>
</ul>

Lower-value icons include cocktails and colourful shooters. The design relies on warm lighting, wood textures, and bright neon signs. The result feels intentionally local, reflecting the social atmosphere of South African taverns rather than the usual casino themes."""),
                ('Gameplay Overview', """The slot runs on a 6x5 grid with a "pays anywhere" system. Instead of fixed paylines, wins are triggered when 8 or more identical symbols appear anywhere on the reels.

Babalas uses a cascading reels mechanic. When a winning combination appears, the winning symbols disappear, remaining symbols drop downward, and new symbols fall into the empty spaces. If the new layout creates another combination, the process repeats. Cascades continue until no new wins appear."""),
                ('Multiplier System', """Multipliers are the main driver of large wins in the game. During both the base game and Free Spins, multiplier symbols can appear randomly on the reels.

Possible values include: 2x, 3x, 4x, 5x, 6x, 8x, 10x, 12x, 15x, 20x, 25x, 50x, 100x, 250x, and up to 500x.

At the end of a cascade sequence, all multipliers visible on the screen are added together and the total win is multiplied by the combined value. This means that multiple multipliers landing during the same cascade chain can significantly increase the final payout."""),
                ('Free Spins Feature', """The main bonus round is triggered by Happy Hour scatter symbols.

<table class="slot-table"><thead><tr><th>Scatter Symbols</th><th>Bonus</th></tr></thead><tbody>
<tr><td>4 Symbols</td><td>15 Free Spins</td></tr>
<tr><td>5 Symbols</td><td>15 Free Spins + higher scatter payout</td></tr>
<tr><td>6 Symbols</td><td>15 Free Spins + maximum scatter payout</td></tr>
</tbody></table>

Retriggering is possible: 3 additional scatters during the feature award 5 extra Free Spins. Multiplier symbols remain active and cascades continue to operate during bonus spins."""),
                ('Stake Boost and Buy Feature', """Two optional mechanics allow players to increase volatility.

<strong>Stake Boost</strong> slightly increases the stake but improves the probability of triggering bonus features.

<table class="slot-table"><thead><tr><th>Mode</th><th>RTP</th></tr></thead><tbody>
<tr><td>Standard Play</td><td>96.55%</td></tr>
<tr><td>Stake Boost</td><td>96.48%</td></tr>
<tr><td>Free Spins Feature</td><td>96.47%</td></tr>
</tbody></table>

Players can also purchase the Free Spins round directly using the <strong>Buy Feature</strong>, gaining immediate access to the 15-spin bonus round."""),
            ],
            'review_summary': """Babalas leans hard into its South African theme. Instead of mythological or fantasy imagery, the game leans into the familiar setting of a neighbourhood pub.

It runs on a 6x5 cluster-pays grid, cascading wins, multipliers up to 500x, and retriggerable Free Spins. With an RTP of 96.55%, the slot sits slightly above the typical industry average.

Players looking for a light-hearted slot with strong multiplier potential will likely find Babalas an entertaining addition to the South African online casino catalogue.""",
            'faqs': [
                ('Where can I play Babalas?', 'Babalas is available at Hollywoodbets and Lucky Fish in South Africa.'),
                ('What does babalas mean?', 'Babalas is South African slang for a hangover. The slot is themed around a pub and the morning-after experience.'),
                ('How do the multipliers work?', 'Multiplier symbols appear randomly and are added together at the end of each cascade sequence. Values can reach up to 500x.'),
                ('Can I buy the Free Spins feature?', 'Yes. The Buy Feature option allows players to purchase immediate access to the 15-spin Free Spins round.'),
            ],
        },
        {
            'id': 'hot-hot-fruit',
            'name': 'Hot Hot Fruit',
            'tagline': 'Classic fruit machine with modern twists',
            'provider': 'Habanero',
            'image': 'slot-hot-hot-fruit.jpg',
            'rtp': '96.84%',
            'volatility': 'Medium',
            'reels': '5',
            'rows': '3',
            'paylines': '15',
            'min_bet': 'R0.40',
            'max_bet': 'Up to R2,000',
            'max_win': 'Varies by combination',
            'bonus_features': 'Hot Hot Feature, Free Spins, Wilds, Double/Triple 7s',
            'jackpot': 'No',
            'availability': 'Hollywoodbets, Supabets, YesPlay, Jackpot City, Lucky Fish',
            'casino_ids': ['hollywoodbets', 'supabets', 'yesplay', 'jackpot-city', 'lucky-fish'],
            'author': 'Lerato Dlamini',
            'features': ['Hot Hot Feature (random symbol upgrades)', 'Locked wilds during Free Spins', 'Double and Triple 7 symbols', '15 fixed paylines', 'Classic fruit machine theme'],
            'intro': """Classic fruit machine slots remain popular for a simple reason. They are easy to understand, fast to play, and built around familiar symbols that have been part of casino culture for decades. Hot Hot Fruit takes that traditional format and adds modern mechanics such as random features and Free Spins.

Developed by Habanero, the slot keeps the classic fruit machine aesthetic while introducing several twists. The game runs on a five-reel layout with traditional symbols like sevens, bars and fruit icons, alongside bonus mechanics that boost win potential.

South African players can find the game at several licensed operators, including Hollywoodbets, Supabets, YesPlay, and Jackpot City.""",
            'body_sections': [
                ('Theme and Design', """Hot Hot Fruit leans heavily into the retro fruit machine theme. The reels feature bright neon colours and symbols commonly associated with classic slot machines.

Typical icons include:
<ul class="slot-symbol-list">
<li>Lucky 7 symbols</li>
<li>Bar symbols</li>
<li>Plums</li>
<li>Oranges</li>
<li>Melons</li>
</ul>

The visual style resembles arcade or television game shows from the 1980s, with glowing colours and simple animations. While the presentation is nostalgic, the slot still uses modern graphics and sound design."""),
                ('Symbols and Special 7s', """The slot includes several standard and special symbols. Classic fruit machine icons dominate the reels, with the Lucky 7 being one of the most valuable.

Some special versions of the symbol can count as multiple icons:

<table class="slot-table"><thead><tr><th>Symbol</th><th>Function</th></tr></thead><tbody>
<tr><td>Double 7</td><td>Counts as two symbols</td></tr>
<tr><td>Triple 7</td><td>Counts as three symbols</td></tr>
</tbody></table>

These symbols increase the probability of completing winning combinations. Two Wild symbols also appear on the reels (standard Wild and Double Wild), substituting for standard symbols on reels 1, 2, 4 and 5."""),
                ('Hot Hot Feature', """The game's defining mechanic is the Hot Hot Feature, which activates randomly during gameplay.

When triggered, certain symbols convert into double symbols, meaning they now count as two matching icons when calculating wins. Lucky 7 symbols can count as three symbols during this feature.

This temporarily increases the probability of forming strong combinations and is the main source of unexpected larger wins in the base game."""),
                ('Free Spins Feature', """Free Spins are triggered when three or more Wild symbols land on the reels.

Players receive 6 Free Spins, and the Wild symbols that triggered the feature remain locked on the reels during the bonus round. These locked wilds increase the likelihood of forming winning combinations on every spin, meaning each bonus spin has the potential to produce larger payouts than the base game."""),
            ],
            'review_summary': """Hot Hot Fruit is a modern update of the classic fruit machine slot. Its strengths include familiar symbols and simple gameplay, a random feature that increases symbol value, locked wilds during Free Spins, and an RTP of 96.84% which sits slightly above the industry average.

The slot is designed for players who prefer straightforward mechanics rather than complex bonus systems. While it does not introduce revolutionary gameplay, it successfully combines nostalgic fruit machine design with modern slot features, making it a reliable option for players who enjoy traditional casino games.""",
            'faqs': [
                ('Where can I play Hot Hot Fruit in South Africa?', 'Hot Hot Fruit is available at Hollywoodbets, Supabets, YesPlay, Jackpot City, and Lucky Fish.'),
                ('What is the Hot Hot Feature?', 'A random feature that converts symbols into double or triple values, increasing the chances of larger winning combinations.'),
                ('What is the RTP?', 'The return to player rate is 96.84%, which is above the industry average.'),
                ('Does Hot Hot Fruit have Free Spins?', 'Yes. Three or more Wild symbols trigger 6 Free Spins with locked wilds on the reels.'),
            ],
        },
    ]

    # ----- Category page -----
    game_cards = ''
    for s in sa_slots:
        game_cards += f"""<a href="{s['id']}.html" class="card" style="padding:0;overflow:hidden;display:flex;flex-direction:column">
          <div style="aspect-ratio:300/229;background:var(--surface-2);overflow:hidden">
            <img src="../assets/{s['image']}" alt="{e(s['name'])}" style="width:100%;height:100%;object-fit:cover" loading="lazy">
          </div>
          <div style="padding:16px;flex:1;display:flex;flex-direction:column">
            <h3 style="font-size:16px;font-weight:700;margin-bottom:4px">{e(s['name'])}</h3>
            <p style="font-size:12px;color:var(--text-muted);margin-bottom:4px">{e(s['provider'])} &middot; RTP: {s['rtp']}</p>
            <p style="font-size:12px;color:var(--text-muted);margin-bottom:8px">Available at: {e(s['availability'])}</p>
            <p style="font-size:13px;color:var(--text-secondary);line-height:1.5;flex:1;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden">{e(s['intro'][:160])}...</p>
            <span style="font-size:13px;color:var(--accent);font-weight:600;margin-top:12px">Read Full Review &rarr;</span>
          </div>
        </a>"""

    hero = category_hero_fn(
        'South African Slots',
        'Locally developed slot games featuring SA culture, from Kaizer Chiefs Megaways to Jack Parow. Reviewed and rated by our team.',
        [{"label": "Home", "href": "../index.html"}, {"label": "Casino", "href": "../casino-sites.html"}, {"label": "SA Slots"}], 1,
        deco_icon='&#x1F3B0;'
    )

    body = f"""
    {hero}
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      <div style="max-width:760px;margin-bottom:32px">
        <p style="font-size:16px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">South African players now have access to slot games built specifically for the local market. These are not reskinned international titles. They feature South African themes, cultural references, and characters that local players recognise.</p>
        <p style="font-size:16px;line-height:1.75;color:var(--text-secondary)">Amakhosi Cash draws on Kaizer Chiefs branding, Jack Parow channels the Cape Town music scene, Babalas leans into pub humour, and Hot Hot Fruit sticks to classic fruit machine mechanics. Our team has reviewed each slot for gameplay quality, bonus mechanics, and where you can play them.</p>
      </div>

      <div class="grid-2" style="margin-bottom:48px">{game_cards}</div>

      <div style="background:var(--card-bg);border:1px solid var(--border);border-radius:12px;padding:24px;max-width:760px;margin-bottom:32px">
        <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Where to Play SA Slots</h2>
        <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">Availability varies by game. Some titles are exclusive to a single operator, while others are available across multiple platforms.</p>
        <table class="slot-table" style="font-size:14px">
          <thead><tr><th style="text-align:left">Game</th><th style="text-align:left">Available At</th></tr></thead>
          <tbody>"""

    for s in sa_slots:
        casino_links = []
        for cid in s['casino_ids']:
            for b in BRANDS:
                if b['id'] == cid:
                    casino_links.append(f'<a href="../betting-site-review/{cid}.html" style="color:var(--accent);text-decoration:none">{e(b["name"])}</a>')
                    break
        body += f"""
            <tr><td><a href="{s['id']}.html" style="color:var(--accent);text-decoration:none;font-weight:600">{e(s['name'])}</a></td><td>{', '.join(casino_links)}</td></tr>"""

    body += """
          </tbody>
        </table>
      </div>

      <div style="background:var(--card-bg);border:1px solid var(--border);border-radius:12px;padding:24px;max-width:760px">
        <h2 style="font-size:18px;font-weight:700;margin-bottom:12px">Why Play South African Slots?</h2>
        <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);margin-bottom:12px">International slot providers create games for a global audience. These SA slots are different. They feature local themes, cultural references, and characters that South African players recognise and connect with.</p>
        <p style="font-size:14px;line-height:1.75;color:var(--text-secondary)">The mechanics are competitive too. Megaways, cluster pays, cascading wins, expanding reels, and multiplier systems are all represented across these titles. Combined with RTPs that sit at or above industry averages, these are not just novelty games. They offer genuine gameplay quality alongside their local identity.</p>
      </div>
    </div>"""

    cat_page = page_fn('South African Slots - SA-Themed Slot Games | MzansiWins',
                       'South African slot game reviews. Amakhosi Cash, Jack Parow, Isibaya Queens, Liefde, Babalas, and Hot Hot Fruit reviewed with gameplay details and where to play.',
                       'sa-slots', body, depth=1, active_nav='casino')
    write_file_fn(f'{OUT}/sa-slots/index.html', cat_page)

    # Build individual slot pages
    for s in sa_slots:
        _build_sa_slot_page(s, sa_slots, page_fn, breadcrumbs_fn, write_file_fn,
                            BRANDS, masked_exit_fn, brand_bg_fn, logo_path_fn,
                            rating_badge_fn, OUT, BASE_URL)

    return [('sa-slots', 0.8)] + [(f'sa-slots/{s["id"]}', 0.7) for s in sa_slots]


def _build_sa_slot_page(slot, all_slots, page_fn, breadcrumbs_fn, write_file_fn,
                         BRANDS, masked_exit_fn, brand_bg_fn, logo_path_fn,
                         rating_badge_fn, OUT, BASE_URL):
    """Build individual SA slot game page with full review content."""
    author_name = slot.get('author', 'Lerato Dlamini')
    author_id = {
        'Thabo Mokoena': 'thabo-mokoena',
        'Lerato Dlamini': 'lerato-dlamini',
        'Sipho Nkosi': 'sipho-nkosi',
        'Naledi Khumalo': 'naledi-khumalo',
    }.get(author_name, 'lerato-dlamini')
    author_photo = {
        'Thabo Mokoena': 'author-thabo-mokoena',
        'Lerato Dlamini': 'author-lerato-dlamini',
        'Sipho Nkosi': 'author-sipho-nkosi',
        'Naledi Khumalo': 'author-naledi-khumalo',
    }.get(author_name, 'author-lerato-dlamini')

    bc = breadcrumbs_fn([
        {"label": "Home", "href": "index.html"},
        {"label": "Casino", "href": "casino-sites.html"},
        {"label": "SA Slots", "href": "sa-slots/index.html"},
        {"label": slot['name']}
    ], 1)

    # Where to play CTA
    casino_ctas = ''
    for cid in slot.get('casino_ids', []):
        for b in BRANDS:
            if b['id'] == cid:
                bg = brand_bg_fn(b)
                lp = logo_path_fn(b, 1)
                bonus = b.get('welcomeBonusAmount', '')
                code = b.get('promoCode', '')
                exit_url = masked_exit_fn(b, 1)
                review_url = f'../betting-site-review/{b["id"]}.html'
                # Determine text colour
                dark_text_brands = ['easybet-south-africa', '10bet-south-africa', 'bettabets', 'playabets', 'yesplay']
                txt = '#111' if cid in dark_text_brands else '#fff'
                code_html = f'<span style="font-size:11px;font-family:monospace;font-weight:700;padding:2px 8px;border-radius:4px;background:rgba(255,255,255,0.2);border:1px dashed rgba(255,255,255,0.4)">{e(code)}</span>' if code and code.lower() not in ('none', 'no code', 'n/a') else ''
                casino_ctas += f"""<a href="{exit_url}" target="_blank" rel="noopener noreferrer nofollow" class="slot-casino-cta" style="background:{bg};color:{txt}">
                  <img src="{lp}" alt="{e(b['name'])}" style="background:{bg}" loading="lazy">
                  <div style="min-width:0;flex:1">
                    <div style="font-size:15px;font-weight:700">{e(b['name'])}</div>
                    <div style="font-size:12px;opacity:0.85">{e(bonus)}</div>
                    {f'<div style="margin-top:3px">{code_html}</div>' if code_html else ''}
                  </div>
                  <span class="slot-cta-btn">Play Now &rarr;</span>
                </a>"""
                break

    cta_section = f"""<div class="slot-where-to-play">
      <h2 style="font-size:18px;font-weight:700;margin-bottom:4px">Where to Play {e(slot['name'])}</h2>
      <p style="font-size:13px;color:var(--text-muted);margin-bottom:16px">{e(slot['availability'])}</p>
      <div style="display:flex;flex-direction:column;gap:10px">{casino_ctas}</div>
      <p style="font-size:11px;color:var(--text-muted);margin-top:12px">18+ | T&amp;Cs apply | Play responsibly</p>
    </div>"""

    # Quick Facts table
    quick_facts = f"""<div class="slot-quick-facts">
      <h2 style="font-size:16px;font-weight:700;margin-bottom:12px">Quick Facts</h2>
      <table class="slot-table slot-table-compact">
        <tbody>
          <tr><td>Provider</td><td><strong>{e(slot['provider'])}</strong></td></tr>
          <tr><td>Availability</td><td><strong>{e(slot['availability'])}</strong></td></tr>
          <tr><td>RTP</td><td><strong>{slot['rtp']}</strong></td></tr>
          <tr><td>Volatility</td><td><strong>{e(slot['volatility'])}</strong></td></tr>
          <tr><td>Reels</td><td><strong>{e(slot['reels'])}</strong></td></tr>
          <tr><td>Rows</td><td><strong>{e(slot['rows'])}</strong></td></tr>
          <tr><td>Paylines / Ways</td><td><strong>{e(slot['paylines'])}</strong></td></tr>
          <tr><td>Min Bet</td><td><strong>{e(slot['min_bet'])}</strong></td></tr>
          <tr><td>Max Bet</td><td><strong>{e(slot['max_bet'])}</strong></td></tr>
          <tr><td>Max Win</td><td><strong>{e(slot['max_win'])}</strong></td></tr>
          <tr><td>Bonus Features</td><td><strong>{e(slot['bonus_features'])}</strong></td></tr>
          <tr><td>Progressive Jackpot</td><td><strong>{e(slot['jackpot'])}</strong></td></tr>
        </tbody>
      </table>
    </div>"""

    # Body sections
    sections_html = ''
    import re as _re
    _p_style = 'font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:14px'
    for title, content in slot.get('body_sections', []):
        # Convert line breaks to paragraphs, preserve HTML tags
        paragraphs = content.strip().split('\n\n')
        section_body = ''
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            if p.startswith('<table') or p.startswith('<ul'):
                section_body += f'<div style="margin:14px 0">{p}</div>'
            elif p.startswith('<strong>'):
                # Sub-header: split <strong>Title</strong> from following text
                m = _re.match(r'(<strong>.*?</strong>)\s*(.*)', p, _re.DOTALL)
                if m:
                    section_body += f'<div class="slot-subheader">{m.group(1)}</div>'
                    rest = m.group(2).strip()
                    if rest:
                        section_body += f'<p style="{_p_style}">{rest}</p>'
                else:
                    section_body += f'<div class="slot-subheader">{p}</div>'
            elif '<ul' in p or '<table' in p:
                # Paragraph contains inline block elements - split text from HTML
                m = _re.split(r'(\n?)(<(?:ul|table)[^>]*>.*)', p, 1, _re.DOTALL)
                if len(m) >= 3:
                    text_before = m[0].strip()
                    block_html = ''.join(m[1:]).strip()
                    if text_before:
                        section_body += f'<p style="{_p_style}">{text_before}</p>'
                    section_body += f'<div style="margin:14px 0">{block_html}</div>'
                else:
                    section_body += f'<p style="{_p_style}">{p}</p>'
            else:
                section_body += f'<p style="{_p_style}">{p}</p>'
        sections_html += f"""
        <h2 class="slot-section-title">{e(title)}</h2>
        {section_body}"""

    # Review summary
    summary_paras = slot.get('review_summary', '').strip().split('\n\n')
    summary_html = ''
    for p in summary_paras:
        p = p.strip()
        if p:
            summary_html += f'<p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:14px">{p}</p>'

    # Related slots
    related = [s2 for s2 in all_slots if s2['id'] != slot['id']]
    related_html = ''
    for r in related:
        related_html += f"""<a href="{r['id']}.html" class="card" style="padding:0;overflow:hidden;display:flex;gap:0">
          <img src="../assets/{r['image']}" alt="{e(r['name'])}" style="width:80px;height:60px;object-fit:cover;flex-shrink:0" loading="lazy">
          <div style="padding:10px 14px;min-width:0">
            <div style="font-size:14px;font-weight:600;margin-bottom:2px">{e(r['name'])}</div>
            <div style="font-size:12px;color:var(--text-muted)">{e(r['provider'])} &middot; RTP: {r['rtp']}</div>
          </div>
        </a>"""

    # FAQ schema
    faq_items = slot.get('faqs', [])
    faq_html = ''
    faq_schema = ''
    if faq_items:
        faq_html = '<h2 class="slot-section-title">Frequently Asked Questions</h2><div class="faq-list">'
        faq_schema_items = []
        for q, a in faq_items:
            faq_html += f"""<details class="faq-item"><summary class="faq-q">{e(q)}</summary><div class="faq-a"><p>{e(a)}</p></div></details>"""
            faq_schema_items.append(f'{{"@type":"Question","name":"{_esc_json(q)}","acceptedAnswer":{{"@type":"Answer","text":"{_esc_json(a)}"}}}}')
        faq_html += '</div>'
        faq_schema = f"""<script type="application/ld+json">{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{','.join(faq_schema_items)}]}}</script>"""

    # Intro paragraphs
    intro_paras = slot.get('intro', '').strip().split('\n\n')
    intro_html = ''
    for p in intro_paras:
        p = p.strip()
        if p:
            intro_html += f'<p class="font-article" style="margin-bottom:14px">{p}</p>'

    # Casino interlinks at bottom
    casino_links_html = ''
    for cid in slot.get('casino_ids', []):
        for b in BRANDS:
            if b['id'] == cid:
                casino_links_html += f' <a href="../betting-site-review/{cid}.html" style="color:var(--accent);font-size:14px;font-weight:600;text-decoration:none;margin-right:16px">{e(b["name"])} Review &rarr;</a>'
                break

    body = f"""
    <div style="background:var(--surface-2);padding:40px 0 32px;border-bottom:1px solid var(--border)">
      <div class="container">
        {bc}
        <div style="display:flex;align-items:flex-start;gap:20px;margin-top:16px;flex-wrap:wrap">
          <img src="../assets/{slot['image']}" alt="{e(slot['name'])}" style="width:120px;border-radius:10px;border:1px solid var(--border)" loading="lazy">
          <div style="flex:1;min-width:200px">
            <h1 style="font-size:clamp(1.5rem, 4vw, 2rem);font-weight:800;letter-spacing:-0.02em">{e(slot['name'])}</h1>
            <p style="font-size:14px;color:var(--text-muted);margin-bottom:8px">{e(slot['provider'])} &middot; RTP: {slot['rtp']} &middot; {e(slot['volatility'])} volatility</p>
            <div class="review-byline-inline" style="margin-top:8px">
              <img src="../assets/{author_photo}.jpg" alt="{e(author_name)}" width="28" height="28" style="width:28px;height:28px;border-radius:50%;object-fit:cover;object-position:center center;vertical-align:middle" loading="lazy">
              Reviewed by <a href="../authors/{author_id}.html" style="color:var(--accent);font-weight:600;text-decoration:none">{e(author_name)}</a> | Last updated: March 2026
            </div>
          </div>
        </div>
      </div>
    </div>
    {faq_schema}
    <div class="container" style="padding-top:32px;padding-bottom:80px">
      <div class="slot-review-layout">
        <div class="slot-review-main">
          {cta_section}

          {intro_html}

          {quick_facts}

          {sections_html}

          <h2 class="slot-section-title">Review Summary</h2>
          {summary_html}

          {faq_html}

          <div style="margin-top:32px;padding-top:20px;border-top:1px solid var(--sep)">
            <h3 style="font-size:15px;font-weight:700;margin-bottom:12px">Read More</h3>
            <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">
              {casino_links_html}
              <a href="index.html" style="color:var(--accent);font-size:14px;font-weight:600;text-decoration:none;margin-right:16px">All SA Slots &rarr;</a>
              <a href="../casino-sites.html" style="color:var(--accent);font-size:14px;font-weight:600;text-decoration:none">Best Casino Sites &rarr;</a>
            </div>
          </div>
        </div>
        <aside class="slot-review-sidebar">
          <h3 style="font-size:15px;font-weight:700;margin-bottom:12px">Other SA Slots</h3>
          <div style="display:flex;flex-direction:column;gap:8px">{related_html}</div>

          <div style="margin-top:24px;padding:16px;background:var(--surface-2);border-radius:10px;border:1px solid var(--border)">
            <h3 style="font-size:14px;font-weight:700;margin-bottom:8px">Related Guides</h3>
            <a href="../casino-guides/online-slots-guide-south-africa.html" style="display:block;font-size:13px;color:var(--accent);text-decoration:none;margin-bottom:6px;font-weight:600">Online Slots Guide SA &rarr;</a>
            <a href="../casino-guides/casino-bonuses-guide-south-africa.html" style="display:block;font-size:13px;color:var(--accent);text-decoration:none;margin-bottom:6px;font-weight:600">Casino Bonuses Guide &rarr;</a>
            <a href="../casino-guides/rtp-and-house-edge-explained.html" style="display:block;font-size:13px;color:var(--accent);text-decoration:none;font-weight:600">RTP &amp; House Edge Explained &rarr;</a>
          </div>
        </aside>
      </div>
    </div>"""

    pg = page_fn(f'{slot["name"]} Slot Review (South Africa) | MzansiWins',
                 f'{slot["name"]} slot review. {slot["provider"]}, RTP {slot["rtp"]}. Where to play in South Africa and full gameplay breakdown.',
                 f'sa-slots/{slot["id"]}', body, depth=1, active_nav='casino')
    write_file_fn(f'{OUT}/sa-slots/{slot["id"]}.html', pg)


def _esc_json(s):
    """Escape string for use in JSON."""
    return str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', '')
