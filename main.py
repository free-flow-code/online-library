import os
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
    parser.add_argument('start_id', help='id первой книги', type=int, nargs='?', default=0)
    parser.add_argument('stop_id', help='id последней книги', type=int, nargs='?', default=10)
    return parser.parse_args()


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.exceptions.HTTPError


def parse_book_page(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')

    book_header = soup.find('body').find('table').find('h1').text
    book_title = book_header.split('::')[0].strip()

    image_src = soup.select_one('div.bookimage img')['src']
    image_url = urljoin(url, image_src)

    comments_soup = soup.find_all(class_='texts')
    comments = []
    if comments_soup:
        for comment in comments_soup:
            comments.append(comment.find(class_='black').text)

    genres_soup = soup.find('span', class_='d_book').find_all('a')
    genres = []
    if genres_soup:
        for genre in genres_soup:
            genres.append(genre.text)

    return {
        'book_title': book_title,
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


def download_image(url):
    response = requests.get(url)
    response.raise_for_status()
    filename = urlsplit(url).path.split('/')[-1]
    filepath = os.path.join('images', filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


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
        response = requests.get(book_text_url, params=book_text_url_params)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            page_details = parse_book_page(page_url)
            filename = f'{book_id}. {page_details["book_title"]}.txt'
            print('Заголовок: ', page_details['book_title'])
            download_txt(response, filename)
            download_image(page_details['image_url'])
            print('Жанры: ', page_details['genres'])
            print('Комментарии:\n', page_details['comments'], end='\n')
        except requests.exceptions.HTTPError as err:
            print(err)
            pass


if __name__ == '__main__':
    main()
