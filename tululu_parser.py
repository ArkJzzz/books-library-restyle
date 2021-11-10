__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

import logging
import requests
import urllib3
import os
import re
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import urlsplit
from urllib.parse import unquote


logger = logging.getLogger('tululu_parser')


def download_image(url, filename, folder='images/'):
    """Функция для скачивания текстовых файлов.

    Args:
        url (str): Cсылка на изображение, которое хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.

    Returns:
        str: Путь до файла, куда сохранён текст.

    """

    Path(folder).mkdir(parents=True, exist_ok=True)

    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    filename = sanitize_filename(filename)
    cover_path = unquote(urlsplit(url).path)
    extension = cover_path.split('.')[-1]
    filepath = os.path.join(folder, f'{filename}.{extension}')
    with open(filepath, 'wb') as file:
        file.write(response.content)
    logger.info(f'Обложка скачана: {filepath}')

    return filepath


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.

    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.

    Returns:
        str: Путь до файла, куда сохранён текст.

    """

    Path(folder).mkdir(parents=True, exist_ok=True)

    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, f'{filename}.txt')
    with open(filepath, 'w') as file:
        file.write(response.text)
    logger.info(f'Книга скачана: {filepath}')

    return filepath


def check_for_redirect(response):
    """Функция для проверки перенаправления запроса

    Поднимает исключение HTTPError,
    если ответ пришел не с запрашиваемой страницы.

    """

    if response.history:
        raise requests.HTTPError


def get_book_page(book_id):
    """Функция запроса страницы книги с сайта https://tululu.org/

    Args:
        book_id (int): id книги на сайте https://tululu.org/

    Returns:
        Response object: ответ сервера на HTTP-запрос.

    """

    url_base = 'https://tululu.org/'
    url = urljoin(url_base, f'b{book_id}/')
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    return response


def parse_book_page(response):
    """Функция парсинга страницы с книгой."""

    soup = BeautifulSoup(response.text, 'lxml')

    title_tag = soup.find('h1')
    title, author = title_tag.text.split('::')
    title = title.strip()
    author = author.strip()

    cover_tag = soup.find('div', class_='bookimage').find('img')
    cover_url = urljoin(response.url, cover_tag['src'])

    txt_tag = soup.find(href=re.compile('txt'))
    txt_url = urljoin(response.url, txt_tag['href']) if txt_tag else None

    comments_tag = soup.find_all('div', class_='texts')
    comments = [tag.find('span', class_='black').text for tag in comments_tag]

    genres_tag = soup.find('span', class_='d_book').find_all('a')
    genres = [tag.text for tag in genres_tag]

    logger.info(f'Получена информация о книге {title}')

    return {
        'title': title,
        'author': author,
        'cover_url': cover_url,
        'txt_url': txt_url,
        'comments': comments,
        'genres': genres,
    }


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

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    description = 'Скрипт для скачивания книг с сайта tululu.ru'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--start_id', default=1, type=int,
                        help='с какой книги начинать скачивать')
    parser.add_argument('--end_id', default=10, type=int,
                        help='по какую книгу скачивать')
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id + 1):
        try:
            response = get_book_page(book_id)
            book = parse_book_page(response)
            filename = f'{book_id}. {book["title"]}'
            download_txt(book['txt_url'], filename)
            download_image(book['cover_url'], filename)

        except requests.HTTPError:
            logger.error('HTTPError: Запрашиваемая страница не найдена')
        except requests.exceptions.MissingSchema:
            logger.error('Invalid URL: Ссылка не действительна')


if __name__ == '__main__':
    main()
