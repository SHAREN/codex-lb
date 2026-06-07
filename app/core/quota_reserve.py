from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

QuotaReserveWindow = Literal["primary", "secondary"]
INTERNAL_QUOTA_RESERVE_ERROR_CODE = "internal_quota_reserve"
INTERNAL_QUOTA_RESERVE_ERROR_MESSAGE = "No accounts available: all eligible accounts are held by internal quota reserve"


@dataclass(frozen=True, slots=True)
class QuotaReserveConfig:
    enabled: bool
    primary_percent: float
    secondary_percent: float


@dataclass(frozen=True, slots=True)
class QuotaReserveEvaluation:
    held: bool
    windows: tuple[QuotaReserveWindow, ...]

    @property
    def reason(self) -> str | None:
        return INTERNAL_QUOTA_RESERVE_ERROR_CODE if self.held else None


def evaluate_quota_reserve(
    *,
    primary_used_percent: float | None,
    secondary_used_percent: float | None,
    config: QuotaReserveConfig,
) -> QuotaReserveEvaluation:
    if not config.enabled:
        return QuotaReserveEvaluation(held=False, windows=())

    windows: list[QuotaReserveWindow] = []
    if _window_is_held(primary_used_percent, config.primary_percent):
        windows.append("primary")
    if _window_is_held(secondary_used_percent, config.secondary_percent):
        windows.append("secondary")
    return QuotaReserveEvaluation(held=bool(windows), windows=tuple(windows))


def _window_is_held(used_percent: float | None, reserve_percent: float) -> bool:
    if used_percent is None or reserve_percent <= 0.0:
        return False
    remaining_percent = 100.0 - float(used_percent)
    return remaining_percent <= float(reserve_percent)
