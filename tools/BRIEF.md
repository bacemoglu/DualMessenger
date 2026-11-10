# Translation brief: Dual Messenger+ website

You are translating a small product website from English into one target language (named in your task).

**The product.** Dual Messenger+ is an iPhone/iPad app. It lets people use a second WhatsApp account on the same
device (it opens WhatsApp's own web service inside the app, linked by scanning a QR code with the phone that has
the second account). It also has an app lock (Face ID / Touch ID / passcode), Voice To Text (audio → text),
an AI chat bot that runs on the device, notes, reminders, sticker packs, fancy fonts and location sharing.
It is an independent app, not made by WhatsApp. Premium features need a subscription sold through the App Store.

## Files

Read all three source files completely before you start:

- `/home/claude/site/web/content/en/site.json` (home page strings)
- `/home/claude/site/web/content/en/privacy.md` (Privacy Policy)
- `/home/claude/site/web/content/en/terms.md` (Terms of Use)

Write exactly these three files (create the folder), where `CODE` is the language code given in your task:

- `/home/claude/site/web/content/CODE/site.json`
- `/home/claude/site/web/content/CODE/privacy.md`
- `/home/claude/site/web/content/CODE/terms.md`

Reference material for your language (read both before translating):

- `/home/claude/site/web/tools/ref/CODE.md`: texts in your language that the app's owner has **already approved
  and published** on the App Store. Reuse their wording and terminology. The file explains which site strings
  must equal which approved text. Approved sublines may contain `<br>`; drop the `<br>` when you reuse them.
- `/home/claude/site/web/tools/ui_ref/CODE.png`: five screenshots of the app in your language (start screen,
  lock screen, Voice To Text, Chat Bot, Notes), and `/home/claude/site/web/tools/ui_ref/CODE_zoom.png`: the
  same screens enlarged where the labels are (start-screen button and tab bar, lock-screen texts, the three
  title bars). Whenever the text refers to something the user sees in the app
  (the "Log In" button on the start screen, feature names such as Voice To Text, Chat Bot, Notes, Reminder),
  use exactly the label shown in these screenshots. If a label in the screenshot is still in English, keep it in
  English.

## Rules

1. **Structure stays identical.**
   - `site.json`: same keys, same nesting, same array lengths, valid UTF-8 JSON, 2-space indent. Never translate
     keys or the values of `"img"`. Set `"lang"` and `"dir"` to the values given in your task. Translate every
     other string value.
   - `privacy.md` / `terms.md`: keep every heading (same count, same numbers: `## 1. …`), every list and list
     item, the two wrapper lines `<div class="summary" markdown="1">` and `</div>`, the `[TOC]` line, every URL
     and link target, the `{{privacy_url}}` placeholder, and the `**bold lead-ins**`. Translate the link texts
     and everything else. Keep one blank line between blocks, exactly as in the source.
2. **Never translate or transliterate:** Dual Messenger+, WhatsApp, Meta, Apple, RevenueCat, App Store,
   Apple Account, Face ID, Touch ID, iPhone, iPad, iPhone Duo, iOS, iCloud, QR, the email address, URLs.
   Keep "Premium" as the plan name. The document title "Licensed Application End User License Agreement" stays in
   English (it is the official title of Apple's agreement); you may add a short translation in parentheses.
3. **Real UI labels.** The WhatsApp menu items (Settings, Linked Devices, Link a Device, Log Out) must be the
   labels that WhatsApp's own iPhone app shows in your language. Names of iOS items (the Settings app, App Store
   account settings, Subscriptions) must be Apple's terms in your language. Use your knowledge; you may run up to
   two web searches to confirm the WhatsApp labels (for example the WhatsApp Help Center article on linking a
   device, in your language).
4. **Tone.** Plain, natural and concise, the way a native copywriter would write it. No word-for-word
   translation. Use the form of address given in your task, consistently.
5. **Legal pages are precise.** Do not add, drop, soften or strengthen any statement, condition or number
   (24 hours, 14 days, 30 days, 13 years, iOS 16 / iOS 17, 8 styles, 15 languages, "weekly, monthly and yearly").
   "Republic of Türkiye" is the governing law and stays.
6. **Typography.** Use your language's own quotation marks and punctuation. Do not use em dashes for asides.
   Write the date in `legal.updated` ("November 9, 2026") in your language's normal long date format.
7. **The 15 languages** in the FAQ answer: write the language names in your language and keep all fifteen
   (English, Arabic, Chinese (Simplified), Dutch, French, German, Hebrew, Hindi, Indonesian, Italian, Japanese,
   Portuguese, Russian, Spanish, Turkish), in the order that is natural in your language.
8. **Special strings in `site.json`.**
   - `language.hint` must say "Read this page in YOUR-LANGUAGE", written in your language (it is shown to
     speakers of your language who land on a page in another language). Example for German: "Diese Seite auf
     Deutsch lesen".
   - `language.label` = the word "Language" in your language.
   - `legal.translation_note` tells readers that the page is a translation of the English original and that the
     English version applies if the two differ. `legal.english_link` = "Read the English version".
   - `meta.home_title` keeps the form `Dual Messenger+ – <short headline>`.
9. **Never** mention themes, colors or app icons as features. Never state or imply that more than two accounts
   can be used.
10. Do not add direction marks (LRM/RLM) or HTML. The build system handles text direction.

## Before you finish

Run the checker and fix everything it reports as an ERROR (warnings are for you to review):

```
python3 /home/claude/site/web/tools/check_lang.py CODE
```

Then report back in under 150 words: the three files written; the labels you used for (a) the Log In button,
(b) WhatsApp's Settings / Linked Devices / Link a Device / Log Out; and anything you were unsure about.
Do not paste the translations into your report.
