// Matches the original Android NetworkClient.USER_AGENT on the upstream baseline.
// Do not modernize the browser version automatically: provider compatibility matters.
export const SOURCE_USER_AGENT =
  "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36";

export const SOURCE_HEADERS = Object.freeze({
  "user-agent": SOURCE_USER_AGENT,
  "accept-language": "en-US,en;q=0.9"
});

/** Allow at most one HTTPS redirect inside the original provider origin. */
export async function fetchProviderSameOrigin(url,options={},fetcher=fetch) {
  const original=new URL(url);
  if(original.protocol!=="https:")throw Error("Provider URL must use HTTPS");
  let response=await fetcher(url,{...options,redirect:"manual"});
  if(response.status>=300 && response.status<400){
    const location=response.headers.get("location");
    if(!location)throw Error("Provider redirect is missing Location");
    let target;
    try{target=new URL(location,url);}catch{throw Error("Invalid provider redirect");}
    if(target.origin!==original.origin || target.protocol!=="https:" ||
       target.username || target.password || target.hash || target.href.length>1500)
      throw Error("Provider redirect left the approved origin");
    response=await fetcher(target.toString(),{...options,redirect:"manual"});
  }
  if(response.status>=300 && response.status<400)
    throw Error("Provider redirected repeatedly; browser challenge may be required");
  return response;
}
