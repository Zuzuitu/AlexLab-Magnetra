import {releaseFallbackIntent} from "./release-fallback.mjs";
// Exactly the owner's 11 curated visible PWA sources. The remaining 35
// backend adapters remain unchanged and are NOT re-enabled in the UI.
export const CURATED_EXACT_PROVIDER_IDS=Object.freeze([
 "0magnet","audiobookbay","btdigg","internetarchive","knaben",
 "nonameclub","oxtorrent","thepiratebay","therarbag","torrent9",
 "torrentscsv"
]);
const EXACT_SET=new Set(CURATED_EXACT_PROVIDER_IDS);

// One origin search per provider, never a hidden series of fallback requests.
// A broad title/year request on generic indexers can return x265, x264 and
// 720p records in the SAME response. BTDigg retains the exact filename
// proven by the owner; broader BTDigg coverage is not promised.
export function sourceQueryFor(id,original,plan){
 if(!EXACT_SET.has(id))return plan.searchedAs;
 if(id==="btdigg")return original;
 return releaseFallbackIntent(original,plan)?plan.searchedAs:original;
}
export function sourceQueryModeFor(id,original,plan){
 if(!EXACT_SET.has(id))return plan.broadened?"title":"literal";
 if(id==="btdigg")return "all-terms-literal";
 return releaseFallbackIntent(original,plan)?"title-ranked-fallback":"all-terms-literal";
}
