// Immutable 46-provider production observation from GitHub Actions run 38373699387 (2026-10-13).
// One benign "ubuntu" test per indexer; this is NOT live uptime.
// Ranking is based on this sample plus this-browser-session outcomes; no deletions.
export const SOURCE_AUDIT = Object.freeze({
  observedAt: "2026-10-13T09:05:03Z",
  query: "ubuntu",
  workflowRunId: 38373699387,
  outcomes: {
    "anirena": {
      "state": "error",
      "code": "REDIRECT_BLOCKED"
    },
    "anilibria": {
      "state": "empty-unverified",
      "count": 0
    },
    "animetosho": {
      "state": "empty-unverified",
      "count": 0
    },
    "bangumimoe": {
      "state": "empty-unverified",
      "count": 0
    },
    "bitsearch": {
      "state": "error",
      "code": "REDIRECT_BLOCKED"
    },
    "audiobookbay": {
      "state": "results",
      "count": 9
    },
    "btdigg": {
      "state": "results",
      "count": 10
    },
    "bt4g": {
      "state": "error",
      "code": "ACCESS_DENIED"
    },
    "dmhy": {
      "state": "results",
      "count": 2
    },
    "blueroms": {
      "state": "empty-unverified",
      "count": 0
    },
    "extdotto": {
      "state": "error",
      "code": "ACCESS_DENIED"
    },
    "eztvx": {
      "state": "error",
      "code": "ACCESS_DENIED"
    },
    "filemood": {
      "state": "empty-unverified",
      "count": 0
    },
    "btsow": {
      "state": "results",
      "count": 30
    },
    "internetarchive": {
      "state": "results",
      "count": 100
    },
    "fitgirlrepacks": {
      "state": "empty-unverified",
      "count": 0
    },
    "limetorrents": {
      "state": "error",
      "code": "REDIRECT_BLOCKED"
    },
    "knaben": {
      "state": "results",
      "count": 100
    },
    "linuxtracker": {
      "state": "results",
      "count": 25
    },
    "megapeer": {
      "state": "empty-unverified",
      "count": 0
    },
    "mypornclub": {
      "state": "error",
      "code": "ACCESS_DENIED"
    },
    "mikanproject": {
      "state": "empty-unverified",
      "count": 0
    },
    "nonameclub": {
      "state": "results",
      "count": 50
    },
    "nekobt": {
      "state": "empty-unverified",
      "count": 0
    },
    "oxtorrent": {
      "state": "error",
      "code": "ACCESS_DENIED"
    },
    "nyaasi": {
      "state": "error",
      "code": "RATE_LIMIT"
    },
    "subsplease": {
      "state": "empty-unverified",
      "count": 0
    },
    "epublibre": {
      "state": "results",
      "count": 1
    },
    "rutorinfo": {
      "state": "empty-unverified",
      "count": 0
    },
    "thepiratebay": {
      "state": "results",
      "count": 100
    },
    "1337x": {
      "state": "error",
      "code": "ACCESS_DENIED"
    },
    "therarbag": {
      "state": "results",
      "count": 39
    },
    "tokyotoshokan": {
      "state": "error",
      "code": "ACCESS_DENIED"
    },
    "torrent9": {
      "state": "error",
      "code": "ACCESS_DENIED"
    },
    "torrentdatabase": {
      "state": "error",
      "code": "ACCESS_DENIED"
    },
    "torrentdownloads": {
      "state": "error",
      "code": "ACCESS_DENIED"
    },
    "torrentkitty": {
      "state": "error",
      "code": "ACCESS_DENIED"
    },
    "torrentdownloadinfo": {
      "state": "error",
      "code": "REDIRECT_BLOCKED"
    },
    "torrentscsv": {
      "state": "results",
      "count": 25
    },
    "uindex": {
      "state": "error",
      "code": "ACCESS_DENIED"
    },
    "torrentz": {
      "state": "error",
      "code": "UPSTREAM_ERROR"
    },
    "xxxclub": {
      "state": "error",
      "code": "UPSTREAM_ERROR"
    },
    "ytsmx": {
      "state": "empty-unverified",
      "count": 0
    },
    "0magnet": {
      "state": "results",
      "count": 29
    },
    "sukebeinyaa": {
      "state": "error",
      "code": "TIMEOUT"
    },
    "xxxtracker": {
      "state": "error",
      "code": "TIMEOUT"
    }
  }
});
export function auditFor(id) {
  const value=SOURCE_AUDIT.outcomes[id];
  return value ? Object.freeze({...value}) : null;
}
