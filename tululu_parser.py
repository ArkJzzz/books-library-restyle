__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

import logging
import requests
import urllib3
import os
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


logger = logging.getLogger('tululu_parser')


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
    logger.debug(f'filepath: {filepath}')
    logger.debug(f'url: {url}')

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


def get_book_title(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('body')\
                    .find('table')\
                    .find(class_='ow_px_td')\
                    .find('h1')

    book_title, book_author = title_tag.text.split('::')
    
    return book_title.strip()


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
            book_txt_url = f'https://tululu.org/txt.php?id={book_id}'
            book_page_url = f'https://tululu.org/b{book_id}/'
            book_title = f'{book_id}. {get_book_title(book_page_url)}'
            download_txt(book_txt_url, book_title)
        except requests.HTTPError:
            logger.error(f'HTTPError: Запрашиваемая страница не найдена')

if __name__ == '__main__':
    main()
