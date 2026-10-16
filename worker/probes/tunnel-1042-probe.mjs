// Optional TEMPORARY Cloudflare runtime diagnostic. Never the production Worker.
// No credentials, magnets, IMDb values, arbitrary URL input, or response bodies.
// Must run in the alexlab.media zone to assess same-zone fetch behavior.
export const TARGET = "https://magnetra-rock64.alexlab.media/healthz";
const ERROR_BODY_LIMIT = 8192;

async function has1042Code(response) {
  if (!response.body) return false;
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let bytes = 0;
  let snippet = "";
  try {
    while (bytes < ERROR_BODY_LIMIT) {
      const {done, value} = await reader.read();
      if (done) break;
      const slice = value.subarray(0, ERROR_BODY_LIMIT - bytes);
      bytes += slice.byteLength;
      snippet += decoder.decode(slice, {stream: true});
    }
    snippet += decoder.decode();
  } finally {
    try { await reader.cancel(); } catch {}
  }
  return /\b1042\b/.test(snippet);
}

export async function probeTunnel(transport = fetch) {
  let response;
  try {
    response = await transport(TARGET, {
      method: "GET",
      redirect: "manual",
      headers: {accept: "application/json"},
      signal: AbortSignal.timeout(8000)
    });
  } catch (error) {
    const name = String(error?.name || "");
    const message = String(error?.message || "");
    if (/\b1042\b/.test(message))
      return {result: "CLOUDFLARE_1042", status: null};
    if (name === "TimeoutError" || name === "AbortError")
      return {result: "TIMEOUT", status: null};
    return {result: "TRANSPORT_ERROR", status: null};
  }
  const status = response.status;
  if (status === 401)
    return {result: "PASS_UNAUTHENTICATED_401", status};
  if (status >= 300 && status < 400)
    return {result: "UNEXPECTED_REDIRECT", status};
  if ([403, 500, 502, 503, 530].includes(status)) {
    try {
      if (await has1042Code(response))
        return {result: "CLOUDFLARE_1042", status};
    } catch {
      return {result: "ERROR_BODY_UNREADABLE", status};
    }
  }
  return {result: "UNEXPECTED_HTTP", status};
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method !== "GET" || url.pathname !== "/probe" || url.search)
      return new Response(null, {status: 404});
    const result = await probeTunnel();
    return new Response(JSON.stringify(result), {
      status: 200,
      headers: {
        "content-type": "application/json; charset=utf-8",
        "cache-control": "private, no-store",
        "x-robots-tag": "noindex",
        "x-content-type-options": "nosniff"
      }
    });
  }
};
