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


def download_image(url, filename=None, folder='images/'):
    """Функция для скачивания текстовых файлов.
    
    Args:
        url (str): Cсылка на изображение, которое хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    
    Returns:
        str: Путь до файла, куда сохранён текст.
    
    """

    Path(folder).mkdir(parents=True, exist_ok=True)

    if filename is None:
        cover_path = unquote(urlsplit(url).path)
        filename = cover_path.split('/')[-1]
    filepath = os.path.join(folder, f'{filename}')

    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

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

    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, f'{filename}.txt')
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    with open(filepath, 'wb') as file:
        file.write(response.content)
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
    content = requests.get(url, verify=False)
    content.raise_for_status()
    check_for_redirect(content)

    return content   


def parse_book_page(content):
    """Функция парсинга страницы с книгой."""

    soup = BeautifulSoup(content.text, 'lxml')

    title_tag = soup.find('body')\
                    .find('table')\
                    .find(class_='ow_px_td')\
                    .find('h1')
    title, author = title_tag.text.split('::')
    title = title.strip()
    author = author.strip()

    cover_tag = soup.find('div', class_='bookimage')\
                    .find('img')
    cover_url = urljoin(content.url, cover_tag['src'])

    txt_tag = soup.find(href=re.compile('txt'))
    if txt_tag:
        txt_url = urljoin(content.url, txt_tag['href'])
    else:
        txt_url = None

    comments = []
    comments_tag = soup.find_all('div', class_='texts')
    for comment_tag in comments_tag:
        comment = comment_tag.find('span', class_='black').text
        comments.append(comment)

    genres = []
    genres_tag = soup.find('span', class_='d_book')\
                    .find_all('a')
    for genre_tag in genres_tag:
        genres.append(genre_tag.text)

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

    parser = argparse.ArgumentParser(
                description='Скрипт для скачивания книг с сайта tululu.ru'
            )
    parser.add_argument(
            '--start_id',
            default=1,
            help='с какой книги начинать скачивать',
            type=int,
        )
    parser.add_argument(
            '--end_id', 
            default=10,
            help='по какую книгу скачивать',
            type=int,
        )
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id+1):
        try:
            logger.debug(f'book id: {book_id}')

            content = get_book_page(book_id)
            book = parse_book_page(content)

            logger.debug(book['title'])

            book_title = f'{book_id}. {book["title"]}'
            download_txt(book['txt_url'], book_title)
            download_image(book['cover_url'])

        except requests.HTTPError:
            logger.error('HTTPError: Запрашиваемая страница не найдена')
        except requests.exceptions.MissingSchema:
            logger.error('Invalid URL: Ссылка не действительна')

if __name__ == '__main__':
    main()
