import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

import config
from handlers import router

# Настройка логирования
logging.basicConfig(level=config.LOG_LEVEL,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   stream=sys.stdout)

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
    logging.info("Запуск бота...")

    # Удаление вебхука, если он был установлен ранее
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        # Запуск процесса получения обновлений
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        sys.exit(1)
    finally:
        logging.info("Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"Непредвиденная ошибка: {e}")