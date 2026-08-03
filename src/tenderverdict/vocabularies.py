"""Offline access to source-traceable EU procurement code snapshots."""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files


@lru_cache(maxsize=1)
def cpv_codes() -> frozenset[str]:
    """Return the bundled official CPV code set."""

    return _load_codes("cpv_codes.txt")


@lru_cache(maxsize=1)
def country_codes() -> frozenset[str]:
    """Return current three-letter country authority codes bundled at release time."""

    return _load_codes("country_codes.txt")


def is_known_cpv(value: str) -> bool:
    return value in cpv_codes()


def is_known_country(value: str) -> bool:
    return value in country_codes()


def _load_codes(filename: str) -> frozenset[str]:
    resource = files("tenderverdict").joinpath("data", filename)
    values = resource.read_text(encoding="ascii").splitlines()
    if not values or len(values) != len(set(values)):
        raise RuntimeError(f"bundled vocabulary is empty or contains duplicates: {filename}")
    return frozenset(values)
