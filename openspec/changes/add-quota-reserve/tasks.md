## 1. OpenSpec

- [x] 1.1 Add OpenSpec delta requirements for quota reserve routing, dashboard display, and database defaults.

## 2. Backend

- [x] 2.1 Add quota reserve fields to `DashboardSettings` and an Alembic migration with disabled/zero defaults.
- [x] 2.2 Thread quota reserve fields through settings schemas, repository, and service.
- [x] 2.3 Add a hard internal quota reserve filter before account selection without mutating persisted account status.
- [x] 2.4 Ensure sticky sessions and API-key scoped account pools cannot bypass the reserve filter.
- [x] 2.5 Add accounts API display metadata for reserve-held active accounts.

## 3. Frontend

- [x] 3.1 Add settings schema/payload support for quota reserve fields.
- [x] 3.2 Add a Settings page quota reserve section after Routing.
- [x] 3.3 Show reserve-held accounts as routing-blocked in the Accounts list without changing account actions that depend on real status.

## 4. Verification

- [x] 4.1 Add backend tests for settings defaults/update and routing reserve behavior.
- [x] 4.2 Add frontend schema/component tests for quota reserve settings and account display.
- [x] 4.3 Run focused backend and frontend tests.
- [x] 4.4 Attempt OpenSpec validation (`openspec` CLI unavailable in this environment).
