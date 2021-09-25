__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

import logging
import logging.config
import requests
import urllib3
from pathlib import Path


logger = logging.getLogger('main')


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

    def download_book(url, folder):
        response = requests.get(url, verify=False)
        response.raise_for_status()

        filename = f'{folder}/id{book_id}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)

        logger.info(f'Книга скачана: {filename} ')



    Path('books').mkdir(parents=True, exist_ok=True)

    for book_id in range(1, 11):
        url = f'https://tululu.org/txt.php?id={book_id}'
        download_book(url, 'books')






if __name__ == '__main__':
    main()
