#!/usr/bin/env python3
"""
ygc-rota.py

A tiny no-dependencies local web app for editing inactive periods in people.py.

Features:
- Pick a person from PEOPLE
- Add / edit / remove inactive periods
- PREVIEW changes before saving
- Keep only ONE backup file: people.py.bak
- Reject dates before today
- Rewrite people.py in a clean canonical format
- Show a neat summary of current days / roles / limits

Run:
    python3 ygc-rota.py --people-file people.py --port 8000

Then open:
    http://127.0.0.1:8000
"""

import argparse
import html
import importlib.util
import json
import shutil
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, urlparse


DAY_ORDER = ["Wed", "Sat", "Sun"]
ROLE_ORDER = [
    "Instructor",
    "Lead Instructor",
    "Tug Pilot",
    "BI/IFP",
    "LPS",
    "Duty Pilot",
]
FIELD_ORDER = [
    "allowed_days",
    "allowed_roles",
    "max_shifts_per_week",
    "requires_snr_di",
    "inactive_periods",
]


def load_people_module(people_file: Path):
    spec = importlib.util.spec_from_file_location("people_module_for_editor", people_file)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {people_file}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "PEOPLE"):
        raise RuntimeError(f"{people_file} does not define PEOPLE")
    return module


def load_people(people_file: Path):
    module = load_people_module(people_file)
    return module.PEOPLE


def to_iso_string(value):
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def normalize_inactive_periods(periods):
    normalized = []
    for start, end in periods:
        start_s = to_iso_string(start).strip()
        end_s = to_iso_string(end).strip()
        if not end_s:
            end_s = start_s
        normalized.append((start_s, end_s))
    return normalized


def sorted_days(days_set):
    return [d for d in DAY_ORDER if d in days_set]


def sorted_roles(roles_set):
    known = [r for r in ROLE_ORDER if r in roles_set]
    extra = sorted(r for r in roles_set if r not in ROLE_ORDER)
    return known + extra


def format_python_set(items):
    items = list(items)
    if not items:
        return "set()"
    quoted = ", ".join(f'"{item}"' for item in items)
    return "{" + quoted + "}"


def format_inactive_periods(periods, indent="        "):
    if not periods:
        return None

    lines = [f'{indent}"inactive_periods": [']
    for idx, (start, end) in enumerate(periods):
        comma = "," if idx < len(periods) - 1 else ""
        lines.append(f'{indent}    ("{start}", "{end}"){comma}')
    lines.append(f"{indent}]")
    return "\n".join(lines)


def render_people_py(people):
    lines = []
    lines.append("PEOPLE = {")
    lines.append("")

    names = list(people.keys())
    for idx, name in enumerate(names):
        info = people[name]
        lines.append(f'    "{name}": {{')

        field_lines = []

        if "allowed_days" in info:
            days = sorted_days(info["allowed_days"])
            field_lines.append(
                f'        "allowed_days": {format_python_set(days)},'
            )

        if "allowed_roles" in info:
            roles = sorted_roles(info["allowed_roles"])
            field_lines.append(
                f'        "allowed_roles": {format_python_set(roles)},'
            )

        if "max_shifts_per_week" in info:
            field_lines.append(
                f'        "max_shifts_per_week": {info["max_shifts_per_week"]},'
            )

        if "requires_snr_di" in info:
            field_lines.append(
                f'        "requires_snr_di": {"True" if info["requires_snr_di"] else "False"}'
                + ("," if "inactive_periods" in info and info["inactive_periods"] else "")
            )

        if info.get("inactive_periods"):
            inactive = normalize_inactive_periods(info["inactive_periods"])
            field_lines.append(format_inactive_periods(inactive))

        known = set(FIELD_ORDER)
        extras = [k for k in info.keys() if k not in known]
        for key in extras:
            value = info[key]
            if isinstance(value, bool):
                rendered = "True" if value else "False"
            elif isinstance(value, int):
                rendered = str(value)
            elif isinstance(value, set):
                rendered = format_python_set(sorted(value))
            elif isinstance(value, list):
                rendered = repr(value)
            else:
                rendered = repr(value)
            field_lines.append(f'        "{key}": {rendered}')

        for line_no, field_line in enumerate(field_lines):
            if (
                line_no < len(field_lines) - 1
                and not field_line.rstrip().endswith(",")
                and not field_line.rstrip().endswith("]")
            ):
                field_line += ","
            lines.append(field_line)

        closing = "    }," if idx < len(names) - 1 else "    }"
        lines.append(closing)
        lines.append("")

    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def backup_people_file(people_file: Path):
    """
    Keep only one backup file: people.py.bak
    Remove any older backup variants first.
    """
    backup = people_file.with_name(f"{people_file.name}.bak")

    for f in people_file.parent.glob(f"{people_file.name}.bak*"):
        try:
            f.unlink()
        except Exception:
            pass

    shutil.copy2(people_file, backup)
    return backup


def validate_periods(periods):
    validated = []
    today = date.today()

    for start, end in periods:
        start = start.strip()
        end = end.strip() or start

        try:
            start_d = date.fromisoformat(start)
            end_d = date.fromisoformat(end)
        except ValueError:
            raise ValueError(
                f"Invalid date format: {start} / {end}. Use YYYY-MM-DD."
            )

        if start_d < today:
            raise ValueError(
                f"Start date {start} is before today ({today})."
            )

        if end_d < today:
            raise ValueError(
                f"End date {end} is before today ({today})."
            )

        if end_d < start_d:
            raise ValueError(
                f"End date {end} is before start date {start}."
            )

        validated.append((start, end))

    return validated


def update_person_inactive_periods(people_file: Path, person_name: str, periods):
    people = load_people(people_file)

    if person_name not in people:
        raise KeyError(f"{person_name} not found in PEOPLE")

    validated = validate_periods(periods)

    if validated:
        people[person_name]["inactive_periods"] = validated
    else:
        people[person_name].pop("inactive_periods", None)

    backup = backup_people_file(people_file)
    people_file.write_text(render_people_py(people), encoding="utf-8")
    return backup


def render_person_summary(person: dict) -> str:
    days = sorted_days(person.get("allowed_days", set()))
    roles = sorted_roles(person.get("allowed_roles", set()))
    requires = person.get("requires_snr_di", False)

    roles_html = "<br>".join(html.escape(r) for r in roles) if roles else "—"

    return f"""
    <div class="summary-card">
        <div class="summary-grid">

            <div class="summary-item">
                <div class="summary-label">Allowed days</div>
                <div class="summary-value">{html.escape(" · ".join(days) if days else "—")}</div>
            </div>

            <div class="summary-item">
                <div class="summary-label">Roles</div>
                <div class="summary-value roles-vertical">{roles_html}</div>
            </div>

            <div class="summary-item">
                <div class="summary-label">Requires Lead Instructor</div>
                <div class="summary-value">{"Yes" if requires else "No"}</div>
            </div>

        </div>
    </div>
    """


def period_row_html(start, end):
    return f"""
    <tr>
        <td><input type="date" name="start" value="{html.escape(start)}"></td>
        <td><input type="date" name="end" value="{html.escape(end)}"></td>
        <td><button class="btn btn-danger" type="button" onclick="removeRow(this)">Remove</button></td>
    </tr>
    """


def format_period_list(periods):
    if not periods:
        return "<div class='summary-value'>None</div>"

    items = []
    for start, end in periods:
        if start == end:
            label = start
        else:
            label = f"{start} → {end}"
        items.append(f"<li>{html.escape(label)}</li>")
    return "<ul class='period-list'>" + "".join(items) + "</ul>"


def render_page(people_file: Path, selected_name: str = "", message: str = "", error: str = ""):
    people = load_people(people_file)
    names = list(people.keys())

    if not names:
        raise RuntimeError("PEOPLE is empty")

    if not selected_name or selected_name not in people:
        selected_name = names[0]

    person = people[selected_name]
    inactive_periods = normalize_inactive_periods(person.get("inactive_periods", []))
    today = date.today().isoformat()

    options_html = []
    for name in names:
        selected_attr = " selected" if name == selected_name else ""
        options_html.append(
            f'<option value="{html.escape(name)}"{selected_attr}>{html.escape(name)}</option>'
        )

    rows_html = []
    if inactive_periods:
        for start, end in inactive_periods:
            rows_html.append(period_row_html(start, end))
    else:
        rows_html.append(period_row_html("", ""))

    message_html = f'<div class="msg ok">{html.escape(message)}</div>' if message else ""
    error_html = f'<div class="msg err">{html.escape(error)}</div>' if error else ""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>YGC Availability Editor</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{
    --bg: #f4f7fb;
    --panel: #ffffff;
    --border: #d8e0ea;
    --text: #1f2937;
    --muted: #667085;
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --secondary: #eef2f7;
    --danger: #c0392b;
    --danger-hover: #a93226;
    --ok-bg: #eaf7ee;
    --ok-border: #99d3aa;
    --err-bg: #fdecec;
    --err-border: #e7aaaa;
}}

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: var(--bg);
    color: var(--text);
}}

.wrapper {{
    max-width: 980px;
    margin: 32px auto;
    padding: 0 20px;
}}

.card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(16, 24, 40, 0.06);
    padding: 24px;
}}

h1 {{
    margin: 0 0 8px 0;
    font-size: 1.9rem;
}}

h2 {{
    margin: 24px 0 10px 0;
    font-size: 1.25rem;
}}

.sub {{
    color: var(--muted);
    margin: 0 0 18px 0;
    line-height: 1.5;
}}

.selector-row {{
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 20px;
}}

label {{
    font-weight: 600;
}}

select,
input[type="date"] {{
    font-size: 1rem;
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: #fff;
}}

select {{
    min-width: 280px;
}}

.summary-card {{
    margin: 12px 0 20px 0;
    padding: 16px 18px;
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: 12px;
}}

.summary-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
}}

.summary-item {{
    min-width: 0;
}}

.summary-label {{
    font-size: 0.9rem;
    color: var(--muted);
    margin-bottom: 4px;
}}

.summary-value {{
    font-weight: 600;
    line-height: 1.4;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
    overflow: hidden;
    border-radius: 12px;
}}

th {{
    text-align: left;
    background: #f8fafc;
    color: var(--muted);
    font-size: 0.95rem;
    font-weight: 700;
}}

th, td {{
    border: 1px solid var(--border);
    padding: 12px;
}}

.actions {{
    margin-top: 18px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}}

.btn {{
    border: 0;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.98rem;
    font-weight: 600;
    cursor: pointer;
}}

.btn-primary {{
    background: var(--primary);
    color: white;
}}

.btn-primary:hover {{
    background: var(--primary-hover);
}}

.btn-secondary {{
    background: var(--secondary);
    color: var(--text);
    border: 1px solid var(--border);
}}

.btn-secondary:hover {{
    background: #e4e9f1;
}}

.btn-danger {{
    background: white;
    color: var(--danger);
    border: 1px solid #efc1bb;
}}

.btn-danger:hover {{
    background: #fff4f2;
    color: var(--danger-hover);
}}

.msg {{
    margin-top: 14px;
    margin-bottom: 0;
    padding: 12px 14px;
    border-radius: 10px;
    line-height: 1.45;
}}

.ok {{
    background: var(--ok-bg);
    border: 1px solid var(--ok-border);
}}

.err {{
    background: var(--err-bg);
    border: 1px solid var(--err-border);
}}

.small {{
    color: var(--muted);
    font-size: 0.95rem;
    margin-top: 0;
}}

code.inline {{
    background: #f2f4f7;
    padding: 2px 6px;
    border-radius: 6px;
}}

.footer-note {{
    margin-top: 18px;
    color: var(--muted);
    font-size: 0.9rem;
}}

.roles-vertical {{
    line-height: 1.6;
    padding-left: 6px;
    border-left: 2px solid #e5e7eb;
}}

.period-list {{
    margin: 8px 0 0 18px;
    padding: 0;
}}

.period-list li {{
    margin: 4px 0;
}}

.preview-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 16px;
}}

.preview-box {{
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
}}

.preview-box h3 {{
    margin-top: 0;
    margin-bottom: 10px;
}}

.note {{
    color: var(--muted);
    line-height: 1.5;
    margin-top: 18px;
}}

@media (max-width: 760px) {{
    .preview-grid {{
        grid-template-columns: 1fr;
    }}
}}

</style>
<script>
const TODAY = "{today}";

function addRow(startValue="", endValue="") {{
    const tbody = document.getElementById("periods-body");
    const tr = document.createElement("tr");
    tr.innerHTML = `
        <td><input type="date" name="start" min="${{TODAY}}" value="${{startValue}}"></td>
        <td><input type="date" name="end" min="${{TODAY}}" value="${{endValue}}"></td>
        <td><button class="btn btn-danger" type="button" onclick="removeRow(this)">Remove</button></td>
    `;
    tbody.appendChild(tr);
}}

function removeRow(button) {{
    const tbody = document.getElementById("periods-body");
    if (tbody.rows.length === 1) {{
        tbody.rows[0].querySelector('input[name="start"]').value = "";
        tbody.rows[0].querySelector('input[name="end"]').value = "";
        return;
    }}
    button.closest("tr").remove();
}}

function onPersonChange() {{
    document.getElementById("person-select-form").submit();
}}
</script>
</head>
<body>
<div class="wrapper">
    <div class="card">
        <h1>YGC Availability Editor</h1>
        <p class="sub">
            Edit inactive periods in <code class="inline">{html.escape(str(people_file))}</code>.
            A backup is created before every save and kept as <code class="inline">{html.escape(people_file.name)}.bak</code>.
        </p>

        <form id="person-select-form" method="get" action="/">
            <div class="selector-row">
                <label for="person">Person</label>
                <select name="person" id="person" onchange="onPersonChange()">
                    {''.join(options_html)}
                </select>
            </div>
        </form>

        <h2>{html.escape(selected_name)}</h2>
        {render_person_summary(person)}

        <form method="post" action="/preview">
            <input type="hidden" name="person" value="{html.escape(selected_name)}">

            <p class="small">
                Enter one or more inactive periods. For a single day, use the same start and end date.
                Dates before today are not allowed.
            </p>

            <table>
                <thead>
                    <tr>
                        <th>Start date</th>
                        <th>End date</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody id="periods-body">
                    {''.join(rows_html).replace('<input type="date"', f'<input type="date" min="{today}"')}
                </tbody>
            </table>

            <div class="actions">
                <button class="btn btn-secondary" type="button" onclick="addRow()">Add another period</button>
                <button class="btn btn-primary" type="submit">Preview changes</button>
            </div>
        </form>

        {message_html}
        {error_html}

        <div class="footer-note">
            Tip: deleting all rows (or clearing the last row) removes inactive periods for this person.
        </div>
    </div>
</div>
</body>
</html>
"""


def render_preview_page(people_file: Path, person_name: str, old_periods, new_periods, payload_json: str):
    old_html = format_period_list(old_periods)
    new_html = format_period_list(new_periods)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Preview Changes - YGC Availability Editor</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{
    --bg: #f4f7fb;
    --panel: #ffffff;
    --border: #d8e0ea;
    --text: #1f2937;
    --muted: #667085;
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --secondary: #eef2f7;
}}

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: var(--bg);
    color: var(--text);
}}

.wrapper {{
    max-width: 980px;
    margin: 32px auto;
    padding: 0 20px;
}}

.card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(16, 24, 40, 0.06);
    padding: 24px;
}}

h1 {{
    margin: 0 0 8px 0;
    font-size: 1.9rem;
}}

h2 {{
    margin: 0 0 18px 0;
    font-size: 1.2rem;
}}

.preview-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 16px;
}}

.preview-box {{
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
}}

.preview-box h3 {{
    margin-top: 0;
    margin-bottom: 10px;
}}

.period-list {{
    margin: 8px 0 0 18px;
    padding: 0;
}}

.period-list li {{
    margin: 4px 0;
}}

.empty {{
    color: var(--muted);
    font-weight: 600;
}}

.actions {{
    margin-top: 22px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}}

.btn {{
    border: 0;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.98rem;
    font-weight: 600;
    cursor: pointer;
}}

.btn-primary {{
    background: var(--primary);
    color: white;
}}

.btn-primary:hover {{
    background: var(--primary-hover);
}}

.btn-secondary {{
    background: var(--secondary);
    color: var(--text);
    border: 1px solid var(--border);
}}

.note {{
    color: var(--muted);
    line-height: 1.5;
    margin-top: 18px;
}}

@media (max-width: 760px) {{
    .preview-grid {{
        grid-template-columns: 1fr;
    }}
}}
</style>
</head>
<body>
<div class="wrapper">
    <div class="card">
        <h1>Preview changes</h1>
        <h2>{html.escape(person_name)}</h2>

        <div class="preview-grid">
            <div class="preview-box">
                <h3>Current inactive periods</h3>
                {old_html if old_periods else '<div class="empty">None</div>'}
            </div>

            <div class="preview-box">
                <h3>New inactive periods</h3>
                {new_html if new_periods else '<div class="empty">None</div>'}
            </div>
        </div>

        <p class="note">
            Review the changes above carefully. Nothing has been saved yet.
            Click <strong>Confirm save</strong> to write changes to <strong>{html.escape(people_file.name)}</strong>,
            or go back to edit.
        </p>

        <div class="actions">
            <form method="post" action="/confirm" style="margin:0;">
                <input type="hidden" name="person" value="{html.escape(person_name)}">
                <input type="hidden" name="periods_json" value='{html.escape(payload_json, quote=True)}'>
                <button class="btn btn-primary" type="submit">Confirm save</button>
            </form>

            <form method="get" action="/" style="margin:0;">
                <input type="hidden" name="person" value="{html.escape(person_name)}">
                <button class="btn btn-secondary" type="submit">Back without saving</button>
            </form>
        </div>
    </div>
</div>
</body>
</html>
"""


class AvailabilityHandler(BaseHTTPRequestHandler):
    people_file: Path = None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/":
            self.send_error(404, "Not found")
            return

        params = parse_qs(parsed.query)
        selected = params.get("person", [""])[0]
        message = params.get("message", [""])[0]
        error = params.get("error", [""])[0]

        try:
            page = render_page(self.people_file, selected, message, error)
            self._send_html(page)
        except Exception as exc:
            self._send_html(
                f"<h1>Error</h1><pre>{html.escape(str(exc))}</pre>",
                status=500
            )

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/preview":
            self.handle_preview()
            return

        if parsed.path == "/confirm":
            self.handle_confirm()
            return

        self.send_error(404, "Not found")

    def handle_preview(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        form = parse_qs(raw)

        person = form.get("person", [""])[0]
        starts = form.get("start", [])
        ends = form.get("end", [])

        periods = []
        for start, end in zip(starts, ends):
            start = start.strip()
            end = end.strip()
            if not start and not end:
                continue
            if start and not end:
                end = start
            periods.append((start, end))

        try:
            people = load_people(self.people_file)
            if person not in people:
                raise KeyError(f"{person} not found in PEOPLE")

            validated = validate_periods(periods)
            old_periods = normalize_inactive_periods(people[person].get("inactive_periods", []))
            new_periods = normalize_inactive_periods(validated)
            payload_json = json.dumps(new_periods)

            page = render_preview_page(
                self.people_file,
                person,
                old_periods,
                new_periods,
                payload_json,
            )
            self._send_html(page)

        except Exception as exc:
            self._redirect(f"/?person={quote_plus(person)}&error={quote_plus(str(exc))}")

    def handle_confirm(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        form = parse_qs(raw)

        person = form.get("person", [""])[0]
        periods_json = form.get("periods_json", ["[]"])[0]

        try:
            periods = json.loads(periods_json)
            if not isinstance(periods, list):
                raise ValueError("Invalid preview payload.")

            normalized_periods = []
            for item in periods:
                if not isinstance(item, (list, tuple)) or len(item) != 2:
                    raise ValueError("Invalid preview payload.")
                normalized_periods.append((str(item[0]), str(item[1])))

            backup = update_person_inactive_periods(self.people_file, person, normalized_periods)
            msg = f"Saved inactive periods for {person}. Backup updated: {backup.name}"
            self._redirect(f"/?person={quote_plus(person)}&message={quote_plus(msg)}")

        except Exception as exc:
            self._redirect(f"/?person={quote_plus(person)}&error={quote_plus(str(exc))}")

    def log_message(self, format, *args):
        print("%s - - [%s] %s" % (
            self.client_address[0],
            self.log_date_time_string(),
            format % args
        ))

    def _send_html(self, content, status=200):
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location):
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Local frontend for editing inactive periods in people.py"
    )
    parser.add_argument(
        "--people-file",
        default="people.py",
        help="Path to people.py (default: people.py)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to serve on (default: 8000)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    people_file = Path(args.people_file).resolve()

    if not people_file.exists():
        raise SystemExit(f"people.py not found: {people_file}")

    handler_class = type(
        "ConfiguredAvailabilityHandler",
        (AvailabilityHandler,),
        {"people_file": people_file},
    )

    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler_class)

    print(f"Serving on http://127.0.0.1:{args.port}")
    print(f"Editing: {people_file}")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()