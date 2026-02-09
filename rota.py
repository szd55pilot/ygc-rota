# rota.py
# v1.5.1 - Instructor Rota Generator with Rolling Window Constraints + Alternate BI Weeks

import argparse
import random
from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, List

from people import PEOPLE

# ==================================================
# CONFIGURATION
# ==================================================

OPERATING_DAYS = {"Wed": 2, "Sat": 5, "Sun": 6}

PRIMARY_ROLES = [
    "Instructor",
    "Tug Pilot",
    "BI/IFP",
    "LPS",
    "Duty Pilot",
]

LEAD_ROLE = "Lead Instructor"
ALL_ROLES = ["Instructor", LEAD_ROLE] + PRIMARY_ROLES[1:]

SHIFT_WINDOW_DAYS = 14

# ==================================================
# DATE HELPERS
# ==================================================

def generate_operating_dates(start: date, months: int) -> List[date]:
    end = start + timedelta(days=months * 31)
    d = start
    days = []
    while d <= end:
        if d.weekday() in OPERATING_DAYS.values():
            days.append(d)
        d += timedelta(days=1)
    return days


def _to_date(d):
    if isinstance(d, date):
        return d
    return date.fromisoformat(d)


def is_person_active_on(person: str, d: date) -> bool:
    periods = PEOPLE.get(person, {}).get("inactive_periods", [])
    for start, end in periods:
        start_d = _to_date(start)
        end_d = _to_date(end)
        if start_d <= d <= end_d:
            return False
    return True


def count_recent_shifts(person: str, current_date: date, shift_history: Dict[str, List[date]]) -> int:
    if person not in shift_history:
        return 0
    cutoff = current_date - timedelta(days=SHIFT_WINDOW_DAYS)
    return sum(1 for d in shift_history[person] if cutoff < d < current_date)


def club_week_anchor(d: date) -> date:
    """
    Return the Wednesday that anchors the 'club week' containing this operating day.
    - For Wed: returns that Wed
    - For Sat/Sun: returns the Wed earlier that week
    """
    offset = (d.weekday() - 2) % 7  # Wed=2
    return d - timedelta(days=offset)


def bi_required_on(d: date, first_anchor: date, alternate: bool, first_off: bool) -> bool:
    """
    If alternate is False: BI always required.
    If alternate is True: BI required on alternating club weeks.
      week_index = 0 for first_anchor, 1 for next anchor, etc.
      - default: week 0 REQUIRED, week 1 OFF, week 2 REQUIRED...
      - if first_off: inverted.
    """
    if not alternate:
        return True

    week_index = (club_week_anchor(d) - first_anchor).days // 7
    required = (week_index % 2 == 0)
    if first_off:
        required = not required
    return required

# ==================================================
# SUPERVISION LOGIC
# ==================================================

def lead_required(assignments: Dict[str, str]) -> bool:
    inst = assignments.get("Instructor")
    return bool(inst and PEOPLE.get(inst, {}).get("requires_snr_di", False))

# ==================================================
# ROTA ENGINE
# ==================================================

def generate_rota(start: date, months: int, bi_alternate: bool, bi_first_off: bool) -> Dict[date, Dict[str, str]]:
    days = generate_operating_dates(start, months)

    shift_history = defaultdict(list)
    last_date_assigned = defaultdict(lambda: None)
    last_assigned = defaultdict(lambda: None)

    rota = {d: {r: "UNFILLED" for r in ALL_ROLES} for d in days}

    # Establish the first club-week anchor used for BI alternation
    first_anchor = club_week_anchor(days[0]) if days else start

    # ---------
    # STEP 0: Pre-mark BI/IFP as not required on "off" weeks
    # ---------
    for d in days:
        if not bi_required_on(d, first_anchor, bi_alternate, bi_first_off):
            rota[d]["BI/IFP"] = "n/a"

    # ---------
    # STEP 1: Assign primary roles
    # ---------
    slots = []
    for d in days:
        for r in PRIMARY_ROLES:
            # Skip BI/IFP slots on off weeks
            if r == "BI/IFP" and rota[d]["BI/IFP"] == "n/a":
                continue
            slots.append((d, r))

    def eligible_count(d, r):
        day = d.strftime("%a")
        return sum(
            1 for p, info in PEOPLE.items()
            if is_person_active_on(p, d)
            and day in info["allowed_days"]
            and r in info["allowed_roles"]
        )

    slots.sort(key=lambda s: (s[0], eligible_count(*s), s[1]))

    for d, role in slots:
        day = d.strftime("%a")
        assigned_today = set()

        for r in ALL_ROLES:
            person = rota[d].get(r)
            if person and person not in ["UNFILLED", "—", "NEED TO FILL", "(REQUIRED)"]:
                assigned_today.add(person)

        candidates = []

        for p, info in PEOPLE.items():
            if not is_person_active_on(p, d):
                continue
            if day not in info["allowed_days"]:
                continue
            if role not in info["allowed_roles"]:
                continue

            recent_shifts = count_recent_shifts(p, d, shift_history)
            if recent_shifts >= info["max_shifts_per_week"]:
                continue

            if p in assigned_today:
                continue

            if last_assigned[role] == p:
                continue

            if last_date_assigned[p] and (d - last_date_assigned[p]).days == 1:
                continue

            candidates.append(p)

        if not candidates:
            candidates = [
                p for p, info in PEOPLE.items()
                if is_person_active_on(p, d)
                and day in info["allowed_days"]
                and role in info["allowed_roles"]
                and p not in assigned_today
                and count_recent_shifts(p, d, shift_history) < info["max_shifts_per_week"]
                and not (last_date_assigned[p] and (d - last_date_assigned[p]).days == 1)
            ]

        if not candidates:
            rota[d][role] = "NEED TO FILL"
            continue

        min_shifts = min(count_recent_shifts(p, d, shift_history) for p in candidates)
        pool = [p for p in candidates if count_recent_shifts(p, d, shift_history) == min_shifts]

        random.shuffle(pool)
        chosen = pool[0]

        rota[d][role] = chosen
        shift_history[chosen].append(d)
        last_assigned[role] = chosen
        last_date_assigned[chosen] = d

    # ---------
    # STEP 2: Assign Lead Instructor (conditional)
    # ---------
    for d in days:
        if not lead_required(rota[d]):
            rota[d][LEAD_ROLE] = "—"
            continue

        day = d.strftime("%a")
        assigned_today = set()

        for r in ALL_ROLES:
            person = rota[d].get(r)
            if person and person not in ["UNFILLED", "—", "NEED TO FILL", "(REQUIRED)"]:
                assigned_today.add(person)

        candidates = []

        for p, info in PEOPLE.items():
            if not is_person_active_on(p, d):
                continue
            if day not in info["allowed_days"]:
                continue
            if LEAD_ROLE not in info["allowed_roles"]:
                continue
            if p in assigned_today:
                continue

            recent_shifts = count_recent_shifts(p, d, shift_history)
            if recent_shifts >= info["max_shifts_per_week"]:
                continue

            if last_date_assigned[p] and (d - last_date_assigned[p]).days == 1:
                continue

            candidates.append(p)

        if not candidates:
            rota[d][LEAD_ROLE] = "(REQUIRED)"
            continue

        min_shifts = min(count_recent_shifts(p, d, shift_history) for p in candidates)
        pool = [p for p in candidates if count_recent_shifts(p, d, shift_history) == min_shifts]
        random.shuffle(pool)
        chosen = pool[0]

        rota[d][LEAD_ROLE] = chosen
        shift_history[chosen].append(d)
        last_assigned[LEAD_ROLE] = chosen
        last_date_assigned[chosen] = d

    return dict(sorted(rota.items()))

# ==================================================
# OUTPUT
# ==================================================

def print_rota_table(rota: Dict[date, Dict[str, str]]):
    headers = ["Day", "Date"] + ALL_ROLES
    widths = [10, 12] + [18] * len(ALL_ROLES)

    def row(vals):
        return " | ".join(str(v).ljust(w) for v, w in zip(vals, widths))

    print(row(headers))
    print("-" * (sum(widths) + 3 * (len(headers) - 1)))

    for d, roles in rota.items():
        print(row(
            [d.strftime("%A"), d.strftime("%d %b %Y")]
            + [roles[r] for r in ALL_ROLES]
        ))

# ==================================================
# COMMAND LINE INTERFACE
# ==================================================

def parse_args():
    p = argparse.ArgumentParser(
        description=(
            "Generate an instructor rota with conditional Lead Instructor oversight.\n\n"
            "Optional feature:\n"
            "  - BI/IFP can be required every other club-week (Wed/Sat/Sun treated as one week)."
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    p.add_argument(
        "--start",
        default=date.today().isoformat(),
        help="Start date (YYYY-MM-DD). Default: today"
    )

    p.add_argument(
        "--months",
        type=int,
        default=1,
        help="Number of months to generate. Default: 1"
    )

    p.add_argument(
        "--bi-alternate",
        action="store_true",
        help=(
            "Make BI/IFP required on alternating club-weeks.\n"
            "Club-week = Wed/Sat/Sun operating cycle.\n"
            "Default pattern: first club-week REQUIRED, next club-week N/A, repeat."
        )
    )

    p.add_argument(
        "--bi-first-off",
        action="store_true",
        help=(
            "Invert the alternate BI/IFP pattern.\n"
            "If set, the first club-week is N/A, the next is REQUIRED, repeat.\n"
            "Only applies when used with --bi-alternate."
        )
    )

    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    start = date.fromisoformat(args.start)

    rota = generate_rota(start, args.months, args.bi_alternate, args.bi_first_off)
    print_rota_table(rota)




