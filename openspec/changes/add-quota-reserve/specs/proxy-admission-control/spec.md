## ADDED Requirements

### Requirement: Internal quota reserve blocks routing before upstream quota reaches zero

When dashboard quota reserve is enabled, the proxy MUST exclude otherwise selectable accounts from account selection when known usage shows either configured quota window at or below the operator reserve. The primary reserve SHALL compare `100 - primary_used_percent` with `quota_reserve_primary_percent`; the secondary reserve SHALL compare `100 - secondary_used_percent` with `quota_reserve_secondary_percent`. Equality MUST block routing.

The reserve guard MUST NOT mutate the persisted account status, and accounts held by reserve MUST remain recoverable by later usage refreshes or settings changes without requiring manual status repair.

#### Scenario: Primary reserve blocks at equality
- **GIVEN** quota reserve is enabled with a primary reserve of `3%`
- **AND** an active account has known primary usage of `97%`
- **WHEN** proxy account selection evaluates candidates
- **THEN** that account is excluded from selection
- **AND** its persisted account status remains `active`

#### Scenario: Secondary reserve blocks at equality
- **GIVEN** quota reserve is enabled with a secondary reserve of `1%`
- **AND** an active account has known secondary usage of `99%`
- **WHEN** proxy account selection evaluates candidates
- **THEN** that account is excluded from selection
- **AND** its persisted account status remains `active`

#### Scenario: Missing usage window does not block
- **GIVEN** quota reserve is enabled with both primary and secondary reserves configured
- **AND** an active account has known primary usage below the primary reserve threshold
- **AND** no known secondary usage window
- **WHEN** proxy account selection evaluates candidates
- **THEN** the secondary reserve rule is ignored for that account

#### Scenario: All candidates held by quota reserve returns explicit local failure
- **GIVEN** quota reserve is enabled
- **AND** every otherwise eligible candidate is held by the internal quota reserve
- **WHEN** proxy account selection evaluates candidates
- **THEN** selection fails with error code `internal_quota_reserve`
- **AND** the proxy does not fall back to spending the reserved quota

### Requirement: Quota reserve overrides sticky and scoped routing affinity

The quota reserve guard MUST apply before sticky-session reuse, prompt-cache affinity reuse, Codex-session affinity reuse, and API-key account assignment selection. Sticky affinity MUST NOT route to a reserve-held account, even when the sticky mapping points only to that account.

#### Scenario: Sticky account held by reserve is released for another account
- **GIVEN** a sticky mapping points to account A
- **AND** quota reserve holds account A
- **AND** account B remains eligible
- **WHEN** proxy account selection evaluates the sticky request
- **THEN** account B may be selected
- **AND** account A is not selected by the sticky mapping

#### Scenario: API-key scoped account held by reserve fails locally
- **GIVEN** an API key is scoped to a single account
- **AND** quota reserve holds that account
- **WHEN** a request authenticated by that API key selects an account
- **THEN** selection fails with error code `internal_quota_reserve`

### Requirement: Quota reserve failover isolates per-account SOCKS egress

When quota reserve rejects a preferred account and the proxy falls back to another eligible account, the proxy MUST force-close the rejected account's cached per-account SOCKS HTTP/WebSocket egress context before opening the fallback account connection. The fallback attempt MUST build a fresh account egress context and MUST NOT reuse a SOCKS connector or TCP pool from the rejected account.

#### Scenario: Preferred account held by reserve falls back through fresh SOCKS egress
- **GIVEN** account A is the preferred bridge or websocket account and has a configured SOCKS proxy
- **AND** quota reserve holds account A
- **AND** account B remains eligible
- **WHEN** the proxy falls back from account A to account B
- **THEN** account A's cached per-account egress client is force-closed before fallback
- **AND** account B's upstream connection is opened with a fresh account egress context

#### Scenario: Retryable SOCKS connect failure during bridge reattach clears stale egress
- **GIVEN** an HTTP bridge reattach is retrying a preferred account through a SOCKS proxy
- **AND** the preferred account connection fails with a retryable SOCKS connect error before visible output
- **WHEN** the proxy retries or fails over
- **THEN** the preferred account's cached SOCKS egress client is force-closed before the next attempt
