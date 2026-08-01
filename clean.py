#!/usr/bin/env python3
"""
clean.py

Purpose
-------
Automatically clean books from Project Gutenberg (and, later, other
sources). Never modifies the original files - it only reads raw/*.txt
and writes new files into cleaned/*.txt.

Input:  raw/*.txt
Output: cleaned/*.txt

Usage:
    python3 clean.py
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

RAW_DIR = Path("raw")
CLEANED_DIR = Path("cleaned")

# How many words must follow a heading (before the next heading, or the
# end of the text) for it to count as the real start of a chapter rather
# than a line in a table of contents. See find_story_start().
MIN_STORY_WORD_COUNT = 50

# --------------------------------------------------------------------------
# Regex patterns
# --------------------------------------------------------------------------

GUTENBERG_START_RE = re.compile(r"START OF (?:THE |THIS )?PROJECT GUTENBERG", re.IGNORECASE)
GUTENBERG_END_RE = re.compile(r"END OF (?:THE |THIS )?PROJECT GUTENBERG", re.IGNORECASE)

TITLE_METADATA_RE = re.compile(r"^\s*Title:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)

CONTENTS_HEADING_RE = re.compile(r"^\s*(CONTENTS|TABLE OF CONTENTS)\s*\.?\s*$", re.IGNORECASE)

# Matches things like "CHAPTER I", "Chapter 12", "LETTER IV", "Book 2",
# "Part III", "Act 1" - keyword, then a roman numeral or a plain number.
NUMBERED_HEADING_RE = re.compile(
    r"^\s*(CHAPTER|LETTER|BOOK|PART|ACT)\s+([IVXLCDM]+|\d+)\b\.?\s*(.*)$",
    re.IGNORECASE,
)

# "PROLOGUE" / "EPILOGUE" standing alone on their own line.
STANDALONE_HEADING_RE = re.compile(r"^\s*(PROLOGUE|EPILOGUE)\s*\.?\s*$", re.IGNORECASE)


# --------------------------------------------------------------------------
# 1. Remove Gutenberg header
# --------------------------------------------------------------------------

def remove_gutenberg_header(text: str) -> str:
    """Remove the '*** START OF ... PROJECT GUTENBERG ...' line and
    everything before it."""
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if GUTENBERG_START_RE.search(line):
            return "".join(lines[i + 1:])
    return text


# --------------------------------------------------------------------------
# 2. Remove Gutenberg footer
# --------------------------------------------------------------------------

def remove_gutenberg_footer(text: str) -> str:
    """Remove the '*** END OF ... PROJECT GUTENBERG ...' line and
    everything after it."""
    lines = text.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if GUTENBERG_END_RE.search(line):
            return "".join(lines[:i])
    return text


# --------------------------------------------------------------------------
# 3. Normalize
# --------------------------------------------------------------------------

def normalize(text: str) -> str:
    """
    - Convert CRLF -> LF
    - Remove trailing spaces on each line
    - Collapse multiple blank lines into a single blank line
    - Strip leading/trailing whitespace from the whole text
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\x0c", "\n")  # old-style page-break markers

    lines = [line.rstrip(" \t") for line in text.split("\n")]
    text = "\n".join(lines)

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text


# --------------------------------------------------------------------------
# 4. Detect a contents / table-of-contents page
# --------------------------------------------------------------------------

def detect_contents(lines: List[str]) -> bool:
    """Return True if the book contains a CONTENTS / Table of Contents
    heading anywhere."""
    return any(CONTENTS_HEADING_RE.match(line) for line in lines)


# --------------------------------------------------------------------------
# 5. Find where the actual story begins (the important one)
# --------------------------------------------------------------------------

def _parse_heading(line: str) -> Optional[Tuple[str, Optional[str]]]:
    """If `line` looks like a chapter-style heading, return
    (KEYWORD, numeral_or_None); otherwise None."""
    m = NUMBERED_HEADING_RE.match(line)
    if m:
        return m.group(1).upper(), m.group(2)
    m = STANDALONE_HEADING_RE.match(line)
    if m:
        return m.group(1).upper(), None
    return None


def _word_count(lines: List[str], start: int, end: int) -> int:
    return sum(len(line.split()) for line in lines[start:end])


def find_story_start(lines: List[str]) -> Optional[int]:
    """
    Find the line index at which the real story begins.

    Detects headings such as CHAPTER I/1, LETTER I/1, BOOK I/1, PART I/1,
    ACT I/1, PROLOGUE, EPILOGUE - and tells a real chapter apart from a
    table of contents that lists those same headings.

    The key difference between the two: a table of contents lists
    headings back-to-back with almost nothing in between (just the next
    entry, maybe a page number). A real chapter is followed by a
    substantial run of prose before the next heading shows up. So this
    walks every heading candidate in the order it appears and returns
    the first one followed by at least MIN_STORY_WORD_COUNT words
    before the next candidate (or the end of the text). That's what
    keeps a "Contents / Chapter 1 / Chapter 2 / Chapter 3" listing from
    being mistaken for the story itself.

    Returns None if no heading could be found at all. Callers should
    leave the text untouched in that case rather than guess.
    """
    candidates: List[Tuple[int, str, Optional[str]]] = []
    for i, line in enumerate(lines):
        parsed = _parse_heading(line)
        if parsed:
            candidates.append((i, parsed[0], parsed[1]))

    if not candidates:
        return None

    for idx, (line_no, _keyword, _numeral) in enumerate(candidates):
        next_line_no = candidates[idx + 1][0] if idx + 1 < len(candidates) else len(lines)
        if _word_count(lines, line_no + 1, next_line_no) >= MIN_STORY_WORD_COUNT:
            return line_no

    # Nothing cleared the threshold - most likely an unusually short
    # piece. The last candidate is the safest guess left, since a table
    # of contents always comes before the real chapters, never after.
    return candidates[-1][0]


# --------------------------------------------------------------------------
# 6. Remove front matter
# --------------------------------------------------------------------------

def remove_front_matter(text: str) -> str:
    """
    Remove publisher pages, copyright, illustrations, title pages,
    contents pages, edition pages, dedication, preface, and foreword -
    everything before the real story, as located by find_story_start().
    If no story-start heading can be found, the text is left untouched
    rather than risk cutting into real content.
    """
    lines = text.splitlines(keepends=True)
    start_idx = find_story_start(lines)
    if start_idx is None:
        return text
    return "".join(lines[start_idx:])


# --------------------------------------------------------------------------
# 7. Full pipeline
# --------------------------------------------------------------------------

def clean_book(text: str) -> str:
    """Remove Gutenberg header -> remove Gutenberg footer -> remove front
    matter -> normalize -> return cleaned text."""
    text = remove_gutenberg_header(text)
    text = remove_gutenberg_footer(text)
    text = remove_front_matter(text)
    text = normalize(text)
    return text


# --------------------------------------------------------------------------
# 8. Save
# --------------------------------------------------------------------------

def save_cleaned_book(filename: str, text: str) -> None:
    """Write cleaned text into cleaned/<filename>. Never touches raw/."""
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    (CLEANED_DIR / filename).write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------
# Small helpers used by main()
# --------------------------------------------------------------------------

def _read_raw_text(path: Path) -> str:
    """Read a raw file, trying UTF-8 first and falling back to Latin-1
    (some older Gutenberg transcriptions aren't UTF-8)."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def _extract_title(text: str, fallback: str) -> str:
    """Pull the 'Title: ...' line out of the Gutenberg header metadata,
    for nicer progress printing. Falls back to the filename stem."""
    m = TITLE_METADATA_RE.search(text)
    return m.group(1) if m else fallback


# --------------------------------------------------------------------------
# 9. main
# --------------------------------------------------------------------------

def main() -> None:
    raw_files = sorted(RAW_DIR.glob("*.txt"))
    if not raw_files:
        print(f"No .txt files found in {RAW_DIR}/")
        return

    cleaned_count = 0
    failed_count = 0

    for path in raw_files:
        try:
            raw_text = _read_raw_text(path)               # raw/ is never written to
            title = _extract_title(raw_text, fallback=path.stem)
            print(f"Cleaning {title}...")
            cleaned = clean_book(raw_text)
            save_cleaned_book(path.name, cleaned)
            print("\u2713 Saved")
            cleaned_count += 1
        except Exception as exc:
            print(f"\u2717 Failed: {exc}")
            failed_count += 1

    print(f"\nDone: {cleaned_count} cleaned, {failed_count} failed.")


if __name__ == "__main__":
    main()