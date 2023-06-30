import os
import json
import time
import requests
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from parse_tululu_books import check_for_redirect, parse_book_page, download_txt, download_image


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Скрипт для скачивания книг из категории "Научная фантастика" с tululu.org'
    )
    parser.add_argument('--start_page', help='номер стартовой страницы', type=int, nargs='?', default=1)
    parser.add_argument('--end_page', help='номер конечной страницы', type=int, nargs='?', default=701)
    parser.add_argument('--dest_folder', help='путь к каталогу с результатами парсинга', type=str, nargs='?', default=0)
    parser.add_argument('--skip_imgs', help='не скачивать картинки', action='store_true')
    parser.add_argument('--skip_txt', help='не скачивать книги', action='store_true')
    return parser.parse_args()


def get_page_books(url_template, response):
    soup = BeautifulSoup(response.text, 'lxml')
    all_books = soup.find_all(class_='d_book')
    book_urls = [urljoin(url_template, book.find('a')['href']) for book in all_books]
    return book_urls


def main():
    url_template = 'https://tululu.org/'
    category = 'l55/'
    book_text_url = 'https://tululu.org/txt.php'
    book_text_url_params = {'id': ''}

    args = parse_arguments()
    start_page = args.start_page
    end_page = args.end_page
    dest_folder = args.dest_folder
    skip_imgs = args.skip_imgs
    skip_txt = args.skip_txt

    category_page_response = requests.get(urljoin(url_template, category))
    category_page_response.raise_for_status()
    book_urls = []

    if dest_folder:
        Path(os.path.join(dest_folder, 'books')).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(dest_folder, 'images')).mkdir(parents=True, exist_ok=True)
    else:
        dest_folder = '.'
        Path('books').mkdir(parents=True, exist_ok=True)
        Path('images').mkdir(parents=True, exist_ok=True)

    for page in range(start_page, end_page):
        try_connection = 0
        while True:
            page_response = requests.get(urljoin(url_template, f'{category}{str(page)}'))
            page_response.raise_for_status()
            try:
                check_for_redirect(page_response)
            except requests.exceptions.HTTPError as err:
                print(err)
                pass
            except requests.exceptions.ConnectionError as err:
                print(err)
                if not try_connection:
                    time.sleep(3)
                else:
                    time.sleep(5)
                try_connection += 1
                continue
            book_urls += get_page_books(url_template, page_response)
            break

    for book_url in book_urls:
        book_id = str(urlsplit(book_url).path.split('/')[-2]).replace('b', '')
        book_text_url_params['id'] = book_id
        while True:
            try_connection = 0
            try:
                file_response = requests.get(book_text_url, params=book_text_url_params)
                file_response.raise_for_status()
                check_for_redirect(file_response)

                page_response = requests.get(book_url)
                page_response.raise_for_status()
                check_for_redirect(page_response)
                page_details = parse_book_page(page_response)

                if not skip_txt:
                    filename = f'{book_id}. {page_details["book_title"]}.txt'
                    book_path = download_txt(file_response, filename)
                    page_details['book_path'] = book_path

                if not skip_imgs:
                    image_path = download_image(page_details['image_url'])
                    page_details['image_url'] = image_path

                with open(os.path.join(dest_folder, 'books_data.json'), 'a', encoding='utf-8') as file:
                    json.dump(page_details, file, ensure_ascii=False)

                print(book_url)
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
