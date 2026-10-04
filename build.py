#!/usr/bin/env python3
"""Builds the Kachingz site. Edit the page bodies below, then run `python3 build.py`.

Every link is relative, so the same files work at echizen92.github.io/kaching-pages/
and at kachingz.com. The JSON files the app downloads (companion-content.json,
prompt-overlay.json, shortcut-guide.json) are not touched by this script.
"""
import hashlib
import re
import pathlib

ROOT = pathlib.Path(__file__).parent
APP_STORE = "https://apps.apple.com/app/id6798360020"
EMAIL = "faiz.rashid@gmx.us"
UPDATED = "30 September 2026"

# The front page is what App Store Connect's privacy URL points at until it is
# changed to /privacy/. While False, the front page is the privacy policy and
# the landing page is published at /home/ for review.
LANDING_AT_ROOT = True

APPLE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16.37 12.62c-.03-2.6 2.12-3.85 2.22-3.91'
         '-1.21-1.77-3.09-2.01-3.76-2.04-1.6-.16-3.12.94-3.93.94-.81 0-2.06-.92-3.39-.89-1.74.03-3.35 1.01-4.25 '
         '2.57-1.81 3.14-.46 7.79 1.3 10.34.86 1.25 1.89 2.65 3.23 2.6 1.3-.05 1.79-.84 3.36-.84 1.56 0 2.01.84 '
         '3.38.81 1.4-.02 2.28-1.27 3.13-2.53.99-1.45 1.39-2.86 1.42-2.93-.03-.01-2.72-1.04-2.75-4.12zM13.8 5.0c'
         '.71-.86 1.19-2.06 1.06-3.25-1.02.04-2.26.68-3 1.54-.66.76-1.23 1.98-1.08 3.15 1.14.09 2.3-.58 3.02-1.44z"/></svg>')


# Self-hosted (assets/fonts), so visitors' browsers make no requests to Google.
FONTS = ('<link rel="preload" href="{up}assets/fonts/fraunces-normal-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
         '<link rel="preload" href="{up}assets/fonts/instrument-sans-normal-latin.woff2" as="font" type="font/woff2" crossorigin>')


def version(asset):
    """A short content hash, so browsers and GitHub Pages' cache pick up changed files at once."""
    return hashlib.sha1((ROOT / asset).read_bytes()).hexdigest()[:8]


def store_button(extra=""):
    return (f'<a class="btn{extra}" href="{APP_STORE}">{APPLE}<span><small>Download on the</small>App Store</span></a>')


def page(path, title, description, body, current="", landing=False):
    depth = path.count("/") + 1 if path else 0
    up = "../" * depth
    home = up or "./"
    nav = (f'<a href="{home}#day">How it works</a>'
           f'<a href="{up}privacy/"{" aria-current=page" if current == "privacy/" else ""}>Privacy</a>'
           f'<a href="{up}support/"{" aria-current=page" if current == "support/" else ""}>Support</a>'
           f'<a class="pill" href="{APP_STORE}">Get the app</a>')
    body = body.replace("{UP}", up)
    script = f'\n<script type="module" src="{up}assets/site.js?v={version("assets/site.js")}"></script>' if landing else ""
    preload = f'\n<link rel="preload" href="{up}assets/room/layout.json" as="fetch" crossorigin>' if landing else ""
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="#FBF3E8">
<meta name="apple-itunes-app" content="app-id=6798360020">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="https://kachingz.com/assets/og.jpg">
<link rel="icon" href="{up}assets/favicon.png">
<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png">
{FONTS.replace('{up}', up)}
<link rel="stylesheet" href="{up}assets/site.css?v={version("assets/site.css")}">{preload}{script}
</head>
<body class="{'landing' if landing else 'doc-page'}">
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
  <a class="brand" href="{home}"><img src="{up}assets/icon.png" alt="" width="34" height="34">Kachingz</a>
  <nav aria-label="Main">{nav}</nav>
</div></header>
<main id="main">
{body}
</main>
<footer><div class="wrap">
  <a class="brand" href="{home}"><img src="{up}assets/icon.png" alt="" width="34" height="34">Kachingz</a>
  <nav aria-label="Footer">
    <a href="{up}privacy/">Privacy Policy</a>
    <a href="{up}terms/">Terms of Use</a>
    <a href="{up}support/">Support</a>
    <a href="{up}your-data/">Your data</a>
    <a href="mailto:{EMAIL}">{EMAIL}</a>
  </nav>
  <p class="copy">© 2026 Kachingz. Kachingz is not a bank and does not move money. Apple, the Apple logo, Apple Pay and Apple Wallet are trademarks of Apple Inc.</p>
</div></footer>
</body>
</html>
"""
    out = ROOT / path / "index.html" if path else ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    print("wrote", out.relative_to(ROOT))


def redirect(filename, target):
    (ROOT / filename).write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Moved</title>
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{target}">
</head><body><p>This page has moved to <a href="{target}">{target}</a>.</p></body></html>
""")
    print("wrote", filename, "->", target)


# ---------------------------------------------------------------------------
HOME = f"""
<section class="hero"><div class="wrap">
  <div>
    <div class="eyebrow fade-in" style="animation-delay:.05s">Budget &amp; expense tracker for iPhone</div>
    <h1><span class="w" style="--i:0">The</span> <span class="w" style="--i:1">budget</span> <span class="w" style="--i:2">app</span> <span class="w" style="--i:3">with</span> <span class="w" style="--i:4">a</span> <span class="w" style="--i:5"><em>cat</em></span> <span class="w" style="--i:6">in</span> <span class="w" style="--i:7">it.</span></h1>
    <p class="lede fade-in">See what you can really spend after bills and savings. Purchases log themselves when you tap to pay. And on Home, a cosy room where your cat keeps count with you.</p>
    <div class="cta fade-in">{store_button()}<a class="link-arrow" href="#day">Spend a day with Mochi</a></div>
    <ul class="trust fade-in"><li>No bank login</li><li>No ads or tracking</li><li>Records stay on your iPhone</li></ul>
  </div>
  <div class="stage fade-in" style="animation-delay:.35s">
    <div class="roomcard">
      <canvas data-room='{{"time":"auto","pose":"idle"}}' data-hero role="img" aria-label="Mochi, an orange tabby cat, in a cosy room. Select Mochi for a cuddle."></canvas>
      <span class="chip left" data-tod-chip>Day · your time</span>
      <span class="chip right" aria-hidden="true">Tap Mochi</span>
      <div class="speech">
        <span class="name">Mochi</span><span class="hearts" aria-label="Friendship: 3 of 4 hearts">♥♥♥♡</span>
        <p data-speech>You have S$1,284 to spend till payday, with bills and savings already tucked away.</p>
        <ul hidden data-lines>
          <li>You have S$1,284 to spend till payday, with bills and savings already tucked away.</li>
          <li>Your phone bill is due Thursday. I've already set S$38 aside for it.</li>
          <li>Seven days of logging in a row! That's a new record for us.</li>
          <li>Food is at 80% of its budget with 9 days to go. Cook tonight?</li>
          <li>Payday's on Friday. Three more sleeps!</li>
        </ul>
        <div class="hint">Mochi talks about your own money</div>
      </div>
    </div>
  </div>
</div></section>

<div class="marquee" aria-hidden="true"><div class="track">
  <span>Know what you can spend</span><span>Purchases that log themselves</span><span>Bills before they bite</span><span>A tabby or a tuxedo</span><span>No bank login</span><span>Your weather in the window</span>
  <span>Know what you can spend</span><span>Purchases that log themselves</span><span>Bills before they bite</span><span>A tabby or a tuxedo</span><span>No bank login</span><span>Your weather in the window</span>
</div></div>

<section class="day" id="day" data-time="dawn">
  <div class="intro wrap">
    <div class="eyebrow" data-reveal>A day with Mochi</div>
    <h2 data-reveal>From <em>sunrise</em> to bedtime.</h2>
    <p data-reveal style="--d:.1s">Kachingz keeps the numbers; Mochi keeps you company. Here's how a day goes.</p>
  </div>
  <div class="wrap split">
    <div class="sticky"><div class="stage"><div class="roomcard bare">
      <canvas data-room='{{"time":"dawn","pose":"idle"}}' data-story role="img" aria-label="Mochi's room, changing with the time of day as you read."></canvas>
      <span class="chip left" data-story-chip>Dawn</span>
    </div></div></div>
    <div class="chapters">
      <article class="chapter" data-chapter='{{"time":"dawn","pose":"idle","furniture":[]}}'>
        <div class="time">07:02</div><div class="when">Dawn</div>
        <div class="chapter-body"><h3>Wake up to one number.</h3>
        <p>Available to spend is your balance minus the bills due before payday and the money you've set aside. It answers "can I?" before the coffee's made.</p></div>
        <div class="ui">
          <div class="card"><div class="label">Available to spend</div><div class="big" data-count="1284.60">S$1,284.60</div><div class="label">After bills &amp; savings · payday in 3 days</div></div>
          <div class="card" style="margin-top:10px">
            <div class="row"><span>Tracked balance</span><span class="amt">S$1,883.97</span></div>
            <div class="row"><span>Bills reserved</span><span class="amt">−S$399.37</span></div>
            <div class="row"><span>Set aside</span><span class="amt">−S$200.00</span></div>
          </div>
        </div>
      </article>
      <article class="chapter" data-chapter='{{"time":"day","pose":"sit","furniture":[]}}'>
        <div class="time">12:41</div><div class="when">Lunchtime</div>
        <div class="chapter-body"><h3>Tap to pay. It logs itself.</h3>
        <p>Set up an Apple Wallet automation once, and every purchase lands in Kachingz with the merchant, amount and card. Prefer to type? Adding one takes seconds.</p></div>
        <div class="ui">
          <div class="notif"><div class="app" aria-hidden="true">💳</div><div style="flex:1"><div class="meta"><b>Wallet</b><span>now</span></div><b>Coffee shop</b><div>S$5.40 with your card</div></div></div>
          <div class="card logged">
            <div class="row"><div class="lead"><div class="icon" style="background:#FDEBD8" aria-hidden="true">☕</div><div><b>Coffee shop</b><span class="muted">Food &amp; drinks · 12:41</span></div></div><span class="amt">−S$5.40</span></div>
            <div class="row"><span class="tag">✓ Logged automatically</span><span class="label">Undo</span></div>
          </div>
        </div>
      </article>
      <article class="chapter" data-chapter='{{"time":"dusk","pose":"idle","furniture":[]}}'>
        <div class="time">18:15</div><div class="when">Dusk</div>
        <div class="chapter-body"><h3>Bills, before they bite.</h3>
        <p>Bills and subscriptions sit in one list. What's due before payday is set aside for you, and Mochi mentions what's coming up.</p></div>
        <div class="ui">
          <div class="card"><div class="label">Reserved before payday</div><div class="big" data-count="399.37">S$399.37</div><div class="label">4 bills due</div></div>
          <div class="card" style="margin-top:10px">
            <div class="row"><div class="lead"><div class="icon" style="background:#E3ECF7" aria-hidden="true">📱</div><div><b>Phone plan</b><span class="muted">Due Thursday</span></div></div><span class="amt">S$38.00</span></div>
            <div class="row"><div class="lead"><div class="icon" style="background:#FFF3D6" aria-hidden="true">⚡</div><div><b>Electricity</b><span class="muted">Due Friday</span></div></div><span class="amt">S$112.40</span></div>
            <div class="row"><div class="lead"><div class="icon" style="background:#E6F1E8" aria-hidden="true">🛡️</div><div><b>Insurance</b><span class="muted">Due Friday</span></div></div><span class="amt">S$238.99</span></div>
            <div class="row"><div class="lead"><div class="icon" style="background:#F1E6F7" aria-hidden="true">🎵</div><div><b>Music</b><span class="muted">Renews Saturday</span></div></div><span class="amt">S$9.98</span></div>
          </div>
        </div>
      </article>
      <article class="chapter" data-chapter='{{"time":"night","pose":"sleep","furniture":["lights"]}}'>
        <div class="time">23:30</div><div class="when">Bedtime</div>
        <div class="chapter-body"><h3>Under budget. Sleep easy.</h3>
        <p>Budgets by category show what's left and whether you're on pace, not just what's gone.</p></div>
        <div class="ui">
          <div class="card" style="background:#E6EEE2"><div class="big" style="font-size:28px">S$462.50 left</div><div class="label">On pace · 12 days left</div></div>
          <div class="card" style="margin-top:10px">
            <div class="row" style="display:block"><div style="display:flex;justify-content:space-between"><b>Food &amp; drinks</b><span class="amt">S$212.40 left</span></div><div class="bar"><i style="--w:58%"></i></div></div>
            <div class="row" style="display:block"><div style="display:flex;justify-content:space-between"><b>Transport</b><span class="amt">S$64.00 left</span></div><div class="bar"><i style="--w:70%"></i></div></div>
            <div class="row" style="display:block"><div style="display:flex;justify-content:space-between"><b>Shopping</b><span class="amt">S$140.00 left</span></div><div class="bar"><i style="--w:30%"></i></div></div>
            <div class="row" style="display:block"><div style="display:flex;justify-content:space-between"><b>Fun</b><span class="amt">S$46.10 left</span></div><div class="bar"><i style="--w:81%"></i></div></div>
          </div>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="yours" id="yours">
  <div class="intro wrap">
    <span class="pro-tag" data-reveal>Kachingz Pro</span>
    <h2 data-reveal>Make the room <em>yours.</em></h2>
    <p data-reveal style="--d:.1s">Pick your cat, bring in the weather, and decorate with paws you earn from good money habits. Go on, try it.</p>
  </div>
  <div class="wrap split">
    <div class="stage" data-reveal><div class="roomcard bare">
      <canvas data-room='{{"time":"day","pose":"sit"}}' data-play role="img" aria-label="Mochi's room, showing the choices you make on the right."></canvas>
      <span class="chip left" data-play-chip>Day · clear</span>
    </div></div>
    <div class="controls" data-reveal style="--d:.15s">
      <div class="control"><h4 id="c-cat">Cat</h4><div class="seg" data-set="cat" role="group" aria-labelledby="c-cat">
        <button type="button" value="tabby" aria-pressed="true">Orange tabby</button><button type="button" value="tuxedo" aria-pressed="false">Tuxedo</button></div></div>
      <div class="control"><h4 id="c-time">Time of day</h4><div class="seg" data-set="time" role="group" aria-labelledby="c-time">
        <button type="button" value="dawn" aria-pressed="false">Dawn</button><button type="button" value="day" aria-pressed="true">Day</button><button type="button" value="dusk" aria-pressed="false">Dusk</button><button type="button" value="night" aria-pressed="false">Night</button></div></div>
      <div class="control"><h4 id="c-weather">Weather</h4><div class="seg" data-set="weather" role="group" aria-labelledby="c-weather">
        <button type="button" value="clear" aria-pressed="true">Clear</button><button type="button" value="cloudy" aria-pressed="false">Cloudy</button><button type="button" value="rain" aria-pressed="false">Rain</button><button type="button" value="storm" aria-pressed="false">Storm</button><button type="button" value="snow" aria-pressed="false">Snow</button></div></div>
      <div class="control"><h4 id="c-temp">Temperature</h4><div class="seg" data-set="climate" role="group" aria-labelledby="c-temp">
        <button type="button" value="mild" aria-pressed="true">Mild</button><button type="button" value="hot" aria-pressed="false">Hot day</button><button type="button" value="cold" aria-pressed="false">Cold day</button></div></div>
      <div class="control"><h4 id="c-deco">Decorate</h4><div class="seg" data-toggle="furniture" role="group" aria-labelledby="c-deco">
        <button type="button" value="lights" aria-pressed="false">Fairy lights <span class="paws">40 paws</span></button><button type="button" value="shelf" aria-pressed="false">Wall shelf <span class="paws">30</span></button><button type="button" value="piggy" aria-pressed="false">Piggy bank <span class="paws">25</span></button><button type="button" value="heartrug" aria-pressed="false">Heart rug <span class="paws">60</span></button><button type="button" value="cushion" aria-pressed="false">Floor cushion <span class="paws">35</span></button></div></div>
      <p class="caption" data-caption aria-live="polite">Every action is a moment with Mochi. Nothing drains or decays.</p>
    </div>
  </div>
</section>

<section class="rest">
  <div class="intro wrap" style="padding-top:0">
    <div class="eyebrow" data-reveal>And the rest</div>
    <h2 data-reveal>Everything else, <em>done properly.</em></h2>
  </div>
  <div class="wrap"><div class="bento">
    <div class="tile ai" data-reveal>
      <h3>Advice from your own numbers.</h3>
      <p>Weekly reviews, budget suggestions and month-end projections, worked out from what you've recorded. Ten reports free; unlimited with Pro. Suggestions are informational, not financial advice.</p>
      <div class="shot"><img src="{{UP}}assets/ui/insights.webp" alt="Insights: S$205.56 spent this week so far, 13% less than the same point last week, with a chart by day" width="900" height="1016" loading="lazy"></div>
    </div>
    <div class="tile travel" data-reveal style="--d:.08s">
      <h3>Travel without the maths.</h3>
      <p>Spend in ringgit, yen or baht and see it in your home currency at the day's rate, with the original kept.</p>
      <div class="fx" aria-live="off"><span class="from"><span class="swap" data-fx-from>MYR 42.50</span></span><span class="swap" data-fx-to>S$13.30</span></div>
    </div>
    <div class="tile hide" data-reveal style="--d:.16s">
      <h3>Hide every amount.</h3>
      <p>One tap masks every figure, for when someone's reading over your shoulder.</p>
      <div class="mask"><span class="val" data-mask-val>S$5,234.24</span><button type="button" data-mask aria-pressed="false" aria-label="Hide amounts">👁</button></div>
    </div>
    <div class="tile add" data-reveal>
      <h3>Logged in seconds.</h3>
      <p>Amount, merchant, done. Undo is always there if you slip.</p>
      <div class="shot"><img src="{{UP}}assets/ui/add.webp" alt="Add Transaction: S$18.50 at Coffee shop for toast and coffee" width="900" height="1031" loading="lazy"></div>
    </div>
    <div class="tile cards" data-reveal style="--d:.08s">
      <h3>Cards and pay-later, sorted.</h3>
      <p>Track credit, debit and buy-now-pay-later accounts. Card repayments are kept apart from your spending.</p>
      <div class="cardstack" aria-hidden="true"><div>Debit<span>•••• 4021</span></div><div>Credit<span>•••• 7781</span></div><div>Pay later<span>3 of 4 paid</span></div></div>
    </div>
  </div></div>
</section>

<section class="promise"><div class="wrap">
  <div class="eyebrow" data-reveal>What Kachingz doesn't do</div>
  <ul>
    <li data-reveal>No bank <em>login.</em></li>
    <li data-reveal>No account to make.</li>
    <li data-reveal>No ads. No <em>tracking.</em></li>
    <li data-reveal>Records stay on your <em>iPhone.</em></li>
  </ul>
  <p data-reveal>Kachingz never connects to your bank or moves money. When you ask for an AI report, a summary of the figures it needs is sent to write it, and our server doesn't keep it. <a href="{{UP}}privacy/">Read the privacy policy</a>.</p>
</div></section>

<section class="price"><div class="wrap">
  <div class="intro" style="padding:0">
    <div class="eyebrow" data-reveal>Pricing</div>
    <h2 data-reveal>Free to start. <em>Pro</em> for the cat.</h2>
  </div>
  <div class="plans">
    <div class="plan" data-reveal><h3>Free</h3><p class="sub">Everything you need to keep count.</p><ul>
      <li>Available to spend, after bills and savings</li><li>Budgets, bills, subscriptions and cards</li><li>Purchases logged from Apple Wallet</li><li>Travel currency conversion</li><li>10 AI reports</li></ul></div>
    <div class="plan pro" data-reveal style="--d:.1s"><h3>Kachingz Pro</h3><p class="sub">Monthly or yearly. Prices are shown in the app.</p><ul>
      <li>Everything in Free</li><li>Mochi's room, with a tabby or a tuxedo</li><li>Decorating with paws you earn</li><li>Your weather in the window</li><li>Unlimited AI reports, ready each morning</li></ul></div>
  </div>
  <p class="fine">Subscriptions renew automatically unless cancelled at least 24 hours before the period ends. Manage them in your App Store account.</p>
</div></section>

<section class="closing"><div class="wrap">
  <h2 data-reveal>Sleep easy about <em>money.</em></h2>
  <p data-reveal style="--d:.08s">Free on the App Store, for iPhone.</p>
  <div data-reveal style="--d:.16s">{store_button()}</div>
  <div class="stage" data-reveal><div class="roomcard bare">
    <canvas data-room='{{"time":"night","pose":"sleep","furniture":["lights","heartrug"]}}' role="img" aria-label="Mochi asleep on the bed at night, under fairy lights."></canvas>
  </div></div>
</div></section>
"""

PRIVACY = f"""
<section class="doc"><div class="wrap">
<div class="eyebrow">Kachingz</div>
<h1>Privacy Policy</h1>
<p class="meta">Last updated {UPDATED}</p>

<div class="summary"><b>In short</b>
<ul>
  <li>There is no Kachingz account and no bank connection. Your records are stored on your iPhone.</li>
  <li>When you use AI reports, a summary of the records that report needs is sent to our AI server and to DeepSeek to write it. We do not keep the content of those requests.</li>
  <li>No advertising, no analytics SDKs, no tracking across apps, and we never sell data.</li>
</ul></div>

<h2>1. Who we are</h2>
<p>Kachingz is an iPhone app for tracking spending, budgets, bills and savings, published by Faiz Rashid in Singapore. Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>

<h2>2. Information stored on your device</h2>
<p>Everything you record in Kachingz stays on your iPhone: purchases, budgets, bills, income, cards, savings goals, notes, your companion and any photo you choose for your profile. It is stored with Apple's on-device database and is included in your iPhone's backups according to your own iCloud and backup settings.</p>
<p>If you log purchases with an Apple Wallet or Shortcuts automation, the notification text is read and stored on your device alongside the purchase so you can check it later. It is not sent to us.</p>
<p>Photos you pick are stored on your device only and are never uploaded.</p>

<h2>3. Information that leaves your device</h2>
<table>
<tr><th>What</th><th>When</th><th>Sent to</th></tr>
<tr><td>A summary of the records an AI report needs: for example category and budget totals, bill and income figures, and for some reports merchant names, amounts and dates. Plus an anonymous app ID.</td>
    <td>When you generate an AI report. With Kachingz Pro, reports also refresh automatically about once a day in the background.</td>
    <td>Our AI server (<code>ai.kachingz.com</code>), which forwards the summary to DeepSeek to write the report.</td></tr>
<tr><td>Your home currency code (for example "sgd") and a date.</td>
    <td>When you log a purchase in a foreign currency, at most once a day per currency set.</td>
    <td>A free public exchange-rate service (currency-api, served by jsDelivr and Cloudflare Pages). No purchase details are sent.</td></tr>
<tr><td>Nothing about you: the app downloads small settings files (companion text, the Shortcuts guide, AI instructions).</td>
    <td>Occasionally, when the app opens.</td>
    <td>This website, hosted by GitHub Pages.</td></tr>
<tr><td>Purchase and subscription status.</td>
    <td>When you subscribe or restore purchases.</td>
    <td>Apple, through the App Store. We never see your payment details.</td></tr>
</table>
<p>Like any internet request, these services can see your device's IP address when the app contacts them.</p>

<h3>The anonymous app ID</h3>
<p>Kachingz creates a random ID the first time you use AI features and keeps it in your iPhone's Keychain. It is not linked to your name, email, Apple Account or device identifiers. Our server uses it only to count how many AI reports you've used this month, to apply the free and fair-use limits.</p>

<h3>What our AI server keeps</h3>
<p>Our server does not store the content of your requests or of the AI's replies. It keeps a short technical log of each request (time, anonymous ID, whether it succeeded, size, AI tokens used and response time) and a monthly usage count per anonymous ID. The log is capped in size and older entries are deleted automatically.</p>
<p>Until 30 September 2026, our server also logged the content of AI requests and replies, which had been enabled to study AI quality during testing. That logging was switched off and all stored request content deleted on 30 September 2026.</p>

<h3>DeepSeek</h3>
<p>AI reports are written by DeepSeek's language model. DeepSeek receives the summary described above, without your name or contact details, and processes it under its own terms and privacy policy. Its servers may be located outside Singapore, including in China.</p>

<h2>4. What we don't do</h2>
<ul>
  <li>We don't sell or rent your data, or use it for advertising.</li>
  <li>We don't use analytics, advertising or crash-reporting SDKs, and we don't track you across other apps or websites.</li>
  <li>We don't connect to your bank or move money. Figures reflect only what you record.</li>
</ul>

<h2>5. How long information is kept</h2>
<p>Records on your device are kept until you delete them or delete the app. On our server, technical log entries are removed automatically as the size-capped log rotates, and monthly usage counts are kept only to apply the monthly limit.</p>

<h2>6. Your choices</h2>
<ul>
  <li>You can use Kachingz without AI reports. Nothing about your records leaves your device unless you use them.</li>
  <li>You can delete any purchase, or delete the app to remove all records from your iPhone.</li>
  <li>See <a href="{{UP}}your-data/">Your data</a> for step-by-step instructions and how to contact us about server-side records.</li>
</ul>

<h2>7. Children</h2>
<p>Kachingz is rated 4+ but is designed for adults managing their own money. We don't knowingly collect personal information from children.</p>

<h2>8. Changes</h2>
<p>If this policy changes, we'll update the date above. Significant changes will also be mentioned in the app's release notes.</p>

<h2>9. Contact</h2>
<p>Questions or requests: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div></section>
"""

TERMS = f"""
<section class="doc"><div class="wrap">
<div class="eyebrow">Kachingz</div>
<h1>Terms of Use</h1>
<p class="meta">Last updated {UPDATED}</p>

<p>Kachingz is licensed to you under Apple's <a href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/">Standard Licensed Application End User License Agreement</a>. These notes add a few things specific to Kachingz.</p>

<h2>Not financial advice</h2>
<p>Kachingz helps you organise records you enter. AI reports and suggestions are generated automatically, can be wrong, and are for information only. They are not financial, tax or investment advice. Check important decisions against your bank statements and, where needed, a qualified adviser.</p>

<h2>Your figures</h2>
<p>Balances, budgets and exchange-rate conversions reflect only what you record and publicly available daily reference rates. Kachingz does not connect to your bank, show your actual bank balance, or move money. Your bank's charges and exchange rates may differ.</p>

<h2>Kachingz Pro</h2>
<p>Kachingz Pro is an optional auto-renewing subscription, offered monthly or yearly. Prices are shown in the app before you buy. Payment is charged to your Apple Account at confirmation. The subscription renews automatically unless cancelled at least 24 hours before the end of the current period, and you can manage or cancel it in your <a href="https://apps.apple.com/account/subscriptions">App Store account settings</a>. Free users receive 10 AI reports; a report that fails does not use one.</p>

<h2>Fair use</h2>
<p>AI reports are subject to a monthly fair-use limit to keep the service available for everyone.</p>

<h2>Contact</h2>
<p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
</div></section>
"""

SUPPORT = f"""
<section class="doc faq"><div class="wrap">
<div class="eyebrow">Kachingz</div>
<h1>Support</h1>
<p class="meta">Email <a href="mailto:{EMAIL}">{EMAIL}</a>. We usually reply within 1–2 business days.</p>

<h2>Getting started</h2>
<details><summary>How do I log purchases automatically from Apple Wallet?</summary>
<p>In Kachingz, tap your profile picture, then <b>Shortcut setup</b>. It walks you through adding a Shortcuts automation for Apple Wallet and includes a ready-made shortcut. Once set up, purchases are logged as you pay, even with your phone locked.</p></details>
<details><summary>How do I add a purchase by hand?</summary>
<p>Tap <b>Add</b> in the middle of the tab bar, enter the amount and merchant, and save. You'll see a confirmation with <b>Undo</b> in case you made a mistake.</p></details>
<details><summary>A purchase was logged with the wrong merchant, card or category.</summary>
<p>Tap it in Activity to edit it. Kachingz remembers the category you choose for that merchant next time. The original notification text is shown at the bottom of the editor, which helps if you need to email us about it.</p></details>

<h2>Money</h2>
<details><summary>What is "Available to spend"?</summary>
<p>Your tracked balance, minus bills due before your next payday and money you've set aside. It only reflects what you record; Kachingz doesn't read your bank balance.</p></details>
<details><summary>How do overseas purchases work?</summary>
<p>A purchase in another currency is converted to your home currency at that day's reference exchange rate, and the original amount is shown beneath it. If your bank charged a different amount, edit the purchase to match; Kachingz keeps both. With no internet connection the purchase waits and converts next time you open the app.</p></details>
<details><summary>How do I hide my balances?</summary>
<p>Tap the eye icon at the top of Home, Activity or Income. Every amount is masked until you tap it again.</p></details>
<details><summary>How do I delete a purchase?</summary>
<p>Swipe it left in Activity, or open it and tap Delete. Undo appears for a few seconds afterwards.</p></details>

<h2>AI reports and Pro</h2>
<details><summary>How many AI reports do I get for free?</summary>
<p>Free users get 10 AI reports. A report only uses one if it's generated successfully; opening a saved report is free. Kachingz Pro includes unlimited reports, within a monthly fair-use limit, and refreshes them automatically.</p></details>
<details><summary>How do I cancel or manage Kachingz Pro?</summary>
<p>Subscriptions are handled by Apple. Open <a href="https://apps.apple.com/account/subscriptions">App Store subscriptions</a> on your iPhone, or go to Settings, your name, then Subscriptions.</p></details>
<details><summary>I bought Pro on another iPhone.</summary>
<p>Open Kachingz Pro in the app and tap <b>Restore Purchases</b> while signed in with the same Apple Account.</p></details>

<h2>Your data</h2>
<details><summary>Where is my data stored, and how do I delete it?</summary>
<p>On your iPhone. See <a href="{{UP}}your-data/">Your data</a> for how to delete it and what our AI server keeps.</p></details>
</div></section>
"""

YOUR_DATA = f"""
<section class="doc"><div class="wrap">
<div class="eyebrow">Kachingz</div>
<h1>Your data</h1>
<p class="meta">Last updated {UPDATED}</p>

<p>Kachingz has no account, so there is no account to delete. Your records live on your iPhone, and you're in control of them.</p>

<h2>Delete individual records</h2>
<p>Swipe a purchase left in Activity, or open any purchase, bill, budget or goal and choose Delete.</p>

<h2>Delete everything on your iPhone</h2>
<ol>
  <li>Delete the Kachingz app from your iPhone. This removes all records stored in the app.</li>
  <li>If you use iCloud Backup, older backups may still contain Kachingz data until they're replaced. You can manage backups in Settings, your name, iCloud, Manage Account Storage, Backups.</li>
</ol>
<p>If you subscribed to Kachingz Pro, deleting the app does not cancel the subscription. Cancel it in your <a href="https://apps.apple.com/account/subscriptions">App Store subscriptions</a>.</p>

<h2>What our AI server keeps</h2>
<p>Our AI server doesn't store the content of your requests. It keeps a short technical log (time, anonymous app ID, status, size and response time) that deletes older entries automatically, and a monthly count of AI reports used. None of this is linked to your name, email or Apple Account. See the <a href="../privacy/">Privacy Policy</a> for details.</p>
<p>The anonymous app ID is kept in your iPhone's Keychain so your monthly count survives reinstalling the app. iOS may keep Keychain items after an app is deleted; resetting your iPhone or erasing its Keychain removes it.</p>

<h2>Requests</h2>
<p>To ask about or request deletion of server-side records, email <a href="mailto:{EMAIL}">{EMAIL}</a>. Because the records are anonymous, we can only find yours if you tell us roughly when you used AI reports and what they were about; we'll delete any matching entries.</p>
</div></section>
"""

NOT_FOUND = """
<section class="doc"><div class="wrap">
<h1>Page not found</h1>
<p>That page doesn't exist. Try the <a href="/">home page</a>, <a href="/privacy/">Privacy Policy</a> or <a href="/support/">Support</a>.</p>
</div></section>
"""

if __name__ == "__main__":
    # site.js imports room.js; stamp its version so a changed room.js isn't served from cache.
    site_js = ROOT / "assets/site.js"
    site_js.write_text(re.sub(r'"\./room\.js(\?v=[0-9a-f]+)?"', f'"./room.js?v={version("assets/room.js")}"', site_js.read_text()))
    page("" if LANDING_AT_ROOT else "home", "Kachingz: the budget app with a cat in it",
         "See what you can really spend after bills and savings, log Apple Pay purchases automatically, and keep a cosy room where your cat keeps count with you. No bank login.",
         HOME, landing=True)
    if not LANDING_AT_ROOT:
        page("", "Privacy Policy · Kachingz",
             "How Kachingz handles your information: records stay on your iPhone, no bank login, no ads or tracking.",
             PRIVACY, "privacy/")
    page("privacy", "Privacy Policy · Kachingz",
         "How Kachingz handles your information: records stay on your iPhone, no bank login, no ads or tracking.",
         PRIVACY, "privacy/")
    page("terms", "Terms of Use · Kachingz", "Terms of use for the Kachingz app and Kachingz Pro.", TERMS)
    page("support", "Support · Kachingz",
         "Help with Kachingz: Apple Wallet auto-logging, budgets, overseas purchases, AI reports and Kachingz Pro.",
         SUPPORT, "support/")
    page("your-data", "Your data · Kachingz",
         "How to delete your Kachingz data and what our AI server keeps.", YOUR_DATA, "your-data/")
    page("404", "Page not found · Kachingz", "Page not found.", NOT_FOUND)
    (ROOT / "404.html").write_text((ROOT / "404" / "index.html").read_text())
    (ROOT / "404" / "index.html").unlink()
    (ROOT / "404").rmdir()
    # Old addresses: App Store Connect and installed apps link to these.
    redirect("support.html", "support/")
    redirect("marketing.html", "./" if LANDING_AT_ROOT else "home/")
    if LANDING_AT_ROOT:
        # /home/ was the landing page's address before it moved to the front.
        (ROOT / "home").mkdir(exist_ok=True)
        redirect("home/index.html", "../")
