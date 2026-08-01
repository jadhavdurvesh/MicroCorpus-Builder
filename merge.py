#!/usr/bin/env python3
"""
merge.py

Merge every cleaned book into a single training corpus.

Input:
    cleaned/*.txt

Output:
    output/data.txt
"""

from pathlib import Path

CLEANED_DIR = Path("cleaned")
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "data.txt"


def load_books():
    """
    Load every cleaned book.
    Returns:
        List[(title, text)]
    """

    books = []

    for file in sorted(CLEANED_DIR.glob("*.txt")):

        text = file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        books.append((file.stem, text.strip()))

    return books


def create_book_header(title):
    """
    Create a separator before each book.
    """

    line = "=" * 80

    return (
        f"\n{line}\n"
        f"TITLE: {title}\n"
        f"{line}\n\n"
    )


def merge_books(books):
    """
    Merge all books into one dataset.
    """

    merged = []

    for title, text in books:

        merged.append(create_book_header(title))
        merged.append(text)
        merged.append("\n\n")

    return "".join(merged)


def save_dataset(text):
    """
    Save merged corpus.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(
        text,
        encoding="utf-8"
    )


def print_statistics(books, merged_text):

    words = len(merged_text.split())

    chars = len(merged_text)

    size_mb = chars / (1024 * 1024)

    print("\n========== Merge Complete ==========\n")

    print(f"Books merged : {len(books)}")
    print(f"Words        : {words:,}")
    print(f"Characters   : {chars:,}")
    print(f"Size         : {size_mb:.2f} MB")

    print("\nSaved to:")
    print(OUTPUT_FILE)


def main():

    books = load_books()

    if not books:

        print("No cleaned books found.")
        return

    merged = merge_books(books)

    save_dataset(merged)

    print_statistics(books, merged)


if __name__ == "__main__":
    main()