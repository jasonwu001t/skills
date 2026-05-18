#!/usr/bin/env python3
# analyze.py — rank combo_*.json files in OUT_DIR by Economy Classic points.
#
# Usage:
#   python3 analyze.py [OUT_DIR] [TOP_N]
#
# Defaults: OUT_DIR=/tmp/va_search, TOP_N=25

import json, glob, re, sys, os
from datetime import date

out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/va-reward-reports")
top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 25

rows = []
for f in sorted(glob.glob(os.path.join(out_dir, "combo_*.json"))):
    m = re.search(r"combo_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.json", f)
    if not m:
        continue
    out_dt = date.fromisoformat(m.group(1))
    ret_dt = date.fromisoformat(m.group(2))
    try:
        j = json.loads(open(f).read())
    except Exception:
        continue
    cabins = j.get("cabins") or []
    if not cabins:
        continue
    by_cabin = {c["cabin"]: c for c in cabins}
    eco = by_cabin.get("Economy Classic") or next((c for c in cabins if "Economy" in c["cabin"]), None)
    prem = by_cabin.get("Premium")
    upper = by_cabin.get("Upper Class")
    rows.append({
        "out": out_dt, "ret": ret_dt, "days": (ret_dt - out_dt).days,
        "eco_pts": eco["pts"] if eco else None,
        "eco_tax": eco["tax"] if eco else None,
        "prem_pts": prem["pts"] if prem else None,
        "upper_pts": upper["pts"] if upper else None,
    })

rows.sort(key=lambda r: r["eco_pts"] if r["eco_pts"] is not None else 10**9)

if not rows:
    print(f"No parsable combo files found in {out_dir}.")
    sys.exit(1)

print(f"Total parsed combos: {len(rows)}\n")
print(f"{'Rank':<6}{'Outbound':<14}{'Return':<14}{'Days':<6}{'Economy':<22}{'Premium':<12}{'Upper':<12}")
print("-" * 86)
for i, r in enumerate(rows[:top_n], 1):
    eco_str = f"{r['eco_pts']:,} + ${r['eco_tax']}" if r['eco_pts'] else "-"
    prem_str = f"{r['prem_pts']:,}" if r['prem_pts'] else "-"
    up_str = f"{r['upper_pts']:,}" if r['upper_pts'] else "-"
    print(f"{i:<6}{r['out'].strftime('%a %b %d'):<14}{r['ret'].strftime('%a %b %d'):<14}{r['days']:<6}{eco_str:<22}{prem_str:<12}{up_str:<12}")

top = rows[0]
print()
print("=== CHEAPEST (Economy Classic, round-trip) ===")
print(f"  Outbound: {top['out'].strftime('%A, %B %d, %Y')}")
print(f"  Return:   {top['ret'].strftime('%A, %B %d, %Y')}")
print(f"  Trip:     {top['days']} days")
print(f"  Cost:     {top['eco_pts']:,} Virgin Points + US${top['eco_tax']} taxes/fees")
