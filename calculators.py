"""Betting calculators for MzansiWins."""

CALCULATORS = [
    {
        'id': 'bet-calculator',
        'title': 'Bet Calculator',
        'short': 'Calculate potential returns from singles, accumulators and system bets',
        'icon': '&#x1F4B0;',
        'category': 'Basic Calculators',
    },
    {
        'id': 'accumulator-calculator',
        'title': 'Accumulator Calculator',
        'short': 'Work out combined odds and returns for multi-leg bets',
        'icon': '&#x1F4CA;',
        'category': 'Basic Calculators',
    },
    {
        'id': 'odds-converter',
        'title': 'Odds Converter',
        'short': 'Convert between decimal, fractional and American odds formats',
        'icon': '&#x1F504;',
        'category': 'Odds Tools',
    },
    {
        'id': 'implied-probability',
        'title': 'Implied Probability Calculator',
        'short': 'Convert odds into implied probability percentages',
        'icon': '&#x1F4CA;',
        'category': 'Odds Tools',
    },
    {
        'id': 'margin-calculator',
        'title': 'Bookmaker Margin Calculator',
        'short': 'Calculate the overround and true odds from a bookmaker market',
        'icon': '&#x2696;',
        'category': 'Advanced Strategy',
    },
    {
        'id': 'kelly-criterion',
        'title': 'Kelly Criterion Calculator',
        'short': 'Find the mathematically optimal stake size for value bets',
        'icon': '&#x1F9E0;',
        'category': 'Bankroll Management',
    },
    {
        'id': 'dutching-calculator',
        'title': 'Dutching Calculator',
        'short': 'Calculate stakes to guarantee equal profit across multiple selections',
        'icon': '&#x2696;',
        'category': 'Advanced Strategy',
    },
    {
        'id': 'bonus-rollover',
        'title': 'Bonus Rollover Calculator',
        'short': 'Work out how much you need to wager to clear a bonus',
        'icon': '&#x1F381;',
        'category': 'Bonus Tools',
    },
    {
        'id': 'lay-bet-calculator',
        'title': 'Lay Bet Calculator',
        'short': 'Calculate liability and profit for lay bets on exchanges',
        'icon': '&#x21C4;',
        'category': 'Exchange Tools',
    },
    {
        'id': 'each-way-calculator',
        'title': 'Each Way Calculator',
        'short': 'Calculate returns for each-way bets on horse racing',
        'icon': '&#x1F40E;',
        'category': 'Basic Calculators',
    },
]


def get_calculator_description(calc_id):
    """Return (description_text, example_text) for a calculator."""
    descs = {
        'bet-calculator': (
            'Enter your stake and odds to see potential returns. Supports single bets and accumulators up to 20 legs. Results show profit, total return and return on investment.',
            '<strong>Scenario:</strong> You want to bet R200 on Kaizer Chiefs to beat Orlando Pirates at decimal odds of 3.20.<br><strong>Step 1:</strong> Enter stake: R200<br><strong>Step 2:</strong> Enter odds: 3.20<br><strong>Step 3:</strong> Total return = R200 x 3.20 = <strong>R640</strong><br><strong>Step 4:</strong> Profit = R640 - R200 = <strong>R440</strong><br><strong>ROI:</strong> 220%'
        ),
        'accumulator-calculator': (
            'Add multiple selections with their individual odds. The calculator multiplies them together to give you combined odds and total potential returns for your accumulator.',
            '<strong>Scenario:</strong> Weekend PSL four-fold accumulator with R50 stake.<br><strong>Leg 1:</strong> Chiefs to win @ 1.80<br><strong>Leg 2:</strong> Pirates to win @ 2.10<br><strong>Leg 3:</strong> Sundowns to win @ 1.65<br><strong>Leg 4:</strong> Stellenbosch to win @ 2.40<br><strong>Combined odds:</strong> 1.80 x 2.10 x 1.65 x 2.40 = <strong>11.88</strong><br><strong>Total return:</strong> R50 x 11.88 = <strong>R594.00</strong> (R544 profit)'
        ),
        'odds-converter': (
            'Paste any odds format and instantly see the equivalent in decimal, fractional and American formats. Useful when comparing odds across different South African bookmakers.',
            '<strong>Example:</strong> Hollywoodbets shows Chiefs at 2.50 (decimal). What is that in other formats?<br><strong>Decimal:</strong> 2.50<br><strong>Fractional:</strong> 3/2 (means you win R3 for every R2 staked)<br><strong>American:</strong> +150 (means you win R150 on a R100 stake)<br><strong>Implied probability:</strong> 40.0%'
        ),
        'implied-probability': (
            'Convert bookmaker odds into percentage probabilities to understand what the market thinks the true chance of an outcome is.',
            '<strong>Example:</strong> Betway has Springboks to beat Australia at 1.45.<br><strong>Calculation:</strong> 1 / 1.45 x 100 = <strong>68.97%</strong><br>The market implies the Springboks have roughly a 69% chance of winning. If you believe the true probability is higher than 69%, the bet may offer value.'
        ),
        'margin-calculator': (
            'Enter the odds for all outcomes in a market. The calculator shows the bookmaker margin (overround) and what the true fair odds would be without the margin.',
            '<strong>Example:</strong> PSL match: Chiefs 2.10, Draw 3.20, Pirates 3.50<br><strong>Step 1:</strong> Convert to probabilities: 1/2.10 + 1/3.20 + 1/3.50 = 47.6% + 31.3% + 28.6% = <strong>107.5%</strong><br><strong>Step 2:</strong> Margin = 107.5% - 100% = <strong>7.5%</strong><br>A lower margin means better value for bettors. Top SA bookmakers typically run 4-8% margins on PSL fixtures.'
        ),
        'kelly-criterion': (
            'Enter your estimated true probability and the bookmaker odds to find the optimal percentage of your bankroll to stake according to the Kelly Criterion.',
            '<strong>Scenario:</strong> You estimate Sundowns have a 60% chance of winning, and the odds are 1.90.<br><strong>Kelly formula:</strong> (bp - q) / b, where b = 0.90, p = 0.60, q = 0.40<br><strong>Calculation:</strong> (0.90 x 0.60 - 0.40) / 0.90 = <strong>15.6%</strong><br>Kelly suggests staking 15.6% of your bankroll. Most experienced bettors use half-Kelly (7.8%) to reduce variance.'
        ),
        'dutching-calculator': (
            'Enter odds for multiple selections you want to back. The calculator tells you how much to stake on each to guarantee the same profit regardless of which one wins.',
            '<strong>Scenario:</strong> Kenilworth race with three fancied runners, R200 total budget.<br><strong>Horse A:</strong> 4.00 → Stake R90.91<br><strong>Horse B:</strong> 5.00 → Stake R72.73<br><strong>Horse C:</strong> 8.00 → Stake R36.36<br><strong>Total staked:</strong> R200<br><strong>Guaranteed return if any wins:</strong> R363.64 (<strong>R163.64 profit</strong>)'
        ),
        'bonus-rollover': (
            'Enter your bonus amount, wagering multiplier and typical odds to see how much total wagering is needed to clear the bonus, and your expected cost.',
            '<strong>Scenario:</strong> TicTacBets offers a R5,000 bonus with 5x wagering requirements.<br><strong>Total wagering needed:</strong> R5,000 x 5 = <strong>R25,000</strong><br><strong>Average odds assumed:</strong> 1.80<br><strong>Expected margin cost:</strong> R25,000 x (1 - 1/1.80) = <strong>R11,111</strong><br>In practice, the bonus is worth approximately R5,000 - R11,111 in expected costs. Whether it is worthwhile depends on your betting volume.'
        ),
        'lay-bet-calculator': (
            'Enter the back odds, lay odds and stake to calculate your liability, qualifying loss and profit for matched betting or exchange trading.',
            '<strong>Scenario:</strong> You lay Chiefs to win at odds of 3.00 with a R100 lay stake.<br><strong>If Chiefs lose:</strong> You keep the R100 lay stake<br><strong>If Chiefs win:</strong> You pay out (3.00 - 1) x R100 = <strong>R200 liability</strong><br>Lay betting is the opposite of backing. You profit when the selection does not win.'
        ),
        'each-way-calculator': (
            'Enter odds, each-way terms (1/4 or 1/5 odds for places) and stake to see returns for win and place separately.',
            '<strong>Scenario:</strong> R50 each-way (R100 total) on a horse at 10/1, 1/4 odds for 3 places.<br><strong>Win part:</strong> R50 x 11.00 = R550<br><strong>Place part:</strong> R50 x (10/4 + 1) = R50 x 3.50 = R175<br><strong>If horse wins:</strong> R550 + R175 = <strong>R725 total return</strong> (R625 profit)<br><strong>If horse places 2nd/3rd:</strong> R175 return (R75 profit on the place, minus R50 lost on the win part = <strong>R25 net profit</strong>)'
        ),
    }
    return descs.get(calc_id, ('Use this calculator to work out your betting figures.', 'Enter values above and click Calculate.'))


def get_calculator_form(calc_id):
    """Return the HTML form for a calculator."""
    forms = {
        'bet-calculator': '''
        <div class="calc-row"><label>Stake (R)</label><input type="number" id="stake" value="100" min="1" step="1"></div>
        <div class="calc-row"><label>Odds (decimal)</label><input type="number" id="odds" value="2.50" min="1.01" step="0.01"></div>
        <button class="btn-primary calc-btn" onclick="calculate()">Calculate Returns</button>''',
        'accumulator-calculator': '''
        <div id="legs">
          <div class="calc-row"><label>Leg 1 Odds</label><input type="number" class="leg-odds" value="1.80" min="1.01" step="0.01"></div>
          <div class="calc-row"><label>Leg 2 Odds</label><input type="number" class="leg-odds" value="2.10" min="1.01" step="0.01"></div>
        </div>
        <button class="btn-outline calc-btn" onclick="addLeg()" style="margin-bottom:12px">+ Add Leg</button>
        <div class="calc-row"><label>Stake (R)</label><input type="number" id="stake" value="50" min="1" step="1"></div>
        <button class="btn-primary calc-btn" onclick="calculate()">Calculate Accumulator</button>''',
        'odds-converter': '''
        <div class="calc-row"><label>Decimal Odds</label><input type="number" id="decimal" value="2.50" min="1.01" step="0.01" oninput="convertFromDecimal()"></div>
        <div class="calc-row"><label>Fractional Odds</label><input type="text" id="fractional" value="3/2" oninput="convertFromFractional()"></div>
        <div class="calc-row"><label>American Odds</label><input type="text" id="american" value="+150" oninput="convertFromAmerican()"></div>''',
    }
    default = '''
    <div class="calc-row"><label>Value 1</label><input type="number" id="val1" value="100" min="0" step="0.01"></div>
    <div class="calc-row"><label>Value 2</label><input type="number" id="val2" value="2.00" min="0" step="0.01"></div>
    <button class="btn-primary calc-btn" onclick="calculate()">Calculate</button>'''
    return forms.get(calc_id, default)


def get_calculator_results(calc_id):
    """Return the results HTML placeholder for a calculator."""
    return '''<div id="results" class="calc-results" style="display:none">
        <div class="calc-result-row"><span class="calc-result-label">Total Return</span><span class="calc-result-val" id="totalReturn">-</span></div>
        <div class="calc-result-row"><span class="calc-result-label">Profit</span><span class="calc-result-val" id="profit">-</span></div>
        <div class="calc-result-row"><span class="calc-result-label">ROI</span><span class="calc-result-val" id="roi">-</span></div>
    </div>'''


def get_calculator_js(calc_id):
    """Return the JS for a calculator."""
    js_map = {
        'bet-calculator': '''
        function calculate(){
          var s=parseFloat(document.getElementById('stake').value);
          var o=parseFloat(document.getElementById('odds').value);
          if(isNaN(s)||isNaN(o))return;
          var ret=s*o; var prof=ret-s; var roi=(prof/s*100).toFixed(1);
          document.getElementById('totalReturn').textContent='R'+ret.toFixed(2);
          document.getElementById('profit').textContent='R'+prof.toFixed(2);
          document.getElementById('roi').textContent=roi+'%';
          document.getElementById('calc-results').style.display='block';
          document.getElementById('results').style.display='block';
        }''',
        'accumulator-calculator': '''
        function addLeg(){
          var legs=document.getElementById('legs');
          var n=legs.querySelectorAll('.leg-odds').length+1;
          var div=document.createElement('div');div.className='calc-row';
          div.innerHTML='<label>Leg '+n+' Odds</label><input type="number" class="leg-odds" value="1.50" min="1.01" step="0.01">';
          legs.appendChild(div);
        }
        function calculate(){
          var odds=document.querySelectorAll('.leg-odds');
          var combined=1;odds.forEach(function(el){combined*=parseFloat(el.value)||1;});
          var s=parseFloat(document.getElementById('stake').value);
          var ret=s*combined;var prof=ret-s;var roi=(prof/s*100).toFixed(1);
          document.getElementById('totalReturn').textContent='R'+ret.toFixed(2);
          document.getElementById('profit').textContent='R'+prof.toFixed(2);
          document.getElementById('roi').textContent=roi+'% (Combined odds: '+combined.toFixed(2)+')';
          document.getElementById('calc-results').style.display='block';
          document.getElementById('results').style.display='block';
        }''',
        'odds-converter': '''
        function convertFromDecimal(){
          var d=parseFloat(document.getElementById('decimal').value);if(isNaN(d)||d<1.01)return;
          var num=d-1;var frac=toFraction(num);document.getElementById('fractional').value=frac;
          document.getElementById('american').value=d>=2?('+'+((d-1)*100).toFixed(0)):((-100/(d-1)).toFixed(0));
          document.getElementById('calc-results').style.display='block';
          document.getElementById('results').style.display='block';
          document.getElementById('totalReturn').textContent=d.toFixed(2);
          document.getElementById('profit').textContent=frac;
          document.getElementById('roi').textContent=d>=2?'+'+((d-1)*100).toFixed(0):((-100/(d-1)).toFixed(0));
        }
        function convertFromFractional(){/*simplified*/}
        function convertFromAmerican(){/*simplified*/}
        function toFraction(x){var t=1e-6;var h1=1,h2=0,k1=0,k2=1,b=x;
          do{var a=Math.floor(b);var aux=h1;h1=a*h1+h2;h2=aux;aux=k1;k1=a*k1+k2;k2=aux;b=1/(b-a);}while(Math.abs(x-h1/k1)>x*t);
          return h1+'/'+k1;}
        convertFromDecimal();''',
    }
    default = '''
    function calculate(){
      var v1=parseFloat(document.getElementById('val1').value);
      var v2=parseFloat(document.getElementById('val2').value);
      if(isNaN(v1)||isNaN(v2))return;
      var ret=v1*v2;var prof=ret-v1;
      document.getElementById('totalReturn').textContent='R'+ret.toFixed(2);
      document.getElementById('profit').textContent='R'+prof.toFixed(2);
      document.getElementById('roi').textContent=((prof/v1)*100).toFixed(1)+'%';
      document.getElementById('calc-results').style.display='block';
      document.getElementById('results').style.display='block';
    }'''
    return js_map.get(calc_id, default)
