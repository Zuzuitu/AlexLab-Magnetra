// Narrow source-specific diagnostics: emit only finite enums, never the
// untrusted provider URL, response body, raw hash, HTML or exception content.
export function classifyTheRarBgResolveError(value){
 const msg=String(value?.message||value||"");
 const http=/^provider HTTP (\d{3})$/.exec(msg);
 if(http){
  const code=Number(http[1]);
  if([403,404,429,500,502,503,504].includes(code))return "SOURCE_HTTP_"+code;
  return "SOURCE_HTTP_OTHER";
 }
 if(/provider (?:anti-bot challenge|challenge requires a browser session)/i.test(msg))return "SOURCE_CHALLENGE";
 if(/provider details page contains no supported magnet link/i.test(msg))return "DETAIL_NO_BTih";
 if(/provider page too large/i.test(msg))return "SOURCE_PAGE_TOO_LARGE";
 if(/provider redirected|provider redirect|redirect left the approved origin/i.test(msg))return "SOURCE_REDIRECT";
 if(/details URL not allowed|outside provider allowlist/i.test(msg))return "DETAIL_URL_REJECTED";
 if(/AbortError|TimeoutError|timed out|timeout|The operation was aborted/i.test(msg))return "SOURCE_TIMEOUT";
 if(/fetch failed|network|connection|socket|TLS/i.test(msg))return "SOURCE_NETWORK";
 if(/HTMLRewriter runtime required/i.test(msg))return "WORKER_RUNTIME";
 return "RESOLVE_UNKNOWN";
}
