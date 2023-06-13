import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.exceptions.HTTPError


def get_book_title(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_header_content = soup.find('body').find('table').find('h1')
    book_header_text = book_header_content.text
    book_title = book_header_text.split('::')[0].strip()
    return book_title


def download_txt(response, filename, folder='books/'):
    book_text = response.content
    clear_filename = sanitize_filename(filename)
    filepath = os.path.join(folder, clear_filename)
    with open(filepath, 'wb') as file:
        file.write(book_text)


def main():
    Path('books').mkdir(parents=True, exist_ok=True)
    book_text_url_template = 'https://tululu.org/txt.php?id='
    book_page_url_template = 'https://tululu.org/b'
    for i in range(1, 11):
        text_url = book_text_url_template + str(i)
        page_url = book_page_url_template + str(i)
        response = requests.get(text_url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            book_title = get_book_title(page_url)
            filename = f'{i}. ' + book_title + '.txt'
            download_txt(response, filename)
        except requests.exceptions.HTTPError:
            pass


if __name__ == '__main__':
    main()
