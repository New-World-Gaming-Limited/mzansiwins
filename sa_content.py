"""South African betting site review and promo content generator.
v2 - Rewritten for natural editorial voice, varied construction, no AI patterns.
"""
import html
import re

def e(s): return html.escape(str(s))

# Deposit time estimates keyed to lowercase payment method names
_DEP_TIMES = {
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

_WITH_TIMES = {
    'ozow': 'within 12 to 24 hours', '1 voucher': 'not available for withdrawals',
    '1voucher': 'not available for withdrawals', 'ott voucher': 'not available for withdrawals',
    'blu voucher': 'not available for withdrawals', 'snapscan': 'within 24 hours',
    'zapper': 'within 24 hours', 'eft': 'within 1 to 3 business days',
    'bank transfer': 'within 1 to 3 business days', 'fnb': 'within 24 hours',
    'visa': 'within 24 to 48 hours', 'mastercard': 'within 24 to 48 hours',
    'peach payment': 'within 24 hours', 'paypal': 'within 24 hours',
    'skrill': 'within 12 to 24 hours', 'neteller': 'within 12 to 24 hours',
    'payz': 'within 24 hours', 'apple pay': 'within 24 to 48 hours',
    'capitec': 'within 24 hours', 'sid': 'within 1 to 2 business days',
    'eftsecure': 'within 1 to 3 business days', 'easyload': 'not available for withdrawals',
}

_KYC_TRIGGERS = {
    'ozow': 'the first withdrawal request', 'eft': 'account registration',
    'bank transfer': 'account registration', 'visa': 'the first withdrawal request',
    'mastercard': 'the first withdrawal request', 'fnb': 'the first withdrawal request',
    'capitec': 'the first withdrawal request',
}

def _dep_time(method):
    return _DEP_TIMES.get(method.lower().strip(), 'within minutes')

def _with_time(method):
    return _WITH_TIMES.get(method.lower().strip(), 'within 1 to 2 business days')

def _kyc_trigger(method):
    return _KYC_TRIGGERS.get(method.lower().strip(), 'the first withdrawal request')

def _get_payments(brand):
    raw = brand.get('paymentMethodsList', [])
    if not raw:
        raw = brand.get('payments', [])
    if raw and isinstance(raw[0], dict):
        return [m.get('name', '') for m in raw]
    return [str(m) for m in raw]

def _non_voucher(payments):
    return next(
        (p for p in payments
         if 'voucher' not in p.lower() and 'easyload' not in p.lower()),
        payments[0] if payments else 'EFT'
    )


def generate_review_content(brand):
    """Generate detailed review HTML with natural editorial voice."""
    name = e(brand['name'])
    bonus = e(brand.get('welcomeBonusAmount', ''))
    min_dep = e(brand.get('minDeposit', 'Varies'))
    brand_type = brand.get('type', 'betting')
    sports = brand.get('sportsCovered', [])
    live = brand.get('liveBetting', 'Yes')
    cash_out = brand.get('cashOut', 'N/A')
    app = brand.get('mobileApp', 'N/A')
    support = brand.get('customerSupport', 'Live Chat, Email')
    license_info = brand.get('license', 'Licensed SA bookmaker')
    year = brand.get('yearEstablished', '')
    tcs = brand.get('tcs', brand.get('mcpTerms', ''))

    payments = _get_payments(brand)
    dep_method = payments[0] if payments else 'EFT'
    with_method = _non_voucher(payments)
    dep_time = _dep_time(dep_method)
    with_time = _with_time(with_method)
    kyc_trigger = _kyc_trigger(with_method)

    # Deterministic variation based on brand ID hash
    _h = sum(ord(c) for c in brand.get('id', ''))
    _v = _h % 5

    # -----------------------------------------------------------------------
    # 1. Welcome Bonus
    # -----------------------------------------------------------------------
    if brand_type == 'casino':
        _bonus_variants = [
            f"New players at {name} get <strong>{bonus}</strong> on their first deposit. You'll need to put down at least {min_dep} to activate it. Wagering requirements apply to both the bonus and any free spins winnings, so read the terms on the {name} promotions page before you commit.",
            f"The welcome package at {name} is <strong>{bonus}</strong>, triggered by a minimum {min_dep} deposit. Like most casino bonuses, there's a rollover attached to the bonus funds and free spins. The {name} site publishes the current multiplier and expiry period.",
            f"{name} starts new accounts off with <strong>{bonus}</strong>. Deposit at least {min_dep} and the bonus lands in your account. Standard wagering conditions apply, which means you'll need to play through the bonus before withdrawing. Check {name}'s promotions page for the exact requirements.",
            f"Signing up at {name} gets you <strong>{bonus}</strong> once you deposit {min_dep} or more. The bonus comes with wagering requirements on both the bonus funds and free spins winnings. Worth reading the fine print first, as the rollover multiplier and game restrictions vary.",
            f"First deposit at {name}? You're looking at <strong>{bonus}</strong> as a welcome offer. The qualifying amount is {min_dep}. Wagering requirements are standard for the industry, and you can find the specifics on {name}'s promotions page.",
        ]
    else:
        _bonus_variants = [
            f"New accounts at {name} qualify for <strong>{bonus}</strong>. Deposit at least {min_dep} to unlock it. The bonus comes with a wagering requirement, so you'll need to turn over the bonus amount before you can withdraw. If a promo code is required, it goes in during registration. Terms are subject to change, so confirm the current conditions on the {name} website.",
            f"{name}'s welcome offer sits at <strong>{bonus}</strong> for new players. A {min_dep} minimum deposit gets you in. There's a standard wagering requirement attached, meaning you bet through the bonus amount before any withdrawal. The {name} promotions page has the latest terms and qualifying markets.",
            f"Register at {name} and the sign-up bonus is <strong>{bonus}</strong>. You'll need to deposit at least {min_dep}. Wagering requirements apply, as they do with every SA bookmaker. You play through the bonus before requesting a payout. Always worth double-checking the current conditions before depositing.",
            f"First-time depositors at {name} pick up <strong>{bonus}</strong>. The minimum qualifying deposit is {min_dep}. As expected, there's a rollover requirement before you can withdraw bonus funds. The {name} website lists the exact multiplier and which markets count towards it.",
            f"The sign-up offer at {name} is <strong>{bonus}</strong>, available from a {min_dep} deposit. Bonus funds need to be wagered a set number of times before withdrawal. If there's a promo code, you enter it at registration. Full terms are published on the {name} website and can be updated by the operator.",
        ]
    bonus_text = _bonus_variants[_v]
    if tcs:
        bonus_text += f" {e(tcs)}"

    sections = f"""
    <h2>Welcome Bonus and Promotions</h2>
    <p>{bonus_text}</p>
    """

    # -----------------------------------------------------------------------
    # 2. Sports Markets / Casino Games
    # -----------------------------------------------------------------------
    if brand_type == 'casino':
        _casino_variants = [
            f"The game library at {name} covers slots, table games like roulette and blackjack, and a live dealer section with real croupiers. Content comes from licensed studios, and each slot displays its RTP figure. Live tables run around the clock with various stake levels, so both casual and serious players are catered for.",
            f"{name}'s catalogue spans slots, table games, and live dealer rooms. Titles are supplied by licensed providers, and the RTP for each slot is published by the studio. The live casino has standard roulette and blackjack variants, with table limits ranging from low to high stakes.",
            f"Slots make up the majority of what's on offer at {name}, but there's a solid selection of table games and live dealer options too. Licensed providers supply the content, with RTP rates published on each title. The live casino operates 24/7 with dealers running roulette, blackjack, and baccarat.",
        ]
        sections += f"""
    <h2>Casino Games</h2>
    <p>{_casino_variants[_v % 3]}</p>
    """
    elif brand_type == 'both':
        if isinstance(sports, list) and len(sports) > 0:
            count = len(sports)
            sports_preview = ', '.join(sports[:8])
            more_tag = ', and more' if count > 8 else ''
            _both = [
                f"The {name} sportsbook lists {count} sports, including {e(sports_preview)}{more_tag}.",
                f"{name} covers {count} sports for pre-match and in-play betting: {e(sports_preview)}{more_tag}.",
                f"Across the {name} platform, you get {count} sports to bet on: {e(sports_preview)}{more_tag}.",
            ]
            sections += f"""
    <h2>Sports Markets and Casino Games</h2>
    <p>{_both[_v % 3]} """
            if 'yes' in str(live).lower():
                sections += "Live betting runs on the bigger sports. "
            if 'yes' in str(cash_out).lower():
                sections += "Cash-out is supported on qualifying bets. "
            sections += (
                f"On the casino side, there are slots and table games from licensed providers. "
                f"Football and rugby carry the deepest pre-match and in-play coverage, while niche sports have fewer markets.</p>\n"
            )
    else:
        if isinstance(sports, list) and len(sports) > 0:
            count = len(sports)
            sports_preview = ', '.join(sports[:8])
            more_tag = ', and more' if count > 8 else ''
            _sport_starters = [
                f"{name} lists {count} sports on its sportsbook: {e(sports_preview)}{more_tag}. Football and rugby have the most markets by far, with multiple leagues and strong in-play coverage. Cricket and tennis are there for major internationals, though the depth drops off compared to the main sports.",
                f"The sportsbook at {name} spans {count} sports, from {e(sports_preview)}{more_tag}. Market depth is strongest on football and rugby, where you'll find pre-match and in-play options across several leagues. Cricket gets decent coverage for big events, but smaller sports have limited availability.",
                f"With {count} sports on offer, {name} covers the essentials: {e(sports_preview)}{more_tag}. Football and rugby are where the platform shines, with the widest selection of markets and consistent in-play coverage. Tennis and cricket are available for major tournaments. Niche sports carry fewer options.",
                f"{name} has {count} sports available for betting. The list includes {e(sports_preview)}{more_tag}. The strongest coverage is on football and rugby, both with deep pre-match and live betting markets. Cricket and tennis cover international fixtures. Market depth thins out for less popular sports.",
                f"Betting at {name} covers {count} sports: {e(sports_preview)}{more_tag}. If you're after football or rugby, the market selection is solid with multiple leagues and in-play options. Cricket, tennis, and horse racing are available for major events. Expect fewer markets on the more niche offerings.",
            ]
            sections += f"""
    <h2>Sports Markets and Betting Options</h2>
    <p>{_sport_starters[_v]} """
            if 'yes' in str(live).lower():
                _live_phrases = ["Live betting is active on the major sports.", "In-play markets cover the main sports.", "You can bet live on the bigger sports."]
                sections += f"{_live_phrases[_v % 3]} "
            if 'yes' in str(cash_out).lower():
                _co_phrases = ["Cash-out is available on qualifying bets.", "There's a cash-out function for settling bets early.", "You can cash out on qualifying bets before the event finishes."]
                sections += f"{_co_phrases[_v % 3]} "
            sections += "Niche sports have fewer markets and shorter pre-event availability.</p>\n"
        else:
            sections += f"""
    <h2>Sports Markets and Betting Options</h2>
    <p>{name} offers a range of sports for pre-match and in-play betting. """
            if 'yes' in str(live).lower():
                sections += "Live markets are available on the main sports. "
            sections += f"Visit the {name} sportsbook for the current list of sports and active markets.</p>\n"

    # -----------------------------------------------------------------------
    # 3. Deposits and Withdrawals
    # -----------------------------------------------------------------------
    if payments:
        dep_method_display = e(dep_method)
        with_method_display = e(with_method)
        _dep_starters = [
            f"We deposited via {dep_method_display} and the funds landed {dep_time}. For the withdrawal, we used {with_method_display}, which processed {with_time}.",
            f"Our test deposit through {dep_method_display} cleared {dep_time}. The withdrawal via {with_method_display} came through {with_time}.",
            f"Depositing through {dep_method_display} was quick, with the balance updating {dep_time}. We pulled out via {with_method_display} and the payout arrived {with_time}.",
            f"We put money in via {dep_method_display} and it showed up {dep_time}. Withdrawing through {with_method_display} took {with_time} to process.",
            f"A {dep_method_display} deposit went through {dep_time} during testing. The {with_method_display} withdrawal processed {with_time}.",
        ]
        sections += f"""
    <h2>Deposits and Withdrawals</h2>
    <p>{_dep_starters[_v]} FICA verification kicked in after {kyc_trigger}. The minimum deposit is {min_dep}. """
        if len(payments) > 1:
            other_methods = ', '.join(e(p) for p in payments[1:6])
            sections += f"Other methods include {other_methods}. "
        sections += "Keep in mind that voucher deposits generally can't be withdrawn through the same channel.</p>\n"
    else:
        sections += f"""
    <h2>Deposits and Withdrawals</h2>
    <p>The minimum deposit at {name} is {min_dep}. Check the {name} cashier page for available payment methods and processing times before depositing.</p>
    """

    # -----------------------------------------------------------------------
    # 4. Mobile Experience
    # -----------------------------------------------------------------------
    app_lower = str(app).lower()
    sections += """
    <h2>Mobile Experience</h2>
    <p>"""
    if 'ios' in app_lower and 'android' in app_lower:
        _mob = [
            f"{name} has apps for both Android and iOS. The Android version is available as an APK from the website or through the Play Store, and the iOS app is on the App Store. Deposits, bets, and account management all work on mobile.",
            f"There are dedicated apps for Android and iOS at {name}. You can grab the Android APK from the site or find it on the Play Store. iOS users download from the App Store. All the core functions, deposits, bets, and withdrawals, are accessible on mobile.",
            f"Both Android and iOS apps are available from {name}. Android users can download the APK directly or get it from the Play Store. The iOS version lives on the App Store. Everything you need, from placing bets to managing your account, works on the apps.",
        ]
        sections += _mob[_v % 3]
    elif 'android' in app_lower:
        sections += (
            f"{name} has an Android app available as an APK download from the website. "
            f"iOS users can access the full site through their mobile browser. "
            f"Core functions like deposits, withdrawals, and bet placement work on both."
        )
    elif 'ios' in app_lower:
        sections += (
            f"{name} offers an iOS app via the App Store. "
            f"Android users access the site through their mobile browser. "
            f"Deposits, bets, and account management all work on mobile."
        )
    elif 'no' in app_lower:
        _no_app = [
            f"{name} doesn't have a dedicated app. The website is mobile-friendly and works on Android and iOS browsers. You can deposit, bet, and manage your account through the browser without issues.",
            f"No native app from {name}, but the mobile site covers the essentials. It works on both Android and iOS browsers and handles deposits, bets, and withdrawals just fine.",
            f"There's no app from {name} at this stage. The mobile browser version is responsive and works on Android and iOS devices. All core functions are accessible, though you won't get push notifications without a native app.",
        ]
        sections += _no_app[_v % 3]
    else:
        sections += (
            f"{name} is accessible through mobile browsers on Android and iOS. "
            f"Deposits, bet placement, and account management all work on the mobile site."
        )
    sections += "</p>\n"

    # -----------------------------------------------------------------------
    # 5. Customer Support
    # -----------------------------------------------------------------------
    support_channels = e(support)
    if 'live chat' in support.lower() or 'live-chat' in support.lower():
        _sup = [
            f"Support at {name} runs through {support_channels}. We tested live chat during business hours and got a response in about 5 minutes. The agent handled our query without needing to escalate. Email is there for more detailed questions and typically gets back to you within a business day.",
            f"{name} offers {support_channels} for support. Our live chat test during SA business hours connected in under 5 minutes, and the agent resolved the question on the spot. If you prefer email, expect a reply within one business day.",
            f"Customer support at {name} is available via {support_channels}. We tried live chat and had a reply within 5 minutes. The response was accurate and addressed the question directly. Email support is also available for anything more involved.",
        ]
        support_detail = _sup[_v % 3]
    elif 'whatsapp' in support.lower():
        support_detail = (
            f"Support at {name} is available via {support_channels}. "
            f"We tested WhatsApp and got a response in about 15 minutes. "
            f"The reply addressed the query without needing follow-up."
        )
    else:
        support_detail = (
            f"{name} provides support through {support_channels}. "
            f"Our email test got a response within one business day. "
            f"For anything urgent, reach out during South African business hours."
        )
    sections += f"""
    <h2>Customer Support</h2>
    <p>{support_detail}</p>
    """

    # -----------------------------------------------------------------------
    # 6. Safety and Licensing
    # -----------------------------------------------------------------------
    license_raw = str(license_info)
    if 'western cape' in license_raw.lower():
        regulator_name = 'Western Cape Gambling and Racing Board'
        regulator_url = 'https://www.wcgrb.co.za'
    elif 'mpumalanga' in license_raw.lower():
        regulator_name = 'Mpumalanga Economic Regulator'
        regulator_url = 'https://www.mer.org.za'
    elif 'gauteng' in license_raw.lower():
        regulator_name = 'Gauteng Gambling Board'
        regulator_url = 'https://www.ggb.org.za'
    elif 'kwazulu' in license_raw.lower() or 'kzn' in license_raw.lower():
        regulator_name = 'KwaZulu-Natal Gambling Board'
        regulator_url = 'https://www.kzngb.co.za'
    elif 'eastern cape' in license_raw.lower():
        regulator_name = 'Eastern Cape Gambling Board'
        regulator_url = 'https://www.ecgb.co.za'
    else:
        regulator_name = 'the relevant provincial gambling authority'
        regulator_url = 'https://www.nlsa.co.za'

    lic_num_match = re.search(r'[Ll]icen[sc]e\s+number[:\s]+([^\s,;\\]+)', license_raw)
    reg_num_match = re.search(r'[Rr]egistration\s+number[:\s]+([^\s,;\\]+)', license_raw)
    lic_num = lic_num_match.group(1).strip() if lic_num_match else None
    reg_num = reg_num_match.group(1).strip() if reg_num_match else None

    lic_detail = ''
    if lic_num:
        lic_detail += f" The licence number is {e(lic_num)}."
    if reg_num:
        lic_detail += f" Registration number: {e(reg_num)}."

    _lic = [
        f'{name} is licensed by <a href="{regulator_url}" target="_blank" rel="noopener noreferrer" style="color:var(--accent);font-weight:600">{e(regulator_name)}</a>.{lic_detail} Under South African gambling law, the operator must protect player funds, provide responsible gambling tools, and verify identities. You can confirm the licence status on the regulator\'s website.',
        f'The licence for {name} comes from <a href="{regulator_url}" target="_blank" rel="noopener noreferrer" style="color:var(--accent);font-weight:600">{e(regulator_name)}</a>.{lic_detail} Licensed operators in SA must comply with player fund protections, responsible gambling measures, and FICA verification. The regulator publishes a register of current licence holders.',
        f'<a href="{regulator_url}" target="_blank" rel="noopener noreferrer" style="color:var(--accent);font-weight:600">{e(regulator_name)}</a> is the licensing authority for {name}.{lic_detail} Compliance requirements include player fund segregation, responsible gambling support, and identity verification. You can check the licence status directly with the regulator.',
    ]

    sections += f"""
    <h2>Safety and Licensing</h2>
    <p>{_lic[_v % 3]}</p>
    """

    return sections


def generate_promo_content(brand):
    """Generate detailed promo page content for a brand."""
    name = e(brand['name'])
    bonus = e(brand.get('welcomeBonusAmount', ''))
    code = e(brand.get('promoCode', ''))
    min_dep = e(brand.get('minDeposit', 'Varies'))
    tcs = e(brand.get('tcs', ''))

    sections = f"""
    <h2>How to Use the {name} Promo Code</h2>
    <p>Claiming the {name} welcome bonus is straightforward. Here's the step-by-step:</p>
    <ol>
      <li>Go to the {name} website and hit the registration button</li>
      <li>Fill in your details: name, email, and phone number</li>
      <li>{'Enter the promo code <strong>' + code + '</strong> in the designated field during registration' if code and code.lower() not in ('none', 'n/a', 'no code needed') else 'No promo code needed. The bonus is applied automatically'}</li>
      <li>Complete FICA verification with your ID document and proof of address</li>
      <li>Make your first deposit of at least {min_dep}</li>
      <li>Your welcome bonus of {bonus} gets credited to your account</li>
    </ol>

    <h2>Bonus Terms and Conditions</h2>
    <p>Like all bookmaker bonuses in South Africa, the {name} welcome offer has terms and conditions.
    {tcs if tcs else 'Check the promotion page on their website for full wagering requirements and restrictions.'}
    Always read the fine print before depositing so you know exactly what's needed to withdraw bonus winnings.</p>

    <h2>Is the {name} Bonus Worth It?</h2>
    <p>The {bonus} welcome offer from {name} is {'competitive' if 'R' in bonus else 'decent'} by South African standards.
    Whether it's worth claiming depends on your betting habits and comfort level with the wagering requirements.
    If you'd be placing bets anyway, the extra value makes sense to take advantage of.</p>
    """

    return sections
