import os
import json
import argparse
from livereload import Server
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape


def parse_arguments():
    parser = argparse.ArgumentParser(description='Скрипт для запуска сайта онлайн-библиотеки.')
    parser.add_argument('--json-path', help='путь к файлу с данными книг', type=str, nargs='?', default='books_data.json')
    return parser.parse_args()


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    args = parse_arguments()
    json_path = args.json_path
    books_per_page = 10

    try:
        with open(json_path, encoding='utf8') as json_file:
            books_in_page = list(chunked(json.load(json_file), books_per_page))
    except FileNotFoundError:
        print('Файл с данными не найден. Укажите путь к json-файлу.')
        exit()

    os.makedirs('pages', exist_ok=True)
    books_per_row = 2
    total_pages = [*range(1, len(books_in_page) + 1)]
    for page_id, books in enumerate(books_in_page, start=1):
        rendered_page = template.render(
            books=list(chunked(books, books_per_row)),
            page_id=page_id,
            total_pages=total_pages
        )
        with open(f'./pages/index{page_id}.html', 'w', encoding='utf8') as file:
            file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.') #default_filename='pages/index1.html'


if __name__ == '__main__':
    main()
