// parse.js — injected into Chrome via `osascript ... execute javascript`.
// DEFAULTS: filters listing results to DIRECT flights only.
//
// Returns JSON:
//   pairs:   [{date,pts}]   wide-search calendar (informational; unreliable cross-combo)
//   cabins:  [{cabin,pts,tax}]   cheapest direct-flight price per cabin (compat for analyze/report)
//   flights: [{airline,flightNum,duration,direct:true,cabins:[...]}]   per-flight detail
//
// On no listing (still loading / login redirect / no availability): {err,url}.
(() => {
  const body = document.body.innerText;
  const startMarker = "Points per person exc. taxes";
  const endMarker = "Sort by:";
  const start = body.indexOf(startMarker);
  const end = body.indexOf(endMarker, start);
  if (start < 0 || end < 0) return JSON.stringify({err: "no markers", url: location.href});

  // Wide-search calendar (above the listing)
  const seg = body.slice(start + startMarker.length, end);
  const calRe = /([A-Za-z]{3}\s\d{1,2}\s[A-Za-z]{3})\s+(?:Cheapest\s+)?([\d,]+)/g;
  const pairs = [];
  let m;
  while ((m = calRe.exec(seg)) !== null) {
    pairs.push({date: m[1], pts: parseInt(m[2].replace(/,/g, ""), 10)});
  }

  // Listing area: split into per-flight blocks at "Flight details"
  const listingStart = body.indexOf(endMarker);
  const listingEnd = body.indexOf("Where we fly", listingStart);
  const listing = body.slice(listingStart, listingEnd > 0 ? listingEnd : undefined);
  const blocks = listing.split(/Flight details/);

  const cabinRe = /(Economy(?:\s(?:Classic|Light|Delight))?|Main Cabin|Premium|Upper Class)\s*\n+\s*([\d,]+)\s*\n*\s*\+US\$([\d,.]+)/g;
  const flightHdrRe = /(\d+h\s+\d+m)\s*\|\s*(Direct|\d+\s*(?:stop|change)s?)/i;
  const airlineRe = /Flying with\s*\n?\s*([^\n|]+?)\s*(?:\n\+\d+\s*)?\n?\s*\|\s*([A-Z]{2}\d+)/;

  const flights = [];
  for (const blk of blocks) {
    const hdr = blk.match(flightHdrRe);
    if (!hdr) continue;
    const isDirect = /^direct$/i.test(hdr[2].trim());
    if (!isDirect) continue;  // DIRECT-ONLY filter
    const al = blk.match(airlineRe);
    const fc = [];
    let c;
    while ((c = cabinRe.exec(blk)) !== null) {
      fc.push({cabin: c[1], pts: parseInt(c[2].replace(/,/g, ""), 10), tax: c[3]});
    }
    flights.push({
      airline: al ? al[1].trim() : "Unknown",
      flightNum: al ? al[2] : "",
      duration: hdr[1],
      direct: true,
      cabins: fc,
    });
  }

  // Compat layer: cheapest per cabin across direct flights, normalized to VA cabin names
  const cabinAlias = c => (c === "Main Cabin" ? "Economy Classic" : c);
  const minByCabin = {};
  for (const f of flights) {
    for (const c of f.cabins) {
      const k = cabinAlias(c.cabin);
      if (!minByCabin[k] || minByCabin[k].pts > c.pts) {
        minByCabin[k] = {cabin: k, pts: c.pts, tax: c.tax};
      }
    }
  }
  return JSON.stringify({url: location.href, pairs, cabins: Object.values(minByCabin), flights});
})()
