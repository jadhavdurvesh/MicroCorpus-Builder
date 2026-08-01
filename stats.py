#!/usr/bin/env python3
"""
stats.py

Generate statistics about the merged corpus.
"""

from pathlib import Path

OUTPUT_DIR = Path("output")
DATASET = OUTPUT_DIR / "data.txt"


def load_dataset():
    """
    Load the merged dataset.
    """
    if not DATASET.exists():
        raise FileNotFoundError(
            "output/data.txt not found. Run merge.py first."
        )

    return DATASET.read_text(
        encoding="utf-8",
        errors="ignore"
    )


def count_books(text):
    """
    Count books using TITLE markers.
    """
    return text.count("TITLE:")


def count_words(text):
    return len(text.split())


def count_characters(text):
    return len(text)


def count_lines(text):
    return len(text.splitlines())


def estimate_tokens(words):
    """
    Rough estimate.
    """
    return int(words * 1.3)


def dataset_size():
    return DATASET.stat().st_size / (1024 * 1024)


def print_report(text):

    books = count_books(text)
    words = count_words(text)
    chars = count_characters(text)
    lines = count_lines(text)
    tokens = estimate_tokens(words)
    size = dataset_size()

    print("\n========== DATASET REPORT ==========\n")

    print(f"Books        : {books}")
    print(f"Words        : {words:,}")
    print(f"Characters   : {chars:,}")
    print(f"Lines        : {lines:,}")
    print(f"Est. Tokens  : {tokens:,}")
    print(f"Size         : {size:.2f} MB")

    print("\n====================================")


def main():

    text = load_dataset()

    print_report(text)


if __name__ == "__main__":
    main()