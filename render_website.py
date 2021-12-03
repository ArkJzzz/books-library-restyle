__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

import logging
import json
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


logger = logging.getLogger('main')

BASE_DIR = Path.cwd()
MEDIA_ROOT = Path() / BASE_DIR / 'media'


def on_reload():
    os.makedirs('pages', exist_ok=True)
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml']),
    )
    template = env.get_template('template.html')
    books_file = os.path.join(MEDIA_ROOT, 'books_description.json')
    with open(books_file, 'r') as my_file:
        books = json.loads(my_file.read())

    books_by_page = list(chunked(books, 10))

    for page_num, books_on_page in enumerate(books_by_page, 1):
        books_by_columns = list(chunked(books_on_page, 2))

        rendered_page = template.render(
            books_by_columns=books_by_columns,
            page_num=page_num,
        )
        with open(f'pages/index{page_num}.html', 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    formatter = logging.Formatter(
        fmt='%(asctime)s %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%b-%d %H:%M:%S (%Z)',
        style='%',
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)

    on_reload()

    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='pages', default_filename='index1.html')


if __name__ == '__main__':
    main()
