import asyncio
import logging

from aiogram import (
    Bot,
    Dispatcher,
    F,
    types,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from infrastructure.database.utils import (
    db_create_user_cart,
    db_get_product_by_id,
    db_get_user_cart,
    db_get_user_cart_by_chat_id,
    db_register_user,
    db_update_to_cart,
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
bot = Bot(token=config.TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
# Диспетчер
dp = Dispatcher()


# Хэндлер на команду /start
@dp.message(CommandStart())
async def command_start(message: types.Message):
    await message.answer(f"Здравствуйте, {message.from_user.full_name}!")

    await start_register_user(message)


async def start_register_user(message: types.Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name

    if db_register_user(full_name, chat_id):
        await message.answer(text="Авторизация прошла успешно")
        await show_main_menu(message)
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
    message.chat.id

    # await bot.send_message(chat_id=chat_id, text="Погнали", reply_markup='')
    await message.answer(
        text="Выберите категорию", reply_markup=generate_category_menu(),
    )


@dp.message(F.text == "Корзина")
async def show_carts(message: types.Message):
    chat_id = message.chat.id

    db_get_user_cart_by_chat_id(chat_id)

    # await bot.send_message(chat_id=chat_id,
    #                     text='')


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
    await bot.edit_message_text(
        text="Выберите продукт",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=show_product_by_category(category_id),
    )


@dp.callback_query(F.data == "return_to_category")
async def return_to_category_button(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="Выберите категорию",
        reply_markup=generate_category_menu(),
    )


@dp.callback_query(F.data.contains(r"product_"))
async def show_product_detail(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    product_id = int(call.data.split("_")[-1])
    product = db_get_product_by_id(product_id)

    await bot.delete_message(chat_id=chat_id, message_id=message_id)

    if user_cart_id := db_get_user_cart(chat_id):
        db_update_to_cart(price=product.price, cart_id=user_cart_id)

        text = f"<b> {product.product_name} </b>\n\n"
        text += f"<b> Ингредиенты: </b> {product.description}\n"
        text += f"<b> Цена: </b> {product.price} сумм"

        await bot.send_photo(
            chat_id=chat_id, photo=types.FSInputFile(path=product.image), caption=text,
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text="К сожалению у нас нет вашего контакта",
            reply_markup=share_phone_button(),
        )


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
