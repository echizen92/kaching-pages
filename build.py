#!/usr/bin/env python3
"""Builds the Kachingz site. Edit the page bodies below, then run `python3 build.py`.

Every link is relative, so the same files work at echizen92.github.io/kaching-pages/
and at kachingz.com. The JSON files the app downloads (companion-content.json,
prompt-overlay.json, shortcut-guide.json) are not touched by this script.
"""
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


def page(path, title, description, body, current=""):
    depth = path.count("/") + 1 if path else 0
    up = "../" * depth
    nav = [("", "Home"), ("privacy/", "Privacy"), ("support/", "Support"), ("your-data/", "Your data")]
    links = "".join(
        f'<a href="{up}{href}"{" aria-current=page" if href == current else ""}'
        f'{" class=hide-sm" if href == "your-data/" else ""}>{label}</a>'
        for href, label in nav[1:])
    body = body.replace("{UP}", up)
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="apple-itunes-app" content="app-id=6798360020">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{up}assets/01-home.jpg">
<link rel="icon" href="{up}assets/favicon.png">
<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png">
<link rel="stylesheet" href="{up}assets/site.css">
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="{up or './'}"><img src="{up}assets/icon.png" alt="">Kachingz</a>
  <nav>{links}</nav>
</div></header>
<main>
{body}
</main>
<footer><div class="wrap">
  <a href="{up}privacy/">Privacy Policy</a>
  <a href="{up}terms/">Terms of Use</a>
  <a href="{up}support/">Support</a>
  <a href="{up}your-data/">Your data</a>
  <a href="mailto:{EMAIL}">{EMAIL}</a>
  <span class="copy">© 2026 Kachingz. Kachingz is not a bank and does not move money.</span>
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
    <div class="eyebrow">Budget &amp; expense tracker for iPhone</div>
    <h1>Know what<br>you can <em>spend.</em></h1>
    <p class="lede">Budgets, bills and spending in one calm place, with an AI money coach and a cat who grows with your habits. No bank login.</p>
    <div class="cta">
      <a class="btn" href="{APP_STORE}">{APPLE} Download on the App Store</a>
      <a class="btn ghost" href="{{UP}}privacy/">How we handle your data</a>
    </div>
    <p class="note">Free to download. Optional Kachingz Pro subscription.</p>
  </div>
  <img class="phone" src="{{UP}}assets/01-home.jpg" alt="Kachingz home screen showing Available to spend of S$11,773.57 after bills and savings, with Mochi the cat in her room" width="560" height="1217">
</div></section>

<div class="promises"><div class="wrap">
  <div><b>No bank login</b><span>You choose what's recorded.</span></div>
  <div><b>On your iPhone</b><span>Records stay on your device.</span></div>
  <div><b>No ads, no tracking</b><span>No analytics or ad SDKs.</span></div>
  <div><b>Hide amounts</b><span>One tap masks every figure.</span></div>
</div></div>

<section class="feature"><div class="wrap">
  <div>
    <h2>Tap to pay.<br>It <em>logs itself.</em></h2>
    <p>Set up an Apple Wallet automation once and purchases land in Kachingz as you pay, with the merchant, amount and card.</p>
    <p>Prefer to type? Adding a purchase takes a few seconds, and Undo is always there.</p>
  </div>
  <img class="phone" src="{{UP}}assets/02-autolog.jpg" alt="Transactions logged automatically from Apple Wallet" loading="lazy" width="560" height="1217">
</div></section>

<section class="feature flip"><div class="wrap">
  <div>
    <h2>See what's left<br>in every <em>budget.</em></h2>
    <p>Set monthly or weekly budgets by category and see whether you're on pace, not just how much is gone.</p>
  </div>
  <img class="phone" src="{{UP}}assets/04-budgets.jpg" alt="Budgets screen showing S$2,479.86 left and comfortably ahead of pace" loading="lazy" width="560" height="1217">
</div></section>

<section class="feature"><div class="wrap">
  <div>
    <h2>Advice from<br><em>your own</em> numbers.</h2>
    <p>AI reports review your budgets, bills, cards and habits and suggest one practical next step. Suggestions are informational, not financial advice.</p>
  </div>
  <img class="phone" src="{{UP}}assets/05-ai.jpg" alt="AI reports including a next-month budget advisor and spending review" loading="lazy" width="560" height="1217">
</div></section>

<section class="feature peach flip"><div class="wrap">
  <div>
    <h2>Bills, without<br>the <em>surprises.</em></h2>
    <p>Keep bills and subscriptions together, see what's due before payday, and track credit, debit and pay-later cards.</p>
  </div>
  <img class="phone" src="{{UP}}assets/06-bills.jpg" alt="Bills and subscriptions with amounts due" loading="lazy" width="560" height="1217">
</div></section>

<section class="feature"><div class="wrap">
  <div>
    <h2>Travelling?<br>It <em>converts.</em></h2>
    <p>Spend in ringgit, yen or baht and see it in your home currency at the day's exchange rate, with the original amount kept beneath.</p>
  </div>
  <img class="phone" src="{{UP}}assets/07-overseas.jpg" alt="An overseas purchase of MYR 42.50 converted to S$13.30" loading="lazy" width="560" height="1217">
</div></section>

<section class="feature dark flip"><div class="wrap">
  <div>
    <h2>Small habits.<br>A <em>happy cat.</em></h2>
    <p>Log, save and check in, and Mochi grows with you in her cosy room.</p>
  </div>
  <img class="phone" src="{{UP}}assets/08-room.jpg" alt="Mochi the cat in her room" loading="lazy" width="560" height="1217">
</div></section>

<section class="closing"><div class="wrap">
  <h2>Money that <em>makes sense.</em></h2>
  <p>Free to download, with 10 AI reports included. Kachingz Pro adds unlimited reports and the full companion.</p>
  <div class="cta"><a class="btn" href="{APP_STORE}">{APPLE} Download on the App Store</a></div>
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
    page("" if LANDING_AT_ROOT else "home", "Kachingz: Budget & Expense Tracker for iPhone",
         "Know what you can spend. Budgets, bills and spending in one place, with an AI money coach and a cat who grows with your habits. No bank login.",
         HOME)
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
