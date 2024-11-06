import asyncio
import logging

from aiogram import (
    Bot,
    Dispatcher,
    F,
    types,
)
from aiogram.filters.command import Command
from infrastructure.database.utils import (
    db_create_user_cart,
    db_register_user,
    db_update_user,
)

from presenter.bot.keyboards.reply import share_phone_button
from settings.config import config


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.TELEGRAM_TOKEN)
# Диспетчер
dp = Dispatcher()


# Хэндлер на команду /start
@dp.message(Command("start"))
async def command_start(message: types.Message):
    await message.answer(f"Здравствуйте, {message.from_user.full_name}!")

    await start_register_user(message)


async def start_register_user(message: types.Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name

    if db_register_user(full_name, chat_id):
        await message.answer(text="Авторизация прошла успешно")
        # TODO: Показать меню
    else:
        await message.answer(
            text="Для связи с Вами нам нужен Ваш контактный номер",
            reply_markup=share_phone_button(),
        )


@dp.message(F.contact)
async def update_user_info_finish_register(message: types.Message):
    chat_id = message.chat.id
    phone = message.contact.phone_number
    db_update_user(chat_id, phone)

    if db_create_user_cart(chat_id):
        await message.answer(text="Регистрация прошла успешно")


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
