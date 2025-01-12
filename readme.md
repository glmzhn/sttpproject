# Order Management API

## Описание проекта

Этот проект представляет собой REST API для управления заказами с поддержкой кэширования, логирования, аутентификации и сбора метрик. Реализованная архитектура соответствует принципам Clean Architecture и использует Django с Django REST Framework.

### Возможности:
- Управление заказами (создание, обновление, удаление, фильтрация).
- Поддержка авторизации пользователей (User, Admin) через Basic Auth или Bearer Token.
- Кэширование данных о заказах.
- Логирование действий пользователей (создание, обновление, удаление заказов).
- Сбор и предоставление метрик API.
- Поддержка событий для изменения состояния заказов.

## Установка и настройка

### 1. Клонирование репозитория

```git clone https://github.com/yourusername/order-management-api.git```

### 2. Deploy и запуск проекта
- ```docker-compose build```
- ```docker-compose up```
- ```docker-compose exec back python manage.py makemigrations orders```
- ```docker-compose exec back python manage.py migrate```

Создание админа(опционально)
- ```docker-compose exec back python manage.py createsuperuser```

### 3. Создание файла .env с параметрами
- Файл уже создан и настроен для локальных тестов ;)

## Использование API

P.S. Для просмотра API с помощью Swagger, переходите на эндпоинт /swagger/

### 1. POST запрос на URL /api/v1/login/
Получение Bearer токена для работы с API

Body - ```{
    "username": "<EXAMPLE>",
     "password": "<EXAMPLE>"
}```

Ответ от сервера - ```{"refresh": "<EXAMPLE>, "access": "<EXAMPLE>"}```

ОБЯЗАТЕЛЬНО УКАЗЫВАЙТЕ ТОКЕН ПРИ ЛЮБОЙ РАБОТЕ С API

### 2. Get запрос на URL /api/v1/orders/
Получение списка записей Order

Запросы GET кэшируются, но обновляются при любом другом HTTP методе и кэш удаляется

### 3. Get запрос на URL /api/v1/orders/order_id/
Получение конкретного заказа по его order_id

### 4. POST запрос на URL /api/v1/login/
Создание записей Order

Пример:

Body - ```{
  "status": "cancelled",
  "total_price": "229",
  "products": [
    {
      "name": "affe",
      "price": "42",
      "quantity": 0
    }
  ]
}```

Ответ сервера - ```{
    "order_id": "bf114532-24df-4163-b571-6b25cf6610d7",
    "user": "admin",
    "status": "cancelled",
    "total_price": "229.00",
    "products": [
        {
            "product_id": "36940128-e340-47f3-a264-214bcacee8ca",
            "name": "affe",
            "price": "42.00",
            "quantity": 0
        }
    ],
    "is_deleted": false
}```

### 5. PUT запрос на URL /api/v1/orders/order_id/
Аналогичен пункту 4 с единственным отличием, указывается order_id в URL адресе

### 6. Delete запрос на URL /api/v1/orders/order_id/
Происходит мягкое удаление в следствии чего запись остается в базе, но при получении спиcка записей не отображается пользователю

### 7. Получению метрик по URL /metrics/
Сервер отдает удобные метрики для каждого эндпоинта, а именно: Общее кол-во вызовов эндпоинта, успешные попытки и неуспешные попытки

## Логи
- Общие логи сохраняются по пути **/sttpproject/project/general.log**
- Сигналы отрабатывающие после обновления статуса существующей записи записывают их по пути **/sttpproject/project/orders/events.log**

## Тесты
Для запуска тестов пропишите команду - ```docker-compose exec back pytest orders/tests.py```
