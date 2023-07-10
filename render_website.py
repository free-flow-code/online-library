import os
import json
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
    for index, value in enumerate(books):
        if index and index % 10 == 0:
            rendered_page = template.render(books=books[index - 10:index])
            del books[index - 10:index]
            with open(f'./pages/index{page}.html', 'w', encoding="utf8") as file:
                file.write(rendered_page)
            page += 1
    rendered_page = template.render(books=books)
    with open(f'./pages/index{page}.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='pages', default_filename='index1.html')


if __name__ == '__main__':
    main()
