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
    db_get_product_by_id,
    db_register_user,
    db_update_user,
)

from presenter.bot.keyboards.inline import (
    generate_category_menu,
    show_product_by_category,
)
from presenter.bot.keyboards.reply import (
    generate_main_menu,
    share_phone_button,
)
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

    await show_main_menu(message)


@dp.message(F.text == "Сделать заказ")
async def make_order(message: types.Message):
    chat_id = message.chat.id

    await bot.send_message(chat_id=chat_id, text="Погнали", reply_markup="")
    await message.answer(text="Выберите катеогнию", reply_markup="")


async def show_main_menu(message: types.Message):

    await message.answer(text="Выберите направление", reply_markup=generate_main_menu())


@dp.message(F.text.regexp(r"^[а-я]+ [а-я]{4}"))
async def return_to_main_menu(message: types.Message):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

    await show_main_menu(message)


@dp.callback_query(F.data.regexp(r"category_[1-9]"))
async def show_product_button(call: types.CallbackQuery):

    chat_id = call.message.chat.id
    message_id = call.message.message_id

    category_id = int(call.data.split("_")[-1])

    await bot.edit_messaget_text(
        text="Выберите продукт",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=show_product_by_category(category_id),
    )


@dp.callback_query(F.data == "return_to_category")
async def return_to_category_button(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    await bot.edit(
        chat_id=chat_id,
        message_id=message_id,
        text="Выберите категорию",
        reply_markup=generate_category_menu(),
    )


@dp.callback_query(F.data.contains(r"product_"))
async def show_product_detail(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    product_id = int(call.data.split("-")[-1])
    db_get_product_by_id(product_id)

    await bot.delete_message(chat_id=chat_id, message_id=message_id)


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
