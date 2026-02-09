# YGC Rota Generator

This project generates a simple rota for York Gliding Centre operating days.

It assigns people to roles on:

- **Wednesday**
- **Saturday**
- **Sunday**

The rota is generated from a `people.py` file containing each person’s:

- allowed days
- allowed roles
- workload limit
- whether they require a Lead Instructor
- optional inactive periods (date windows)

Output is printed as a fixed-width table to the terminal.

---

## Files

### `rota.py`
The rota generator script.

### `people.py`
Contains a dictionary called `PEOPLE` which defines who can do what and when.

---

## Roles

The rota currently assigns:

- Instructor
- Lead Instructor (only when required)
- Tug Pilot
- BI/IFP
- LPS
- Duty Pilot

---

## `people.py` format

The `people.py` file must contain a dictionary named `PEOPLE`.

Example:

```python
PEOPLE = {
    #
    # Instructors
    #
    "A NAME": {
        "allowed_days": {"Wed"},
        "allowed_roles": {"Instructor", "Lead Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False,
        "inactive_periods": [
            ("2026-02-21", "2026-02-23"),
        ]
    },

    "A NOTHERNAME": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"Instructor"},
        "max_shifts_per_week": 1,
        "requires_snr_di": False
    }
}
```

Notes

Allowed_days and allowed_roles are sets

Inactive_periods are optional

Dates must be ISO format: YYYY-MM-DD

### Inactive periods
Inactive periods prevent a person from being scheduled during a given date range.

Single day inactive and multiple inactive periods

```python

"inactive_periods": [
    ("2026-02-21", "2026-02-21")
]

"inactive_periods": [
    ("2026-02-21", "2026-02-23"),
    ("2026-03-10", "2026-03-10"),
    ("2026-04-01", "2026-04-07")
]
```

### Lead Instructor logic
If the person assigned as Instructor has:

"requires_snr_di": True
Then a Lead Instructor is required for that day.

If no Lead Instructor can be assigned, the rota prints:

(REQUIRED)

### Running the rota
Basic usage (1 month)
Generate one month starting from a specific date:

```bash

python3 rota.py --start 2026-02-01
```
Generate multiple months

Generate 3 months starting from a specific date:

```bash

python3 rota.py --start 2026-02-01 --months 3
```
View help / options

```bash

python3 rota.py --help
```
### Alternate BI/IFP weeks (optional)
By default, the rota schedules a BI/IFP every operating day.

If you want BI/IFP to be required only on alternate club-weeks, you can use:

```bash

python3 rota.py --start 2026-02-01 --months 2 --bi-alternate
```
A "club-week" means the Wed/Sat/Sun operating cycle (treated as one unit).

The default pattern is:

Week 1: BI/IFP required
Week 2: BI/IFP not required (shown as N/A)
Week 3: BI/IFP required

etc.

Starting with a no-BI week
If you want the first club-week to be the "no BI required" week, use:

```bash

python3 rota.py --start 2026-02-01 --months 2 --bi-alternate --bi-first-off
```

### Output notes

If no eligible person can be found, the role is shown as: NEED TO FILL

If a Lead Instructor is required but cannot be assigned, it is shown as: (REQUIRED)

If BI/IFP is not required for that club-week (alternate BI mode), it is shown as: n/a
