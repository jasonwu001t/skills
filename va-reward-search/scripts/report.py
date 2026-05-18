#!/usr/bin/env python3
# report.py — render combo_*.json files as a self-contained HTML report.
#
# Usage:
#   python3 report.py [OUT_DIR] [--origin SEA --dest LHR --pax a1t0c0i0]
#
# Defaults: OUT_DIR=/tmp/va_search, origin/dest inferred from the first combo's URL.

import json, glob, re, sys, os, html
from datetime import date, datetime
from urllib.parse import urlencode, parse_qs, urlparse

def parse_args(argv):
    out_dir = os.path.expanduser("~/va-reward-reports")
    out_html = None
    origin = dest = pax = None
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--origin": origin = argv[i+1]; i += 2
        elif a == "--dest": dest = argv[i+1]; i += 2
        elif a == "--pax":  pax = argv[i+1];   i += 2
        elif a == "--out":  out_html = argv[i+1]; i += 2
        elif a.startswith("--"): print(f"unknown flag {a}"); sys.exit(2)
        else: out_dir = a; i += 1
    return out_dir, out_html, origin, dest, pax

def load_rows(out_dir):
    rows = []
    for f in sorted(glob.glob(os.path.join(out_dir, "combo_*.json"))):
        m = re.search(r"combo_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.json", f)
        if not m: continue
        try: j = json.loads(open(f).read())
        except Exception: continue
        cabins = j.get("cabins") or []
        if not cabins: continue
        by = {c["cabin"]: c for c in cabins}
        eco = by.get("Economy Classic") or next((c for c in cabins if "Economy" in c["cabin"]), None)
        prem = by.get("Premium")
        upper = by.get("Upper Class")
        rows.append({
            "out": date.fromisoformat(m.group(1)),
            "ret": date.fromisoformat(m.group(2)),
            "eco": eco, "prem": prem, "upper": upper,
            "url": j.get("url", ""),
        })
    rows.sort(key=lambda r: (r["eco"]["pts"] if r["eco"] else 10**9))
    return rows

def infer_route(rows):
    if not rows: return None, None, None
    qs = parse_qs(urlparse(rows[0]["url"]).query)
    origins = qs.get("origin", [])
    pax = (qs.get("passengers", ["?"]) or ["?"])[0]
    if len(origins) >= 2: return origins[0], origins[1], pax
    return None, None, pax

def humanize_pax(pax):
    # a2t0c0i0 -> "2 adults"; a1t0c1i0 -> "1 adult, 1 child"
    if not pax: return ""
    parts = []
    for code, label_s, label_p in [("a","adult","adults"),("t","teen","teens"),("c","child","children"),("i","infant","infants")]:
        m = re.search(rf"{code}(\d+)", pax)
        if m and int(m.group(1)) > 0:
            n = int(m.group(1))
            parts.append(f"{n} {label_s if n == 1 else label_p}")
    return ", ".join(parts) if parts else pax

def book_url(origin, dest, pax, out_dt, ret_dt):
    return ("https://www.virginatlantic.com/en-US/flights/search/slice"
            f"?passengers={pax}&origin={origin}&origin={dest}"
            f"&awardSearch=true&destination={dest}&destination={origin}"
            f"&departing={out_dt.isoformat()}&departing={ret_dt.isoformat()}")

def color_for(pts, lo, hi):
    if pts is None: return "#f5f5f5"
    if hi == lo: t = 0.5
    else: t = (pts - lo) / (hi - lo)
    t = max(0.0, min(1.0, t))
    # green (cheap) → amber → red (expensive)
    r = int(34 + (220 - 34) * t)
    g = int(170 - (170 - 80) * t)
    b = int(60 + (60 - 60) * 0)
    return f"rgb({r},{g},{b})"

def fmt_pts(p): return f"{p:,}" if p is not None else "—"

CSS = """
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; margin: 0; background: #fafafa; color: #1d1d1f; }
header { padding: 32px 40px 20px; background: linear-gradient(135deg,#e0115f,#cc0000); color: #fff; }
header h1 { margin: 0 0 6px; font-weight: 600; font-size: 28px; }
header .meta { opacity: 0.85; font-size: 14px; }
main { max-width: 1280px; margin: 0 auto; padding: 24px 32px 64px; }
.card { background: #fff; border-radius: 12px; padding: 24px 28px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px; }
.card h2 { margin: 0 0 12px; font-size: 18px; font-weight: 600; }
.cheapest { display: grid; grid-template-columns: repeat(4,1fr); gap: 24px; }
.cheapest .label { font-size: 12px; text-transform: uppercase; color: #6e6e73; letter-spacing: 0.04em; margin-bottom: 4px; }
.cheapest .value { font-size: 22px; font-weight: 600; }
.cheapest .pts { color: #e0115f; }
.book { display: inline-block; margin-top: 12px; padding: 10px 18px; background: #1d1d1f; color: #fff; text-decoration: none; border-radius: 8px; font-weight: 500; font-size: 14px; }
.book:hover { background: #444; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th { text-align: left; padding: 10px 12px; background: #f5f5f7; font-weight: 600; font-size: 12px; text-transform: uppercase; color: #6e6e73; letter-spacing: 0.04em; cursor: pointer; user-select: none; }
th.sorted-asc::after { content: " ▲"; }
th.sorted-desc::after { content: " ▼"; }
td { padding: 10px 12px; border-bottom: 1px solid #ececec; }
tr:hover td { background: #fafafa; }
tr.top td:first-child { font-weight: 700; color: #e0115f; }
.pts-cell { font-variant-numeric: tabular-nums; padding: 4px 8px; border-radius: 6px; color: #fff; font-weight: 500; display: inline-block; min-width: 70px; text-align: right; }
.tax { color: #6e6e73; font-size: 12px; margin-left: 6px; }
a.row-link { color: #0070c9; text-decoration: none; }
a.row-link:hover { text-decoration: underline; }
.legend { display: flex; align-items: center; gap: 10px; font-size: 12px; color: #6e6e73; margin-top: 12px; }
.legend .bar { flex: 0 0 200px; height: 10px; border-radius: 4px; background: linear-gradient(90deg, rgb(34,170,60), rgb(127,125,60), rgb(220,80,60)); }
footer { text-align: center; color: #86868b; font-size: 12px; padding: 32px 0; }
"""

JS = """
function sortTable(idx, type) {
  const table = document.getElementById('combos');
  const tbody = table.tBodies[0];
  const rows = Array.from(tbody.rows);
  const ths = table.tHead.rows[0].cells;
  const cur = ths[idx].classList.contains('sorted-asc') ? 'asc' : 'desc';
  const next = cur === 'asc' ? 'desc' : 'asc';
  for (const th of ths) th.classList.remove('sorted-asc','sorted-desc');
  ths[idx].classList.add(next === 'asc' ? 'sorted-asc' : 'sorted-desc');
  rows.sort((a,b) => {
    const av = a.cells[idx].dataset.sort, bv = b.cells[idx].dataset.sort;
    let cmp;
    if (type === 'num') cmp = (parseFloat(av)||0) - (parseFloat(bv)||0);
    else cmp = av.localeCompare(bv);
    return next === 'asc' ? cmp : -cmp;
  });
  for (const r of rows) tbody.appendChild(r);
}
"""

def render(rows, origin, dest, pax, out_dir):
    if not rows:
        return f"<html><body><p>No parsable combo files in {html.escape(out_dir)}.</p></body></html>"

    eco_vals = [r["eco"]["pts"] for r in rows if r["eco"]]
    lo, hi = min(eco_vals), max(eco_vals)
    top = rows[0]
    top_url = book_url(origin or "?", dest or "?", pax or "a1t0c0i0", top["out"], top["ret"])
    generated = datetime.now().strftime("%a %b %d, %Y %H:%M")

    parts = []
    parts.append(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>VA Reward Sweep — {html.escape(origin or '?')}→{html.escape(dest or '?')}</title>
<style>{CSS}</style></head><body>
<header>
  <h1>Virgin Atlantic Reward Sweep</h1>
  <div class="meta">{html.escape(origin or '?')} ⇄ {html.escape(dest or '?')} · {len(rows)} combos · {html.escape(humanize_pax(pax))} · direct flights only · generated {html.escape(generated)}</div>
</header>
<main>
<div class="card">
  <h2>Cheapest combo</h2>
  <div class="cheapest">
    <div><div class="label">Outbound</div><div class="value">{top['out'].strftime('%a %b %d, %Y')}</div></div>
    <div><div class="label">Return</div><div class="value">{top['ret'].strftime('%a %b %d, %Y')}</div></div>
    <div><div class="label">Trip</div><div class="value">{(top['ret']-top['out']).days} days</div></div>
    <div><div class="label">Economy Classic</div><div class="value pts">{fmt_pts(top['eco']['pts'])} pts <span class="tax">+ US${html.escape(top['eco']['tax'])}</span></div></div>
  </div>
  <a class="book" href="{html.escape(top_url)}" target="_blank">Open in Virgin Atlantic →</a>
</div>

<div class="card">
  <h2>All combos (click a column header to sort)</h2>
  <table id="combos"><thead><tr>
    <th onclick="sortTable(0,'num')">Rank</th>
    <th onclick="sortTable(1,'str')">Outbound</th>
    <th onclick="sortTable(2,'str')">Return</th>
    <th onclick="sortTable(3,'num')">Days</th>
    <th onclick="sortTable(4,'num')" class="sorted-asc">Economy</th>
    <th onclick="sortTable(5,'num')">Tax (USD)</th>
    <th onclick="sortTable(6,'num')">Premium</th>
    <th onclick="sortTable(7,'num')">Upper Class</th>
    <th>Book</th>
  </tr></thead><tbody>""")

    for i, r in enumerate(rows, 1):
        eco_pts = r["eco"]["pts"] if r["eco"] else None
        eco_tax = r["eco"]["tax"] if r["eco"] else ""
        prem_pts = r["prem"]["pts"] if r["prem"] else None
        upper_pts = r["upper"]["pts"] if r["upper"] else None
        days = (r["ret"] - r["out"]).days
        url = book_url(origin or "?", dest or "?", pax or "a1t0c0i0", r["out"], r["ret"])
        eco_color = color_for(eco_pts, lo, hi)
        cls = "top" if i == 1 else ""
        parts.append(
            f"<tr class='{cls}'>"
            f"<td data-sort='{i}'>{i}</td>"
            f"<td data-sort='{r['out'].isoformat()}'>{r['out'].strftime('%a %b %d')}</td>"
            f"<td data-sort='{r['ret'].isoformat()}'>{r['ret'].strftime('%a %b %d')}</td>"
            f"<td data-sort='{days}'>{days}</td>"
            f"<td data-sort='{eco_pts or ''}'><span class='pts-cell' style='background:{eco_color}'>{fmt_pts(eco_pts)}</span></td>"
            f"<td data-sort='{eco_tax.replace(',','') or ''}'>${html.escape(eco_tax)}</td>"
            f"<td data-sort='{prem_pts or ''}'>{fmt_pts(prem_pts)}</td>"
            f"<td data-sort='{upper_pts or ''}'>{fmt_pts(upper_pts)}</td>"
            f"<td><a class='row-link' href='{html.escape(url)}' target='_blank'>book →</a></td>"
            f"</tr>"
        )

    parts.append(f"""</tbody></table>
  <div class="legend">Economy points heatmap: <span class="bar"></span> {lo:,} (cheap) → {hi:,} (expensive)</div>
</div>

<footer>Generated by va-reward-search skill · data parsed from {html.escape(out_dir)}</footer>
<script>{JS}</script>
</body></html>""")
    return "".join(parts)

def main():
    out_dir, out_html, origin, dest, pax = parse_args(sys.argv)
    rows = load_rows(out_dir)
    inf_o, inf_d, inf_p = infer_route(rows)
    origin = origin or inf_o
    dest = dest or inf_d
    pax = pax or inf_p or "a1t0c0i0"
    out_html = out_html or os.path.join(out_dir, "report.html")
    open(out_html, "w").write(render(rows, origin, dest, pax, out_dir))
    print(out_html)

if __name__ == "__main__":
    main()
