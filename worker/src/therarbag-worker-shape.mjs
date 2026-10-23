// Bounded, non-sensitive shape diagnosis for a failed TheRarBg Resolve.
// Enumerates only what the same Worker fetch/parser observed; never exports
// URL, torrent title, source HTML, infohash, full magnet or tokens.
const STAGES=Object.freeze(new Set([
  "REWRITER_MATCHED_BUT_REJECTED",
  "MAGNET_HTML_PRESENT_REWRITER_MISSED",
  "LABELED_BTIH_PRESENT_FALLBACK_REJECTED",
  "INFO_HASH_LABEL_VALUE_UNAVAILABLE",
  "MAGNET_CONTROL_WITHOUT_MARKUP_LINK",
  "SOURCE_DETAIL_MARKERS_ABSENT",
  "SOURCE_HTML_UNEXPECTED"
]));
export const THERARBAG_SHAPE_STAGES=STAGES;

export function classifyTheRarBgWorkerHtmlShape(html,rewriterMatched=0){
  if(typeof html!=="string"||html.length===0||html.length>3_000_000)
    return "SOURCE_HTML_UNEXPECTED";
  // Do not inspect executable or hidden/commented content; the classification
  // must describe candidate metadata, not strings from a JS bundle or advert.
  const safe=html
    .replace(/<(script|style|noscript|template)\b[^>]*>[\s\S]*?<\/\1\s*>/gi," ")
    .replace(/<!--[\s\S]*?-->/g," ");
  const visible=safe.replace(/<[^>]*>/g," ")
    .replace(/&nbsp;|&#(?:160|xA0);/gi," ")
    .replace(/&colon;|&#(?:58|x3A);/gi,":")
    .replace(/\s+/g," ");
  if(rewriterMatched>0)return "REWRITER_MATCHED_BUT_REJECTED";
  // This catches valid-looking href markup that HTMLRewriter did not select,
  // without copying the href, query, hash or title to the diagnostic result.
  if(/<a\b[^>]*\bhref\s*=\s*(?:"magnet:\?|'magnet:\?)/i.test(safe))
    return "MAGNET_HTML_PRESENT_REWRITER_MISSED";
  if(/\bInfo\s*Hash\s*:\s*[a-f0-9]{40}\b/i.test(visible))
    return "LABELED_BTIH_PRESENT_FALLBACK_REJECTED";
  if(/\bInfo\s*Hash\s*:/i.test(visible))
    return "INFO_HASH_LABEL_VALUE_UNAVAILABLE";
  if(/\bMagnet\s+Download\b/i.test(visible))
    return "MAGNET_CONTROL_WITHOUT_MARKUP_LINK";
  if(/<html\b|<main\b|<body\b/i.test(safe))
    return "SOURCE_DETAIL_MARKERS_ABSENT";
  return "SOURCE_HTML_UNEXPECTED";
}

// Fixed route and an opt-in request header prevent ordinary UI requests from
// acquiring extra fields. This adds no new fetch, origin, authentication flow,
// cookies, query fallback or mutable state. The original /api/resolve remains.
const OWNER_TESTED_URL=
  "https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/";
export function allowTheRarBgWorkerShapeDiagnostic(request,provider,details){
  return provider==="therarbag"&&details===OWNER_TESTED_URL&&
    request.headers.get("x-magnetra-shape-diagnostic")==="20261024-readonly-exact";
}
