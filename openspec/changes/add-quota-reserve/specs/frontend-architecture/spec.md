## ADDED Requirements

### Requirement: Settings page exposes quota reserve controls

The Settings page SHALL include a Quota reserve section immediately after routing settings. The section SHALL provide an enable toggle, a primary-window reserve percent input, and a secondary-window reserve percent input. The copy SHALL explain that routing stops when remaining quota reaches the configured reserve.

#### Scenario: Save quota reserve settings
- **WHEN** a user enables quota reserve and sets primary reserve to `3` and secondary reserve to `1`
- **THEN** the app calls `PUT /api/settings` with those quota reserve values
- **AND** the saved settings are reflected in the form

### Requirement: Accounts page distinguishes quota reserve display from persisted status

The Accounts page SHALL surface active accounts held by internal quota reserve as routing-blocked by quota reserve without changing account actions that depend on the persisted account status. Reserve-held accounts SHOULD use the same visual urgency family as rate-limited accounts while labeling the reason as quota reserve.

#### Scenario: Reserve-held active account shows quota reserve badge
- **GIVEN** an account response has `status: active`
- **AND** routing availability metadata identifies `internal_quota_reserve`
- **WHEN** the Accounts list renders the account
- **THEN** the status badge communicates quota reserve routing hold
- **AND** pause/resume controls still treat the account as active
