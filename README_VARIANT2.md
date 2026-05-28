# TeamFinder, вариант 2

Реализован вариант 2: навыки пользователей и фильтрация участников по навыкам.

Автор: Матюхин Даниил  
Телефон: 89081376958

Основные страницы:
- `/projects/list/` - список проектов;
- `/projects/<id>/` - страница проекта;
- `/projects/create-project/` - создание проекта;
- `/users/register/` и `/users/login/` - регистрация и вход;
- `/users/<id>/` - профиль пользователя с блоком навыков;
- `/users/list/` - список участников с фильтром `?skill=<Название>`;
- `/users/change-password/` - смена пароля.

Для проверки можно создать демо-данные:

```bash
python manage.py seed_demo
```

Демо-пользователь:

```text
email: maria@yandex.ru
password: password
```

Основной режим проекта по заданию использует PostgreSQL. Скопируйте `.env_example` в `.env`, запустите базу и примените миграции:

```bash
docker compose up -d
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Автотесты:

```bash
python manage.py test
```
