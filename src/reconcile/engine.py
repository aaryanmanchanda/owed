"""Pure verdict engine (HANDOFF.md §7). No AWS, no I/O, no Bedrock calls.

The DynamoDB claim layer is deliberately NOT here (HANDOFF.md §11): this module
takes plain Python objects in, plain Python objects out, so it can be unit
tested without AWS. A caller (a Lambda, a CLI, a test) is responsible for
loading `credits` and `existing_claims` from wherever they actually live and
persisting the returned claims back.

Ordering (§7 "Exactly-once and ordering"): photos are always processed sorted
by `(screen_time, photo_id)`, with `screen_time is None` sorted last, so the
result never depends on the order the caller passed photos in — the same
input set always produces the same claims, whatever order photos arrived in
or were re-run in.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from src.common.models import (
    ClaimInfo,
    ClaimState,
    CreditRecord,
    PhotoExtraction,
    PhotoResult,
    ReconciliationResult,
    RiderInput,
    RiderResult,
    Verdict,
)

DEFAULT_WINDOW_MIN = 10


def _within_window(credit_ts: Optional[datetime], screen_time: Optional[datetime], window_min: int) -> bool:
    """§7 PROBABLE/AMBIGUOUS: amount match "within WINDOW_MIN of screen_time".

    Fails closed: if either timestamp is unknown, we cannot safely claim the
    two events are close in time, so no candidate match is reported. This
    only ever pushes a photo toward NOT_FOUND ("check this"), never toward a
    false VERIFIED/PROBABLE — the safe direction per §7's misread-safety
    guarantee.
    """
    if credit_ts is None or screen_time is None:
        return False
    return abs(credit_ts - screen_time) <= timedelta(minutes=window_min)


def _claimant(claims: dict[str, ClaimInfo], credit_key: str) -> Optional[str]:
    claim = claims.get(credit_key)
    return claim.photo_id if claim else None


def _reconcile_photo(
    photo: PhotoExtraction,
    shift_id: str,
    credits: list[CreditRecord],
    credits_by_utr: dict[str, CreditRecord],
    claims: dict[str, ClaimInfo],
    window_min: int,
) -> PhotoResult:
    # §7 rules, applied IN THIS ORDER.

    # 1. NOT_SUCCESS
    if photo.status_text in ("pending", "failed"):
        return PhotoResult(photo=photo, verdict=Verdict.NOT_SUCCESS)

    # 2. UNREADABLE
    if photo.utr is None and photo.amount_inr is None:
        return PhotoResult(photo=photo, verdict=Verdict.UNREADABLE)

    credit = credits_by_utr.get(photo.utr) if photo.utr else None

    if credit is not None:
        # 3. DUPLICATE / VERIFIED / AMOUNT_MISMATCH — valid utr found in the record.
        claimant = _claimant(claims, credit.credit_key)
        if claimant is not None and claimant != photo.photo_id:
            return PhotoResult(
                photo=photo,
                verdict=Verdict.DUPLICATE,
                duplicate_of=claims[credit.credit_key],
            )
        # No claim yet, or this same photo already owns it (idempotent re-run).
        if photo.amount_inr is not None and photo.amount_inr == credit.amount:
            claims[credit.credit_key] = ClaimInfo(
                credit_key=credit.credit_key,
                photo_id=photo.photo_id,
                shift_id=shift_id,
                rider=photo.rider,
                state=ClaimState.FINAL,
            )
            return PhotoResult(photo=photo, verdict=Verdict.VERIFIED, claimed_credit_key=credit.credit_key)
        # Amount missing or differs from the matched utr's credit — "check this",
        # never silently VERIFIED without an amount match (not in §7's table
        # verbatim, but the conservative reading of "amount differs").
        return PhotoResult(photo=photo, verdict=Verdict.AMOUNT_MISMATCH)

    # utr is null, or a valid utr that isn't in the record: amount+time matching.
    if photo.amount_inr is None:
        return PhotoResult(photo=photo, verdict=Verdict.NOT_FOUND)

    candidates = [
        c
        for c in credits
        if c.amount == photo.amount_inr
        and _within_window(c.timestamp, photo.screen_time, window_min)
        and (_claimant(claims, c.credit_key) in (None, photo.photo_id))
    ]

    if not candidates:
        return PhotoResult(photo=photo, verdict=Verdict.NOT_FOUND)

    if len(candidates) == 1:
        chosen = candidates[0]
        claims[chosen.credit_key] = ClaimInfo(
            credit_key=chosen.credit_key,
            photo_id=photo.photo_id,
            shift_id=shift_id,
            rider=photo.rider,
            state=ClaimState.PENDING_CONFIRM,
        )
        return PhotoResult(photo=photo, verdict=Verdict.PROBABLE, claimed_credit_key=chosen.credit_key)

    # 2+ candidates: AMBIGUOUS, no claim — the owner picks one (Phase 4 resolve flow).
    return PhotoResult(
        photo=photo,
        verdict=Verdict.AMBIGUOUS,
        candidate_credit_keys=tuple(c.credit_key for c in candidates),
    )


def reconcile_shift(
    shift_id: str,
    riders: list[RiderInput],
    photos: list[PhotoExtraction],
    credits: list[CreditRecord],
    existing_claims: Optional[dict[str, ClaimInfo]] = None,
    window_min: int = DEFAULT_WINDOW_MIN,
) -> ReconciliationResult:
    """Reconcile one shift's photos against its payment-record credits.

    `existing_claims` is the caller's current CLAIM# snapshot (may span other
    shifts — §7 DUPLICATE is "any shift"). Re-running the same shift with the
    same `existing_claims` snapshot yields identical verdicts (idempotent).

    Same bytes uploaded twice: photos are de-duplicated by `photo_id`
    (`photo_id` = sha256 of the image bytes, per §7) before processing, so one
    `photo_id` always yields exactly one claim, never two.
    """
    claims: dict[str, ClaimInfo] = dict(existing_claims or {})
    credits_by_utr = {c.utr: c for c in credits if c.utr}

    unique_photos: dict[str, PhotoExtraction] = {}
    for p in photos:
        unique_photos.setdefault(p.photo_id, p)

    ordered_photos = sorted(
        unique_photos.values(),
        key=lambda p: (p.screen_time is None, p.screen_time or datetime.min, p.photo_id),
    )

    photo_results_by_rider: dict[str, list[PhotoResult]] = {r.name: [] for r in riders}
    for photo in ordered_photos:
        result = _reconcile_photo(photo, shift_id, credits, credits_by_utr, claims, window_min)
        photo_results_by_rider.setdefault(photo.rider, []).append(result)

    rider_results = []
    for rider in riders:
        photo_results = photo_results_by_rider.get(rider.name, [])
        verified_total = sum(
            (pr.photo.amount_inr for pr in photo_results if pr.verdict == Verdict.VERIFIED and pr.photo.amount_inr),
            Decimal("0"),
        )
        # "or ₹Y if the flagged payments are genuine" (§6): only PROBABLE/AMBIGUOUS
        # are resolvable by the owner into a verified payment (Phase 4 resolve
        # flow); AMOUNT_MISMATCH/NOT_FOUND/UNREADABLE/NOT_SUCCESS have no such path.
        pending_total = sum(
            (
                pr.photo.amount_inr
                for pr in photo_results
                if pr.verdict in (Verdict.PROBABLE, Verdict.AMBIGUOUS) and pr.photo.amount_inr
            ),
            Decimal("0"),
        )
        cash_owed_max = rider.order_total - verified_total
        cash_owed_min = cash_owed_max - pending_total
        rider_results.append(
            RiderResult(
                name=rider.name,
                order_total=rider.order_total,
                verified_total=verified_total,
                cash_owed_min=cash_owed_min,
                cash_owed_max=cash_owed_max,
                photo_results=photo_results,
            )
        )

    claimed_keys = {c.credit_key for c in claims.values()}
    unclaimed_credits = [c for c in credits if c.credit_key not in claimed_keys]

    return ReconciliationResult(riders=rider_results, claims=claims, unclaimed_credits=unclaimed_credits)
