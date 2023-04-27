### homework_bot
python telegram bot

Telegram-бот, который будет обращаться к API сервиса Практикум.Домашка и узнавать статус вашей домашней работы


#Что делает бот:

раз в 10 минут запрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;
при обновлении статуса анализирует ответ API и отправляет вам соответствующее уведомление в Telegram;
логирует свою работу и сообщает вам о важных проблемах сообщением в Telegram.

### Установка:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:juliana-str/api_final_yatube.git
```

```
cd api_final_yatube/
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
