import os
import json
import math
import argparse
from livereload import Server
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape


def parse_arguments():
    parser = argparse.ArgumentParser(description='Скрипт для запуска сайта онлайн-библиотеки.')
    parser.add_argument('--json-folder', help='путь к файлу с данными книг', type=str, nargs='?', default='.')
    return parser.parse_args()


def on_reload(json_folder):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')
    books_in_row = 2

    with open(os.path.join(json_folder, 'books_data.json'), encoding="utf8") as json_file:
        books = list(chunked(json.load(json_file), books_in_row))

    os.makedirs("pages", exist_ok=True)
    page = 1
    books_per_page = 10
    total_pages = [*range(1, math.ceil(len(books) / books_per_page) + 1)]
    for index, value in enumerate(books):
        if index and index % books_per_page == 0:
            rendered_page = template.render(
                books=books[index - books_per_page:index],
                page_id=page,
                total_pages=total_pages
            )
            del books[index - books_per_page:index]
            with open(f'./pages/index{page}.html', 'w', encoding="utf8") as file:
                file.write(rendered_page)
            page += 1
    rendered_page = template.render(books=books, page_id=page, total_pages=total_pages)
    with open(f'./pages/index{page}.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    args = parse_arguments()
    json_folder = args.json_folder
    on_reload(json_folder)
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.', default_filename='pages/index1.html')


if __name__ == '__main__':
    main()
