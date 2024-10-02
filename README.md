# kitten_show


Этот проект представляет собой API для сайта-выставки, который позволяет пользователям просматривать кошек и фильтровать их по породе, цвету, возрасту. А зарегистрированному пользователю создавать породы и добавлять/изменять/удалять кошек. Проект Kitten Show работает на Docker, что позволяет легко развернуть и управлять средой разработки без необходимости установки зависимостей на локальной машине.

## Технологии

- **FastAPI**: веб-фреймворк для создания API на Python.
- **SQLAlchemy**: библиотека для работы с базами данных.
- **PostgreSQL**: база данных.
- **Docker**: для контейниризации данных.


### Запуск проекта

Клонировать репозиторий и перейти в него в командной строке: 
```
git clone https://github.com/LenarSag/kitten_show
cd kitten_show

```

Запуск проекта:
```
docker-compose up --build

```

После запуска контейнеров, откройте браузер и перейдите по адресу, там будет документация:

http://localhost:8000/docs


Создание пользователя http://localhost:8000/api/v1/auth/user:

```
{
  "email": "test@test.com",
  "password": "Q123werty!23",
  "username": "admin"
}
```

Получение токена http://localhost:8000/api/v1/auth/user:

```
{
  "password": "Q123werty!23",
  "username": "admin"
}
```

Ответ:

```
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZThiYjIxMi0yOGYwLTQwYWYtODdkNi1lNzE0OGVlNjQwOTQiLCJleHAiOjE3MzA0NDg3NzB9.92juWq9fDYaNV096uGSqcAh5fnVwvWa-scpWS0cBHpM",
    "token_type": "Bearer"
}
```

### Примеры запросов

пример запроса POST http://localhost:8000/api/v1/breeds/

```
{
    "name": "scottish",
}
```

Ответ:

```
{
    "name": "scottish",
    "id": 1
}
```

пример запроса GET http://localhost:8000/api/v1/breeds/

Ответ:

```
{
    "items": [
        {
            "name": "british",
            "id": 2
        },
        {
            "name": "chinese",
            "id": 3
        },
        {
            "name": "scottish",
            "id": 1
        }
    ],
    "total": 3,
    "page": 1,
    "size": 50,
    "pages": 1
}
```

пример запроса POST http://localhost:8000/api/v1/kittens/

```
{
    "name": "Kotik",
    "birth_date": "2023-10-12",
    "sex": "female",
    "color": "black",
    "description": "bad boy",
    "breed_id": 2
}
```

Ответ:

```
{
    "id": 1,
    "name": "Kotik",
    "color": "black",
    "sex": "female",
    "age_in_months": 11,
    "description": "bad boy",
    "breed": {
        "name": "british",
        "id": 2
    }
}
```

пример запроса GET http://localhost:8000/api/v1/kittens/

Ответ:

```
{
    "items": [
        {
            "id": 1,
            "name": "Kotik",
            "color": "black",
            "sex": "female",
            "age_in_months": 11,
            "description": "bad boy",
            "breed": {
                "name": "british",
                "id": 2
            }
        },
        {
            "id": 2,
            "name": "Vasiliy",
            "color": "white",
            "sex": "male",
            "age_in_months": 47,
            "description": "good boy",
            "breed": {
                "name": "chinese",
                "id": 3
            }
        }
    ],
    "total": 2,
    "page": 1,
    "size": 50,
    "pages": 1
}
```


пример запроса GET http://localhost:8000/api/v1/kittens/2/

Ответ:

```
{
    "id": 2,
    "name": "Vasiliy",
    "color": "white",
    "sex": "male",
    "age_in_months": 47,
    "description": "good boy",
    "breed": {
        "name": "chinese",
        "id": 3
    }
}
```

пример запроса PATCH http://localhost:8000/api/v1/kittens/2/

Ответ:

```
{
    "name": "Vasiliy",
    "birth_date": "2022-10-12",
    "sex": "male",
    "color": "white",
    "description": "good boy",
    "breed_id": 3
}
```

Ответ

```
{
    "id": 2,
    "name": "Vasiliy",
    "color": "white",
    "sex": "male",
    "age_in_months": 23,
    "description": "good boy",
    "breed": {
        "name": "chinese",
        "id": 3
    }
}
```

пример запроса DELETE http://localhost:8000/api/v1/kittens/2/

Ответ: HTTP_204_NO_CONTENT


пример запроса GET c фильтрацией по возрасту http://localhost:8000/api/v1/kittens/?age_in_months__gt=2

Ответ

```
{
    "items": [
        {
            "id": 1,
            "name": "Kotik",
            "color": "black",
            "sex": "female",
            "age_in_months": 11,
            "description": "bad boy",
            "breed": {
                "name": "british",
                "id": 2
            }
        },
        {
            "id": 2,
            "name": "Vasiliy",
            "color": "white",
            "sex": "male",
            "age_in_months": 23,
            "description": "good boy",
            "breed": {
                "name": "chinese",
                "id": 3
            }
        }
    ],
    "total": 2,
    "page": 1,
    "size": 50,
    "pages": 1
}
```


пример запроса GET c фильтрацией по породе http://localhost:8000/api/v1/kittens/?breed__name__ilike=chi

Ответ:

```
{
    "items": [
        {
            "id": 2,
            "name": "Vasiliy",
            "color": "white",
            "sex": "male",
            "age_in_months": 23,
            "description": "good boy",
            "breed": {
                "name": "chinese",
                "id": 3
            }
        }
    ],
    "total": 1,
    "page": 1,
    "size": 50,
    "pages": 1
}
```


### Тесты

Cоздать и активировать виртуальное окружение: 
```
python3.9 -m venv venv 
```
* Если у вас Linux/macOS 

    ```
    source venv/bin/activate
    ```
* Если у вас windows 
 
    ```
    source venv/Scripts/activate
    ```
```
python3.9 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```

Запустить тесты:

```
pytest
```
