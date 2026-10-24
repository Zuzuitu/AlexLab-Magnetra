# NoNameClub exact anonymous source read-only differential — 25 October 2026

Owner physically accepted the recent 0Magnet iPhone fix ("Fixuo0magnet functionewza")
and provided two Safari screenshots:
- Original public NoNameClub page https://nnmclub.to/forum/viewtopic.php?t=1896364
  for Lupin S04; site shows image marked magnet and a torrent download
  affordance without owner account.
- Magnetra PWA NoNameClub results show "Sursă indisponibilă" after tapping
  Obține magnet. Do not assume the requested icon is itself an inline link.

Verified repo code: NoNameClub uses a source-owned original details URL,
`worker/src/legacy-specs.mjs` has `magnetDetails: "a[href^='magnet:']"`
and `resolution: "page"`; unlike 0Magnet, no magnetSource is configured,
so changing PWA source priority would be unsupported.

Official NoNameClub site explicitly advertises some magnet-marked public
releases that can be used without account. Its "view available to registered"
message in release description does NOT prove public magnet is forbidden.

Safe, owner-approved one-shot diagnostic: a single public GET of exact
original URL and, if source HTTP 200 and not challenged, one metadata-only
POST to the existing https://index.alexlab.media/api/resolve with
`{"provider":"nonameclub","details":"<exact original>"}`.
Classify raw HTML inline magnet anchor, icon-only links, onclick, and
prod error codes without outputting any magnet/hash, source body, title,
cookie, passkey, URL in logs. No torrent downloads, Flud/Shield, proxy,
captcha/challenge bypass, repeats, new infrastructure, uploads, or paid APIs.
No PWA code fix is claimed or deployed by diagnostic.

After observing real outcome, design smallest nonameclub-only regression-tested
fix if evidence permits; preserve original TheRarBg/0Magnet stable production
and rollback and 46 provider identity/12 visible picker.
