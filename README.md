# Социальная сеть блогеров

# Описание
## Социальная сеть дающая возможности:
- создать свою страницу с уникальным именем(адресом)
- создавать публикации на своей странице
- просматривать страницы других авторов
- подписываться/отписываться на авторов
- оставлять комментарии под публикациями

## В планах:
- добавить возможность редактирования/удаления комментариев
- ввести систему лайков

# Использованные технологии~
- SQLite3
- Python 3.8.10
- Django 2.2.6

# Инструкции по запуску
## Клонируем репозиторий:
- $: git clone https://github.com/KolesnikRV/hw05_final.git

## Создаём и активируем виртуальное окружение:
- $: python -m venv venv
- $: source venv/bin/activate

## Устанавливаем зависимости:
- $: pip install -r requirements.txt

## Выполняем миграции:
- python manage.py migrate

## Создание суперпользователя:
- $: python manage.py createsuperuser

## Запускаем проект:
- $: python manage.py runserver
 И переходим по адресу - http://127.0.0.1:8000

# Автор
## Студент яндекс практикум 12 когорта Роман Колесник