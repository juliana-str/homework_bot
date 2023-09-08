### homework_bot


## 1. [Описание](#1)
## 2. [Установка](#2)
## 3. [Создание виртуального окружения](#3)
## 4. [Команды для запуска](#4)
## 5. [Об авторе](#5)

---
## 1. Описание <a id=1></a>

Telegram-бот, который будет обращаться к API сервиса Практикум.Домашка и узнавать статус вашей домашней работы

Что делает бот:

- Раз в 10 минут запрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;
- При обновлении статуса анализирует ответ API и отправляет вам соответствующее уведомление в Telegram;
- Логирует свою работу и сообщает вам о важных проблемах сообщением в Telegram.

---
## 2. Установка  <a id=2></a>

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:juliana-str/homework_bot.git
```

```
cd homework_bot/
```
---
## 3. Создание виртуального окружения <a id=3></a>

Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```
```bash
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate
```

---
## 4. Команды для запуска <a id=4></a>

И установить зависимости из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```
```bash
python3 manage.py makemigrations
```
```bash
python3 manage.py migrate
```
```bash
python3 manage.py runserver
```

Проект использует базу данных sqlite3.  

---
## 5. Об авторе <a id=5></a>

Стрельникова Юлиана Сергеевна  
Python-разработчик (Backend)  
Россия, г. Санкт-Петербург                                                                                                                                                               
E-mail: julianka.str@yandex.ru  
Telegram: @JulianaStr
