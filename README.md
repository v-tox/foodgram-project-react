# praktikum_new_diplom

### Описание:

Проект Foodgram «Продуктовый помощник» - онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Технологии:

Python
Django REST Framework
API REST
Postman
Djoser
Docker

## Локальная установка:
- Клонируем репозиторий на компьютер:

```
git@github.com:v-tox/foodgram-project-react.git
```
```
cd foodgram-project-react
```

- Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```
- Установить зависимости проекта:

```
cd backend/foodgram/
```
```
pip install -r requirements.txt
```

- Создать и выполнить миграции:
```
python manage.py makemigrations
```
```
python manage.py migrate
```

- Запуск сервера локально:
```
python manage.py runserver
```