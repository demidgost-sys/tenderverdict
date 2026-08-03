"""Deterministic, explainable metadata qualification rules."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from urllib.parse import urlsplit

from .models import Notice, Profile, QualificationResult, Verdict

_COMPETITION_NOTICE_TYPES = {
    "competition",
    "competition notice",
    "contract notice",
    "cn-social",
    "cn-standard",
}

_NEXT_STEPS = {
    Verdict.OPEN_DOCUMENTS: (
        "Open and review the official procurement documents; a human decides whether to proceed."
    ),
    Verdict.WATCH: "Verify the flagged metadata before opening the procurement documents.",
    Verdict.REJECT: "Stop review unless the notice metadata is corrected.",
}


def qualify_notices(
    profile: Profile,
    notices: tuple[Notice, ...] | list[Notice],
    as_of: date | datetime,
) -> tuple[QualificationResult, ...]:
    """Qualify notices in their input order without network access or scoring."""

    _validate_review_point(as_of)
    return tuple(qualify_notice(profile, notice, as_of) for notice in notices)


def qualify_notice(
    profile: Profile,
    notice: Notice,
    as_of: date | datetime,
) -> QualificationResult:
    """Return one traceable verdict from supplied metadata only."""

    _validate_review_point(as_of)

    reasons: list[str] = []
    unknowns: list[str] = []
    hard_reject = False
    needs_review = False

    for warning in notice.metadata_warnings:
        reasons.append(f"Source metadata warning: {warning}")
        unknowns.append(warning)
        needs_review = True

    # Notice type
    if notice.notice_type is None:
        reasons.append("Notice type is missing.")
        unknowns.append("Confirm that this is a competition notice.")
        needs_review = True
    elif _normalize_notice_type(notice.notice_type) not in _COMPETITION_NOTICE_TYPES:
        reasons.append(f"Notice type is not a competition notice: {notice.notice_type}.")
        hard_reject = True
    else:
        reasons.append("Notice type is competition.")

    # Human-readable evidence
    if notice.title is None:
        reasons.append("Notice title is missing.")
        unknowns.append("Confirm the notice title from the official source.")
        needs_review = True
    else:
        reasons.append("Notice title is supplied.")

    if notice.buyer is None:
        reasons.append("Buyer metadata is missing.")
        unknowns.append("Confirm the contracting buyer from the official source.")
        needs_review = True
    else:
        reasons.append("Buyer metadata is supplied.")

    # Deadline
    if notice.deadline is None and notice.deadline_at is None:
        reasons.append("Submission deadline is missing.")
        unknowns.append("Confirm the submission deadline before reviewing documents.")
        needs_review = True
    elif notice.deadline_at is not None:
        deadline_reasons, deadline_unknowns, deadline_reject, deadline_review = (
            _evaluate_exact_deadline(
                notice.deadline_at,
                as_of,
                profile.minimum_days_to_deadline,
            )
        )
        reasons.extend(deadline_reasons)
        unknowns.extend(deadline_unknowns)
        hard_reject = hard_reject or deadline_reject
        needs_review = needs_review or deadline_review
    else:
        assert notice.deadline is not None
        review_date = as_of.date() if type(as_of) is datetime else as_of
        days_remaining = (notice.deadline - review_date).days
        if days_remaining <= 0:
            reasons.append(f"Submission deadline is closed as of {review_date.isoformat()}.")
            hard_reject = True
        elif days_remaining < profile.minimum_days_to_deadline:
            reasons.append(
                "Submission deadline leaves "
                f"{days_remaining} days, below the {profile.minimum_days_to_deadline}-day minimum."
            )
            hard_reject = True
        else:
            reasons.append(
                "Submission deadline leaves "
                f"{days_remaining} days, meeting the "
                f"{profile.minimum_days_to_deadline}-day minimum."
            )

    # CPV fit: exact beats class; class means the first four digits match.
    if not notice.cpv_codes:
        reasons.append("CPV metadata is missing.")
        unknowns.append("Confirm at least one CPV code from the official source.")
        needs_review = True
    else:
        exact_cpv = _first_exact_match(profile.cpv_codes, notice.cpv_codes)
        if exact_cpv is not None:
            reasons.append(f"Exact CPV match: {exact_cpv}.")
        else:
            family_pair = _first_family_match(profile.cpv_codes, notice.cpv_codes)
            if family_pair is not None:
                profile_cpv, notice_cpv = family_pair
                reasons.append(
                    f"Four-digit CPV class match only: profile {profile_cpv}, notice {notice_cpv}."
                )
                unknowns.append("Confirm the exact procurement scope in the documents.")
                needs_review = True
            else:
                reasons.append("No profile CPV code or four-digit CPV class matches.")
                hard_reject = True

    # Geography
    if not notice.countries:
        reasons.append("Country metadata is missing.")
        unknowns.append("Confirm the place of performance from the official source.")
        needs_review = True
    else:
        matched_country = _first_exact_match(profile.countries, notice.countries)
        if matched_country is None:
            reasons.append("Notice countries do not match the profile countries.")
            hard_reject = True
        else:
            reasons.append(f"Country match: {matched_country}.")

    # Source provenance. This checks syntax only and never fetches the URL.
    if notice.source_url is None:
        reasons.append("Source URL is missing.")
        unknowns.append("Locate a syntactically valid HTTPS source URL.")
        needs_review = True
    elif not is_verifiable_source_url(notice.source_url):
        reasons.append("Source URL is not a syntactically valid HTTPS URL.")
        unknowns.append("Replace the source URL with a syntactically valid HTTPS URL.")
        needs_review = True
    else:
        reasons.append("A syntactically valid HTTPS source URL is supplied.")

    if hard_reject:
        verdict = Verdict.REJECT
    elif needs_review:
        verdict = Verdict.WATCH
    else:
        verdict = Verdict.OPEN_DOCUMENTS

    return QualificationResult(
        notice=notice,
        verdict=verdict,
        reasons=tuple(reasons),
        unknowns=tuple(unknowns),
        human_next_step=_NEXT_STEPS[verdict],
    )


def _validate_review_point(as_of: date | datetime) -> None:
    if type(as_of) is date:
        return
    if type(as_of) is datetime and as_of.utcoffset() is not None:
        return
    raise TypeError("as_of must be a date or a timezone-aware datetime")


def _evaluate_exact_deadline(
    deadline_at: datetime,
    as_of: date | datetime,
    minimum_days: int,
) -> tuple[list[str], list[str], bool, bool]:
    reasons: list[str] = []
    unknowns: list[str] = []
    if deadline_at.utcoffset() is None:
        reasons.append("Submission deadline timestamp has no UTC offset.")
        unknowns.append("Replace deadline_at with a timezone-aware RFC 3339 timestamp.")
        return reasons, unknowns, False, True

    if type(as_of) is datetime:
        remaining = deadline_at.astimezone(UTC) - as_of.astimezone(UTC)
        if remaining <= timedelta(0):
            reasons.append(f"Submission deadline is closed as of {as_of.isoformat()}.")
            return reasons, unknowns, True, False
        if remaining < timedelta(days=minimum_days):
            hours = remaining.total_seconds() / 3600
            reasons.append(
                "Submission deadline leaves "
                f"{hours:.1f} hours, below the {minimum_days}-day minimum."
            )
            return reasons, unknowns, True, False
        reasons.append(
            "Submission deadline timestamp meets the "
            f"{minimum_days}-day minimum at {deadline_at.isoformat()}."
        )
        return reasons, unknowns, False, False

    calendar_days = (deadline_at.date() - as_of).days
    if calendar_days < 0:
        reasons.append(f"Submission deadline is closed as of {as_of.isoformat()}.")
        return reasons, unknowns, True, False
    if calendar_days == 0:
        reasons.append("Submission deadline is on the date-only review boundary.")
        unknowns.append("Use an RFC 3339 --as-of instant to determine whether it is still open.")
        return reasons, unknowns, False, True
    if calendar_days < minimum_days:
        reasons.append(
            "Submission deadline leaves fewer than "
            f"{minimum_days} full days from the date-only review point."
        )
        return reasons, unknowns, True, False
    if calendar_days == minimum_days:
        reasons.append("Submission deadline is on the exact lead-time boundary.")
        unknowns.append(
            "Use an RFC 3339 --as-of instant to verify the configured minimum lead time."
        )
        return reasons, unknowns, False, True
    reasons.append(
        "Submission deadline timestamp is beyond the "
        f"{minimum_days}-day minimum from the supplied review date."
    )
    return reasons, unknowns, False, False


def is_verifiable_source_url(value: str) -> bool:
    """Return whether a source value has a safe, absolute HTTPS URL shape.

    This is deliberately a syntax check, not a claim that TenderVerdict fetched
    or endorsed the source.
    """

    if not value or any(character.isspace() or ord(character) < 32 for character in value):
        return False
    try:
        parsed = urlsplit(value)
        # Accessing port catches malformed forms such as ``:not-a-port``.
        _ = parsed.port
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.hostname
        and parsed.username is None
        and parsed.password is None
        and parsed.fragment == ""
    )


def _normalize_notice_type(value: str) -> str:
    return " ".join(value.casefold().split())


def _first_exact_match(preferred: tuple[str, ...], candidates: tuple[str, ...]) -> str | None:
    candidate_set = set(candidates)
    return next((value for value in preferred if value in candidate_set), None)


def _first_family_match(
    profile_codes: tuple[str, ...], notice_codes: tuple[str, ...]
) -> tuple[str, str] | None:
    for profile_code in profile_codes:
        for notice_code in notice_codes:
            if profile_code[:4] == notice_code[:4]:
                return profile_code, notice_code
    return None
