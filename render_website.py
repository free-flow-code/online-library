import os
import json
import math
from livereload import Server
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open('books_data.json', encoding="utf8") as json_file:
        books = list(chunked(json.load(json_file), 2))

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
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='./pages', default_filename='index1.html')


if __name__ == '__main__':
    main()
