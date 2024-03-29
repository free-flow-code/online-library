import os
import time
import requests
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Скрипт для скачивания книг с tululu.org'
    )
    parser.add_argument('start_id', help='id первой книги', type=int, nargs='?', default=1)
    parser.add_argument('stop_id', help='id последней книги', type=int, nargs='?', default=10)
    return parser.parse_args()


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.exceptions.HTTPError


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')

    book_header = soup.select('body table h1')[0].text
    book_title = book_header.split('::')[0].strip()

    author = book_header.split('::')[1].strip()

    image_src = soup.select_one('div.bookimage img')['src']
    image_url = urljoin(response.url, image_src)

    comments_soup = soup.select('.texts .black')
    comments = [comment.text for comment in comments_soup]

    genres_soup = soup.select('span.d_book a')
    genres = [genre.text for genre in genres_soup]

    return {
        'title': book_title,
        'author': author,
        'image_url': image_url,
        'comments': comments,
        'genres': genres
    }


def download_txt(response, filename, folder='books/'):
    book_text = response.content
    clear_filename = sanitize_filename(filename)
    filepath = os.path.join(folder, clear_filename)
    with open(filepath, 'wb') as file:
        file.write(book_text)

    return filepath


def download_image(url, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    filename = urlsplit(url).path.split('/')[-1]
    filepath = os.path.join(folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)

    return filepath


def main():
    Path('books').mkdir(parents=True, exist_ok=True)
    Path('images').mkdir(parents=True, exist_ok=True)

    book_text_url = 'https://tululu.org/txt.php'
    book_text_url_params = {'id': ''}
    book_page_url_template = 'https://tululu.org/b'

    args = parse_arguments()
    start_book_id = args.start_id
    stop_book_id = args.stop_id + 1

    for book_id in range(start_book_id, stop_book_id):
        book_text_url_params['id'] = str(book_id)
        page_url = f'{book_page_url_template}{str(book_id)}'
        while True:
            try_connection = 0
            try:
                file_response = requests.get(book_text_url, params=book_text_url_params)
                file_response.raise_for_status()
                check_for_redirect(file_response)

                page_response = requests.get(page_url)
                page_response.raise_for_status()
                check_for_redirect(page_response)
                page_details = parse_book_page(page_response)

                filename = f'{book_id}. {page_details["title"]}.txt'
                download_txt(file_response, filename)
                download_image(page_details['image_url'])

                print('Заголовок: ', page_details['title'])
                print('Жанры: ', page_details['genres'])
                print('Комментарии:\n', page_details['comments'], end='\n')
            except requests.exceptions.HTTPError as err:
                print(err)
            except requests.exceptions.ConnectionError as err:
                print(err)
                if not try_connection:
                    time.sleep(3)
                else:
                    time.sleep(5)
                try_connection += 1
                continue
            break


if __name__ == '__main__':
    main()
