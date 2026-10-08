// Immutable observation from GitHub deploy run 37816874771 (2026-10-08).
// This is NOT a live health feed or an uptime guarantee. Do not replace this
// snapshot with guessed status; update only after a recorded full source audit.
export const SOURCE_AUDIT = Object.freeze({
  observedAt: "2026-10-08T17:29:37Z",
  query: "ubuntu",
  workflowRunId: 37816874771,
  outcomes: {
  "audiobookbay": {
    "state": "results",
    "count": 9
  },
  "dmhy": {
    "state": "results",
    "count": 2
  },
  "btsow": {
    "state": "results",
    "count": 30
  },
  "epublibre": {
    "state": "results",
    "count": 1
  },
  "internetarchive": {
    "state": "results",
    "count": 100
  },
  "knaben": {
    "state": "results",
    "count": 100
  },
  "linuxtracker": {
    "state": "results",
    "count": 25
  },
  "nonameclub": {
    "state": "results",
    "count": 50
  },
  "thepiratebay": {
    "state": "results",
    "count": 100
  },
  "therarbag": {
    "state": "results",
    "count": 39
  },
  "torrentscsv": {
    "state": "results",
    "count": 25
  },
  "0magnet": {
    "state": "results",
    "count": 29
  },
  "anilibria": {
    "state": "empty-unverified"
  },
  "animetosho": {
    "state": "empty-unverified"
  },
  "bangumimoe": {
    "state": "empty-unverified"
  },
  "blueroms": {
    "state": "empty-unverified"
  },
  "filemood": {
    "state": "empty-unverified"
  },
  "fitgirlrepacks": {
    "state": "empty-unverified"
  },
  "megapeer": {
    "state": "empty-unverified"
  },
  "mikanproject": {
    "state": "empty-unverified"
  },
  "nekobt": {
    "state": "empty-unverified"
  },
  "subsplease": {
    "state": "empty-unverified"
  },
  "rutorinfo": {
    "state": "empty-unverified"
  },
  "ytsmx": {
    "state": "empty-unverified"
  },
  "anirena": {
    "state": "error",
    "code": "REDIRECT_BLOCKED"
  },
  "bitsearch": {
    "state": "error",
    "code": "REDIRECT_BLOCKED"
  },
  "bt4g": {
    "state": "error",
    "code": "ACCESS_DENIED"
  },
  "extdotto": {
    "state": "error",
    "code": "ACCESS_DENIED"
  },
  "eztvx": {
    "state": "error",
    "code": "ACCESS_DENIED"
  },
  "btdigg": {
    "state": "error",
    "code": "TIMEOUT"
  },
  "limetorrents": {
    "state": "error",
    "code": "REDIRECT_BLOCKED"
  },
  "mypornclub": {
    "state": "error",
    "code": "ACCESS_DENIED"
  },
  "oxtorrent": {
    "state": "error",
    "code": "ACCESS_DENIED"
  },
  "nyaasi": {
    "state": "error",
    "code": "RATE_LIMIT"
  },
  "1337x": {
    "state": "error",
    "code": "ACCESS_DENIED"
  },
  "tokyotoshokan": {
    "state": "error",
    "code": "UNCLASSIFIED"
  },
  "torrent9": {
    "state": "error",
    "code": "ACCESS_DENIED"
  },
  "torrentdatabase": {
    "state": "error",
    "code": "ACCESS_DENIED"
  },
  "torrentdownloadinfo": {
    "state": "error",
    "code": "REDIRECT_BLOCKED"
  },
  "torrentdownloads": {
    "state": "error",
    "code": "ACCESS_DENIED"
  },
  "torrentkitty": {
    "state": "error",
    "code": "ACCESS_DENIED"
  },
  "torrentz": {
    "state": "error",
    "code": "UPSTREAM_ERROR"
  },
  "uindex": {
    "state": "error",
    "code": "ACCESS_DENIED"
  },
  "xxxclub": {
    "state": "error",
    "code": "UPSTREAM_ERROR"
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
