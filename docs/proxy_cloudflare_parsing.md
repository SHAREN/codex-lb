# Cloudflare Evasion and Proxy URL Parsing Notes

## 1. URL Parsing & Special Characters (Semicolons)
When passing SOCKS5 proxy strings through `aiohttp_socks` and `websockets` (which internally use Python's standard `urllib.parse`), special characters in usernames/passwords (like `;`, `:`, `@`, `!`) can abruptly truncate the parsing buffer.

### Solution implemented
The code in `codex-lb` (`app/core/clients/account_http_default_provider.py` and probes) has been patched to explicitly run `urllib.parse.unquote` on the credentials extracted from the database. 

**Web Admin Usage**: When entering proxies via the web dashboard or inserting them into `account-proxy-map.json`, always URL-encode special characters. 
For example:
- Replace `;` with `%3B` 
- Replace `!` with `%21`

A user containing a semicolon: `fbab51361598f577c839__cr.my;anon.1` MUST be inserted as `fbab51361598f577c839__cr.my%3Banon.1`. The python unquoter will decode it right before TLS/SOCKS handshakes. Validation regexes `pattern="\d*"` in frontend forms have also been relaxed to allow dynamic ports.

## 2. Cloudflare managed challenge (403 Forbidden) vs 401 Unauthorized
For rotating residential proxies (like `cr.my`), Cloudflare strictly monitors the `User-Agent` and header fingerprint:

- **Missing/Vanilla curl headers:** Throw a hard `403 Forbidden` (`cf-mitigated: challenge`) demanding JS execution, blocking `codex-lb` connection entirely (resulting in `server disconnected` or `proxy_unreachable` tracker blocks).
- **Realistic Browser/Plugin headers:** (e.g. `Sec-Ch-Ua`, `Accept-Language`, `User-Agent: Mozilla/5.0...`) bypass the Cloudflare heuristic and hit the backend-api. An OpenAI `401 Unauthorized` without a payload response implies a *perfect proxy bypass*, meaning traffic reached the Auth server. `Codex-lb` handles headers accurately mimicking the official Copilot/Chat clients.
