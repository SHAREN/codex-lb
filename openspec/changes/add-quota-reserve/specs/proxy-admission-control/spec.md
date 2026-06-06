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
