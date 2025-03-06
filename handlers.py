from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from datetime import datetime
import calendar_utils
import logging

# Инициализация роутера для обработки сообщений
router = Router()
calendar_manager = None

try:
    calendar_manager = calendar_utils.CalendarManager()
except Exception as e:
    logging.error(f"Ошибка при инициализации календаря: {e}")

@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    """
    Обработчик команды /start
    Отправляет приветственное сообщение и список возможностей бота
    """
    try:
        await message.answer(
            f"Привет, {hbold(message.from_user.full_name)}!\n"
            f"Я бот для работы с календарем. Вот что я умею:\n"
            f"- /events - Показать события на неделю\n"
            f"- /add_event [название] [дата] [время] - Добавить событие\n"
            f"- /help - Показать справку\n"
        )
    except Exception as e:
        await message.answer("Извините, произошла ошибка при обработке вашего запроса.")
        logging.error(f"Ошибка в обработчике start: {e}")

@router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """
    Обработчик команды /help
    Показывает список доступных команд
    """
    try:
        help_text = (
            "Доступные команды:\n"
            "/start - Запустить бота\n"
            "/help - Показать это сообщение помощи\n"
            "/events - Показать события на неделю\n"
            "/add_event [название] [дата] [время] - Добавить событие\n"
            "\nПример добавления события:\n"
            "/add_event Встреча 2024-03-07 15:00"
        )
        await message.answer(help_text)
    except Exception as e:
        await message.answer("Извините, произошла ошибка при показе справки.")
        logging.error(f"Ошибка в обработчике help: {e}")

@router.message(Command("events"))
async def command_events_handler(message: Message) -> None:
    """
    Обработчик команды /events
    Показывает список событий на ближайшую неделю
    """
    if not calendar_manager or not calendar_manager.connected:
        await message.answer("Извините, календарь в данный момент недоступен. Пожалуйста, проверьте настройки CalDAV или попробуйте позже.")
        return

    try:
        events = await calendar_manager.list_events()
        if not events:
            await message.answer("На ближайшую неделю событий не запланировано.")
            return

        response = "События на ближайшую неделю:\n\n"
        for event in events:
            start_time = event['start'].strftime("%d.%m.%Y %H:%M")
            response += f"📅 {event['summary']} - {start_time}\n"

        await message.answer(response)
    except Exception as e:
        await message.answer("Извините, произошла ошибка при получении списка событий.")
        logging.error(f"Ошибка в обработчике events: {e}")

@router.message(Command("add_event"))
async def command_add_event_handler(message: Message) -> None:
    """
    Обработчик команды /add_event
    Добавляет новое событие в календарь
    """
    if not calendar_manager or not calendar_manager.connected:
        await message.answer("Извините, календарь в данный момент недоступен. Пожалуйста, проверьте настройки CalDAV или попробуйте позже.")
        return

    try:
        # Парсинг аргументов команды
        args = message.text.split()[1:]  # Пропускаем саму команду
        if len(args) < 3:
            await message.answer(
                "Пожалуйста, укажите название события, дату и время.\n"
                "Пример: /add_event Встреча 2024-03-07 15:00"
            )
            return

        summary = args[0]
        try:
            start_time = datetime.strptime(f"{args[1]} {args[2]}", "%Y-%m-%d %H:%M")
        except ValueError:
            await message.answer(
                "Неверный формат даты или времени.\n"
                "Используйте формат: ГГГГ-ММ-ДД ЧЧ:ММ"
            )
            return

        # Добавление события в календарь
        success = await calendar_manager.add_event(summary, start_time)
        if success:
            await message.answer(f"Событие '{summary}' успешно добавлено в календарь.")
        else:
            await message.answer("Произошла ошибка при добавлении события в календарь. Пожалуйста, повторите попытку.")

    except Exception as e:
        await message.answer("Извините, произошла ошибка при добавлении события.")
        logging.error(f"Ошибка в обработчике add_event: {e}")
@router.message(F.text)
async def echo_handler(message: Message) -> None:
    """
    Обработчик текстовых сообщений
    Повторяет полученное сообщение обратно пользователю
    """
    try:
        await message.answer(
            f"Вы сказали: {message.text}"
        )
    except Exception as e:
        await message.answer("Извините, я не смог обработать ваше сообщение.")
        logging.error(f"Ошибка в обработчике echo: {e}")

@router.error()
async def error_handler(event, error) -> None:
    """
    Общий обработчик ошибок
    Логирует все непредвиденные ошибки
    """
    logging.error(f"Обновление: {event}")
    logging.error(f"Ошибка: {error}")