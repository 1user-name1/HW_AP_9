# ДЗ 9 — API библиотеки

**Зачем этот API:** чтобы читатели могли смотреть какие книги есть в библиотеке, а библиотекарь мог их добавлять, менять и удалять.

## Что лежит в репозитории

- `api.yaml` — спецификация OpenAPI 3.0
- `service/` — сервис на Python (Flask + connexion), сгенерированный по спеке
- `README.md` — этот файл

## Эндпоинты

| Метод | Путь | Что делает | Ошибки |
|-------|------|-----------|--------|
| GET | /books | список книг (можно фильтр `author` и `limit`) | 401 |
| GET | /books/{bookId} | одна книга по id | 401, 404 |
| POST | /books | добавить книгу | 400, 401, 403 |
| PUT | /books/{bookId} | изменить книгу | 400, 401, 403, 404 |
| DELETE | /books/{bookId} | удалить книгу | 401, 403, 404 |

Авторизация через заголовок `X-API-Key`.

- **401** — ключа нет или он неправильный, то есть мы не знаем кто это
- **403** — ключ правильный (знаем кто это), но это читатель, а менять книги может только библиотекарь
- **404** — книги с таким id нет

Схемы (DTO) лежат в `components/schemas`: `Book`, `BookCreate`, `BookUpdate`, `Message`, `Error`.
Внутри сервиса у книги есть еще поля `purchase_price` (цена закупки) и `added_by` (кто добавил), но в `Book` их нет, наружу они не отдаются.
В `BookCreate` нет `id`, потому что его назначает сервер.

## Как делали

Делал с агентом: **Claude Code**, модель **Claude Fable 5.2**.

Итоговые промты:

1. Спека:
   > Напиши api.yaml в формате OpenAPI 3.0 для API библиотеки. Нужно 5 эндпоинтов для книг: получить список (с фильтром по автору и limit), получить одну по id, добавить, изменить (PUT) и удалить. У каждого должен быть summary, параметры и ответы. Авторизация по API ключу в заголовке X-API-Key. Ошибки: 401 если ключа нет или он неправильный, 403 если ключ правильный но это читатель а не библиотекарь, 404 если книги нет. Схемы вынеси в components: отдельно Book для ответа, отдельно BookCreate и BookUpdate для запросов, и Error. В Book не должно быть внутренних полей типа цены закупки.

2. Кодоген:
   > Проверь что спека валидная и сгенерируй по ней сервис на Python через openapi-generator, генератор python-flask, в папку service. npm у меня нет, есть только java.

3. Логика:
   > В сгенерированных контроллерах заглушки. Допиши простую реализацию, базу не надо, храни книги в списке в памяти. Сделай два тестовых ключа: для читателя и для библиотекаря. Внутри у книги пусть будут purchase_price и added_by, но в ответ они попадать не должны.

4. Исправление ошибки:
   > POST и PUT возвращают 500, в логе `create_book() missing 1 required positional argument: 'book_create'`. Исправь и проверь все эндпоинты, в том числе ошибки 401, 403, 404.

5. README:
   > Напиши README: зачем этот API одной фразой, таблица эндпоинтов, как делали, что поменяли после генератора, как запустить и что не доделано.

Шаги:

1. Агент написал `api.yaml` на тему библиотеки.
2. Проверил спеку валидатором:
   ```
   java -jar openapi-generator-cli-7.10.0.jar validate -i api.yaml
   ```
   Ответ: `No validation issues detected.`
3. Сгенерировал каркас:
   ```
   java -jar openapi-generator-cli-7.10.0.jar generate -i api.yaml -g python-flask -o service
   ```
   (npm на компьютере не было, поэтому скачал jar генератора с Maven Central, это то же самое что `openapi-generator-cli generate ...`)
4. Дописал логику в контроллеры и проверил запросами.

## Что поправили после генератора

Генератор сделал только заглушки, которые возвращают `'do some magic!'`. Поменяно два файла:

- `service/openapi_server/controllers/books_controller.py`
  - добавлен список книг в памяти (базы данных нет, после перезапуска все сбрасывается)
  - написаны все 5 функций
  - добавлена функция `to_dto`, которая убирает внутренние поля
  - проверка роли и ответ 403
  - параметр тела запроса переименован из `book_create` / `book_update` в `body`, потому что иначе была ошибка 500 (`missing 1 required positional argument`), connexion передает тело под именем `body`
- `service/openapi_server/controllers/security_controller.py`
  - добавлены два тестовых ключа: `reader-key` (читатель) и `admin-key` (библиотекарь). Если ключ не найден, возвращается None и получается 401

Остальные файлы в `service/` как выдал генератор.

## Как запустить

```
cd service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m openapi_server
```

Сервис запустится на http://localhost:8080/api/v1, Swagger UI будет на http://localhost:8080/api/v1/ui/

Примеры:

```
curl -H "X-API-Key: reader-key" http://localhost:8080/api/v1/books
curl -H "X-API-Key: reader-key" http://localhost:8080/api/v1/books/1
curl -X POST -H "X-API-Key: admin-key" -H "Content-Type: application/json" \
     -d '{"title": "Идиот", "author": "Федор Достоевский", "year": 1869}' \
     http://localhost:8080/api/v1/books
curl -X PUT -H "X-API-Key: admin-key" -H "Content-Type: application/json" \
     -d '{"title": "Идиот", "author": "Ф. Достоевский", "available": false}' \
     http://localhost:8080/api/v1/books/3
curl -X DELETE -H "X-API-Key: admin-key" http://localhost:8080/api/v1/books/3
```

## Что проверено

| Запрос | Ответ |
|--------|-------|
| GET /books без ключа | 401 |
| GET /books с неправильным ключом | 401 |
| GET /books?author=Лев Толстой&limit=1 | 200, одна книга |
| GET /books/1 | 200 |
| GET /books/99 | 404 |
| POST /books с ключом читателя | 403 |
| POST /books с ключом библиотекаря | 201 |
| POST /books без title | 400 |
| PUT /books/3 | 200 |
| PUT /books/99 | 404 |
| DELETE /books/3 с ключом читателя | 403 |
| DELETE /books/3 с ключом библиотекаря | 200 |
| DELETE /books/3 еще раз | 404 |

## Что не доделано

- Ошибки 401 и 400 отдает сам connexion в своем формате (`detail`, `status`, `title`), а не в формате схемы `Error` как в спеке. 403 и 404 отдаются как в спеке.
- Данные хранятся в памяти, базы нет.
- Сгенерированные тесты в `service/openapi_server/test` не трогал и не запускал.
