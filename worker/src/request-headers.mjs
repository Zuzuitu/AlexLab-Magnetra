// Matches the original Android NetworkClient.USER_AGENT on the upstream baseline.
// Do not modernize the browser version automatically: provider compatibility matters.
export const SOURCE_USER_AGENT =
  "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36";

export const SOURCE_HEADERS = Object.freeze({
  "user-agent": SOURCE_USER_AGENT,
  "accept-language": "en-US,en;q=0.9"
});
