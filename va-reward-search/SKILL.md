---
name: va-reward-search
description: Sweep Virgin Atlantic Flying Club reward-seat (award flight) availability across many date combinations on virginatlantic.com using osascript-driven Google Chrome automation. Use when the user wants to find the cheapest Virgin Points cost for a route, compare miles prices across flexible travel dates, identify the cheapest month or week for an award trip, or pick the optimal outbound/return combo for an award redemption (e.g., "cheapest SEA→LHR reward seats end of June, 12-16 day trip", "which month is cheapest to fly to London Jul-Sep", "find lowest-points VA award between July 1-15"). Requires macOS with Google Chrome and an active virginatlantic.com login session. Defaults: 2 adults, direct flights only.
when_to_use: User wants Virgin Atlantic award/reward/miles seat availability checked across multiple dates, asks which month/week is cheapest for an award trip, or wants the lowest points price for a route on Virgin Atlantic. Not for cash-fare searches or other airlines.
---

# Virgin Atlantic Reward-Seat Sweep

Sweeps SEA-style award searches across N outbound × M return date combinations and ranks them by Virgin Points cost, surfacing the single cheapest combo plus a sortable table.

## Defaults

- **2 adults** (`PAX=a2t0c0i0`). Override per-call via `PAX=a1t0c0i0` (solo) or `a2t0c1i0` (2 adults + 1 child), etc.
- **Direct flights only.** `parse.js` filters out any flight whose listing card says "1 stop" / "1 change" / "2 stops" — only blocks marked "Direct" feed the cabin-price extractor.
- **Round-trip, miles search** (`awardSearch=true` in URL).
- **Output dir** `~/va-reward-reports/` (persistent — survives reboots, unlike `/tmp`). Override with `OUT_DIR`.

## What this skill does

For each (outbound, return) date pair the user cares about, navigate Chrome to a Virgin Atlantic award-search deep link, parse the **listing** prices (Economy Classic / Premium / Upper Class) for *direct flights only*, save the JSON, then rank all combos.

A 2-adult search may surface multiple direct options (e.g., Virgin Atlantic VS106 SEA-LHR + Delta DL20 SEA-LHR as a SkyTeam partner award). The parser captures all direct flights in `flights[]` and exposes the cheapest per cabin in `cabins[]` for ranking.

The skill exists because:

- Virgin Atlantic's homepage form is a React SPA with anti-bot guards on autocomplete; driving it via JS works but is fragile.
- The fare-calendar prices shown above the listing are **NOT reliable** as round-trip totals for cross-combo comparison — they reflect projections that often disagree with the listing price for the same date. Only the listing block (`Economy Classic\n129,000\n+US$565`) is trustworthy.
- A single deep-link URL (see "URL pattern" below) lets you skip the form entirely once you have one successful search.

## Prerequisites

1. **macOS** with `osascript` available.
2. **Google Chrome** installed and Chrome's "Allow JavaScript from Apple Events" enabled (View → Developer → Allow JavaScript from Apple Events). Verify with:
   ```bash
   osascript -e 'tell application "Google Chrome" to execute front window'"'"'s active tab javascript "1+1"'
   ```
   Expect `2`.
3. **Active VA login session.** The user must already be signed into virginatlantic.com in Chrome's front window (look for "Hello {firstname}" in the top nav). If the session expires mid-sweep, the skill will detect the redirect to `identity.virginatlantic.com` and pause; ask the user for credentials and refill (do **NOT** save them).
4. `python3` and `bash` on PATH (default on macOS).

## URL pattern (key insight — skip the form)

Virgin Atlantic's award-search deep link:

```
https://www.virginatlantic.com/en-US/flights/search/slice
  ?passengers=a2t0c0i0           # a=adults, t=teens, c=children, i=infants
  &origin=SEA&origin=LHR         # outbound origin, then return origin (= destination)
  &awardSearch=true              # CRITICAL: miles mode
  &destination=LHR&destination=SEA
  &departing=2026-06-30          # outbound date
  &departing=2026-07-15          # return date
```

Once `awardSearch=true` is in the URL, no form interaction is required for further combos — just `set URL of active tab` per combo.

Note on points totals: when `passengers=a2t0c0i0`, listing prices are **totals for all passengers** (e.g., 36,000 pts for 2 adults = 18,000/person). Compare per-person across pax counts by dividing.

## Procedure

1. **Confirm scope with the user**: origin, destination, outbound-date window, trip-duration window (or explicit return-date window), cabin preference if any.

2. **Run a pilot search via the form** (only the first time — to land on the search results page and confirm the deep-link URL still works). If the URL pattern still resolves, you can skip this and go straight to step 4.

3. **Build the combo list**: every (outbound, return) pair where `return − outbound ∈ [min_days, max_days]`.

4. **Sweep**: for each combo, set the Chrome tab to the deep-link URL, sleep ~9–11s for SPA hydration, run the parser JS, save JSON to `/tmp/va_search/combo_<MM>-<DD>_<MM>-<DD>.json`. If the URL ends up at `identity.virginatlantic.com`, run the login flow (see "Login recovery").

5. **Analyze**: load all combo JSONs, build a table sorted by Economy Classic points, surface the cheapest. Open the cheapest combo's URL in Chrome for the user to review/book.

## Bundled scripts

Run these via `${CLAUDE_SKILL_DIR}/scripts/<file>`. The skill dir resolves to `~/.claude/skills/va-reward-search/`.

- **`scripts/parse.js`** — JS injected via Chrome's `execute javascript`. Extracts `pairs` (calendar dates → points) and `cabins` (Economy Classic / Premium / Upper Class with points + tax) from the current results page. Returns JSON. Works for both `en-US/flights/search/slice` and intermediate states.
- **`scripts/sweep.sh`** — Bash driver. Reads `COMBOS_FILE` (one `YYYY-MM-DD YYYY-MM-DD` per line), navigates Chrome per combo, calls `parse.js`, saves outputs to `OUT_DIR/combo_<out>_<ret>.json`, prints one-line price per combo. Required env: `ORIGIN`, `DEST`, `COMBOS_FILE`. Optional: `OUT_DIR` (default `/tmp/va_search`), `PAX` (default `a1t0c0i0`).
- **`scripts/analyze.py`** — Loads `OUT_DIR/combo_*.json`, builds a terminal table sorted by Economy Classic points, prints top-N and the single cheapest. Usage: `python3 analyze.py [OUT_DIR] [TOP_N]`.
- **`scripts/report.py`** — Renders the same data as a self-contained HTML report (no external assets) with a hero card for the cheapest combo, a sortable table, a points heatmap (green→red), tax columns, and direct booking links per row. Usage: `python3 report.py [OUT_DIR] [--origin SEA --dest LHR --pax a1t0c0i0] [--out path.html]`. Origin/dest are inferred from the first combo's URL if not passed. Default output: `OUT_DIR/report.html`. Open it via `osascript -e 'tell application "Google Chrome" to open location "file://…/report.html"'`.

Each is small enough to inline if a quick run is needed; copy them into the working session as starting points.

## Form-driving (only needed for the pilot search or first-time setup)

When you must drive the form (e.g., to validate the URL pattern still works):

1. **Toggle miles mode**: `document.getElementById('switch-checkbox').click()` — confirm `input[name=payment_type].value === 'PAY_WITH_POINTS'`.
2. **Fill from / to** — these are React-controlled with autocomplete that requires *real* keystroke events:
   ```js
   const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
   for (const ch of 'SEA') {
     cur += ch; setter.call(input, cur);
     input.dispatchEvent(new InputEvent('input',{bubbles:true,data:ch,inputType:'insertText'}));
     input.dispatchEvent(new KeyboardEvent('keydown',{bubbles:true,key:ch}));
     input.dispatchEvent(new KeyboardEvent('keyup',{bubbles:true,key:ch}));
   }
   ```
   Then click the matching `button[role=option]` from the dropdown. Plain `value=` setters or single `input` events do NOT trigger the dropdown.
3. **Open date picker**: dispatch the full sequence `pointerdown,mousedown,pointerup,mouseup,click` on the date input's wrapper `div` (the input itself is `readonly`).
4. **Pick dates**: every day in the next 12 months is in the DOM with `aria-label="26th of June"` etc. Use the same mouse-event sequence on the matching button. Outbound first, then return.
5. **Submit**: `[...form.querySelectorAll('button[type=submit]')].find(b => /search flights/i.test(b.innerText)).click()`.

After submit, the URL becomes the deep link.

## Login recovery

If a navigation lands on `identity.virginatlantic.com/...`, the form there can have **two shapes**:

- 3-field (initial / signup-signin policy): `signInName`, `lastName`, `password` + button `#continue`.
- 2-field (re-auth flash): email + password only.

Fill what's present, click `#continue`, sleep 8–12s, then re-issue the search URL. Do **not** persist credentials anywhere (not in scripts, not in shell history, not in memory). Ask the user each time the session dies.

## Gotchas

- **Calendar prices ≠ listing prices.** When `outbound` is at one date and you read the calendar's value for a *different* date, that number can disagree with what the listing shows when you actually search that other date. Always confirm via direct navigation before reporting.
- **`/flights-search-information/reward-flights.html` 404s.** That URL doesn't exist; don't link users there.
- **The "Reward seat checker" Flying Club page is `aria-disabled`** in the menu — don't try to use it as an alternative.
- **Sessions are short** (~10–15 min). Build login recovery into any sweep longer than ~10 min; use 2–3 retries per combo before giving up.
- **Chrome JS bridge returns the *last expression*, not async values.** Promises get serialized to `{}`. Chain async work via separate `osascript` calls with `sleep` between.
- **The `switch-checkbox` toggle clears `flights_from` / `flights_to` state** in the React form. Toggle miles mode *before* filling cities, or after filling re-verify both inputs are populated.
- **AppleScript can't parse `\u` escapes**, so `parse.js` must be loaded with `json.dumps(..., ensure_ascii=False)` — non-ASCII characters (em-dash, accents) in JS comments otherwise become `—` and crash osascript with "syntax error: Expected '\"'". Fix is in `sweep.sh`.
- **Pax count affects flight count shown.** A solo (`a1t0c0i0`) SEA-LHR search may show only 1 flight; a 2-adult search can reveal 5+ flights including SkyTeam partner direct flights (e.g., Delta DL20 redeemable with VA points). Direct-only filtering becomes essential as soon as connections appear.
- **Listing points are totals across all passengers**, not per-person. Divide by adult count for fair comparison across pax counts.

## Example invocations

- "Find cheapest VA reward seat SEA→LHR, depart end of June through 7/10, 12–16 day trip."
- "Which month is cheapest to fly Seattle to London for 2 weeks Jul-Sep?" (sample at ~5-day intervals across the window for a monthly mean/min/median comparison.)
- "Compare Virgin Points prices for SFO→LHR every Friday departure in September, 7-night returns."
- "What's the lowest VA Upper Class award JFK→LHR over the next 30 days?"

Sample output:

```
Rank  Outbound      Return        Days  Economy               Premium     Upper
1     Fri Jul 03    Wed Jul 15    12    49,000 + $571         153,000     410,000
2     Tue Jun 30    Wed Jul 15    15    58,000 + $571         189,000     485,000
...
=== CHEAPEST: Fri Jul 03 → Wed Jul 15 (12 days) — 49,000 pts + US$571
```
