import unittest

from flask import json

from openapi_server.models.book import Book  # noqa: E501
from openapi_server.models.book_create import BookCreate  # noqa: E501
from openapi_server.models.book_update import BookUpdate  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.message import Message  # noqa: E501
from openapi_server.test import BaseTestCase


class TestBooksController(BaseTestCase):
    """BooksController integration test stubs"""

    def test_create_book(self):
        """Test case for create_book

        Добавить новую книгу
        """
        book_create = {"year":1869,"author":"Лев Толстой","title":"Война и мир"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'ApiKeyAuth': 'special-key',
        }
        response = self.client.open(
            '/api/v1/books',
            method='POST',
            headers=headers,
            data=json.dumps(book_create),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_book(self):
        """Test case for delete_book

        Удалить книгу
        """
        headers = { 
            'Accept': 'application/json',
            'ApiKeyAuth': 'special-key',
        }
        response = self.client.open(
            '/api/v1/books/{book_id}'.format(book_id=56),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_book_by_id(self):
        """Test case for get_book_by_id

        Получить одну книгу по id
        """
        headers = { 
            'Accept': 'application/json',
            'ApiKeyAuth': 'special-key',
        }
        response = self.client.open(
            '/api/v1/books/{book_id}'.format(book_id=56),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_books(self):
        """Test case for get_books

        Получить список книг
        """
        query_string = [('author', 'author_example'),
                        ('limit', 20)]
        headers = { 
            'Accept': 'application/json',
            'ApiKeyAuth': 'special-key',
        }
        response = self.client.open(
            '/api/v1/books',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_book(self):
        """Test case for update_book

        Изменить книгу
        """
        book_update = {"year":1869,"author":"Лев Толстой","available":False,"title":"Война и мир"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'ApiKeyAuth': 'special-key',
        }
        response = self.client.open(
            '/api/v1/books/{book_id}'.format(book_id=56),
            method='PUT',
            headers=headers,
            data=json.dumps(book_update),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
