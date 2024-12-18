import asyncio
import logging

from aiogram import (
    Bot,
    Dispatcher,
    F,
    types,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from infrastructure.database.utils import (
    db_clear_finally_cart,
    db_create_user_cart,
    db_delete_product,
    db_get_product_by_id,
    db_get_product_by_name,
    db_get_user_cart,
    db_get_user_info,
    db_ins_or_upd_finally_cart,
    db_register_user,
    db_update_to_cart,
    db_update_user,
)

from presenter.bot.keyboards.inline import (
    generate_category_menu,
    generate_constructor_button,
    generate_delete_product,
    show_product_by_category,
)
from presenter.bot.keyboards.reply import (
    back_arrow_button,
    back_to_main_menu,
    generate_main_menu,
    share_phone_button,
)
from presenter.bot.utils import (
    counting_products_from_cart,
    text_for_caption,
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
    chat_id = message.chat.id

    await bot.send_message(
        chat_id=chat_id,
        text="Погнали",
        reply_markup=back_to_main_menu(),
    )
    await message.answer(
        text="Выберите категорию",
        reply_markup=generate_category_menu(chat_id),
    )


@dp.message(F.text == "Корзина")
async def show_carts(message: types.Message):
    message_id = message.message_id
    chat_id = message.chat.id
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    context = counting_products_from_cart(chat_id, "Ваша корзина")
    if context:
        count, text, *_ = context
        await bot.send_message(
            chat_id=chat_id, text=text, reply_markup=generate_delete_product(chat_id),
        )
    else:
        await bot.send_message(chat_id=chat_id, text="Ваша корзина пуста")
        await make_order(message)


@dp.message(F.text == "Главное меню")
async def show_main_menu(message: types.Message):
    await message.answer(text="Выберите направление", reply_markup=generate_main_menu())


@dp.message(F.text.regexp(r"^[а-я]+ [а-я]{4}"))
async def return_to_main_menu(message: types.Message):
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1,
        )
    except TelegramBadRequest:
        pass

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
        reply_markup=generate_category_menu(chat_id),
    )


@dp.callback_query(F.data.contains(r"product_"))
async def show_product_detail(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    product_id = int(call.data.split("_")[-1])
    product = db_get_product_by_id(product_id)

    await bot.delete_message(chat_id=chat_id, message_id=message_id)

    if user_cart := db_get_user_cart(chat_id):
        db_update_to_cart(price=product.price, cart_id=user_cart.id)

        text = text_for_caption(
            product.product_name,
            product.description,
            product.price,
        )

        await bot.send_message(
            chat_id=chat_id,
            text="Выберите модификатор",
            reply_markup=back_arrow_button(),
        )

        await bot.send_photo(
            chat_id=chat_id,
            photo=types.FSInputFile(path=product.image),
            caption=text,
            reply_markup=generate_constructor_button(),
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text="К сожалению у нас нет вашего контакта",
            reply_markup=share_phone_button(),
        )


@dp.message(F.text == "Назад")
async def return_to_category_menu(message: types.Message):
    try:
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1,
        )
    except TelegramBadRequest:
        pass
    await make_order(message)


@dp.callback_query(F.data.regexp(r"action [+-]"))
async def constructor_change(call: types.CallbackQuery):
    chat_id = call.from_user.id
    message_id = call.message.message_id
    action = call.data.split()[-1]
    product_name = call.message.caption.split("\n")[0]
    user_cart = db_get_user_cart(chat_id)
    product = db_get_product_by_name(product_name)
    product_price = product.price

    match action:
        case "+":
            user_cart.total_products += 1
            product_price = product_price * user_cart.total_products
            db_update_to_cart(
                price=product_price,
                quantity=user_cart.total_products,
                cart_id=user_cart.id,
            )
        case "-":
            if user_cart.total_products < 2:
                await call.answer("Меньше одного нельзя")
            else:
                user_cart.total_products -= 1
                product_price = product_price * user_cart.total_products
                db_update_to_cart(
                    price=product_price,
                    quantity=user_cart.total_products,
                    cart_id=user_cart.id,
                )

    text = text_for_caption(
        name=product_name,
        description=product.description,
        price=product_price,
    )

    try:
        await bot.edit_message_media(
            chat_id=chat_id,
            message_id=message_id,
            media=types.InputMediaPhoto(
                media=types.FSInputFile(path=product.image),
                caption=text,
            ),
            reply_markup=generate_constructor_button(user_cart.total_products),
        )
    except TelegramBadRequest:
        pass


@dp.callback_query(F.data == "put into cart")
async def put_into_cart(call: types.CallbackQuery):
    chat_id = call.from_user.id
    product_name = call.message.caption.split("\n")[0]
    cart = db_get_user_cart(chat_id)

    await bot.delete_message(
        chat_id=chat_id,
        message_id=call.message.message_id,
    )

    if db_ins_or_upd_finally_cart(
        cart_id=cart.id,
        product_name=product_name,
        total_products=cart.total_products,
        total_price=cart.total_price,
    ):
        await bot.send_message(chat_id=chat_id, text="Продукт успешно добавлен")
    else:
        await bot.send_message(chat_id=chat_id, text="Количество успешно изменено")

    await return_to_category_menu(call.message)


@dp.callback_query(F.data == "Ваша корзина")
async def show_finally_cart(call: types.CallbackQuery):
    message_id = call.message.message_id
    chat_id = call.from_user.id
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    context = counting_products_from_cart(chat_id, "Ваша корзина")
    if context:
        count, text, *_ = context
        await bot.send_message(
            chat_id=chat_id, text=text, reply_markup=generate_delete_product(chat_id),
        )
    else:
        await bot.send_message(chat_id=chat_id, text="Ваша корзина пуста")
        await make_order(call.message)


@dp.callback_query(F.data.regexp(r"delete_\d+"))
async def delete_cart_product(call: types.CallbackQuery):
    call.from_user.id

    finally_id = int(call.data.split("_")[-1])
    db_delete_product(finally_id)
    await bot.answer_callback_query(callback_query_id=call.id, text="Продукт удален!")
    await show_finally_cart(call)


@dp.callback_query(F.data == "order_pay")
async def create_order(call: types.CallbackQuery):
    chat_id = call.from_user.id
    message_id = call.message.message_id
    await bot.delete_message(chat_id=chat_id, message_id=message_id)

    count, text, total_price, cart_id = counting_products_from_cart(
        chat_id=chat_id, user_text="Итоговый список для оплаты",
    )
    text += "\nДоставка по городу 1000 сум"

    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="Ваш заказ",
        description=text,
        payload="bot-defined invoice payload",
        provider_token=config.PAYMENT_TOKEN,
        currency="RUB",
        prices=[
            types.LabeledPrice(label="Общая стоимость", amount=int(total_price)),
            types.LabeledPrice(label="Доставка", amount=int(total_price)),
        ],
    )

    await bot.send_message(chat_id=chat_id, text="Заказ оплачен")
    await sending_report_to_manager(chat_id, text)
    db_clear_finally_cart(chat_id)


async def sending_report_to_manager(chat_id: int, text: str):
    user = db_get_user_info(chat_id)
    text += f"\n\n<b>Имя заказчика: {user.name}\nКонтакт: {user.phone}</b>\n\n"
    await bot.send_message(chat_id=config.MANAGER_ID, text=text)


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
