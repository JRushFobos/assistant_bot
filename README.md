# Assitant bot
Бот-асситент для проверки статуса домашней работы на код ревью в Яндекс.Практикум

Каждые 10 минут проверять статус вашей домашней работы.
Если работа проверена вы получите сообщение о статусе вашего код ревью.

Бот работает с api Практикум.Домашка через https://practicum.yandex.ru/api/user_api/homework_statuses/

### Статусы работ
- работа принята на проверку
- работа возвращена для исправления ошибок
- работа принята

### 1. Токен
Для работы бота нужно получить токен, получем через Url
https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a

### 2. Запуск бота
2.1. Клонируем проект:

```bash
git clone https://github.com/JRushFobos/assistant_bot.git
```

или

```bash
git clone git@github.com:JRushFobos/assistant_bot.git
```

2.2. Переходим в папку с ботом.

```bash
cd assistant_bot
```

2.3. Устанавливаем виртуальное окружение

```bash
python -m venv venv
```

2.4. Активируем виртуальное окружение

```bash
source venv/Scripts/activate
```

2.5. Устанавливаем зависимости

```bash
pip install -r requirements.txt
```

2.6. В консоле импортируем токены для ЯндексюПрактикум и для Телеграмм:

```bash
export PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
export TELEGRAM_TOKEN=<TELEGRAM_TOKEN>
export CHAT_ID=<CHAT_ID>
```

2.6. Запускаем бота

```bash
python homework.py
```

### Об авторе
Мокрушин Евгений [@JRushFobos](https://github.com/JRushFobos)