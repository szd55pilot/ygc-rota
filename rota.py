# rota.py
# v1.5 - Instructor Rota Generator with Rolling Window Constraints
#
# This script generates a rota (schedule) for gliding club operations across
# multiple roles. It enforces several constraints to ensure fair distribution
# and prevent overwork:
#
# - No person works consecutive days
# - No person exceeds their max_shifts_per_week within a 14-day rolling window
# - Lead Instructor supervision is provided when required
# - People are only assigned to days/roles they're qualified for
# - Inactive periods (holidays, etc.) are respected

import argparse
import random
from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, List

from people import PEOPLE

# ==================================================
# CONFIGURATION
# ==================================================

# Define which days of the week the club operates (as weekday numbers)
# Wednesday = 2, Saturday = 5, Sunday = 6
OPERATING_DAYS = {"Wed": 2, "Sat": 5, "Sun": 6}

# Primary roles that need to be filled every operating day
PRIMARY_ROLES = [
    "Instructor",      # Primary flying instructor
    "Tug Pilot",       # Tows gliders into the air
    "BI/IFP",          # Basic Instructor / Instructor Full Panel
    "LPS",             # Launch Point Supervisor
    "Duty Pilot",      # Overall duty pilot for the day
]

# Special supervisory role (only needed for certain instructors)
LEAD_ROLE = "Lead Instructor"

# Complete list of all roles (Instructor appears twice: once as primary, once as Lead)
ALL_ROLES = ["Instructor", LEAD_ROLE] + PRIMARY_ROLES[1:]

# Rolling window for counting shifts (in days)
# If someone works on day X, they can't work again until day X + SHIFT_WINDOW_DAYS
# This handles the Wed/Sat/Sun pattern that crosses calendar week boundaries
SHIFT_WINDOW_DAYS = 14

# ==================================================
# DATE HELPERS
# ==================================================

def generate_operating_dates(start: date, months: int) -> List[date]:
    """
    Generate a list of all operating dates within the specified period.
    
    Args:
        start: First date to consider
        months: Number of months to generate (approximate - uses 31 days per month)
    
    Returns:
        List of dates that fall on operating days (Wed, Sat, Sun)
    """
    end = start + timedelta(days=months * 31)
    d = start
    days = []
    while d <= end:
        # Check if this date's weekday is one we operate on
        if d.weekday() in OPERATING_DAYS.values():
            days.append(d)
        d += timedelta(days=1)
    return days


def _to_date(d):
    """
    Helper to convert either a date object or ISO string to a date object.
    Used for processing inactive_periods which may be stored as strings or dates.
    """
    if isinstance(d, date):
        return d
    return date.fromisoformat(d)


def is_person_active_on(person: str, d: date) -> bool:
    """
    Check if a person is available (not on holiday/inactive) on a given date.
    
    A person is inactive if the date falls within any of their inactive_periods
    defined in people.py.
    
    Args:
        person: Person's name (as it appears in PEOPLE dict)
        d: Date to check
    
    Returns:
        False if person is inactive on this date, True otherwise
    """
    periods = PEOPLE.get(person, {}).get("inactive_periods", [])
    for start, end in periods:
        start_d = _to_date(start)
        end_d = _to_date(end)
        # Check if date falls within this inactive period (inclusive)
        if start_d <= d <= end_d:
            return False
    return True


def count_recent_shifts(person: str, current_date: date, shift_history: Dict[str, List[date]]) -> int:
    """
    Count how many shifts a person has worked in the recent rolling window.
    
    This looks back SHIFT_WINDOW_DAYS from current_date and counts all shifts
    the person worked in that period (excluding current_date itself).
    
    Args:
        person: Person's name
        current_date: The date we're checking for (not included in count)
        shift_history: Dictionary mapping person names to lists of dates worked
    
    Returns:
        Number of shifts worked in the rolling window
    """
    if person not in shift_history:
        return 0
    
    cutoff = current_date - timedelta(days=SHIFT_WINDOW_DAYS)
    # Count shifts between cutoff and current_date (exclusive of current_date)
    return sum(1 for d in shift_history[person] if cutoff < d < current_date)

# ==================================================
# SUPERVISION LOGIC
# ==================================================

def lead_required(assignments: Dict[str, str]) -> bool:
    """
    Determine if a Lead Instructor is required for a given day's assignments.
    
    A Lead Instructor is needed when the primary Instructor assigned has
    requires_snr_di set to True (indicating they need senior supervision).
    
    Args:
        assignments: Dictionary of {role: person} for one day
    
    Returns:
        True if Lead Instructor supervision is required, False otherwise
    """
    inst = assignments.get("Instructor")
    return bool(inst and PEOPLE.get(inst, {}).get("requires_snr_di", False))

# ==================================================
# ROTA ENGINE
# ==================================================

def generate_rota(start: date, months: int) -> Dict[date, Dict[str, str]]:
    """
    Generate a complete rota for the specified period.
    
    This is the main function that coordinates the entire scheduling process.
    It processes all dates chronologically, assigning people to roles while
    respecting all constraints.
    
    Args:
        start: First date to include in rota
        months: Number of months to generate
    
    Returns:
        Dictionary mapping dates to role assignments:
        {date: {role: person_name}}
    """
    # Get all dates we need to schedule
    days = generate_operating_dates(start, months)
    
    # Track all dates each person has worked (for rolling window check)
    # Format: {person_name: [date1, date2, ...]}
    shift_history = defaultdict(list)
    
    # Track the last date each person worked (for consecutive day prevention)
    # Format: {person_name: last_date_worked}
    last_date_assigned = defaultdict(lambda: None)
    
    # Track the last person assigned to each role (to avoid same person/role repeatedly)
    # Format: {role_name: last_person_assigned}
    last_assigned = defaultdict(lambda: None)
    
    # Initialize the rota structure with all dates and roles
    rota = {
        d: {r: "UNFILLED" for r in ALL_ROLES}
        for d in days
    }

    # ---------
    # STEP 1: Assign primary roles (Instructor, Tug Pilot, BI/IFP, LPS, Duty Pilot)
    # ---------
    
    # Create a list of all (date, role) combinations that need filling
    slots = [(d, r) for d in days for r in PRIMARY_ROLES]

    def eligible_count(d, r):
        """
        Count how many people are eligible for a given role on a given date.
        
        This is used for prioritization: slots with fewer eligible people
        are harder to fill, so we consider them when sorting.
        """
        day = d.strftime("%a")
        return sum(
            1 for p, info in PEOPLE.items()
            if is_person_active_on(p, d)
            and day in info["allowed_days"]
            and r in info["allowed_roles"]
        )

    # Sort slots to process them in optimal order:
    # 1. By DATE first (chronological) - critical for consecutive day checks
    # 2. By eligible_count - harder-to-fill slots get priority
    # 3. By role name - consistent ordering for ties
    slots.sort(key=lambda s: (s[0], eligible_count(*s), s[1]))

    # Process each (date, role) slot
    for d, role in slots:
        day = d.strftime("%a")  # e.g., "Wed", "Sat", "Sun"
        assigned_today = set()
        
        # Collect who's already assigned on this date (to prevent double-booking)
        for r in ALL_ROLES:
            person = rota[d].get(r)
            if person and person not in ["UNFILLED", "—", "NEED TO FILL", "(REQUIRED)"]:
                assigned_today.add(person)
        
        # Build list of candidates who meet ALL constraints
        candidates = []

        for p, info in PEOPLE.items():
            # Constraint 1: Person must be active (not on holiday)
            if not is_person_active_on(p, d):
                continue
            
            # Constraint 2: Person must be available on this day of week
            if day not in info["allowed_days"]:
                continue
            
            # Constraint 3: Person must be qualified for this role
            if role not in info["allowed_roles"]:
                continue
            
            # Constraint 4: Check rolling window shift limit
            # Person can't exceed their max_shifts_per_week in the last 14 days
            recent_shifts = count_recent_shifts(p, d, shift_history)
            if recent_shifts >= info["max_shifts_per_week"]:
                continue
            
            # Constraint 5: Person can't be assigned twice on same day
            if p in assigned_today:
                continue
            
            # Constraint 6: Avoid assigning same person to same role consecutively
            # (helps distribute roles fairly)
            if last_assigned[role] == p:
                continue
            
            # Constraint 7: No consecutive days - person can't work if they worked yesterday
            if last_date_assigned[p] and (d - last_date_assigned[p]).days == 1:
                continue
            
            # All constraints passed - this person is a valid candidate
            candidates.append(p)

        # If no candidates found with all constraints, try relaxing some
        if not candidates:
            # Fallback: only relax the role rotation constraint (last_assigned check)
            # Still enforce: availability, qualifications, rolling window, no double-booking, no consecutive days
            candidates = [
                p for p, info in PEOPLE.items()
                if is_person_active_on(p, d)
                and day in info["allowed_days"]
                and role in info["allowed_roles"]
                and p not in assigned_today
                and count_recent_shifts(p, d, shift_history) < info["max_shifts_per_week"]
                and not (last_date_assigned[p] and (d - last_date_assigned[p]).days == 1)
            ]

        # If still no candidates, mark slot as needing manual filling
        if not candidates:
            rota[d][role] = "NEED TO FILL"
            continue

        # From eligible candidates, prefer those with fewest recent shifts (load balancing)
        min_shifts = min(count_recent_shifts(p, d, shift_history) for p in candidates)
        pool = [p for p in candidates if count_recent_shifts(p, d, shift_history) == min_shifts]
        
        # Randomly select from the pool (fairness)
        random.shuffle(pool)
        chosen = pool[0]

        # Assign the person and update tracking structures
        rota[d][role] = chosen
        shift_history[chosen].append(d)  # Record this shift in history
        last_assigned[role] = chosen      # Track for role rotation
        last_date_assigned[chosen] = d    # Track for consecutive day prevention

    # ---------
    # STEP 2: Assign Lead Instructor (conditional - only when required)
    # ---------
    
    # Process each date to determine if Lead Instructor is needed
    for d in days:
        # Check if the assigned Instructor requires supervision
        if not lead_required(rota[d]):
            # No Lead Instructor needed - mark with dash
            rota[d][LEAD_ROLE] = "—"
            continue

        # Lead Instructor IS required - try to find someone
        day = d.strftime("%a")
        assigned_today = set()
        
        # Collect who's already assigned (can't assign Lead if already doing another role)
        for r in ALL_ROLES:
            person = rota[d].get(r)
            if person and person not in ["UNFILLED", "—", "NEED TO FILL", "(REQUIRED)"]:
                assigned_today.add(person)
        
        # Build candidate list with same constraints as primary roles
        candidates = []

        for p, info in PEOPLE.items():
            # Same constraints as before, but for Lead Instructor role
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

        # If no one available, mark as required but unfilled
        if not candidates:
            rota[d][LEAD_ROLE] = "(REQUIRED)"
            continue

        # Select from candidates with fewest recent shifts
        min_shifts = min(count_recent_shifts(p, d, shift_history) for p in candidates)
        pool = [p for p in candidates if count_recent_shifts(p, d, shift_history) == min_shifts]
        random.shuffle(pool)
        chosen = pool[0]

        # Assign and update tracking
        rota[d][LEAD_ROLE] = chosen
        shift_history[chosen].append(d)
        last_assigned[LEAD_ROLE] = chosen
        last_date_assigned[chosen] = d

    # Return rota sorted by date
    return dict(sorted(rota.items()))

# ==================================================
# OUTPUT
# ==================================================

def print_rota_table(rota: Dict[date, Dict[str, str]]):
    """
    Print the rota in a formatted table suitable for display/printing.
    
    Outputs a nicely aligned table with columns for:
    - Day of week
    - Date
    - Each role's assignment
    
    Args:
        rota: The complete rota dictionary from generate_rota()
    """
    # Define column headers and widths
    headers = ["Day", "Date"] + ALL_ROLES
    widths = [10, 12] + [18] * len(ALL_ROLES)

    def row(vals):
        """Format a row with proper column widths and separators."""
        return " | ".join(str(v).ljust(w) for v, w in zip(vals, widths))

    # Print header
    print(row(headers))
    print("-" * (sum(widths) + 3 * (len(headers) - 1)))

    # Print each date's assignments
    for d, roles in rota.items():
        print(row(
            [d.strftime("%A"), d.strftime("%d %b %Y")]
            + [roles[r] for r in ALL_ROLES]
        ))

# ==================================================
# COMMAND LINE INTERFACE
# ==================================================

def parse_args():
    """
    Parse command line arguments for the rota generator.
    
    Supported arguments:
        --start: Start date in ISO format (YYYY-MM-DD). Defaults to today.
        --months: Number of months to generate. Defaults to 1.
    """
    p = argparse.ArgumentParser(
        description="Generate an instructor rota with conditional Lead Instructor oversight.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    p.add_argument("--start", default=date.today().isoformat(),
                   help="Start date (YYYY-MM-DD). Default: today")
    p.add_argument("--months", type=int, default=1,
                   help="Number of months to generate. Default: 1")
    return p.parse_args()


if __name__ == "__main__":
    # Main entry point when script is run directly
    args = parse_args()
    start = date.fromisoformat(args.start)
    
    # Generate the rota
    rota = generate_rota(start, args.months)
    
    # Display it
    print_rota_table(rota)