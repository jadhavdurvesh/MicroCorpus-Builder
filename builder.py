#!/usr/bin/env python3

import shutil

import download
import clean
import merge
import stats


def banner():
    width = shutil.get_terminal_size((80, 20)).columns

    def center(text=""):
        print(text.center(width))

    print("─" * width)
    print()

    center("📚 MicroCorpus-Builder")
    print()

    center("Build clean, high-quality text corpora for language model training")
    print()

    center("v1.0.0")
    print()

    center("Created by Durvesh Jadhav")
    center("DMJ Group • DMJ Labs")

    print()
    print("─" * width)
    print()


def success():
    width = shutil.get_terminal_size((80, 20)).columns

    def center(text=""):
        print(text.center(width))

    print()
    print("─" * width)
    print()

    center("✔ Build Completed Successfully!")
    print()

    center("Dataset : output/data.txt")
    center("Logs    : logs/")
    print()

    center("Thank you for using MicroCorpus-Builder")
    print()

    center("Created by Durvesh Jadhav")
    center("DMJ Group • DMJ Labs")

    print()
    print("─" * width)


def main():

    banner()

    print("[1/4] Downloading books...\n")
    download.main()

    print("\n[2/4] Cleaning books...\n")
    clean.main()

    print("\n[3/4] Merging dataset...\n")
    merge.main()

    print("\n[4/4] Generating statistics...\n")
    stats.main()

    success()


if __name__ == "__main__":
    main()