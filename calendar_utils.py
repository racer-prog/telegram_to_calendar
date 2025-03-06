import caldav
import logging
from datetime import datetime, timedelta
from config import CALDAV_URL, CALDAV_USERNAME, CALDAV_PASSWORD

class CalendarManager:
    def __init__(self):
        """Инициализация подключения к CalDAV серверу"""
        self.client = None
        self.principal = None
        self.calendar = None
        self.connected = False
        
        try:
            self.client = caldav.DAVClient(
                url=CALDAV_URL,
                username=CALDAV_USERNAME,
                password=CALDAV_PASSWORD,
                ssl_verify_cert=False  # Отключаем проверку SSL-сертификата (для отладки)
            )
            self.principal = self.client.principal()
            calendars = self.principal.calendars()
            
            if calendars:
                # Получаем первый доступный календарь пользователя
                self.calendar = calendars[0]
                self.connected = True
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
        try:
            if not end_time:
                end_time = start_time + timedelta(hours=1)
            
            event = self.calendar.save_event(
                dtstart=start_time,
                dtend=end_time,
                summary=summary
            )
            return True
        except Exception as e:
            logging.error(f"Ошибка при создании события: {e}")
            return False

    async def list_events(self, start_date: datetime = None, end_date: datetime = None) -> list:
        """
        Получение списка событий за указанный период
        
        :param start_date: Начальная дата (по умолчанию сегодня)
        :param end_date: Конечная дата (по умолчанию +7 дней)
        :return: Список событий
        """
        try:
            if not start_date:
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if not end_date:
                end_date = start_date + timedelta(days=7)

            events = self.calendar.date_search(start=start_date, end=end_date)
            return [
                {
                    'summary': event.vobject_instance.vevent.summary.value,
                    'start': event.vobject_instance.vevent.dtstart.value,
                    'end': event.vobject_instance.vevent.dtend.value
                }
                for event in events
            ]
        except Exception as e:
            logging.error(f"Ошибка при получении списка событий: {e}")
            return []
