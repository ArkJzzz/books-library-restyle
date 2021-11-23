__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

import logging
import requests
import urllib3
import hashlib
import json
import os
import argparse
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


logger = logging.getLogger('parse_tululu_category')


URL_BASE = 'https://tululu.org/'
GENRE_ID = 55  # Книги жанра :: Научная фантастика


def check_for_redirect(response):
    """Функция для проверки перенаправления запроса

    Поднимает исключение HTTPError,
    если ответ пришел не с запрашиваемой страницы.

    """

    if response.history:
        raise requests.HTTPError


def get_page_response(url):
    """Возвращает страницу по запрашиваему url"""

    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    return response


def get_num_of_pages_genre():
    """Возвращает номер последней страницы с книгами жанра"""

    url = urljoin(URL_BASE, f'l{GENRE_ID}/')
    page_response = get_page_response(url)
    soup = BeautifulSoup(page_response.text, 'lxml')
    last_page_tag = soup.select_one('.npage:last-child')

    return int(last_page_tag.text)


def get_books_urls(genre_page_response):
    """Возвращает ссылки на книги со страницы жанра"""

    soup = BeautifulSoup(genre_page_response.text, 'lxml')
    books_tag = soup.select('#content .d_book .bookimage')
    books_paths = [tag.select_one('a').get('href') for tag in books_tag]

    return [urljoin(URL_BASE, path) for path in books_paths]


def get_genre_books_urls(start_page=1, end_page=None):
    """Возвращает все ссылки на книги с указанного диапазона страниц жанра"""

    books_urls = []
    last_page = get_num_of_pages_genre()
    end_page = last_page if not end_page else end_page

    if start_page > end_page or end_page > last_page:
        raise ValueError

    for page_num in range(start_page, end_page + 1):
        url = urljoin(URL_BASE, f'l{GENRE_ID}/{page_num}/')
        genre_page_response = get_page_response(url)
        books_urls.extend(get_books_urls(genre_page_response))

    logger.info('Ссылки на книги жанра получены')

    return books_urls


def save_books_descriptions(books_descriptions, json_path):
    """Сохраняет описания книг в json-файл"""

    Path(json_path).parent.mkdir(parents=True, exist_ok=True)

    with open(json_path, 'w', encoding='utf8') as json_file:
        json.dump(books_descriptions, json_file, ensure_ascii=False)

    logger.info(f'Описания книг сохранены в файле {json_path}')

    return json_path


def download_image(url, filename, folder):
    """Функция для скачивания текстовых файлов.

    Args:
        url (str): Cсылка на изображение, которое хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.

    Returns:
        str: Путь до файла, куда сохранено изображение.

    """

    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    Path(folder).mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(filename)
    extension = Path(url).suffix
    filepath = os.path.join(folder, f'{filename}{extension}')
    with open(filepath, 'wb') as file:
        file.write(response.content)
    logger.info(f'Обложка скачана: {filepath}')

    return filepath


def download_txt(url, filename, folder):
    """Функция для скачивания текстовых файлов.

    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.

    Returns:
        str: Путь до файла, куда сохранён текст.

    """

    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    Path(folder).mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, f'{filename}.txt')
    with open(filepath, 'w') as file:
        file.write(response.text)
    logger.info(f'Книга скачана: {filepath}')

    return filepath


def parse_book_page(response):
    """Функция парсинга страницы с книгой."""

    soup = BeautifulSoup(response.text, 'lxml')

    title_tag = soup.select_one('h1')
    title, author = title_tag.text.split('::')
    title = title.strip()
    author = author.strip()

    cover_tag = soup.select_one('.bookimage img')
    cover_url = urljoin(response.url, cover_tag['src'])

    txt_tag = soup.select_one('[href^="/txt.php?id="]')
    txt_url = urljoin(response.url, txt_tag['href']) if txt_tag else None

    comments_tag = soup.select('.texts')
    comments = [tag.select_one('.black').text for tag in comments_tag]

    genres_tag = soup.select('span.d_book a')
    genres = [tag.text for tag in genres_tag]

    logger.info(f'Получено описание книги {title}')

    return {
        'title': title,
        'author': author,
        'cover_url': cover_url,
        'txt_url': txt_url,
        'comments': comments,
        'genres': genres,
    }


def create_parser():
    parser_description = '''
        Скрипт для скачивания книг жанра "Научная фантастика"
        с сайта tululu.ru
    '''
    parser = argparse.ArgumentParser(description=parser_description)
    parser.add_argument('--start_page', type=int, default=1,
                        help='с какой страницы начинать скачивать')
    parser.add_argument('--end_page', type=int,
                        help='по какую страницу скачивать')
    parser.add_argument('--dest_folder', default='.',
                        help='путь к каталогу с результатами парсинга')
    parser.add_argument('--json_path', default='books_description.json',
                        help='указать свой путь к *.json файлу с результатами')
    parser.add_argument('--skip_img', action='store_true',
                        help='не скачивать картинки')
    parser.add_argument('--skip_txt', action='store_true',
                        help='не скачивать файлы книг')

    return parser


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

    parser = create_parser()
    args = parser.parse_args()

    books_folder = Path(args.dest_folder) / 'books'
    imgages_folder = Path(args.dest_folder) / 'images'
    json_path = Path(args.dest_folder) / args.json_path
    books_descriptions = []
    books_urls = get_genre_books_urls(args.start_page, args.end_page)

    for book_url in books_urls:
        try:
            response = get_page_response(book_url)
            book = parse_book_page(response)

            url_hash = hashlib.md5(book_url.encode()).hexdigest()
            filename = f'{url_hash[-5:]} {book["title"]}'

            book_path = download_txt(
                url=book['txt_url'],
                filename=filename,
                folder=books_folder,
            ) if not args.skip_txt else None

            img_src = download_image(
                url=book['cover_url'],
                filename=filename,
                folder=imgages_folder,
            ) if not args.skip_img else None

            book_description = {
                'title': book['title'],
                'author': book['author'],
                'img_src': img_src,
                'book_path': book_path,
                'comments': book['comments'],
                'genres': book['genres'],
            }
            books_descriptions.append(book_description)

        except requests.HTTPError:
            logger.error('HTTPError: Запрашиваемая страница не найдена')
        except requests.exceptions.MissingSchema:
            logger.error('Invalid URL: Ссылка не действительна')

    save_books_descriptions(books_descriptions, json_path)


if __name__ == '__main__':
    main()
