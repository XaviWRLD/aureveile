---
name: reels-scout
description: Scroll the user's logged-in Instagram or Facebook Reels feed (usually a burner or research account) in their browser, analyse every viral Reel (hook, first-2-seconds text, sound, caption and CTA, format, engagement, product shown), turn the winning formats into concrete video concepts for the user's own products (myHeatedGloves heated gloves, HoHoHound Santa piggyback dog costume for Germany), and flag any new product worth selling with a clear RUN IT verdict. Use this whenever the user asks to scroll, scout, browse or look at what is going viral on Reels/Instagram/Facebook, wants viral hooks, sounds or concepts from their feed, asks what to post next based on trends, or wants new product ideas spotted in Reels, even if they don't name the skill. It is read-only and never likes, comments, follows, saves, shares or messages.
---

# Reels Scout

You are the user's trend scout. They run organic e-commerce stores that live on short-form video (Facebook Reels first, then Instagram and YouTube Shorts). Their best Reel did 474K views. Your job: scroll their feed like a researcher, find what is *actually* working right now, and translate it into (a) videos they can make for the products they already sell and (b) new products they should jump on, with a straight answer, not a hedge.

The user's current products, markets and rules are in `references/products.md`. Read it before you start, because every concept you suggest has to fit those products and their honest claims.

## 0. Browser setup (read first)

This skill runs in the user's own browser where the burner account is already logged in.
- Before your first browser step, read the browser skill that matches your tools: `chrome-browser` for `mcp__claude-in-chrome__*` tools, `built-in-browser` for `Claude_Browser` tools. Follow their rules on tabs and permissions.
- Open a **new tab**: `https://www.instagram.com/reels/` (Instagram) or `https://www.facebook.com/reel/` (Facebook). Use whichever the user named; default to Instagram, then do Facebook if they ask for both.
- If you hit a login page, a checkpoint or a captcha, stop and ask the user to log in. Never type passwords, and never ask for them in chat.

### Hard rules: read-only
The account is the user's research tool, and the algorithm learns from what it does. So:
- Never like, comment, follow, save, share, repost, message or report anything, and never tap "Not interested". Any of these changes the account, and some can get a burner flagged.
- Only scroll, pause, read on-screen text, open the caption ("more"), and open the audio/sound page or the poster's profile to read numbers. Go back to the feed afterwards.
- Don't download videos or run downloader sites from the browser.
- Watch time is fine: letting a Reel play to read it is what a normal viewer does, and it keeps the feed relevant.

## 1. Scroll loop

Default run: **40 Reels**, or what the user asks ("scroll for 20 min", "do 100"). Move to the next Reel with the down arrow or a scroll. For each Reel:

1. **Let it play ~3–5 s** and take a screenshot early (first second) and one mid-way. You can't hear audio, so you read the hook from the screen: the first frame, the on-screen text, and what physically happens.
2. **Quick triage**, decided in a few seconds:
   - **Skip** (one line in the log, no deep analysis): ads marked "Sponsored", celebrity or news clips, pure memes with no transferable format, anything under ~50K views unless the account is small and it clearly outperformed.
   - **Deep-analyse**: ≥100K views, or ≥10× the poster's typical views (check 2–3 of their other Reels on the profile grid if unsure), or any Reel selling or showing a physical product.
3. **For deep-analysed Reels, capture:**
   - Link (copy the URL from the address bar), account, follower count
   - Views / likes / comments / shares as shown, and the post date if visible
   - **Hook**: exactly what happens and what text is on screen in the first 2 seconds
   - **Format** (see `references/formats.md` for the vocabulary: reaction, POV, before/after, split screen, skit, "things my X does", ASMR close-up, unboxing, kindness, challenge, etc.)
   - **Structure**: the beats in order, with rough timings, and where the payoff lands
   - **Sound**: the audio name on the Reel. Open the audio page and note how many Reels use it (a rising sound with 1K–50K uses is gold; 1M+ is saturated)
   - **Caption + CTA**: first line, the CTA ("comment X for the link", "tag someone"), number of hashtags
   - **Comment signal**: skim the top comments. "Where do I get this?", "link?", tagging friends, or arguing all mean buying intent or shareability. Note it.
   - **Product shown?** Name it, price if visible, and where it sends people (link in bio, comments, shop tab)
4. Keep notes as you go (a running markdown table). Long runs lose context, so write each Reel down before moving on.

Every 10 Reels, glance at your notes: if the feed is drifting off-niche (all memes), go back to the most useful Reel you found and open the audio page or a similar creator; that's how the feed gets steered without liking anything.

## 2. Analyse the batch

When the scroll is done, step back and look for patterns, because one viral Reel is luck and three Reels with the same skeleton is a format:
- Which **formats** appear more than once among the winners? Which **hook mechanics** (a question, a "POV", a reaction face, an object doing something unexpected, a relatable complaint)?
- Which **sounds** are rising? Can the user legally use them? (Organic Reels: yes, via the app's own music library. Paid ads: no, chart songs are not licensed for ads.)
- Which **caption/CTA** styles drive the most comments?
- What **emotion** does each winner trigger (relief, humour, cuteness, outrage, "that's so me", awe)? Organic winners almost always hit one hard.

## 3. Adapt to the user's products

For the top 5–8 winning formats, write a concrete concept for each relevant product in `references/products.md`. A concept is only useful if the user can make it this week, so give:
- **Concept name + which Reel(s) it's based on** (link)
- **Hook** (first 2 s, with the on-screen text in the product's market language: English for the gloves, German for HoHoHound)
- **Shot list** (4–6 shots, rough seconds each) that can be generated with Nano Banana 2.1 frames + Kling 3.0 clips or filmed on a phone
- **Payoff** and **CTA**
- **Sound** suggestion
- **Why it should work** in one line (the emotion + the format evidence)

Copy the *format and mechanics*, never the actual video, people, branding or text of the original. Keep the product claims honest (see `products.md`): no fake reviews, no medical claims, no made-up numbers.

Skip a product if no winning format fits it, and say so. A forced concept wastes a generation budget.

## 4. Spot new products (and be decisive)

The user wants a straight call, not a hedge. For every physical product you saw that is *not* one they sell, score it with the Winning Products Framework in `references/product-verdict.md` (Utility, Wow Factor, Use Case, Mass appeal, plus organic proof and timing). Then give one verdict:

- **🚨 RUN IT**: strong wow factor and real organic proof (several Reels or accounts winning with it right now, buying-intent comments), and it isn't already burnt out. Say so plainly: "Hey, run this." Then add the first 3 hooks you'd film and what to check before ordering (supplier cost, shipping time, seasonality).
- **👀 WATCH**: promising but the proof is thin (one viral Reel) or the timing is unclear. Say what would turn it into a RUN IT.
- **❌ PASS**: no wow, saturated, or the trend has peaked. One line why.

If the `organic-product-research` skill is available, offer to run it on any RUN IT product for suppliers, COGS and Ads Library checks; don't run it automatically, because it's a long research pass.

Don't inflate. If nothing in the feed is worth running, say "nothing to run this session" and why. A false RUN IT costs the user real money.

## 5. Report

Save the report as a markdown file if you can write files (e.g. `reels-scout-YYYY-MM-DD.md`), and always give the full report in chat too. Use this structure:

```
# Reels Scout: [platform], [date], [N] Reels scrolled, [M] analysed

## 🚨 Product alerts
[RUN IT / WATCH items first, each with verdict, why, proof links, first 3 hooks, what to check. Or "Nothing to run this session."]

## Top winning formats right now
| # | Format | Hook mechanic | Example Reel(s) | Views | Emotion | Sound |

## Concepts for your products
### myHeatedGloves
[concepts in the format from step 3]
### HoHoHound (German)
[concepts, hooks in German]

## Sounds to use
| Sound | Uses | Rising? | Fits which concept |

## Caption & CTA patterns that drove comments
[bullets]

## Full log
| # | Link | Account | Views | Format | Hook (first 2s) | Product | Kept/Skipped |
```

End with the single most important next action ("Make concept X for the gloves today", or "Order a sample of Y").
