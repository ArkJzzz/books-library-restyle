__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

import logging
import requests
import urllib3
import os
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import urlsplit
from urllib.parse import unquote


logger = logging.getLogger('tululu_parser')


def download_image(url, filename=False, folder='images/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на изображение, которое хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """

    logger.debug(f'url: {url}')

    Path(folder).mkdir(parents=True, exist_ok=True)

    if not filename:
        cover_path = unquote(urlsplit(url).path)
        filename = cover_path.split('/')[-1]
    filepath = os.path.join(folder, f'{filename}')

    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    logger.info(f'Обложка скачана: {filepath} ')

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

    logger.debug(f'url: {url}')

    Path(folder).mkdir(parents=True, exist_ok=True)
    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, f'{filename}.txt')   

    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    logger.info(f'Книга скачана: {filepath} ')

    return filepath


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_book_page(book_id):
    url_base = 'https://tululu.org/'
    url = urljoin(url_base, f'b{book_id}/')

    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')

    title_tag = soup.find('body')\
                    .find('table')\
                    .find(class_='ow_px_td')\
                    .find('h1')
    title, author = title_tag.text.split('::')
    title = title.strip()
    author = author.strip()

    cover_tag = soup.find('div', class_='bookimage')\
                    .find('img')
    cover_url = urljoin(response.url, cover_tag['src'])

    txt_url = urljoin(response.url, f'/txt.php?id={book_id}')

    # comments = []
    # comments_tag = soup.find_all('div', class_='texts')
    # for comment_tag in comments_tag:
    #     comment = comment_tag.find('span', class_='black').text
    #     comments.append(comment)

    comments = []
    comments_tag = soup.find_all('div', class_='texts')\
                    .find_all('span', class_='black')
    for comment_tag in comments_tag:
        comments.append(comment_tag.text)

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


    for book_id in range(1, 11):
        try:
            book = parse_book_page(book_id)

            logger.debug(book['title'])
            logger.debug(book['cover_url'])
            logger.debug(book['txt_url'])
            logger.debug(book['comments'])
            logger.debug(book['genres'])
            print()

            # book_title = f'{book_id}. {book['title']}'
            # download_txt(book['txt_url'], book_title)
            # download_image(book['cover_url'])

        except requests.HTTPError:
            logger.error(f'HTTPError: Запрашиваемая страница не найдена')

if __name__ == '__main__':
    main()
