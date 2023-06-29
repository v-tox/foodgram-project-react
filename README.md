# Дипломный проект Foodgram
![Github actions](https://github.com/v-tox/foodgram-project-react/actions/workflows/main.yml/badge.svg)

### Описание:

Проект Foodgram «Продуктовый помощник» - онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Описание workflow
* проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
* сборка и доставка докер-образа для контейнера web на Docker Hub
* автоматический деплой проекта на боевой сервер

## Используемые технологии:
![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![image](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![image](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![image](https://img.shields.io/badge/django%20rest-ff1709?style=for-the-badge&logo=django&logoColor=white)
![image](https://img.shields.io/badge/VSCode-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)
![image](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)
![image](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![image](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![image](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

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