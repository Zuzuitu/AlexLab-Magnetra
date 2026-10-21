# Owner-approved Magnetra PWA source curation — AnimeTosho and Mikan

On 2026-10-21 the owner explicitly requested hiding AnimeTosho and Mikan, adding to the previous 17 indexers. This activation records approval to publish the reviewed 27-visible PWA while preserving all 46 original Worker and Android source adapters.

The one-shot workflow `.github/workflows/magnetra-hide-anime-mikan-one-shot.yml` is intentionally triggered only by a **new merged main push changing this file**, with commit marker `[magnetra-hide-anime-mikan-publish-20261021]`. A workflow file change alone never deploys. This release must start from the previously verified immutable split `9bbb227f-7f2a-4a9b-acac-ce8cae620c51@100%` / `c86c9a32-31fd-4952-86ed-b35f1763b342@0%`, confirm old public JS SHA prefix `0945914b2f7bf266` and all three binding names/types, and test the new immutable JS, CSS, HTML and all original 46 provider IDs at 0%, canary 5%, then 100%. Preserve previous 9bbb at 0% as rollback. Stop and do not retry blindly if any traffic/version/hash mismatch occurs.

No Cloudflare tokens written to repository, no Rock64/Tunnel/DNS/Flud modifications, no provider requests or torrents downloaded. A merged activation record is not proof of release success; verify the dedicated workflow run and public asset hashes first.
