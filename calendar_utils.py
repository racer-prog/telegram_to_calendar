import caldav
import logging
import urllib3
import warnings
from datetime import datetime, timedelta
from config import CALDAV_URL, CALDAV_USERNAME, CALDAV_PASSWORD

# Отключение предупреждений о SSL верификации
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Отключение предупреждений от библиотеки caldav
logging.getLogger("caldav").setLevel(logging.ERROR)

class CalendarManager:
    def __init__(self):
        """Инициализация подключения к CalDAV серверу"""
        self.client = None
        self.principal = None
        self.calendar = None
        self.connected = False

        try:
            # Заголовки для CalDAV серверов
            headers = {
                "User-Agent": "CalendarBot/1.0",
                "Content-Type": "application/xml; charset=utf-8",
                "Accept": "application/xml",
                "Depth": "1"
            }

            logging.info(f"Подключение к CalDAV серверу: {CALDAV_URL}")

            # Определяем тип сервера и корректируем URL
            caldav_url = CALDAV_URL
            if "googleapis.com" in caldav_url:
                # Для Google Calendar
                if not caldav_url.endswith("/events"):
                    if caldav_url.endswith("/user"):
                        caldav_url = caldav_url.replace("/user", "/events")
                    elif not caldav_url.endswith("/events"):
                        caldav_url = caldav_url + "/events"
            elif "calendar.yandex.ru" in caldav_url:
                # Для Yandex Calendar
                # Yandex использует специфический формат URL для CalDAV
                caldav_url = f"https://caldav.yandex.ru/calendars/{CALDAV_USERNAME}/"
                logging.info(f"Переопределен URL для Yandex Calendar: {caldav_url}")
                headers = {
                    "Content-Type": "application/xml; charset=utf-8",
                    "Accept": "application/xml",
                    "Depth": "1",
                    "User-Agent": "Mozilla/5.0 CalendarBot/1.0"
                }

            logging.info(f"Используемый URL CalDAV: {caldav_url}")

            # Создаем клиент с учетом типа сервера
            if "calendar.yandex.ru" in caldav_url:
                # Для Yandex Calendar
                self.client = caldav.DAVClient(
                    url=caldav_url,
                    username=CALDAV_USERNAME,
                    password=CALDAV_PASSWORD,
                    ssl_verify_cert=False,
                    headers=headers
                )
            else:
                # Для других серверов
                self.client = caldav.DAVClient(
                    url=caldav_url,
                    username=CALDAV_USERNAME,
                    password=CALDAV_PASSWORD,
                    ssl_verify_cert=False,  # В продакшене этот параметр следует установить в True
                    headers=headers
                )

            # Пробуем получить информацию о пользователе
            self.principal = self.client.principal()
            logging.info(f"Получен principal: {self.principal}")

            # Получаем доступные календари
            calendars = self.principal.calendars()
            logging.info(f"Найдено календарей: {len(calendars)}")

            if calendars:
                # Получаем первый доступный календарь пользователя
                self.calendar = calendars[0]
                self.connected = True
                logging.info(f"Выбран календарь: {self.calendar}")
                logging.info("Подключение к CalDAV успешно установлено")
            else:
                logging.error("Нет доступных календарей")
        except Exception as e:
            logging.error(f"Ошибка при подключении к CalDAV серверу: {e}")
            # Не вызываем raise, чтобы бот продолжал работать

    async def add_event(self, summary: str, start_time: datetime, end_time: datetime = None) -> bool:
        """
        Добавление события в календарь

        :param summary: Название события
        :param start_time: Время начала события
        :param end_time: Время окончания события (по умолчанию +1 час от начала)
        :return: True если событие успешно добавлено
        """
        if not self.calendar:
            logging.error("Календарь не инициализирован")
            return False

        try:
            if not end_time:
                end_time = start_time + timedelta(hours=1)

            logging.info(f"Попытка создания события: {summary} (начало: {start_time}, конец: {end_time})")

            event = self.calendar.save_event(
                dtstart=start_time,
                dtend=end_time,
                summary=summary
            )

            # Проверяем, что событие действительно создалось
            events = self.calendar.date_search(
                start=start_time,
                end=end_time + timedelta(minutes=1)
            )

            for ev in events:
                if (hasattr(ev.vobject_instance.vevent, 'summary') and 
                    ev.vobject_instance.vevent.summary.value == summary):
                    logging.info(f"Событие успешно создано и найдено: {summary}")
                    return True

            logging.error(f"Событие создано, но не найдено при проверке: {summary}")
            return False

        except Exception as e:
            logging.error(f"Ошибка при создании события {summary}: {str(e)}")
            return False

    async def list_events(self, start_date: datetime = None, end_date: datetime = None) -> list:
        """
        Получение списка событий за указанный период

        :param start_date: Начальная дата (по умолчанию сегодня)
        :param end_date: Конечная дата (по умолчанию +7 дней)
        :return: Список событий
        """
        if not self.calendar:
            logging.error("Календарь не инициализирован")
            return []

        try:
            if not start_date:
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if not end_date:
                end_date = start_date + timedelta(days=7)

            logging.info(f"Запрос событий с {start_date} по {end_date}")
            events = self.calendar.date_search(start=start_date, end=end_date)

            result = []
            for event in events:
                if hasattr(event.vobject_instance.vevent, 'summary'):
                    event_data = {
                        'summary': event.vobject_instance.vevent.summary.value,
                        'start': event.vobject_instance.vevent.dtstart.value,
                        'end': event.vobject_instance.vevent.dtend.value
                    }
                    result.append(event_data)
                    logging.info(f"Найдено событие: {event_data['summary']} на {event_data['start']}")

            return result
        except Exception as e:
            logging.error(f"Ошибка при получении списка событий: {e}")
            return []