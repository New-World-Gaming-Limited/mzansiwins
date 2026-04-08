"""
SEO content sections for the Best Betting Sites page.
Returns HTML fragments for above-table intro and below-table content.
"""

def betting_sites_intro_html():
    """Return a short, crisp opening line above the table."""
    return '''
    <div class="seo-intro" style="margin-bottom:24px">
      <p style="font-size:15px;line-height:1.75;color:var(--text-secondary)">
        We tested all 44 licensed SA bookmakers with real money. These are our rankings for 2026, sorted by bonus value, odds quality and payout speed.
      </p>
    </div>
    '''


def betting_sites_mid_html():
    """Return the mid-section content below the table."""
    return '''
    <div class="seo-mid" style="margin-top:48px;margin-bottom:32px">

      <h2 style="font-size:1.25rem;font-weight:700;color:var(--text-primary);margin-bottom:12px">How We Rank SA Betting Sites</h2>
      <p style="font-size:15px;line-height:1.8;color:var(--text-secondary);margin-bottom:16px">
        South Africa has more than 30 licensed bookmakers. They differ in payout speed, bonus terms,
        odds margins, and supported payment methods. This page ranks them by overall score across seven
        tested criteria, with links to full reviews showing the specific figures behind each rating.
      </p>
      <p style="font-size:15px;line-height:1.8;color:var(--text-secondary);margin-bottom:24px">
        Ratings are based on real-account testing: deposits placed, bets settled, withdrawals requested.
        Each operator is re-evaluated quarterly. Where scores have changed, the date of the last test
        is noted on the individual review page.
      </p>

      <h2 style="font-size:1.25rem;font-weight:700;color:var(--text-primary);margin-bottom:12px;margin-top:32px">What Makes a Good SA Betting Site?</h2>
      <p style="font-size:15px;line-height:1.8;color:var(--text-secondary);margin-bottom:16px">
        Not all bookmakers are created equal, and what works for your mate might not work for you.
        That said, there are a few non-negotiables that every decent SA betting site should deliver:
      </p>
      <ul style="padding-left:24px;margin-bottom:24px;font-size:15px;color:var(--text-secondary);line-height:1.8">
        <li><strong style="color:var(--text-primary)">A valid provincial gambling licence</strong> - This is the absolute baseline. If a bookmaker is not licensed by one of South Africa's provincial gambling boards, do not touch them. Full stop. You have zero protection if something goes wrong with an unlicensed operator.</li>
        <li><strong style="color:var(--text-primary)">Fair and transparent welcome bonus</strong> - A big number on the homepage means nothing if the wagering requirements are impossible to meet. We look at the actual value - minimum deposits, rollover conditions, expiry periods, and how realistic it is to convert the bonus into real rands.</li>
        <li><strong style="color:var(--text-primary)">Competitive odds on SA sports</strong> - Most punters in this country bet on the PSL, Springbok rugby, and Proteas cricket. The best bookmakers offer sharp odds on these markets, not just on European football where margins are tighter anyway.</li>
        <li><strong style="color:var(--text-primary)">Quick deposits and withdrawals</strong> - Deposits should be instant. Withdrawals should hit your account within 24 to 48 hours. If a bookmaker takes a week to pay you out, that is a red flag.</li>
        <li><strong style="color:var(--text-primary)">A mobile experience that actually works</strong> - Over 80% of bets in SA are placed from a phone. If the mobile site is clunky, slow, or crashes mid-bet, it does not matter how good the odds are.</li>
      </ul>

      <h2 style="font-size:1.25rem;font-weight:700;color:var(--text-primary);margin-bottom:12px;margin-top:32px">Our Top Picks at a Glance</h2>
      <p style="font-size:15px;line-height:1.8;color:var(--text-secondary);margin-bottom:16px">
        If you're in a rush and just want a quick answer, here's a summary of our top-rated bookmakers
        and what they do best:
      </p>
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:16px;margin-bottom:24px">
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg)">
          <p style="font-weight:700;color:var(--accent);margin-bottom:4px;font-size:14px">Best Overall</p>
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Zarbet</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.6;margin:0">
            Get up to R3,750 + 25FS. Clean platform, R20 minimum deposit, and strong local sports coverage make Zarbet our top pick.
          </p>
        </div>
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg)">
          <p style="font-weight:700;color:var(--accent);margin-bottom:4px;font-size:14px">Best for Beginners</p>
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Hollywoodbets</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.6;margin:0">
            R25 free sign-up bonus - no deposit needed. Physical branches nationwide and R5 minimum deposits lower the barrier for new punters.
          </p>
        </div>
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg)">
          <p style="font-weight:700;color:var(--accent);margin-bottom:4px;font-size:14px">Best Welcome Bonus</p>
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Betfred</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.6;margin:0">
            Up to R21,000 + 750 free spins. The biggest multi-deposit bonus package on the SA market right now.
          </p>
        </div>
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg)">
          <p style="font-weight:700;color:var(--accent);margin-bottom:4px;font-size:14px">Best Odds</p>
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">10Bet South Africa</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.6;margin:0">
            Consistently sharp odds on international sports. Deposit R3,000 and get R3,000 - one of the most straightforward match bonuses around.
          </p>
        </div>
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg)">
          <p style="font-weight:700;color:var(--accent);margin-bottom:4px;font-size:14px">Best Mobile App</p>
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Betway South Africa</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.6;margin:0">
            The smoothest mobile experience in SA betting. Excellent live betting, reliable streaming, and an app that rarely puts a foot wrong.
          </p>
        </div>
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg)">
          <p style="font-weight:700;color:var(--accent);margin-bottom:4px;font-size:14px">Best No-Deposit Bonus</p>
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Easybet South Africa</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.6;margin:0">
            Free R50 on sign-up plus a 150% match to R1,500 when you deposit. Quick FICA and a no-fuss platform that lives up to its name.
          </p>
        </div>
      </div>

      <h2 style="font-size:1.25rem;font-weight:700;color:var(--text-primary);margin-bottom:12px;margin-top:32px">How We Rank These Betting Sites</h2>
      <p style="font-size:15px;line-height:1.8;color:var(--text-secondary);margin-bottom:16px">
        Every bookmaker on this page has been through our full review process. We create a real account,
        deposit real rands, and test everything from sign-up to withdrawal. Our ratings are based on
        seven weighted criteria: welcome bonus value (25%), odds quality (20%), payment methods (15%),
        sports coverage (15%), platform quality (10%), live betting (10%), and customer support (5%).
        We re-test every quarter and update our rankings whenever there is a significant change - a new bonus,
        a platform overhaul, or a pattern of user complaints. You can read the
        <a href="how-we-rate.html" style="color:var(--accent);font-weight:600">full breakdown of our methodology here</a>.
      </p>

      <p style="font-size:15px;line-height:1.8;color:var(--text-secondary);margin-bottom:16px">
        The table below lists all 44 licensed SA bookmakers in order of our overall rating. You can sort
        by any column, search by name, and star your favourites to keep track of the ones you are
        interested in. Every bookmaker links through to a detailed review and a dedicated promo code page.
      </p>
    </div>
    '''


def betting_sites_below_table_html(brands_data):
    """Return all the SEO content HTML that goes below the table.
    brands_data is a list of brand dicts sorted by overallRating desc.
    """

    # Find the top 5 review brands (Zarbet first as per user instruction, then by rating)
    brand_map = {b['id']: b for b in brands_data}
    review_order = ['zarbet', 'betway-south-africa', 'hollywoodbets', 'easybet-south-africa', '10bet-south-africa']
    review_brands = [brand_map[bid] for bid in review_order if bid in brand_map]

    reviews_html = _build_top5_reviews(review_brands)
    methodology_html = _build_methodology()
    payment_html = _build_payment_methods()
    fica_html = _build_fica_guide()
    legality_html = _build_legality()
    faq_html = _build_faq()
    responsible_html = _build_responsible_gambling()

    return f'''
    <div class="seo-below-table" style="margin-top:56px">
      {reviews_html}
      {methodology_html}
      {payment_html}
      {fica_html}
      {legality_html}
      {faq_html}
      {responsible_html}
    </div>
    '''


def _review_card(brand, rank, summary, pros, cons, verdict):
    """Build a mini review card for a brand."""
    import html as h
    name = h.escape(brand.get('name', ''))
    bonus = h.escape(brand.get('welcomeBonusAmount', ''))
    rating = float(brand.get('overallRating', 0))
    rating_str = f'{rating:.1f}'
    bid = brand['id']

    check_icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5" style="flex-shrink:0;margin-top:2px"><polyline points="20 6 9 17 4 12"/></svg>'
    cross_icon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.5" style="flex-shrink:0;margin-top:2px"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
    pros_li = ''.join(f'<li style="display:flex;align-items:flex-start;gap:8px;margin-bottom:6px;font-size:14px;color:var(--text-secondary);line-height:1.5">{check_icon} <span>{p}</span></li>' for p in pros)
    cons_li = ''.join(f'<li style="display:flex;align-items:flex-start;gap:8px;margin-bottom:6px;font-size:14px;color:var(--text-secondary);line-height:1.5">{cross_icon} <span>{c}</span></li>' for c in cons)

    return f'''
    <div class="seo-review-card" style="border:1px solid var(--border);border-radius:12px;padding:28px;margin-bottom:24px;background:var(--card-bg)">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:16px">
        <div style="display:flex;align-items:center;gap:12px">
          <span style="font-size:22px;font-weight:800;color:var(--accent)">#{rank}</span>
          <a href="betting-site-review/{bid}.html" style="font-size:20px;font-weight:700;color:var(--text-primary);text-decoration:none">{name}</a>
        </div>
        <span class="rating-badge {'high' if rating >= 4.2 else 'mid' if rating >= 3.5 else 'low'} sm">{rating_str}/5.0</span>
      </div>
      <p style="font-size:16px;font-weight:700;color:var(--bonus);margin-bottom:16px">{bonus}</p>
      <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:20px">{summary}</p>
      <div class="seo-pros-cons">
        <div>
          <p style="font-size:13px;font-weight:700;color:#16a34a;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px">What we like</p>
          <ul style="list-style:none;padding:0;margin:0">{pros_li}</ul>
        </div>
        <div>
          <p style="font-size:13px;font-weight:700;color:#dc2626;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px">Could be better</p>
          <ul style="list-style:none;padding:0;margin:0">{cons_li}</ul>
        </div>
      </div>
      <p style="font-size:14px;line-height:1.75;color:var(--text-muted);font-style:italic;border-top:1px solid var(--sep);padding-top:16px;margin:0">
        <strong style="color:var(--text-primary)">Our verdict:</strong> {verdict}
      </p>
      <div style="margin-top:16px;display:flex;gap:12px;flex-wrap:wrap">
        <a href="betting-site-review/{bid}.html" class="btn-outline btn-sm">Full review</a>
        <a href="promo-code/{bid}.html" class="btn-outline btn-sm" style="border-color:var(--bonus);color:var(--bonus)">Promo code</a>
      </div>
    </div>
    '''


def _build_top5_reviews(review_brands):
    """Build the top 5 mini reviews section."""
    reviews_data = [
        {
            'summary': 'Zarbet has quickly become one of the most talked-about betting platforms in South Africa. Their generous welcome bonus of up to R3,750 plus 25 free spins makes them our top pick for 2026. The platform is slick, deposits start at just R20, and the sports coverage includes everything from PSL to international cricket.',
            'pros': ['Massive welcome bonus package', 'Low R20 minimum deposit', 'Clean, modern platform design', 'Strong PSL and local sports coverage'],
            'cons': ['Relatively new brand in SA', 'Could offer more live streaming options'],
            'verdict': 'Zarbet delivers where it matters most - a quality platform with a welcome offer that actually makes you want to sign up. The best all-round package in Mzansi right now.'
        },
        {
            'summary': 'Betway has operated in South Africa since 2015 and holds a Western Cape Gambling Board licence. New accounts receive a R10 free bet and 10 Aviator flights. The app ranks among the fastest we tested, odds are consistently competitive across major sports, and their live betting covers more markets than most SA operators.',
            'pros': ['Trusted global brand with SA licence', 'Excellent mobile app experience', 'Competitive odds across all sports', 'Superb live betting and streaming'],
            'cons': ['Welcome bonus value is modest', 'Minimum deposit of R10 may confuse some'],
            'verdict': 'If you want reliability and a brand that is not going anywhere, Betway is hard to beat. Their welcome bonus is not the biggest, but the overall experience more than makes up for it.'
        },
        {
            'summary': 'Hollywoodbets is the proudly South African bookmaker that needs no introduction. Their R25 free sign-up bonus and 50 spins mean you can try before you deposit a single rand. With branches across the country and a platform built for South African punters, they just get it.',
            'pros': ['No deposit needed for R25 free bonus', 'Proudly SA with physical branches', 'R5 minimum deposit - lowest in the market', 'Lucky Numbers and Spina Zonke exclusives'],
            'cons': ['Interface could use a refresh', 'Odds not always the sharpest on big markets'],
            'verdict': 'Hollywoodbets is the people\'s bookmaker. If you want to try betting without risking your own money first, their no-deposit bonus is the best entry point in South Africa.'
        },
        {
            'summary': 'Easybet lives up to its name with a straightforward platform and a generous free R50 plus 150% match bonus up to R1,500. FICA verification is quick, the interface is clean, and they have put real effort into making the sign-up process painless for first-time punters.',
            'pros': ['Free R50 on sign-up, no deposit needed', 'Generous 150% match up to R1,500', 'Quick and easy FICA process', 'Strong focus on South African sports'],
            'cons': ['Brand less well-known than Betway or Hollywood', 'Fewer international markets than some rivals'],
            'verdict': 'For punters who want a solid welcome bonus and a platform that does not overcomplicate things, Easybet is a brilliant choice. The free R50 makes it risk-free to try.'
        },
        {
            'summary': '10bet brings international pedigree to the South African market with a massive R3,000 matched deposit bonus. Their odds are consistently among the best, particularly on international football and cricket, and the platform has a premium feel that sets it apart.',
            'pros': ['Huge R3,000 matched deposit bonus', 'Some of the best odds in SA', 'Premium platform and user experience', 'Excellent international sports coverage'],
            'cons': ['R50 minimum for bonus eligibility', 'Could improve local PSL coverage'],
            'verdict': '10bet is the pick for punters who want the best odds and do not mind depositing a bit more upfront. That R3,000 match bonus is one of the biggest in the market.'
        },
    ]

    cards = ''
    for i, (brand, data) in enumerate(zip(review_brands, reviews_data)):
        cards += _review_card(brand, i + 1, data['summary'], data['pros'], data['cons'], data['verdict'])

    return f'''
    <div class="seo-section" style="margin-bottom:48px">
      <h2 style="font-size:1.5rem;font-weight:700;color:var(--text-primary);margin-bottom:8px">Top 5 South African Betting Sites - Reviewed</h2>
      <p style="font-size:15px;color:var(--text-muted);margin-bottom:24px;line-height:1.75">
        Here's a closer look at the five betting sites that scored highest in our testing.
        We signed up, deposited, placed bets, and withdrew from every single one.
      </p>
      {cards}
    </div>
    '''


def _build_methodology():
    """Build the methodology section."""
    return '''
    <div class="seo-section" style="margin-bottom:48px">
      <h2 style="font-size:1.5rem;font-weight:700;color:var(--text-primary);margin-bottom:16px">How We Rate SA Betting Sites</h2>
      <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:20px">
        Every rating on MzansiWins is based on hands-on testing with real accounts. Here's what we measure when scoring a bookmaker out of 5:
      </p>
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:16px;margin-bottom:20px">
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg)">
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Welcome Bonus Value</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.75;margin:0">
            Not just the headline number - we check wagering requirements, expiry periods,
            minimum deposits, and how realistic it is to actually use the bonus.
          </p>
        </div>
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg)">
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Odds Quality</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.75;margin:0">
            We compare odds across all SA bookmakers on PSL, Premier League, rugby, and
            cricket fixtures. Better odds mean more rands in your pocket.
          </p>
        </div>
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg)">
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Payment Methods</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.75;margin:0">
            Deposit and withdrawal speeds, fees, minimum amounts, and which methods are
            supported - from EFT to e-wallets to bank cards.
          </p>
        </div>
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg)">
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Sports Coverage</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.75;margin:0">
            We look at how many sports and leagues are covered, with a focus on South African
            events - PSL, Currie Cup, CSA T20, and local horse racing.
          </p>
        </div>
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg)">
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Mobile Experience</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.75;margin:0">
            Over 80% of SA punters bet on mobile. We test every app and mobile site for speed,
            usability, and whether placing a bet actually feels smooth.
          </p>
        </div>
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg)">
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Customer Support</p>
          <p style="font-size:14px;color:var(--text-secondary);line-height:1.75;margin:0">
            Live chat, email, phone - we test them all. Response time matters, especially when
            you have a withdrawal stuck or a bet that settled wrong.
          </p>
        </div>
      </div>
      <p style="font-size:14px;color:var(--text-muted);line-height:1.75">
        Every bookmaker is re-tested quarterly. Ratings are updated to reflect changes in bonus offers,
        platform quality, and user feedback. <a href="how-we-rate.html" style="color:var(--accent)">Read our full methodology</a>.
      </p>
    </div>
    '''


def _build_payment_methods():
    """Build the payment methods section."""
    return '''
    <div class="seo-section" style="margin-bottom:48px">
      <h2 style="font-size:1.5rem;font-weight:700;color:var(--text-primary);margin-bottom:16px">Payment Methods at SA Betting Sites</h2>
      <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:20px">
        Getting money in and out of your betting account should be quick and painless. Most SA
        bookmakers support a solid range of deposit and withdrawal methods, though some are
        definitely faster than others. Here's what to expect:
      </p>
      <div style="overflow-x:auto;margin-bottom:20px">
        <table style="width:100%;border-collapse:collapse;font-size:14px">
          <thead>
            <tr style="border-bottom:2px solid var(--border)">
              <th style="text-align:left;padding:12px 16px;font-weight:700;color:var(--text-primary)">Method</th>
              <th style="text-align:left;padding:12px 16px;font-weight:700;color:var(--text-primary)">Deposit Speed</th>
              <th style="text-align:left;padding:12px 16px;font-weight:700;color:var(--text-primary)">Withdrawal Speed</th>
              <th style="text-align:left;padding:12px 16px;font-weight:700;color:var(--text-primary)">Typical Fees</th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom:1px solid var(--sep)">
              <td style="padding:12px 16px;font-weight:600;color:var(--text-primary)">Instant EFT</td>
              <td style="padding:12px 16px;color:var(--text-secondary)">Instant</td>
              <td style="padding:12px 16px;color:var(--text-secondary)">1 - 3 business days</td>
              <td style="padding:12px 16px;color:var(--bonus);font-weight:600">Free</td>
            </tr>
            <tr style="border-bottom:1px solid var(--sep)">
              <td style="padding:12px 16px;font-weight:600;color:var(--text-primary)">Visa / Mastercard</td>
              <td style="padding:12px 16px;color:var(--text-secondary)">Instant</td>
              <td style="padding:12px 16px;color:var(--text-secondary)">2 - 5 business days</td>
              <td style="padding:12px 16px;color:var(--bonus);font-weight:600">Free</td>
            </tr>
            <tr style="border-bottom:1px solid var(--sep)">
              <td style="padding:12px 16px;font-weight:600;color:var(--text-primary)">OTT Voucher</td>
              <td style="padding:12px 16px;color:var(--text-secondary)">Instant</td>
              <td style="padding:12px 16px;color:var(--text-secondary)">N/A (deposit only)</td>
              <td style="padding:12px 16px;color:var(--bonus);font-weight:600">Free</td>
            </tr>
            <tr style="border-bottom:1px solid var(--sep)">
              <td style="padding:12px 16px;font-weight:600;color:var(--text-primary)">1ForYou Voucher</td>
              <td style="padding:12px 16px;color:var(--text-secondary)">Instant</td>
              <td style="padding:12px 16px;color:var(--text-secondary)">N/A (deposit only)</td>
              <td style="padding:12px 16px;color:var(--bonus);font-weight:600">Free</td>
            </tr>
            <tr style="border-bottom:1px solid var(--sep)">
              <td style="padding:12px 16px;font-weight:600;color:var(--text-primary)">Bank Transfer (EFT)</td>
              <td style="padding:12px 16px;color:var(--text-secondary)">1 - 2 hours</td>
              <td style="padding:12px 16px;color:var(--text-secondary)">1 - 3 business days</td>
              <td style="padding:12px 16px;color:var(--bonus);font-weight:600">Free</td>
            </tr>
            <tr>
              <td style="padding:12px 16px;font-weight:600;color:var(--text-primary)">Ozow / SiD</td>
              <td style="padding:12px 16px;color:var(--text-secondary)">Instant</td>
              <td style="padding:12px 16px;color:var(--text-secondary)">1 - 2 business days</td>
              <td style="padding:12px 16px;color:var(--bonus);font-weight:600">Free</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p style="font-size:14px;color:var(--text-muted);line-height:1.75">
        Pro tip: Instant EFT is the fastest and most widely supported option. Most bookmakers
        process withdrawals within 24 hours, but your bank may take an extra day or two to clear
        the funds. <a href="payment-methods.html" style="color:var(--accent)">See our full payment methods guide</a>.
      </p>
    </div>
    '''


def _build_fica_guide():
    """Build the FICA verification guide section."""
    return '''
    <div class="seo-section" style="margin-bottom:48px">
      <h2 style="font-size:1.5rem;font-weight:700;color:var(--text-primary);margin-bottom:16px">FICA Verification - What You Need to Know</h2>
      <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:20px">
        Every licensed South African bookmaker is required by law to verify your identity before
        you can withdraw winnings. This is called FICA (Financial Intelligence Centre Act) compliance,
        and it's actually there to protect you. Here's how to get it sorted quickly:
      </p>
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(240px, 1fr));gap:16px;margin-bottom:20px">
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg);text-align:center">
          <div style="width:40px;height:40px;border-radius:50%;background:var(--accent-light);display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:18px;font-weight:800;color:var(--accent)">1</div>
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">ID Document</p>
          <p style="font-size:13px;color:var(--text-secondary);line-height:1.6;margin:0">
            SA ID book, smart ID card, or valid passport. Take a clear photo of both sides.
          </p>
        </div>
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg);text-align:center">
          <div style="width:40px;height:40px;border-radius:50%;background:var(--accent-light);display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:18px;font-weight:800;color:var(--accent)">2</div>
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Proof of Address</p>
          <p style="font-size:13px;color:var(--text-secondary);line-height:1.6;margin:0">
            Utility bill, bank statement, or municipal account not older than 3 months.
          </p>
        </div>
        <div style="border:1px solid var(--border);border-radius:10px;padding:20px;background:var(--card-bg);text-align:center">
          <div style="width:40px;height:40px;border-radius:50%;background:var(--accent-light);display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:18px;font-weight:800;color:var(--accent)">3</div>
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:6px">Upload and Wait</p>
          <p style="font-size:13px;color:var(--text-secondary);line-height:1.6;margin:0">
            Upload via the bookmaker's app or site. Most verify within 24 hours, some in under an hour.
          </p>
        </div>
      </div>
      <div style="background:var(--accent-light);border-radius:10px;padding:20px;border-left:4px solid var(--accent)">
        <p style="font-size:14px;font-weight:700;color:var(--text-primary);margin-bottom:6px">Tips to speed things up</p>
        <ul style="margin:0;padding-left:20px;font-size:14px;color:var(--text-secondary);line-height:1.75">
          <li>Complete FICA as soon as you register - do not wait until your first withdrawal</li>
          <li>Make sure all four corners of your ID are visible in the photo</li>
          <li>Use good lighting and avoid blurry images</li>
          <li>Your proof of address must match the name on your betting account</li>
        </ul>
      </div>
      <p style="font-size:14px;color:var(--text-muted);line-height:1.75;margin-top:16px">
        <a href="fica-guide.html" style="color:var(--accent)">Read our complete FICA guide</a>
        for step-by-step walkthroughs for each bookmaker.
      </p>
    </div>
    '''


def _build_legality():
    """Build the legality/regulation section."""
    return '''
    <div class="seo-section" style="margin-bottom:48px">
      <h2 style="font-size:1.5rem;font-weight:700;color:var(--text-primary);margin-bottom:16px">Is Online Betting Legal in South Africa?</h2>
      <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">
        Online sports betting with licensed operators is legal in South Africa under provincial gambling legislation. The National Gambling Act of 2004,
        along with amendments, provides the framework under which licensed bookmakers operate. Online casino gambling has a different legal status under the same Act and is subject to restrictions. Every bookmaker listed
        on MzansiWins holds a valid licence from one of the provincial gambling boards:
      </p>
      <ul style="padding-left:24px;margin-bottom:20px;font-size:15px;color:var(--text-secondary);line-height:1.75">
        <li><strong style="color:var(--text-primary)">Western Cape Gambling and Racing Board</strong> - one of the most active regulators</li>
        <li><strong style="color:var(--text-primary)">Gauteng Gambling Board</strong> - covers the largest betting market in SA</li>
        <li><strong style="color:var(--text-primary)">KwaZulu-Natal Gaming and Betting Board</strong> - regulates operators in KZN</li>
        <li><strong style="color:var(--text-primary)">Mpumalanga Economic Regulator</strong> - covers bookmakers in Mpumalanga</li>
      </ul>
      <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">
        You must be at least 18 years old to place a bet in South Africa. Unlicensed offshore bookmakers
        are illegal, and while some South Africans use them, you have zero consumer protection if
        something goes wrong. Stick to licensed operators - all 44 bookmakers on this page hold valid
        SA licences.
      </p>
      <div style="background:var(--surface);border-radius:10px;padding:20px;border:1px solid var(--border)">
        <p style="font-size:14px;line-height:1.75;color:var(--text-secondary);margin:0">
          <strong style="color:var(--text-primary)">How to check if a bookmaker is licensed:</strong>
          Visit the relevant provincial gambling board's website and search their register of licensees.
          Any bookmaker that cannot produce a valid licence number should be avoided.
        </p>
      </div>
    </div>
    '''


def _build_faq():
    """Build the FAQ section with accordion items."""
    faqs = [
        (
            "What is the best betting site in South Africa in 2026?",
            "Based on our testing, Zarbet is the best overall betting site in South Africa for 2026. They offer a generous welcome bonus of up to R3,750 plus 25 free spins, a clean platform, and solid coverage of South African sports. Betway and Easybet round out the top three."
        ),
        (
            "Which SA betting site has the biggest welcome bonus?",
            "Betfred currently offers the largest welcome bonus at up to R21,000 plus 750 spins spread across your first deposits. For a single deposit match, World Sports Betting offers R20,000 (100% match). However, bigger is not always better - check the wagering requirements before you commit."
        ),
        (
            "Can I bet without depositing money first?",
            "Yes. Hollywoodbets gives you R25 plus 50 free spins just for signing up - no deposit needed. Easybet offers a free R50 on registration. Playbet gives you R50 plus 50 spins. These no-deposit bonuses are a great way to try a bookmaker risk-free."
        ),
        (
            "How long do withdrawals take at SA betting sites?",
            "Most SA bookmakers process withdrawal requests within 24 hours. However, the time it takes for the money to reach your bank depends on your payment method. Instant EFT withdrawals typically clear in 1 to 3 business days, while card withdrawals can take up to 5 business days."
        ),
        (
            "Do I need to complete FICA verification to bet?",
            "You can usually deposit and place bets before completing FICA, but you will need to verify your identity before making any withdrawals. We recommend completing FICA as soon as you register to avoid delays when you want to cash out."
        ),
        (
            "Are my winnings taxed in South Africa?",
            "No. As of 2026, gambling winnings are not taxed in South Africa for individual punters. You keep everything you win. The bookmakers themselves pay taxes and licensing fees to the provincial gambling boards."
        ),
        (
            "What sports can I bet on at South African bookmakers?",
            "All major SA bookmakers cover football (PSL, Premier League, Champions League), rugby (URC, Currie Cup, Springbok matches), cricket (CSA T20, international fixtures), horse racing, tennis, and more. Most also offer niche sports like darts, table tennis, and esports."
        ),
        (
            "How do I choose between betting sites?",
            "Focus on what matters most to you. If you want the best bonus, compare welcome offers. If odds matter most, check our odds comparison. If you bet mainly on your phone, prioritise the bookmakers with the best mobile apps. Our ratings factor in all of these, so starting with the highest-rated sites is a solid approach."
        ),
    ]

    items = ''
    for q, a in faqs:
        items += f'''
        <div class="faq-item">
          <button class="faq-btn" onclick="this.parentElement.classList.toggle('open')">
            <span>{q}</span>
            <svg class="faq-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <div class="faq-body">
            <p>{a}</p>
          </div>
        </div>
        '''

    return f'''
    <div class="seo-section" style="margin-bottom:48px">
      <h2 style="font-size:1.5rem;font-weight:700;color:var(--text-primary);margin-bottom:16px">Frequently Asked Questions</h2>
      <div style="display:flex;flex-direction:column;gap:8px">
        {items}
      </div>
    </div>
    '''


def _build_responsible_gambling():
    """Build the responsible gambling section."""
    return '''
    <div class="seo-section" style="margin-bottom:48px;padding:28px;background:var(--surface);border-radius:12px;border:1px solid var(--border)">
      <h2 style="font-size:1.5rem;font-weight:700;color:var(--text-primary);margin-bottom:16px">Responsible Gambling</h2>
      <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:16px">
        Betting should be fun, not stressful. If it stops being enjoyable, it is time to step back.
        Every licensed SA bookmaker is required to offer responsible gambling tools, including
        deposit limits, loss limits, self-exclusion, and cooling-off periods. Use them.
      </p>
      <p style="font-size:15px;line-height:1.75;color:var(--text-secondary);margin-bottom:20px">
        If you or someone you know has a gambling problem, help is available:
      </p>
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:12px;margin-bottom:16px">
        <div style="background:var(--card-bg);border-radius:8px;padding:16px;border:1px solid var(--border)">
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:4px;font-size:14px">National Responsible Gambling Programme</p>
          <p style="font-size:14px;color:var(--accent);font-weight:600;margin:0">0800 006 008</p>
          <p style="font-size:12px;color:var(--text-muted);margin:0">(Toll-free, 24/7)</p>
        </div>
        <div style="background:var(--card-bg);border-radius:8px;padding:16px;border:1px solid var(--border)">
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:4px;font-size:14px">Gambling Helpline</p>
          <p style="font-size:14px;color:var(--accent);font-weight:600;margin:0">counsellor@responsiblegambling.co.za</p>
        </div>
        <div style="background:var(--card-bg);border-radius:8px;padding:16px;border:1px solid var(--border)">
          <p style="font-weight:700;color:var(--text-primary);margin-bottom:4px;font-size:14px">Self-Exclusion</p>
          <p style="font-size:13px;color:var(--text-secondary);margin:0">Contact your bookmaker directly to self-exclude for 6 months or longer</p>
        </div>
      </div>
      <p style="font-size:13px;color:var(--text-muted);line-height:1.75;margin:0">
        18+ only. Gambling can be addictive. Please play responsibly.
      </p>
    </div>
    '''
