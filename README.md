# YGC Rota Generator

A Python tool that generates instructor rotas for York Gliding Centre operating days (Wednesday, Saturday, Sunday) with intelligent scheduling constraints and optional alternating BI/IFP weeks.

---

## Features

- **Smart scheduling**: Respects person workload limits and allowed days/roles
- **14-day rolling window**: Prevents overwork by tracking recent shifts
- **Consecutive day prevention**: Blocks same person from flying two consecutive operating days
- **Lead Instructor logic**: Automatically assigns supervision when required
- **Inactive periods**: Support for vacation/unavailability windows
- **Alternate BI/IFP weeks**: Optional every-other-week scheduling for BI/IFP role
- **Club-week anchoring**: Groups Wed/Sat/Sun as a single scheduling unit

---

## Files

| File | Purpose |
|------|---------|
| `rota.py` | Main rota generator engine |
| `people.py` | Person definitions and availability |
| `tests/test_rota.py` | Unit tests |

---

## Roles

The rota assigns the following roles:

- **Instructor** – Primary flying instructor
- **Lead Instructor** – Senior supervisor (conditional, when required)
- **Tug Pilot** – Tow plane operator
- **BI/IFP** – Basic Instruction / Instructor familiarisation pass
- **LPS** – Launch Point Supervisor
- **Duty Pilot** – Daily operations coordinator

---

## `people.py` Configuration

The `people.py` file must contain a `PEOPLE` dictionary.

### Example

```python
PEOPLE = {
    "ALICE": {
        "allowed_days": {"Wed", "Sat", "Sun"},
        "allowed_roles": {"Instructor", "Lead Instructor"},
        "max_shifts_per_week": 2,
        "requires_snr_di": False,
        "inactive_periods": [
            ("2026-02-21", "2026-02-23"),
            ("2026-04-01", "2026-04-07"),
        ],
    },
    
    "BOB": {
        "allowed_days": {"Wed", "Sat"},
        "allowed_roles": {"Tug Pilot", "Duty Pilot"},
        "max_shifts_per_week": 3,
    },
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `allowed_days` | Set[str] | Yes | Days person can fly: `{"Wed", "Sat", "Sun"}` |
| `allowed_roles` | Set[str] | Yes | Roles person can perform |
| `max_shifts_per_week` | int | Yes | Maximum shifts per 7-day period |
| `requires_snr_di` | bool | No | If `True`, a Lead Instructor is required when this person is assigned as Instructor (default: `False`) |
| `inactive_periods` | List[Tuple[str, str]] | No | Date ranges when unavailable (inclusive). Dates must be ISO format: `YYYY-MM-DD` |

---

## Usage

### Basic (one month from today)

```bash
python3 rota.py
```

### Specific start date

```bash
python3 rota.py --start 2026-02-01
```

### Multiple months

```bash
python3 rota.py --start 2026-02-01 --months 3
```

### Alternate BI/IFP weeks

By default, BI/IFP is required on every operating day. Use `--bi-alternate` to require BI/IFP only on alternating club-weeks (Wed/Sat/Sun groupings):

```bash
python3 rota.py --start 2026-02-01 --bi-alternate
```

Pattern:
- Week 1: BI/IFP required
- Week 2: BI/IFP not required (shown as `n/a`)
- Week 3: BI/IFP required
- ...

### Invert alternate pattern (start with no BI week)

```bash
python3 rota.py --start 2026-02-01 --bi-alternate --bi-first-off
```

### View all options

```bash
python3 rota.py --help
```

---

## Scheduling Constraints

The rota respects the following constraints:

1. **Workload limit**: No person exceeds their `max_shifts_per_week` per calendar week
2. **14-day rolling window**: No person assigned more than their limit in the past 14 days
3. **Consecutive day prevention**: Same person cannot fly on consecutive operating days (e.g., Wed then Sat)
4. **Inactive periods**: People are excluded during specified date ranges
5. **Role restrictions**: Only people with allowed roles are considered for each slot
6. **Day restrictions**: Only people available on that specific day are considered

---

## Output

### Status Messages

| Status | Meaning |
|--------|---------|
| `NEED TO FILL` | No eligible person found for this role |
| `(REQUIRED)` | Lead Instructor required but could not be assigned |
| `n/a` | Role not required for this club-week (BI/IFP alternate mode only) |

### Example Output

```
Day        Date             Instructor    Lead Instructor  Tug Pilot       BI/IFP         LPS            Duty Pilot     
------------------------------------------------------------------------------------------------------------------------------
Wednesday  2026-02-01       ALICE         BOB              CHARLIE         DAVE           EVE            FRANK          
Saturday   2026-02-04       BOB           (REQUIRED)       ALICE           NEED TO FILL   CHARLIE        DAVE           
Sunday     2026-02-05       CHARLIE       EVE              DAVE            n/a            FRANK          ALICE          
```

---

## Testing

Run the test suite:

```bash
pytest tests/test_rota.py -v
```

---

## Notes

- All dates must be in ISO format: `YYYY-MM-DD`
- Inactive periods are **inclusive** on both start and end dates
- The "club-week" always starts on **Wednesday** for consistency