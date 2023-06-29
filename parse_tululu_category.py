import os
import json
import time
import requests
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from parse_tululu_books import check_for_redirect, parse_book_page, download_txt, download_image


def get_page_books(url_template, response):
    soup = BeautifulSoup(response.text, 'lxml')
    all_books = soup.find_all(class_='d_book')
    books_url = [urljoin(url_template, book.find('a')['href']) for book in all_books]
    return books_url


def main():
    Path('books').mkdir(parents=True, exist_ok=True)
    Path('images').mkdir(parents=True, exist_ok=True)

    url_template = 'https://tululu.org/'
    category = 'l55/'
    book_text_url = 'https://tululu.org/txt.php'
    book_text_url_params = {'id': ''}

    category_page_response = requests.get(urljoin(url_template, category))
    category_page_response.raise_for_status()

    # soup = BeautifulSoup(category_page_response.text, 'lxml')
    # max_category_page = int(soup.find_all(class_='npage')[-1].text)
    books_url = get_page_books(url_template, category_page_response)

    for page in range(2, 5):
        page_response = requests.get(urljoin(url_template, category + str(page)))
        page_response.raise_for_status()
        books_url += get_page_books(url_template, page_response)

    for book_url in books_url:
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

                filename = f'{book_id}. {page_details["book_title"]}.txt'
                download_txt(file_response, filename)
                download_image(page_details['image_url'])

                page_details['image_url'] = os.path.join('images', page_details['image_url'].split('/')[-1])
                page_details['book_path'] = os.path.join('books', filename)
                with open('books_data.json', 'w', encoding='utf8') as file:
                    json.dump(page_details, file)

                print(page_details)
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
