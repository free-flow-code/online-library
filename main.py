import os
import requests
from pathlib import Path


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.exceptions.HTTPError


def download_book(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    return response.content


def save_book(book, filename):
    with open(f'books/{filename}', 'wb') as file:
        file.write(book)


def main():
    Path('books').mkdir(parents=True, exist_ok=True)
    url_template = 'https://tululu.org/txt.php?id='
    for i in range(1, 11):
        url = url_template + str(i)
        try:
            book = download_book(url)
            filename = f'id{i}.txt'
            save_book(book, filename)
        except requests.exceptions.HTTPError:
            pass


if __name__ == '__main__':
    main()
