import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

import config
from handlers import router

# Настройка расширенного логирования
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)

# Создаем логгер для детальной информации о работе бота
logger = logging.getLogger("telegram_bot")
logger.setLevel(config.LOG_LEVEL)

# Инициализация бота и диспетчера
# ParseMode.HTML позволяет использовать HTML-разметку в сообщениях
from aiogram.client.default import DefaultBotProperties
bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрация обработчиков сообщений
dp.include_router(router)

async def main() -> None:
    """
    Основная функция запуска бота
    """
    logging.info("=============================================")
    logging.info("Запуск бота...")
    logging.info(f"Уровень логирования: {config.LOG_LEVEL}")
    
    bot_info = await bot.get_me()
    logging.info(f"Бот запущен с именем: @{bot_info.username} ({bot_info.first_name})")
    
    # Удаление вебхука, если он был установлен ранее
    logging.info("Удаление старых вебхуков...")
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Вебхуки удалены")

    try:
        # Запуск процесса получения обновлений
        logging.info("Начинаем получать обновления...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        logging.exception("Подробная информация об ошибке:")
        sys.exit(1)
    finally:
        logging.info("Бот остановлен")
        logging.info("=============================================")

if __name__ == "__main__":
    try:
        logging.info("Запуск асинхронного цикла событий...")
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем (KeyboardInterrupt)")
    except Exception as e:
        logging.error(f"Непредвиденная ошибка: {e}")
        logging.exception("Подробная информация об ошибке:")