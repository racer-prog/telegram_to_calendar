from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold

# Инициализация роутера для обработки сообщений
router = Router()

@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    """
    Обработчик команды /start
    Отправляет приветственное сообщение и список возможностей бота
    """
    try:
        await message.answer(
            f"Привет, {hbold(message.from_user.full_name)}!\n"
            f"Я простой Telegram бот. Вот что я умею:\n"
            f"- Повторять ваши сообщения\n"
            f"- Отвечать на команду /help\n"
            f"Отправьте мне любое сообщение!"
        )
    except Exception as e:
        await message.answer("Извините, произошла ошибка при обработке вашего запроса.")
        # Логирование ошибки
        print(f"Ошибка в обработчике start: {e}")

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
            "\nТакже вы можете отправить любое сообщение, и я повторю его!"
        )
        await message.answer(help_text)
    except Exception as e:
        await message.answer("Извините, произошла ошибка при показе справки.")
        print(f"Ошибка в обработчике help: {e}")

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
        print(f"Ошибка в обработчике echo: {e}")

@router.error()
async def error_handler(event, error) -> None:
    """
    Общий обработчик ошибок
    Логирует все непредвиденные ошибки
    """
    print(f"Обновление: {event}")
    print(f"Ошибка: {error}")