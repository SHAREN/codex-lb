from __future__ import annotations

from cryptography.fernet import Fernet

from app.core.crypto import TokenEncryptor
from app.core.quota_reserve import QuotaReserveConfig
from app.db.models import Account, AccountStatus, UsageHistory
from app.modules.accounts.mappers import _account_to_summary, _effective_status_from_usage


def _account(status: AccountStatus = AccountStatus.QUOTA_EXCEEDED) -> Account:
    return Account(
        id="account-1",
        email="account@example.com",
        plan_type="plus",
        access_token_encrypted=b"",
        refresh_token_encrypted=b"",
        id_token_encrypted=b"",
        status=status,
        reset_at=1_700_003_600,
        limit_warmup_enabled=False,
    )


def _primary_usage(**overrides) -> UsageHistory:
    values = {
        "account_id": "account-1",
        "window": "primary",
        "used_percent": 40.0,
        "reset_at": None,
        "window_minutes": 300,
    }
    values.update(overrides)
    return UsageHistory(**values)


def _secondary_usage(**overrides) -> UsageHistory:
    values = {
        "account_id": "account-1",
        "window": "secondary",
        "used_percent": 100.0,
        "reset_at": 1_700_003_600,
        "window_minutes": 10080,
    }
    values.update(overrides)
    return UsageHistory(**values)


def test_effective_status_uses_secondary_credits_to_reactivate_quota_exceeded_account() -> None:
    account = _account()
    primary = _primary_usage()
    secondary = _secondary_usage(
        credits_has=False,
        credits_unlimited=False,
        credits_balance=25.0,
    )

    assert (
        _effective_status_from_usage(
            account,
            primary,
            primary.used_percent,
            secondary,
            secondary.used_percent,
        )
        == AccountStatus.ACTIVE
    )


def test_effective_status_uses_primary_credits_when_secondary_has_no_credit_fields() -> None:
    account = _account()
    primary = _primary_usage(credits_balance=25.0)
    secondary = _secondary_usage()

    assert (
        _effective_status_from_usage(
            account,
            primary,
            primary.used_percent,
            secondary,
            secondary.used_percent,
        )
        == AccountStatus.ACTIVE
    )


def test_effective_status_keeps_primary_rate_limit_precedence_with_usable_credits() -> None:
    account = _account(AccountStatus.ACTIVE)
    primary = _primary_usage(used_percent=100.0, reset_at=1_700_000_300, credits_balance=25.0)
    secondary = _secondary_usage(used_percent=100.0, credits_balance=25.0)

    assert (
        _effective_status_from_usage(
            account,
            primary,
            primary.used_percent,
            secondary,
            secondary.used_percent,
        )
        == AccountStatus.RATE_LIMITED
    )


def test_effective_status_keeps_paused_account_paused_with_usable_credits() -> None:
    account = _account(AccountStatus.PAUSED)
    primary = _primary_usage(credits_balance=25.0)
    secondary = _secondary_usage(credits_balance=25.0)

    assert (
        _effective_status_from_usage(
            account,
            primary,
            primary.used_percent,
            secondary,
            secondary.used_percent,
        )
        == AccountStatus.PAUSED
    )


def test_free_account_exposes_reported_primary_30d_usage() -> None:
    account = _account(AccountStatus.ACTIVE)
    account.plan_type = "free"
    usage = _primary_usage(used_percent=5.0, reset_at=1_783_098_041, window_minutes=43_200)

    summary = _account_to_summary(
        account,
        usage,
        None,
        None,
        None,
        None,
        TokenEncryptor(key=Fernet.generate_key()),
        include_auth=False,
    )

    assert summary.usage is not None
    assert summary.usage.primary_remaining_percent == 95.0
    assert summary.window_minutes_primary == 43_200
    assert summary.reset_at_primary is not None
    assert summary.usage.secondary_remaining_percent is None
    assert summary.window_minutes_secondary is None
    assert summary.status == AccountStatus.ACTIVE.value


def test_effective_status_recovers_quota_exceeded_when_only_primary_has_available_quota() -> None:
    account = _account(AccountStatus.QUOTA_EXCEEDED)
    primary = _primary_usage(used_percent=5.0, reset_at=1_783_098_041, window_minutes=43_200)

    assert (
        _effective_status_from_usage(
            account,
            primary,
            primary.used_percent,
            None,
            None,
        )
        == AccountStatus.ACTIVE
    )


def test_account_summary_marks_active_account_held_by_quota_reserve_without_status_change() -> None:
    account = _account(AccountStatus.ACTIVE)
    primary = _primary_usage(used_percent=97.0)
    secondary = _secondary_usage(used_percent=50.0)

    summary = _account_to_summary(
        account,
        primary,
        secondary,
        None,
        None,
        None,
        TokenEncryptor(key=Fernet.generate_key()),
        quota_reserve_config=QuotaReserveConfig(
            enabled=True,
            primary_percent=3.0,
            secondary_percent=1.0,
        ),
        include_auth=False,
    )

    assert summary.status == "active"
    assert summary.routing_availability.available is False
    assert summary.routing_availability.reason == "internal_quota_reserve"
    assert summary.routing_availability.held_windows == ["primary"]
