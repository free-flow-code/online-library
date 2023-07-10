import os
import json
from livereload import Server
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)


def on_reload():
    template = env.get_template('template.html')

    with open('books_data.json', encoding="utf8") as json_file:
        books = list(chunked(json.load(json_file), 2))

    os.makedirs("pages", exist_ok=True)
    page = 1
    for index, value in enumerate(books):
        if index % 10 == 0:
            rendered_page = template.render(books=books[index - 10:index])
            with open(f'./pages/index{page}.html', 'w', encoding="utf8") as file:
                file.write(rendered_page)
            page += 1


on_reload()
server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')
