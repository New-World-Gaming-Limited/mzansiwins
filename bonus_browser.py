"""
BonusBrowser page builder for MzansiWins.
Generates a full-screen carousel for rapidly browsing brand bonuses with arrow keys.
"""
import os, json


def build_bonus_browser(BRANDS, OUT, page_fn, logo_path_fn, masked_exit_fn, _esc_json_fn, BASE_URL):
    """Build the BonusBrowser page."""
    brands_js_items = []
    for b in BRANDS:
        logo = logo_path_fn(b, 0)
        m_exit = masked_exit_fn(b, 0)
        has_desktop = os.path.exists(f'{OUT}/assets/screenshots/{b["id"]}-desktop.jpg')
        has_mobile = os.path.exists(f'{OUT}/assets/screenshots/{b["id"]}-mobile.jpg')
        d_img = f'"assets/screenshots/{b["id"]}-desktop.jpg"' if has_desktop else 'null'
        m_img = f'"assets/screenshots/{b["id"]}-mobile.jpg"' if has_mobile else 'null'
        brands_js_items.append(
            '{'
            f'id:"{b["id"]}",'
            f'name:"{_esc_json_fn(b["name"])}",'
            f'rating:{b["overallRating"]},'
            f'bonus:"{_esc_json_fn(b["welcomeBonusAmount"])}",'
            f'promo:"{_esc_json_fn(b.get("promoCode",""))}",'
            f'logo:"{logo}",'
            f'exit:"{m_exit or ""}",'
            f'review:"betting-site-review/{b["id"]}.html",'
            f'promoLink:"promo-code/{b["id"]}.html",'
            f'dImg:{d_img},'
            f'mImg:{m_img},'
            f'type:"{b.get("type","betting")}",'
            f'bg:"{_esc_json_fn(b.get("baseColour","#1641B4"))}"'
            '}'
        )
    brands_json = ',\n    '.join(brands_js_items)
    total = len(BRANDS)

    body = f'''
<div class="bb-wrap" id="bbWrap">
  <div class="bb-counter" id="bbCounter">1 / {total}</div>

  <div class="bb-main">
    <button class="bb-arrow bb-prev" id="bbPrev" aria-label="Previous brand">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
    </button>

    <div class="bb-card" id="bbCard">
      <div class="bb-brand-header" id="bbHeader">
        <img id="bbLogo" alt="" width="48" height="48" style="border-radius:10px;background:var(--surface-2);padding:4px;object-fit:contain">
        <div>
          <h2 id="bbName" style="font-size:22px;font-weight:800;line-height:1.2;margin:0"></h2>
          <div style="display:flex;align-items:center;gap:10px;margin-top:4px">
            <span class="rating-badge" id="bbRating"></span>
            <span id="bbType" style="font-size:11px;font-weight:600;color:var(--text-muted);background:var(--surface-2);padding:2px 8px;border-radius:4px;text-transform:capitalize"></span>
            <span id="bbFeatured" style="font-size:10px;font-weight:600;color:var(--text-muted);background:var(--surface-2);padding:2px 8px;border-radius:4px;display:none">Featured</span>
          </div>
        </div>
      </div>

      <div class="bb-screenshots" id="bbScreenshots">
        <div class="bb-ss-desktop" id="bbDesktopWrap">
          <img id="bbDesktop" alt="Desktop view">
          <span class="bb-ss-label">Desktop</span>
        </div>
        <div class="bb-ss-mobile" id="bbMobileWrap">
          <img id="bbMobile" alt="Mobile view">
          <span class="bb-ss-label">Mobile</span>
        </div>
      </div>

      <div class="bb-cta-area">
        <div class="bb-bonus" id="bbBonus"></div>
        <div class="bb-promo" id="bbPromo" style="display:none">
          <span style="font-size:12px;color:var(--text-muted)">Promo Code:</span>
          <code id="bbPromoCode" style="font-size:15px;font-weight:700;color:var(--accent);background:var(--accent-light);padding:4px 12px;border-radius:6px;letter-spacing:1px"></code>
        </div>
        <div class="bb-actions">
          <a id="bbVisit" href="#" target="_blank" rel="noopener noreferrer nofollow" class="btn-primary" style="border-radius:24px;padding:12px 28px;font-size:15px">Visit Site</a>
          <a id="bbReview" href="#" class="btn-outline" style="border-radius:24px;padding:12px 24px;font-size:14px">Full Review</a>
          <a id="bbPromoPage" href="#" class="btn-outline" style="border-radius:24px;padding:12px 24px;font-size:14px">Promo Details</a>
        </div>
      </div>
    </div>

    <button class="bb-arrow bb-next" id="bbNext" aria-label="Next brand">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>
    </button>
  </div>

  <div class="bb-dots" id="bbDots"></div>

  <div class="bb-keyboard-hint">
    <kbd>&larr;</kbd> <kbd>&rarr;</kbd> arrow keys to browse &nbsp;&middot;&nbsp; swipe on mobile
  </div>
</div>

<script>
(function(){{
  var B=[{brands_json}];
  var i=0,card=document.getElementById('bbCard'),
      FT=['tictacbets','10bet-south-africa','easybet-south-africa'];
  function show(n){{
    if(n<0)n=B.length-1;if(n>=B.length)n=0;i=n;var b=B[i];
    document.getElementById('bbLogo').src=b.logo;
    document.getElementById('bbLogo').alt=b.name;
    document.getElementById('bbLogo').style.background=b.bg;
    document.getElementById('bbName').textContent=b.name;
    var rb=document.getElementById('bbRating');
    rb.textContent=b.rating.toFixed(1)+'/5.0';
    rb.className='rating-badge '+(b.rating>=4.5?'rb-green':b.rating>=4?'rb-amber':'rb-red');
    document.getElementById('bbType').textContent=b.type==='both'?'betting + casino':b.type;
    document.getElementById('bbFeatured').style.display=FT.indexOf(b.id)>=0?'inline-block':'none';
    document.getElementById('bbBonus').textContent=b.bonus;
    if(b.promo){{document.getElementById('bbPromo').style.display='flex';document.getElementById('bbPromoCode').textContent=b.promo;}}
    else{{document.getElementById('bbPromo').style.display='none';}}
    document.getElementById('bbVisit').href=b.exit||'#';
    document.getElementById('bbVisit').style.display=b.exit?'':'none';
    document.getElementById('bbReview').href=b.review;
    document.getElementById('bbPromoPage').href=b.promoLink;
    var dw=document.getElementById('bbDesktopWrap'),mw=document.getElementById('bbMobileWrap');
    if(b.dImg){{dw.style.display='';document.getElementById('bbDesktop').src=b.dImg;}}else{{dw.style.display='none';}}
    if(b.mImg){{mw.style.display='';document.getElementById('bbMobile').src=b.mImg;}}else{{mw.style.display='none';}}
    document.getElementById('bbCounter').textContent=(i+1)+' / '+B.length;
    document.querySelectorAll('.bb-dot').forEach(function(d,di){{d.classList.toggle('active',di===i);}});
    card.style.opacity='0';card.style.transform='translateY(6px)';
    requestAnimationFrame(function(){{requestAnimationFrame(function(){{card.style.opacity='1';card.style.transform='translateY(0)';}});}});
  }}
  var dots=document.getElementById('bbDots');
  for(var d=0;d<B.length;d++){{var dot=document.createElement('button');dot.className='bb-dot'+(d===0?' active':'');
    dot.setAttribute('aria-label',B[d].name);dot.dataset.idx=d;
    dot.onclick=function(){{show(parseInt(this.dataset.idx));}};dots.appendChild(dot);}}
  document.getElementById('bbPrev').onclick=function(){{show(i-1);}};
  document.getElementById('bbNext').onclick=function(){{show(i+1);}};
  document.addEventListener('keydown',function(ev){{
    if(ev.key==='ArrowLeft'||ev.key==='ArrowUp'){{ev.preventDefault();show(i-1);}}
    if(ev.key==='ArrowRight'||ev.key==='ArrowDown'){{ev.preventDefault();show(i+1);}}
  }});
  var sx=0;var w=document.getElementById('bbWrap');
  w.addEventListener('touchstart',function(ev){{sx=ev.touches[0].clientX;}},{{passive:true}});
  w.addEventListener('touchend',function(ev){{var d=ev.changedTouches[0].clientX-sx;if(Math.abs(d)>50){{d>0?show(i-1):show(i+1);}}}});
  show(0);
}})();
</script>
'''

    # Pre-rendered static bonus list for crawlers
    static_cards = ''
    for idx, b in enumerate(BRANDS[:8]):
        logo = logo_path_fn(b, 0)
        logo_img = f'<img src="{logo}" alt="{b["name"]}" style="width:40px;height:40px;object-fit:contain;border-radius:8px;background:{b.get("baseColour","#333")};padding:3px">' if logo else ''
        static_cards += f'''<div style="display:flex;align-items:center;gap:14px;padding:14px 0;border-bottom:1px solid var(--border)">
          <span style="font-weight:700;color:var(--accent);width:24px">{idx+1}</span>
          {logo_img}
          <div style="flex:1">
            <strong><a href="betting-site-review/{b['id']}.html" style="color:var(--text-primary);text-decoration:none">{b['name']}</a></strong>
            <div style="font-size:13px;color:var(--bonus)">{b.get('welcomeBonusAmount','')}</div>
          </div>
          <span style="font-weight:700;font-size:15px">{b.get('overallRating',0):.1f}/5.0</span>
        </div>'''

    body += f'''
    <div style="max-width:700px;margin:40px auto 0">
      <h2 style="font-size:17px;font-weight:700;margin-bottom:12px">Top Bonuses at a Glance</h2>
      <p style="font-size:14px;color:var(--text-secondary);margin-bottom:16px">The highest-rated welcome bonuses from licensed SA bookmakers, ranked by overall score.</p>
      {static_cards}
      <a href="promo-codes.html" style="display:inline-block;margin-top:16px;font-size:14px;color:var(--accent);font-weight:600">View all promo codes &rarr;</a>
    </div>
    '''

    return page_fn(
        'BonusBrowser - Compare SA Betting Bonuses | MzansiWins',
        f'Browse and compare welcome bonuses from {total} licensed South African betting sites. Use arrow keys or swipe to navigate.',
        'bonus-browser',
        body,
        active_nav='betting',
        bc_items=[{'label': 'Home', 'href': 'index.html'}, {'label': 'Betting Sites', 'href': 'betting-sites.html'}, {'label': 'BonusBrowser'}]
    )
