"""Verify reviewed static HTML modulo only Cloudflare's trailing analytics injection.

A Cloudflare edge normally redirects /index.html -> / (HTTP 307), and
dynamically inserts its RUM script before the last </body>. We never drop
arbitrary HTML differences, only that exact narrowly scoped insertion.
"""
import re

class HTMLAssetMismatch(ValueError):
    pass

def verify_reviewed_html(raw:bytes,served:bytes)->str:
    if raw==served:
        return "EXACT"
    anchor=b"</body>"
    pos=raw.rfind(anchor)
    if pos<0 or not raw.endswith(b"</body>\n</html>"):
        raise HTMLAssetMismatch("UNEXPECTED_SOURCE_HTML_END")
    before,after=raw[:pos],raw[pos:]
    if not served.startswith(before) or not served.endswith(after):
        raise HTMLAssetMismatch("NON_CLOUDFLARE_HTML_DIFFERENCE")
    inserted=served[len(before):len(served)-len(after)]
    low=inserted.lower()
    if not 200<=len(inserted)<=2400:
        raise HTMLAssetMismatch("UNEXPECTED_HTML_INJECTION_LENGTH")
    required=(b"static.cloudflareinsights.com",b"beacon.min.js",
              b"data-cf-beacon",b"/cdn-cgi/",b"<script",b"</script")
    if any(marker not in low for marker in required):
        raise HTMLAssetMismatch("UNKNOWN_NON_CLOUDFLARE_HTML_INJECTION")
    tags=re.findall(rb"<\s*(?:/)?\s*([a-z][a-z0-9]*)",low)
    if not tags or any(tag!=b"script" for tag in tags):
        raise HTMLAssetMismatch("UNEXPECTED_HTML_INJECTION_TAGS")
    return "EXACT_PLUS_CLOUDFLARE_BEACON"
