import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Конфигурация бота
# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# Настройка CalDAV
CALDAV_URL = os.getenv("CALDAV_URL")
CALDAV_USERNAME = os.getenv("CALDAV_USERNAME")
CALDAV_PASSWORD = os.getenv("CALDAV_PASSWORD")

# Проверка наличия необходимых переменных окружения для CalDAV
if not all([CALDAV_URL, CALDAV_USERNAME, CALDAV_PASSWORD]):
    raise ValueError("Не установлены необходимые переменные окружения для CalDAV")

# Настройка уровня логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")