# Magnetra owner 0Magnet safe differential (24 October 2026)

Owner reports iPhone PWA error "Sursă indisponibilă" when using **0Magnet**
on the 2.26 GB Little.House.on.the.Prairie.2026 result, while the original
source-owned 9mag.net page displays a magnet input value for the same item.
The screenshots establish an incident, not the specific cause.

Authorized scope: one guarded, automatic-on-merge **read-only** diagnostic,
only after all four PR checks pass. The script may do at most two distinct
search GET requests scoped to the original provider in the production PWA,
one bounded GET of the source-owned same-card details page, and one PWA
/api/resolve POST that performs metadata lookup **only**. No client send
command, no Shield/Flud, no .torrent fetch, no download, no retries,
no rate-limit bypass, no broad provider scan, no DNS/Worker/Rock64 changes,
no deployment percentage changes or secret disclosure.

Output MUST be stage categories and numeric statuses only; never print
magnet, BTIH, title, source detail URL, raw HTML, tokens or response JSON.
If the owner's same card cannot be distinguished, stop without a candidate
magnet or guessing another record. One-shot activation only.
