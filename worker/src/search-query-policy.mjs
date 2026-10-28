import {releaseFallbackIntent} from "./release-fallback.mjs";
// Owner's 11 visible, curated PWA indexers are entitled to full release
// metadata in ONE upstream request. Keep a separate explicit list so the
// original 35 hidden adapters retain their existing compatible search route.
// This policy cannot alter user-requested quality/group matching: the global
// relevance gate always filters by the ORIGINAL query.
export const CURATED_EXACT_PROVIDER_IDS=Object.freeze([
 "0magnet","audiobookbay","btdigg","internetarchive","knaben",
 "nonameclub","oxtorrent","thepiratebay","therarbag","torrent9",
 "torrentscsv"
]);
const EXACT_SET=new Set(CURATED_EXACT_PROVIDER_IDS);

// Normalize ONLY a recognizable full release filename. Keep every term,
// including release group, audio, codec, quality, and year; normalize dots
// and other release separators to spaces for generic provider query engines.
// The sole confirmed exact punctuation-sensitive path is BTDigg, which keeps
// the owner's literal filename that was proven on the physical Rock64.
// No source probing, automatic fallback, additional requests or retries.
export function sourceQueryFor(id,original,plan){
 if(!EXACT_SET.has(id))return plan.searchedAs;
 // Owner's confirmed successful BTDigg request was the literal full release.
 if(id==="btdigg")return original;
 const fallback=releaseFallbackIntent(original,plan);
 if(fallback)return [fallback.titleQuery,...fallback.technicalTerms].join(" ");
 if(!plan.broadened)return original;
 const tokens=String(original).match(/[\p{L}\p{N}]+/gu);
 return tokens?.length?tokens.join(" "):original;
}
export function sourceQueryModeFor(id,original,plan){
 if(!EXACT_SET.has(id))return plan.broadened?"title":"literal";
 if(id==="btdigg")return "all-terms-literal";
 if(releaseFallbackIntent(original,plan))return "quality-terms-without-group";
 return plan.broadened?"all-terms-normalized":"all-terms-literal";
}
