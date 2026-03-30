#!/usr/bin/env python3
"""
Move past weeks from 'Upcoming Weeks' to 'Previous Weeks' in a semester
forecast markdown file, marking all task items as complete.

Relies on <!-- upcoming -->...<!-- /upcoming --> and
<!-- previous -->...<!-- /previous --> comment markers in the file.

Usage:
    python3 archive_weeks.py <file.md> [--dry-run] [--date YYYY-MM-DD]
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

DATE_RE = re.compile(r"(?:MON|TUE|WED|THR|FRI|SAT|SUN)\s+(\d{1,2})/(\d{1,2})")
WEEK_RE = re.compile(r"^##\s+Week\s+(\d+)")


def year_from_filename(path: Path) -> int:
    """Derive the four-digit year from a filename like Sp26.md -> 2026."""
    m = re.search(r"(\d{2})", path.stem)
    if not m:
        print(f"Error: cannot derive year from '{path.name}'.", file=sys.stderr)
        sys.exit(1)
    return 2000 + int(m.group(1))


def extract_latest_date(text: str, year: int) -> date | None:
    """Return the latest valid date found in text, or None."""
    dates = []
    for m in DATE_RE.finditer(text):
        try:
            dates.append(date(year, int(m.group(1)), int(m.group(2))))
        except ValueError:
            continue
    return max(dates) if dates else None


def find_marker(lines: list[str], marker: str) -> int | None:
    """Return the index of the line containing the given HTML comment marker."""
    for i, line in enumerate(lines):
        if line.strip() == marker:
            return i
    return None


def parse_week_blocks(lines: list[str]) -> list[tuple[int, list[str]]]:
    """Parse lines into a list of (week_num, lines) blocks."""
    blocks: list[tuple[int, list[str]]] = []
    current_week = None
    current_lines: list[str] = []

    for line in lines:
        m = WEEK_RE.match(line.strip())
        if m:
            if current_week is not None:
                blocks.append((current_week, current_lines))
            current_week = int(m.group(1))
            current_lines = [line]
        elif current_week is not None:
            current_lines.append(line)

    if current_week is not None:
        blocks.append((current_week, current_lines))

    return blocks


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        print(f"Usage: {sys.argv[0]} <file.md> [--dry-run]", file=sys.stderr)
        sys.exit(1)

    src = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv
    year = year_from_filename(src)

    today = date.today()
    if "--date" in sys.argv:
        today = date.fromisoformat(sys.argv[sys.argv.index("--date") + 1])

    lines = src.read_text().split("\n")

    # Locate comment markers
    up_start = find_marker(lines, "<!-- upcoming -->")
    up_end = find_marker(lines, "<!-- /upcoming -->")
    prev_start = find_marker(lines, "<!-- previous -->")
    prev_end = find_marker(lines, "<!-- /previous -->")

    for name, idx in [("upcoming", up_start), ("/upcoming", up_end),
                      ("previous", prev_start), ("/previous", prev_end)]:
        if idx is None:
            print(f"Error: missing <!-- {name} --> marker.", file=sys.stderr)
            sys.exit(1)

    # Extract region contents (excluding the marker lines themselves)
    upcoming_lines = lines[up_start + 1 : up_end]
    previous_lines = lines[prev_start + 1 : prev_end]

    up_blocks = parse_week_blocks(upcoming_lines)

    # ---- Classify upcoming weeks ----
    week_past: dict[int, bool | None] = {}
    for wn, wlines in up_blocks:
        latest = extract_latest_date("\n".join(wlines), year)
        week_past[wn] = (latest < today) if latest is not None else None

    # Resolve dateless weeks: past only if both nearest dated neighbours are past
    ordered = [b[0] for b in up_blocks]
    for idx, wn in enumerate(ordered):
        if week_past[wn] is not None:
            continue
        prev_dated = next_dated = False
        for j in range(idx - 1, -1, -1):
            if week_past[ordered[j]] is not None:
                prev_dated = week_past[ordered[j]]
                break
        for j in range(idx + 1, len(ordered)):
            if week_past[ordered[j]] is not None:
                next_dated = week_past[ordered[j]]
                break
        week_past[wn] = prev_dated and next_dated

    to_move = [(wn, wl) for wn, wl in up_blocks if week_past[wn]]
    to_keep = [(wn, wl) for wn, wl in up_blocks if not week_past[wn]]

    if not to_move:
        print("No past weeks to move.")
        return

    names = ", ".join(f"Week {w}" for w, _ in to_move)
    if dry_run:
        print(f"[dry-run] Would move: {names}")
        return

    # ---- Build new region contents ----
    new_upcoming: list[str] = []
    for _, wlines in to_keep:
        new_upcoming.extend(wlines)

    new_previous: list[str] = list(previous_lines)
    for _, wlines in to_move:
        # Ensure blank line before each moved week
        if new_previous and new_previous[-1].strip():
            new_previous.append("")
        new_previous.extend(line.replace("- [ ] ", "- [x] ") for line in wlines)

    # ---- Reassemble file ----
    result: list[str] = []
    result.extend(lines[: up_start + 1])       # everything through <!-- upcoming -->
    result.extend(new_upcoming)                 # kept upcoming weeks
    result.extend(lines[up_end : prev_start + 1])  # <!-- /upcoming --> through <!-- previous -->
    result.extend(new_previous)                 # all previous weeks (existing + moved)
    result.extend(lines[prev_end:])             # <!-- /previous --> through end of file

    src.write_text("\n".join(result))
    print(f"Archived: {names}")


if __name__ == "__main__":
    main()
