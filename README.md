# YGC Rota Generator

This repository contains a Python script to generate a **gliding club instructor rota** with conditional Lead Instructor oversight, designed for flexible scheduling and handling instructor unavailability.

> **Private repository – internal use only.**

---

## Files

- `rota.py` – main script to generate the rota.
- `people.py` – configuration file listing instructors, roles, availability, maximum shifts, and inactive periods.
- `.gitignore` – ignores Python cache files (`__pycache__/`).

---

## Features

- Supports multiple roles per day:
  - Instructor
  - Lead Instructor (scheduled automatically if an Instructor requires supervision)
  - Tug Pilot
  - BI/IFP
  - LPS
  - Duty Pilot
- Handles instructor availability by day and per-week shift limits.
- Supports **inactive periods** for instructors (single days or date ranges).
- Distributes workload fairly and avoids assigning the same person consecutively for the same role.
- Generates clean **table output** for the rota.

---

## Usage

## Alternate BI/IFP weeks (optional)

By default, the rota schedules a BI/IFP every operating day.

If you want BI/IFP to be required only on alternate club-weeks, you can use:

```bash
python3 rota.py --start 2026-02-01 --months 2 --bi-alternate


