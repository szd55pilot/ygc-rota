# rota.py
# v1.1.2

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
    """
    Person is inactive if date d falls within any inactive_period.
    Supports date or ISO string boundaries.
    """
    periods = PEOPLE.get(person, {}).get("inactive_periods", [])
    for start, end in periods:
        start_d = _to_date(start)
        end_d = _to_date(end)
        if start_d <= d <= end_d:
            return False
    return True

# ==================================================
# SUPERVISION LOGIC
# ==================================================
def lead_required(assignments: Dict[str, str]) -> bool:
    inst = assignments.get("Instructor")
    return bool(inst and PEOPLE.get(inst, {}).get("requires_snr_di", False))

# ==================================================
# ROTA ENGINE
# ==================================================
def generate_week_rota(
    dates: List[date],
    shifts_used: Dict[str, int],
) -> Dict[date, Dict[str, str]]:

    rota = {
        d: {r: "UNFILLED" for r in ALL_ROLES}
        for d in dates
    }

    assigned_today = defaultdict(set)
    last_assigned = defaultdict(lambda: None)

    # ---------
    # STEP 1: Assign normal roles
    # ---------
    slots = [(d, r) for d in dates for r in PRIMARY_ROLES]

    def eligible_count(d, r):
        day = d.strftime("%a")
        return sum(
            1 for p, info in PEOPLE.items()
            if is_person_active_on(p, d)
            and day in info["allowed_days"]
            and r in info["allowed_roles"]
        )

    slots.sort(key=lambda s: (eligible_count(*s), s[0], s[1]))

    for d, role in slots:
        day = d.strftime("%a")
        candidates = []

        for p, info in PEOPLE.items():
            if not is_person_active_on(p, d):
                continue
            if day not in info["allowed_days"]:
                continue
            if role not in info["allowed_roles"]:
                continue
            if shifts_used[p] >= info["max_shifts_per_week"]:
                continue
            if p in assigned_today[d]:
                continue
            if last_assigned[role] == p:
                continue
            candidates.append(p)

        if not candidates:
            candidates = [
                p for p, info in PEOPLE.items()
                if is_person_active_on(p, d)
                and day in info["allowed_days"]
                and role in info["allowed_roles"]
                and p not in assigned_today[d]
            ]

        if not candidates:
            rota[d][role] = "NEED TO FILL"
            continue

        min_shifts = min(shifts_used[p] for p in candidates)
        pool = [p for p in candidates if shifts_used[p] == min_shifts]
        random.shuffle(pool)
        chosen = pool[0]

        rota[d][role] = chosen
        shifts_used[chosen] += 1
        assigned_today[d].add(chosen)
        last_assigned[role] = chosen

    # ---------
    # STEP 2: Lead Instructor (conditional)
    # ---------
    for d in dates:
        if not lead_required(rota[d]):
            rota[d][LEAD_ROLE] = "—"
            continue

        day = d.strftime("%a")
        candidates = []

        for p, info in PEOPLE.items():
            if not is_person_active_on(p, d):
                continue
            if day not in info["allowed_days"]:
                continue
            if LEAD_ROLE not in info["allowed_roles"]:
                continue
            if p in assigned_today[d]:
                continue
            candidates.append(p)

        if not candidates:
            rota[d][LEAD_ROLE] = "(REQUIRED)"
            continue

        min_shifts = min(shifts_used[p] for p in candidates)
        pool = [p for p in candidates if shifts_used[p] == min_shifts]
        random.shuffle(pool)
        chosen = pool[0]

        rota[d][LEAD_ROLE] = chosen
        shifts_used[chosen] += 1
        assigned_today[d].add(chosen)
        last_assigned[LEAD_ROLE] = chosen

    return rota

def generate_rota(start: date, months: int) -> Dict[date, Dict[str, str]]:
    days = generate_operating_dates(start, months)
    weeks = defaultdict(list)
    for d in days:
        weeks[d.isocalendar()[1]].append(d)

    shifts_used = defaultdict(int)
    rota = {}

    for week in weeks.values():
        rota.update(generate_week_rota(week, shifts_used))

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
# CLI
# ==================================================
def parse_args():
    p = argparse.ArgumentParser(
        description="Generate an instructor rota with conditional Lead Instructor oversight.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    p.add_argument("--start", default=date.today().isoformat())
    p.add_argument("--months", type=int, default=1)
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    start = date.fromisoformat(args.start)
    rota = generate_rota(start, args.months)
    print_rota_table(rota)
