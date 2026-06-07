## ADDED Requirements

### Requirement: Quota reserve settings are disabled by default after migration

The database SHALL persist dashboard quota reserve settings with a disabled default and zero primary and secondary reserve percentages. Existing installations MUST observe unchanged routing behavior until an operator enables quota reserve.

#### Scenario: Existing settings row receives disabled quota reserve defaults
- **WHEN** the quota reserve settings migration is applied to a database with an existing dashboard settings row
- **THEN** `quota_reserve_enabled` defaults to false
- **AND** `quota_reserve_primary_percent` defaults to `0`
- **AND** `quota_reserve_secondary_percent` defaults to `0`
