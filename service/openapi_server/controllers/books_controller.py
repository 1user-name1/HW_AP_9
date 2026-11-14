import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.book import Book  # noqa: E501
from openapi_server.models.book_create import BookCreate  # noqa: E501
from openapi_server.models.book_update import BookUpdate  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.message import Message  # noqa: E501
from openapi_server import util

# база данных пока нет, храню книги просто в списке
# purchase_price и added_by это внутренние поля, наружу их не отдаем
books = [
    {'id': 1, 'title': 'Война и мир', 'author': 'Лев Толстой', 'year': 1869,
     'available': True, 'purchase_price': 500, 'added_by': 'librarian'},
    {'id': 2, 'title': 'Преступление и наказание', 'author': 'Федор Достоевский', 'year': 1866,
     'available': False, 'purchase_price': 350, 'added_by': 'librarian'},
]
next_id = 3


def to_dto(b):
    # делаем из внутренней книги ту которую можно отдать (без цены и added_by)
    return Book(id=b['id'], title=b['title'], author=b['author'],
                year=b['year'], available=b['available'])


def find_book(book_id):
    for b in books:
        if b['id'] == book_id:
            return b
    return None


def create_book(body, token_info=None):  # noqa: E501
    """Добавить новую книгу

     # noqa: E501

    :param body: тело запроса (connexion передает его как body)
    :type body: dict | bytes

    :rtype: Union[Book, Tuple[Book, int], Tuple[Book, int, Dict[str, str]]
    """
    global next_id
    if token_info['role'] != 'librarian':
        return Error(code=403, message='Добавлять книги может только библиотекарь'), 403
    if connexion.request.is_json:
        book_create = BookCreate.from_dict(connexion.request.get_json())  # noqa: E501
    new_book = {
        'id': next_id,
        'title': book_create.title,
        'author': book_create.author,
        'year': book_create.year,
        'available': True,
        'purchase_price': 0,
        'added_by': token_info['uid'],
    }
    next_id = next_id + 1
    books.append(new_book)
    return to_dto(new_book), 201


def delete_book(book_id, token_info=None):  # noqa: E501
    """Удалить книгу

     # noqa: E501

    :param book_id: id книги
    :type book_id: int

    :rtype: Union[Message, Tuple[Message, int], Tuple[Message, int, Dict[str, str]]
    """
    if token_info['role'] != 'librarian':
        return Error(code=403, message='Удалять книги может только библиотекарь'), 403
    b = find_book(book_id)
    if b is None:
        return Error(code=404, message='Книга не найдена'), 404
    books.remove(b)
    return Message(message='Книга удалена')


def get_book_by_id(book_id):  # noqa: E501
    """Получить одну книгу по id

     # noqa: E501

    :param book_id: id книги
    :type book_id: int

    :rtype: Union[Book, Tuple[Book, int], Tuple[Book, int, Dict[str, str]]
    """
    b = find_book(book_id)
    if b is None:
        return Error(code=404, message='Книга не найдена'), 404
    return to_dto(b)


def get_books(author=None, limit=None):  # noqa: E501
    """Получить список книг

     # noqa: E501

    :param author: Фильтр по автору
    :type author: str
    :param limit: Сколько книг вернуть максимум
    :type limit: int

    :rtype: Union[List[Book], Tuple[List[Book], int], Tuple[List[Book], int, Dict[str, str]]
    """
    result = []
    for b in books:
        if author is not None and b['author'] != author:
            continue
        result.append(to_dto(b))
    if limit is not None:
        result = result[:limit]
    return result


def update_book(book_id, body, token_info=None):  # noqa: E501
    """Изменить книгу

     # noqa: E501

    :param book_id: id книги
    :type book_id: int
    :param body: тело запроса (connexion передает его как body)
    :type body: dict | bytes

    :rtype: Union[Book, Tuple[Book, int], Tuple[Book, int, Dict[str, str]]
    """
    if token_info['role'] != 'librarian':
        return Error(code=403, message='Менять книги может только библиотекарь'), 403
    if connexion.request.is_json:
        book_update = BookUpdate.from_dict(connexion.request.get_json())  # noqa: E501
    b = find_book(book_id)
    if b is None:
        return Error(code=404, message='Книга не найдена'), 404
    b['title'] = book_update.title
    b['author'] = book_update.author
    b['year'] = book_update.year
    if book_update.available is not None:
        b['available'] = book_update.available
    return to_dto(b)
