# rota.py
# v1.5 - Fixed slot sorting to process dates chronologically for consecutive day checks

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

# Number of days to look back when counting shifts
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

def count_recent_shifts(person: str, current_date: date, shift_history: Dict[str, List[date]]) -> int:
    """Count how many shifts person has worked in the last SHIFT_WINDOW_DAYS days"""
    if person not in shift_history:
        return 0
    
    cutoff = current_date - timedelta(days=SHIFT_WINDOW_DAYS)
    return sum(1 for d in shift_history[person] if cutoff < d < current_date)

# ==================================================
# SUPERVISION LOGIC
# ==================================================
def lead_required(assignments: Dict[str, str]) -> bool:
    inst = assignments.get("Instructor")
    return bool(inst and PEOPLE.get(inst, {}).get("requires_snr_di", False))

# ==================================================
# ROTA ENGINE
# ==================================================
def generate_rota(start: date, months: int) -> Dict[date, Dict[str, str]]:
    days = generate_operating_dates(start, months)
    
    # Track all dates each person has worked (for rolling window check)
    shift_history = defaultdict(list)
    
    # Track last date assigned per person (for consecutive day prevention)
    last_date_assigned = defaultdict(lambda: None)
    
    # Track last person assigned to each role (for role rotation)
    last_assigned = defaultdict(lambda: None)
    
    rota = {
        d: {r: "UNFILLED" for r in ALL_ROLES}
        for d in days
    }

    # ---------
    # STEP 1: Assign normal roles
    # ---------
    slots = [(d, r) for d in days for r in PRIMARY_ROLES]

    def eligible_count(d, r):
        day = d.strftime("%a")
        return sum(
            1 for p, info in PEOPLE.items()
            if is_person_active_on(p, d)
            and day in info["allowed_days"]
            and r in info["allowed_roles"]
        )

    # Sort by DATE FIRST, then by eligible count, then by role
    # This ensures chronological processing for consecutive day checks
    slots.sort(key=lambda s: (s[0], eligible_count(*s), s[1]))

    for d, role in slots:
        day = d.strftime("%a")
        assigned_today = set()
        
        # Collect who's already assigned on this date
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
            # Check rolling window shift limit
            recent_shifts = count_recent_shifts(p, d, shift_history)
            if recent_shifts >= info["max_shifts_per_week"]:
                continue
            if p in assigned_today:
                continue
            if last_assigned[role] == p:
                continue
            # Check if person worked yesterday
            if last_date_assigned[p] and (d - last_date_assigned[p]).days == 1:
                continue
            candidates.append(p)

        if not candidates:
            # Fallback: relax some constraints but keep rolling window limit and consecutive day check
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
    # STEP 2: Lead Instructor (conditional)
    # ---------
    for d in days:
        if not lead_required(rota[d]):
            rota[d][LEAD_ROLE] = "—"
            continue

        day = d.strftime("%a")
        assigned_today = set()
        
        # Collect who's already assigned on this date
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
            # Check rolling window shift limit
            recent_shifts = count_recent_shifts(p, d, shift_history)
            if recent_shifts >= info["max_shifts_per_week"]:
                continue
            # Check consecutive days
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