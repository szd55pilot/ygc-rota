from __future__ import annotations

from collections import defaultdict
from datetime import date
import argparse

import pytest

import rota


@pytest.fixture(autouse=True)
def deterministic_shuffle(monkeypatch):
    monkeypatch.setattr(rota.random, "shuffle", lambda seq: None)


def test_generate_operating_dates_only_returns_wed_sat_sun_and_is_inclusive():
    days = rota.generate_operating_dates(date(2026, 4, 1), 1)

    assert days[0] == date(2026, 4, 1)  # Wed, inclusive start
    assert all(d.weekday() in rota.OPERATING_DAYS.values() for d in days)
    assert date(2026, 4, 4) in days  # Sat
    assert date(2026, 4, 5) in days  # Sun
    assert date(2026, 4, 2) not in days  # Thu


def test_to_date_accepts_date_objects_and_iso_strings():
    d = date(2026, 4, 1)
    assert rota._to_date(d) is d
    assert rota._to_date("2026-04-01") == d


def test_is_person_active_on_honours_inactive_periods(monkeypatch):
    monkeypatch.setattr(
        rota,
        "PEOPLE",
        {"ALICE": {"inactive_periods": [("2026-04-10", "2026-04-12")]}} ,
    )

    assert rota.is_person_active_on("ALICE", date(2026, 4, 9)) is True
    assert rota.is_person_active_on("ALICE", date(2026, 4, 10)) is False
    assert rota.is_person_active_on("ALICE", date(2026, 4, 12)) is False
    assert rota.is_person_active_on("ALICE", date(2026, 4, 13)) is True
    assert rota.is_person_active_on("UNKNOWN", date(2026, 4, 10)) is True


def test_count_recent_shifts_uses_strict_14_day_rolling_window():
    history = defaultdict(list)
    history["ALICE"] = [
        date(2026, 4, 1),   # exactly 14 days before Apr 15 -> excluded
        date(2026, 4, 2),   # included
        date(2026, 4, 10),  # included
        date(2026, 4, 15),  # same day -> excluded
    ]

    assert rota.count_recent_shifts("ALICE", date(2026, 4, 15), history) == 2
    assert rota.count_recent_shifts("BOB", date(2026, 4, 15), history) == 0


@pytest.mark.parametrize(
    ("operating_day", "expected_anchor"),
    [
        (date(2026, 4, 1), date(2026, 4, 1)),  # Wed
        (date(2026, 4, 4), date(2026, 4, 1)),  # Sat anchored to prior Wed
        (date(2026, 4, 5), date(2026, 4, 1)),  # Sun anchored to prior Wed
        (date(2026, 4, 8), date(2026, 4, 8)),  # next Wed
    ],
)
def test_club_week_anchor(operating_day, expected_anchor):
    assert rota.club_week_anchor(operating_day) == expected_anchor


def test_bi_required_on_supports_alternating_pattern_and_first_off_inversion():
    first_anchor = date(2026, 4, 1)

    assert rota.bi_required_on(date(2026, 4, 1), first_anchor, alternate=False, first_off=False) is True

    assert rota.bi_required_on(date(2026, 4, 4), first_anchor, alternate=True, first_off=False) is True
    assert rota.bi_required_on(date(2026, 4, 8), first_anchor, alternate=True, first_off=False) is False
    assert rota.bi_required_on(date(2026, 4, 11), first_anchor, alternate=True, first_off=False) is False
    assert rota.bi_required_on(date(2026, 4, 15), first_anchor, alternate=True, first_off=False) is True

    assert rota.bi_required_on(date(2026, 4, 1), first_anchor, alternate=True, first_off=True) is False
    assert rota.bi_required_on(date(2026, 4, 8), first_anchor, alternate=True, first_off=True) is True


def test_lead_required_only_when_assigned_instructor_requires_supervision(monkeypatch):
    monkeypatch.setattr(
        rota,
        "PEOPLE",
        {
            "ALICE": {"requires_snr_di": True},
            "BOB": {"requires_snr_di": False},
        },
    )

    assert rota.lead_required({"Instructor": "ALICE"}) is True
    assert rota.lead_required({"Instructor": "BOB"}) is False
    assert rota.lead_required({"Instructor": "UNKNOWN"}) is False
    assert rota.lead_required({}) is False


def test_generate_rota_marks_bi_ifp_na_on_alternate_off_weeks_and_preserves_other_roles(monkeypatch):
    people = {
        "INST": {
            "allowed_days": {"Wed", "Sat", "Sun"},
            "allowed_roles": {"Instructor"},
            "max_shifts_per_week": 99,
            "requires_snr_di": False,
        },
        "TUG": {
            "allowed_days": {"Wed", "Sat", "Sun"},
            "allowed_roles": {"Tug Pilot"},
            "max_shifts_per_week": 99,
        },
        "BI": {
            "allowed_days": {"Wed", "Sat", "Sun"},
            "allowed_roles": {"BI/IFP"},
            "max_shifts_per_week": 99,
        },
        "LPS1": {
            "allowed_days": {"Wed", "Sat", "Sun"},
            "allowed_roles": {"LPS"},
            "max_shifts_per_week": 99,
        },
        "DP1": {
            "allowed_days": {"Wed", "Sat", "Sun"},
            "allowed_roles": {"Duty Pilot"},
            "max_shifts_per_week": 99,
        },
    }
    monkeypatch.setattr(rota, "PEOPLE", people)

    generated = rota.generate_rota(date(2026, 4, 1), 1, bi_alternate=True, bi_first_off=False)

    assert generated[date(2026, 4, 1)]["BI/IFP"] == "BI"
    assert generated[date(2026, 4, 4)]["BI/IFP"] == "BI"
    # Same-role back-to-back assignment is blocked, so the second consecutive
    # operating day falls back to an unfilled BI slot rather than reusing BI.
    assert generated[date(2026, 4, 5)]["BI/IFP"] == "NEED TO FILL"
    assert generated[date(2026, 4, 8)]["BI/IFP"] == "n/a"
    assert generated[date(2026, 4, 11)]["BI/IFP"] == "n/a"
    assert generated[date(2026, 4, 12)]["BI/IFP"] == "n/a"
    assert generated[date(2026, 4, 8)]["Instructor"] == "INST"
    assert generated[date(2026, 4, 8)][rota.LEAD_ROLE] == "—"


def test_generate_rota_assigns_lead_instructor_when_required(monkeypatch):
    people = {
        "STUDENT_INST": {
            "allowed_days": {"Wed"},
            "allowed_roles": {"Instructor"},
            "max_shifts_per_week": 99,
            "requires_snr_di": True,
        },
        "LEAD": {
            "allowed_days": {"Wed"},
            "allowed_roles": {rota.LEAD_ROLE},
            "max_shifts_per_week": 99,
            "requires_snr_di": False,
        },
        "TUG": {
            "allowed_days": {"Wed"},
            "allowed_roles": {"Tug Pilot"},
            "max_shifts_per_week": 99,
        },
        "BI": {
            "allowed_days": {"Wed"},
            "allowed_roles": {"BI/IFP"},
            "max_shifts_per_week": 99,
        },
        "LPS1": {
            "allowed_days": {"Wed"},
            "allowed_roles": {"LPS"},
            "max_shifts_per_week": 99,
        },
        "DP1": {
            "allowed_days": {"Wed"},
            "allowed_roles": {"Duty Pilot"},
            "max_shifts_per_week": 99,
        },
    }
    monkeypatch.setattr(rota, "PEOPLE", people)

    generated = rota.generate_rota(date(2026, 4, 1), 0, bi_alternate=False, bi_first_off=False)

    day = date(2026, 4, 1)
    assert generated[day]["Instructor"] == "STUDENT_INST"
    assert generated[day][rota.LEAD_ROLE] == "LEAD"


def test_generate_rota_uses_required_and_need_to_fill_fallbacks(monkeypatch):
    people = {
        "STUDENT_INST": {
            "allowed_days": {"Wed"},
            "allowed_roles": {"Instructor"},
            "max_shifts_per_week": 99,
            "requires_snr_di": True,
        },
    }
    monkeypatch.setattr(rota, "PEOPLE", people)

    generated = rota.generate_rota(date(2026, 4, 1), 0, bi_alternate=False, bi_first_off=False)
    day = date(2026, 4, 1)

    assert generated[day]["Instructor"] == "STUDENT_INST"
    assert generated[day]["Tug Pilot"] == "NEED TO FILL"
    assert generated[day]["BI/IFP"] == "NEED TO FILL"
    assert generated[day]["LPS"] == "NEED TO FILL"
    assert generated[day]["Duty Pilot"] == "NEED TO FILL"
    assert generated[day][rota.LEAD_ROLE] == "(REQUIRED)"


def test_generate_rota_prevents_same_person_being_double_booked_on_the_same_day(monkeypatch):
    people = {
        "MULTI": {
            "allowed_days": {"Wed"},
            "allowed_roles": {"Instructor", "Tug Pilot"},
            "max_shifts_per_week": 99,
            "requires_snr_di": False,
        },
        "BI": {
            "allowed_days": {"Wed"},
            "allowed_roles": {"BI/IFP"},
            "max_shifts_per_week": 99,
        },
        "LPS1": {
            "allowed_days": {"Wed"},
            "allowed_roles": {"LPS"},
            "max_shifts_per_week": 99,
        },
        "DP1": {
            "allowed_days": {"Wed"},
            "allowed_roles": {"Duty Pilot"},
            "max_shifts_per_week": 99,
        },
    }
    monkeypatch.setattr(rota, "PEOPLE", people)

    generated = rota.generate_rota(date(2026, 4, 1), 0, bi_alternate=False, bi_first_off=False)
    day = date(2026, 4, 1)

    assert generated[day]["Instructor"] == "MULTI"
    assert generated[day]["Tug Pilot"] == "NEED TO FILL"


def test_generate_rota_prevents_consecutive_day_assignments_for_same_person(monkeypatch):
    people = {
        "INST": {
            "allowed_days": {"Sat", "Sun"},
            "allowed_roles": {"Instructor"},
            "max_shifts_per_week": 99,
            "requires_snr_di": False,
        },
        "TUG_SAT": {
            "allowed_days": {"Sat"},
            "allowed_roles": {"Tug Pilot"},
            "max_shifts_per_week": 99,
        },
        "TUG_SUN": {
            "allowed_days": {"Sun"},
            "allowed_roles": {"Tug Pilot"},
            "max_shifts_per_week": 99,
        },
        "BI_SAT": {
            "allowed_days": {"Sat"},
            "allowed_roles": {"BI/IFP"},
            "max_shifts_per_week": 99,
        },
        "BI_SUN": {
            "allowed_days": {"Sun"},
            "allowed_roles": {"BI/IFP"},
            "max_shifts_per_week": 99,
        },
        "LPS_SAT": {
            "allowed_days": {"Sat"},
            "allowed_roles": {"LPS"},
            "max_shifts_per_week": 99,
        },
        "LPS_SUN": {
            "allowed_days": {"Sun"},
            "allowed_roles": {"LPS"},
            "max_shifts_per_week": 99,
        },
        "DP_SAT": {
            "allowed_days": {"Sat"},
            "allowed_roles": {"Duty Pilot"},
            "max_shifts_per_week": 99,
        },
        "DP_SUN": {
            "allowed_days": {"Sun"},
            "allowed_roles": {"Duty Pilot"},
            "max_shifts_per_week": 99,
        },
    }
    monkeypatch.setattr(rota, "PEOPLE", people)

    generated = rota.generate_rota(date(2026, 4, 4), 1, bi_alternate=False, bi_first_off=False)

    assert generated[date(2026, 4, 4)]["Instructor"] == "INST"
    assert generated[date(2026, 4, 5)]["Instructor"] == "NEED TO FILL"


def test_parse_args_supports_defaults_and_flags(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["rota.py", "--start", "2026-04-01", "--months", "2", "--bi-alternate", "--bi-first-off"],
    )

    args = rota.parse_args()

    assert isinstance(args, argparse.Namespace)
    assert args.start == "2026-04-01"
    assert args.months == 2
    assert args.bi_alternate is True
    assert args.bi_first_off is True


def test_print_rota_table_outputs_headers_and_rows(capsys):
    sample = {
        date(2026, 4, 1): {
            "Instructor": "INST",
            rota.LEAD_ROLE: "—",
            "Tug Pilot": "TUG",
            "BI/IFP": "BI",
            "LPS": "LPS1",
            "Duty Pilot": "DP1",
        }
    }

    rota.print_rota_table(sample)
    output = capsys.readouterr().out

    assert "Day" in output
    assert "Lead Instructor" in output
    assert "Wednesday" in output
    assert "01 Apr 2026" in output
    assert "INST" in output
