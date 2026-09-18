"""Domain types shared by the reconcile engine and (later) the AWS-facing layers.

Kept dependency-free (stdlib only) so `reconcile/` can be unit-tested with no
AWS SDK, no network, and no Bedrock calls, per HANDOFF.md §11.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Optional

UTR_RE = re.compile(r"^\d{12}$")


class Verdict(str, Enum):
    """HANDOFF.md §7 per-photo verdicts, plus UNCLAIMED_CREDIT for credits with no claim."""

    NOT_SUCCESS = "NOT_SUCCESS"
    UNREADABLE = "UNREADABLE"
    DUPLICATE = "DUPLICATE"
    VERIFIED = "VERIFIED"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    PROBABLE = "PROBABLE"
    AMBIGUOUS = "AMBIGUOUS"
    NOT_FOUND = "NOT_FOUND"
    UNCLAIMED_CREDIT = "UNCLAIMED_CREDIT"


class ClaimState(str, Enum):
    """§9 CLAIM item `state` attribute."""

    FINAL = "final"
    PENDING_CONFIRM = "pending_confirm"


def _clean_utr(utr: Optional[str]) -> Optional[str]:
    """§7: "If `utr` doesn't match `^\\d{12}$`, set it to null." Never trust the model."""
    if utr is None:
        return None
    if UTR_RE.fullmatch(utr):
        return utr
    return None


def _clean_amount(amount: Optional[Decimal]) -> Optional[Decimal]:
    """§7: "If `amount_inr` isn't positive with at most 2 decimals, set it to null."""
    if amount is None:
        return None
    try:
        amount = Decimal(amount)
    except (InvalidOperation, TypeError):
        return None
    if amount <= 0:
        return None
    # at most 2 decimal places
    if amount != amount.quantize(Decimal("0.01")):
        return None
    return amount


@dataclass(frozen=True)
class PhotoExtraction:
    """One photo's Bedrock extraction (§7 schema), after code-side validation.

    Validation is enforced here (never trusted from the model) so any caller
    constructing this type gets the same guarantees, regardless of what the
    extraction Lambda already checked.
    """

    photo_id: str
    rider: str
    utr: Optional[str] = None
    amount_inr: Optional[Decimal] = None
    screen_time: Optional[datetime] = None
    payment_app: Optional[str] = None
    status_text: Optional[str] = None
    payee_name: Optional[str] = None
    notes: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "utr", _clean_utr(self.utr))
        object.__setattr__(self, "amount_inr", _clean_amount(self.amount_inr))


@dataclass(frozen=True)
class CreditRecord:
    """One CREDIT# row derived from the payment record (§9).

    `credit_key` is the UTR when present, or the `H#{sha256(...)}` hash key
    HANDOFF specifies for a row with no reference number.
    """

    credit_key: str
    amount: Decimal
    timestamp: Optional[datetime] = None
    utr: Optional[str] = None
    narration: str = ""


@dataclass(frozen=True)
class ClaimInfo:
    """A CLAIM# row: which photo currently owns a credit_key, and how."""

    credit_key: str
    photo_id: str
    shift_id: str
    rider: str
    state: ClaimState


@dataclass
class PhotoResult:
    photo: PhotoExtraction
    verdict: Verdict
    claimed_credit_key: Optional[str] = None
    duplicate_of: Optional[ClaimInfo] = None
    candidate_credit_keys: tuple[str, ...] = field(default_factory=tuple)


@dataclass
class RiderInput:
    name: str
    order_total: Decimal


@dataclass
class RiderResult:
    name: str
    order_total: Decimal
    verified_total: Decimal
    cash_owed_min: Decimal
    cash_owed_max: Decimal
    photo_results: list[PhotoResult] = field(default_factory=list)


@dataclass
class ReconciliationResult:
    riders: list[RiderResult]
    claims: dict[str, ClaimInfo]
    unclaimed_credits: list[CreditRecord]
