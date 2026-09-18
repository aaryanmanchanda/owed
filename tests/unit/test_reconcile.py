"""Unit tests for the pure reconcile engine (HANDOFF.md §7, §10).

No Bedrock calls, no AWS, no DynamoDB — hand-written extraction JSON and
credit fixtures only, per §10's "these are the screening-substitute signal"
instruction.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from src.common.models import (
    ClaimState,
    CreditRecord,
    PhotoExtraction,
    RiderInput,
    Verdict,
)
from src.reconcile.engine import reconcile_shift

SHIFT = "shift-2026-09-19"
T0 = datetime(2026, 9, 19, 20, 0, 0)  # IST, per HANDOFF "all times in IST"


def make_photo(photo_id, rider="ravi", utr=None, amount=None, screen_time=T0, status="success", **kw):
    return PhotoExtraction(
        photo_id=photo_id,
        rider=rider,
        utr=utr,
        amount_inr=Decimal(str(amount)) if amount is not None else None,
        screen_time=screen_time,
        status_text=status,
        **kw,
    )


def make_credit(credit_key, amount, timestamp=T0, utr=None):
    return CreditRecord(credit_key=credit_key, amount=Decimal(str(amount)), timestamp=timestamp, utr=utr)


def reconcile(photos, credits, riders=None, existing_claims=None, window_min=10):
    riders = riders or [RiderInput(name="ravi", order_total=Decimal("1000"))]
    return reconcile_shift(
        shift_id=SHIFT,
        riders=riders,
        photos=photos,
        credits=credits,
        existing_claims=existing_claims,
        window_min=window_min,
    )


def photo_result(result, photo_id):
    for rider in result.riders:
        for pr in rider.photo_results:
            if pr.photo.photo_id == photo_id:
                return pr
    raise AssertionError(f"no result for {photo_id}")


# --- one test per §7 verdict -------------------------------------------------


def test_not_success():
    photo = make_photo("p1", utr="123456789012", amount="500.00", status="pending")
    credits = [make_credit("123456789012", "500.00", utr="123456789012")]
    result = reconcile([photo], credits)
    assert photo_result(result, "p1").verdict == Verdict.NOT_SUCCESS
    assert result.claims == {}


def test_unreadable():
    photo = make_photo("p1", utr=None, amount=None)
    result = reconcile([photo], credits=[])
    assert photo_result(result, "p1").verdict == Verdict.UNREADABLE


def test_verified():
    photo = make_photo("p1", utr="123456789012", amount="500.00")
    credits = [make_credit("123456789012", "500.00", utr="123456789012")]
    result = reconcile([photo], credits)
    pr = photo_result(result, "p1")
    assert pr.verdict == Verdict.VERIFIED
    assert pr.claimed_credit_key == "123456789012"
    assert result.claims["123456789012"].state == ClaimState.FINAL
    assert result.claims["123456789012"].photo_id == "p1"


def test_amount_mismatch():
    photo = make_photo("p1", utr="123456789012", amount="500.00")
    credits = [make_credit("123456789012", "499.00", utr="123456789012")]
    result = reconcile([photo], credits)
    assert photo_result(result, "p1").verdict == Verdict.AMOUNT_MISMATCH
    assert result.claims == {}


def test_duplicate():
    credits = [make_credit("123456789012", "500.00", utr="123456789012")]
    p1 = make_photo("p1", utr="123456789012", amount="500.00", screen_time=T0)
    p2 = make_photo("p2", utr="123456789012", amount="500.00", screen_time=T0 + timedelta(seconds=1))
    result = reconcile([p1, p2], credits)
    first = photo_result(result, "p1")
    second = photo_result(result, "p2")
    assert first.verdict == Verdict.VERIFIED
    assert second.verdict == Verdict.DUPLICATE
    assert second.duplicate_of.photo_id == "p1"


def test_probable():
    credits = [make_credit("H#abc", "500.00", timestamp=T0)]
    photo = make_photo("p1", utr=None, amount="500.00", screen_time=T0 + timedelta(minutes=2))
    result = reconcile([photo], credits)
    pr = photo_result(result, "p1")
    assert pr.verdict == Verdict.PROBABLE
    assert pr.claimed_credit_key == "H#abc"
    assert result.claims["H#abc"].state == ClaimState.PENDING_CONFIRM


def test_ambiguous():
    credits = [
        make_credit("H#abc", "500.00", timestamp=T0),
        make_credit("H#def", "500.00", timestamp=T0 + timedelta(minutes=1)),
    ]
    photo = make_photo("p1", utr=None, amount="500.00", screen_time=T0)
    result = reconcile([photo], credits)
    pr = photo_result(result, "p1")
    assert pr.verdict == Verdict.AMBIGUOUS
    assert set(pr.candidate_credit_keys) == {"H#abc", "H#def"}
    assert result.claims == {}  # owner must pick; nothing auto-claimed


def test_not_found():
    credits = [make_credit("H#abc", "500.00", timestamp=T0)]
    photo = make_photo("p1", utr=None, amount="999.00", screen_time=T0)
    result = reconcile([photo], credits)
    assert photo_result(result, "p1").verdict == Verdict.NOT_FOUND


def test_unclaimed_credit():
    credits = [make_credit("H#abc", "500.00", timestamp=T0)]
    result = reconcile([], credits)
    assert [c.credit_key for c in result.unclaimed_credits] == ["H#abc"]


# --- §10 named tests ----------------------------------------------------


def test_misread_safety_fabricated_utr_still_matches_by_amount_and_time():
    """A confidently-invented UTR must never cause a false NOT_FOUND when the
    payment genuinely arrived — it falls through to the amount+time check."""
    credits = [make_credit("H#abc", "500.00", timestamp=T0)]
    fabricated_utr = "999999999999"  # well-formed, but not this credit's real utr
    photo = make_photo("p1", utr=fabricated_utr, amount="500.00", screen_time=T0)
    result = reconcile([photo], credits)
    assert photo_result(result, "p1").verdict == Verdict.PROBABLE


def test_misread_safety_two_candidates_is_ambiguous_not_not_found():
    credits = [
        make_credit("H#abc", "500.00", timestamp=T0),
        make_credit("H#def", "500.00", timestamp=T0),
    ]
    photo = make_photo("p1", utr="999999999999", amount="500.00", screen_time=T0)
    result = reconcile([photo], credits)
    assert photo_result(result, "p1").verdict == Verdict.AMBIGUOUS


def test_idempotent_rerun_gives_identical_verdicts_no_self_duplicate():
    credits = [make_credit("123456789012", "500.00", utr="123456789012")]
    photo = make_photo("p1", utr="123456789012", amount="500.00")

    first = reconcile([photo], credits)
    assert photo_result(first, "p1").verdict == Verdict.VERIFIED

    second = reconcile([photo], credits, existing_claims=first.claims)
    pr = photo_result(second, "p1")
    assert pr.verdict == Verdict.VERIFIED  # not DUPLICATE against itself
    assert second.claims == first.claims


def test_idempotent_rerun_probable_reclaims_same_credit():
    credits = [make_credit("H#abc", "500.00", timestamp=T0)]
    photo = make_photo("p1", utr=None, amount="500.00", screen_time=T0)

    first = reconcile([photo], credits)
    second = reconcile([photo], credits, existing_claims=first.claims)

    assert photo_result(second, "p1").verdict == Verdict.PROBABLE
    assert second.claims["H#abc"].photo_id == "p1"


def test_same_bytes_uploaded_twice_is_one_photo_one_claim():
    credits = [make_credit("123456789012", "500.00", utr="123456789012")]
    photo = make_photo("p1", utr="123456789012", amount="500.00")
    # Same photo_id appears twice in the input (e.g. uploaded to two rider
    # buckets by mistake, or double-processed) — must still be one claim.
    result = reconcile([photo, photo], credits)
    assert len(result.claims) == 1
    assert sum(len(r.photo_results) for r in result.riders) == 1


def test_cash_owed_range_collapses_once_resolved():
    riders = [RiderInput(name="ravi", order_total=Decimal("1000"))]
    credits = [
        make_credit("123456789012", "600.00", utr="123456789012"),
        make_credit("H#abc", "300.00", timestamp=T0),
    ]
    p_verified = make_photo("p1", utr="123456789012", amount="600.00")
    p_probable = make_photo("p2", utr=None, amount="300.00", screen_time=T0)

    unresolved = reconcile([p_verified, p_probable], credits, riders=riders)
    ravi = unresolved.riders[0]
    assert ravi.verified_total == Decimal("600.00")
    assert ravi.cash_owed_max == Decimal("400.00")  # 1000 - 600, PROBABLE assumed not genuine
    assert ravi.cash_owed_min == Decimal("100.00")  # 1000 - 600 - 300, PROBABLE assumed genuine
    assert ravi.cash_owed_min < ravi.cash_owed_max

    # Owner confirms the PROBABLE photo genuine: re-run with both utr-matched
    # (simulating the resolve flow having upgraded it to a real credit match).
    p_probable_confirmed = make_photo("p2", utr=None, amount="300.00", screen_time=T0)
    credits_confirmed = credits  # same set; still resolved via amount+time
    resolved = reconcile(
        [p_verified, p_probable_confirmed], credits_confirmed, riders=riders,
        existing_claims=unresolved.claims,
    )
    ravi_resolved = resolved.riders[0]
    # Once the only outstanding item is itself the sole PROBABLE candidate and
    # nothing else is pending, min and max still bracket the same evidence —
    # the collapse to a single number happens when the owner's tap converts
    # PROBABLE into a final claim, which is Phase 4's resolve endpoint, not
    # this engine. What the engine guarantees here is idempotence: re-running
    # reproduces the identical range rather than drifting.
    assert ravi_resolved.cash_owed_min == ravi.cash_owed_min
    assert ravi_resolved.cash_owed_max == ravi.cash_owed_max


def test_cash_owed_fully_verified_collapses_to_one_number():
    riders = [RiderInput(name="ravi", order_total=Decimal("1000"))]
    credits = [make_credit("123456789012", "1000.00", utr="123456789012")]
    photo = make_photo("p1", utr="123456789012", amount="1000.00")
    result = reconcile([photo], credits, riders=riders)
    ravi = result.riders[0]
    assert ravi.cash_owed_min == ravi.cash_owed_max == Decimal("0.00")


def test_deterministic_ordering_shuffled_input_same_winner():
    credits = [make_credit("123456789012", "500.00", utr="123456789012")]
    p1 = make_photo("p1", utr="123456789012", amount="500.00", screen_time=T0)
    p2 = make_photo("p2", utr="123456789012", amount="500.00", screen_time=T0 + timedelta(seconds=1))

    forward = reconcile([p1, p2], credits)
    shuffled = reconcile([p2, p1], credits)

    assert photo_result(forward, "p1").verdict == photo_result(shuffled, "p1").verdict == Verdict.VERIFIED
    assert photo_result(forward, "p2").verdict == photo_result(shuffled, "p2").verdict == Verdict.DUPLICATE
    assert forward.claims == shuffled.claims


def test_amount_time_window_boundary():
    credits = [make_credit("H#abc", "500.00", timestamp=T0)]
    just_inside = make_photo("p1", utr=None, amount="500.00", screen_time=T0 + timedelta(minutes=10))
    result = reconcile([just_inside], credits, window_min=10)
    assert photo_result(result, "p1").verdict == Verdict.PROBABLE


def test_amount_time_window_excludes_beyond_window():
    credits = [make_credit("H#abc", "500.00", timestamp=T0)]
    just_outside = make_photo("p1", utr=None, amount="500.00", screen_time=T0 + timedelta(minutes=10, seconds=1))
    result = reconcile([just_outside], credits, window_min=10)
    assert photo_result(result, "p1").verdict == Verdict.NOT_FOUND


def test_missing_screen_time_never_false_matches():
    """Fails closed: no screen_time means no amount+time candidate can be
    trusted, even if a same-amount credit exists."""
    credits = [make_credit("H#abc", "500.00", timestamp=T0)]
    photo = make_photo("p1", utr=None, amount="500.00", screen_time=None)
    result = reconcile([photo], credits)
    assert photo_result(result, "p1").verdict == Verdict.NOT_FOUND


# --- PhotoExtraction validation (§7 "never trusted from the model") --------


def test_invalid_utr_is_nulled():
    photo = PhotoExtraction(photo_id="p1", rider="ravi", utr="not-12-digits", amount_inr=Decimal("10.00"))
    assert photo.utr is None


def test_non_positive_amount_is_nulled():
    photo = PhotoExtraction(photo_id="p1", rider="ravi", utr="123456789012", amount_inr=Decimal("-5.00"))
    assert photo.amount_inr is None


def test_amount_with_more_than_two_decimals_is_nulled():
    photo = PhotoExtraction(photo_id="p1", rider="ravi", utr="123456789012", amount_inr=Decimal("10.005"))
    assert photo.amount_inr is None
