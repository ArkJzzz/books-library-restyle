# tululu parser

Скрипт для скачивания книг с сайта онлайн-библиотеки [tululu.org](https://tululu.org/)


## Что используется

- [Библиотека requests](https://dvmn.org/encyclopedia/modules/requests/)
- [BeautifulSoup4](https://beautiful-soup-4.readthedocs.io/)
- [Библиотека pathvalidate](https://github.com/thombashi/pathvalidate)
- [Библиотека argparse](https://docs.python.org/3.6/howto/argparse.html)


## Установка

- Клонируйте репозиторий:
```
git clone https://github.com/ArkJzzz/books-library-restyle
```

- Установите зависимости:
```
pip3 install -r requirements.txt
```

## Как пользоваться

- **Скачивание первых 10 книг из онлайн-библиотеки**
```sh
python3 tululu_parser.py
```

Вывод: 

```sh
$ python tululu_parser.py
book id: 1
Административные рынки СССР и России
Книга скачана: books/1. Административные рынки СССР и России.txt
Обложка скачана: images/nopic.gif
book id: 2
HTTPError: Запрашиваемая страница не найдена
book id: 3
Азбука экономики
Книга скачана: books/3. Азбука экономики.txt
Обложка скачана: images/nopic.gif

...

book id: 10
Бизнес путь: Amazon.com
Книга скачана: books/10. Бизнес путь Amazon.com.txt
Обложка скачана: images/10.jpg
```

- **Скачивание произвольного количества книг из онлайн-библиотеки**

```sh
python tululu_parser.py  --start_id 35 --end_id 37
```

Вывод:

```sh
$ python tululu_parser.py  --start_id 35 --end_id 37
book id: 35
Искусство доминировать
Книга скачана: books/35. Искусство доминировать.txt
Обложка скачана: images/35.jpg
book id: 36
Искусство коммуникации в сетевом маркетинге
Книга скачана: books/36. Искусство коммуникации в сетевом маркетинге.txt
Обложка скачана: images/nopic.gif
book id: 37
HTTPError: Запрашиваемая страница не найдена
```
