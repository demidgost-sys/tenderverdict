"""Bundled fictional data for the installed offline demo."""

from __future__ import annotations

from typing import Any

DEMO_AS_OF = "2026-08-02"


def demo_profile() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "name": "Example Software GmbH",
        "cpv_codes": ["72260000"],
        "countries": ["AUT", "DEU"],
        "minimum_days_to_deadline": 14,
    }


def demo_notices() -> list[dict[str, Any]]:
    return [
        {
            "publication_number": "SYN-OPEN-001",
            "notice_type": "competition",
            "title": "Application maintenance services",
            "buyer": "Example City Procurement Office",
            "cpv_codes": ["72260000"],
            "countries": ["AUT"],
            "deadline": "2026-09-15",
            "source_url": "https://procurement.example/notices/SYN-OPEN-001",
        },
        {
            "publication_number": "SYN-WATCH-001",
            "notice_type": "competition",
            "title": "Software support services",
            "buyer": "Example Regional Authority",
            "cpv_codes": ["72261000"],
            "countries": ["DEU"],
            "deadline": "2026-09-20",
            "source_url": "https://procurement.example/notices/SYN-WATCH-001",
        },
        {
            "publication_number": "SYN-REJECT-001",
            "notice_type": "competition",
            "title": "Software implementation services",
            "buyer": "Example Federal Agency",
            "cpv_codes": ["72260000"],
            "countries": ["AUT"],
            "deadline": "2026-08-05",
            "source_url": "https://procurement.example/notices/SYN-REJECT-001",
        },
    ]


__all__ = ["DEMO_AS_OF", "demo_notices", "demo_profile"]
