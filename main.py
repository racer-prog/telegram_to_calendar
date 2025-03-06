import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

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

# Добавляем handler для вывода в stdout, если его еще нет
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(handler)

async def main() -> None:
    """
    Основная функция запуска бота
    """
    try:
        logging.info("=============================================")
        logging.info("Инициализация бота...")
        logging.info(f"Уровень логирования: {config.LOG_LEVEL}")

        # Проверка наличия токена
        if not config.BOT_TOKEN:
            logging.error("Токен бота не найден в конфигурации!")
            sys.exit(1)

        # Инициализация бота и диспетчера
        logging.info("Создание экземпляра бота...")
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        logging.info("Создание диспетчера...")
        dp = Dispatcher()

        # Регистрация обработчиков
        logging.info("Регистрация обработчиков сообщений...")
        dp.include_router(router)

        # Получение информации о боте
        bot_info = await bot.get_me()
        logging.info(f"Бот успешно инициализирован: @{bot_info.username} ({bot_info.first_name})")

        # Удаление вебхука
        logging.info("Удаление старых вебхуков...")
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Вебхуки успешно удалены")

        # Запуск процесса получения обновлений
        logging.info("Запуск получения обновлений...")
        await dp.start_polling(bot)

    except Exception as e:
        logging.error(f"Критическая ошибка при запуске бота: {e}")
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
        logging.error(f"Непредвиденная ошибка в главном цикле: {e}")
        logging.exception("Подробная информация об ошибке:")
        sys.exit(1)