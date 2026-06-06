## Why

Operators want to preserve a small internal reserve of upstream account quota so Codex accounts are not routed all the way to 0% remaining. Existing account statuses represent real upstream or operator lifecycle state, so using `rate_limited` or `quota_exceeded` for this operator reserve would make recovery and persistence semantics misleading.

## What Changes

- Add dashboard settings for an optional quota reserve guard with independent primary-window and secondary-window reserve percentages.
- Exclude accounts from proxy selection when fresh known usage shows remaining quota at or below the configured reserve, without mutating the persisted account status.
- Return an explicit local 429-style selection failure when every otherwise eligible account is held by the internal quota reserve.
- Surface reserve-held accounts in the dashboard account list as routing-blocked by quota reserve while preserving their real account status.

## Impact

- Backend settings schema and database migrations gain three disabled-by-default quota reserve fields.
- Proxy account selection gets a hard pre-selection routing filter that applies before normal and sticky selection, including API-key-scoped pools.
- Accounts API responses gain display-only routing availability metadata for dashboard badges and filters.
- Frontend Settings and Accounts views gain quota reserve controls and reserve-held display treatment.
