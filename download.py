import json
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

BOOK_FOLDER = "raw"

os.makedirs(BOOK_FOLDER, exist_ok=True)


def search_book(title, author):
    query = quote(f"{title} {author}")

    url = f"https://www.gutenberg.org/ebooks/search/?query={query}"

    html = requests.get(url).text

    soup = BeautifulSoup(html, "html.parser")

    link = soup.select_one("li.booklink a")

    if link is None:
        return None

    href = link["href"]

    book_id = href.split("/")[-1]

    return book_id


def download_book(book_id, title):

    urls = [

        f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",

        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",

        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt"

    ]

    for url in urls:

        try:

            r = requests.get(url, timeout=30)

            if r.status_code == 200:

                filename = os.path.join(
                    BOOK_FOLDER,
                    title.replace("/", "-") + ".txt"
                )

                with open(filename, "w", encoding="utf8") as f:
                    f.write(r.text)

                print("Downloaded:", title)

                return

        except:
            pass

    print("Failed:", title)


def main():

    with open("config.json", encoding="utf8") as f:
        config = json.load(f)

    for book in config["books"]:

        book_id = search_book(
            book["title"],
            book["author"]
        )

        if book_id is None:

            print("Not found:", book["title"])

            continue

        download_book(book_id, book["title"])


if __name__ == "__main__":
    main()