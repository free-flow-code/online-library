import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit


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
    book_text_url_template = 'https://tululu.org/txt.php?id='
    book_page_url_template = 'https://tululu.org/b'
    for i in range(1, 11):
        text_url = book_text_url_template + str(i)
        page_url = book_page_url_template + str(i)
        response = requests.get(text_url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            page_details = parse_book_page(page_url)
            filename = f'{i}. ' + page_details['book_title'] + '.txt'
            # print(page_details['book_title'])
            # download_txt(response, filename)
            # download_image(page_details['image_url'])
            # print(page_details['comments'])
            print(page_details['genres'])
        except requests.exceptions.HTTPError:
            pass


if __name__ == '__main__':
    main()
