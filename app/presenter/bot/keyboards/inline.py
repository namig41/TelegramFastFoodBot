from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from infrastructure.database.utils import (
    db_get_all_category,
    db_get_finally_price,
    db_get_product,
)


def generate_category_menu(chat_id: int) -> InlineKeyboardMarkup:
    categories = db_get_all_category()
    total_price = db_get_finally_price(chat_id)
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"Ваша корзина ({total_price if total_price else 0} сум)",
        callback_data="Ваша корзинка",
    )
    [
        builder.button(
            text=category.category_name,
            callback_data=f"category_{category.id}",
        )
        for category in categories
    ]

    builder.adjust(1, 2)
    return builder.as_markup()


def show_product_by_category(category_id: int) -> InlineKeyboardMarkup:
    products = db_get_product(category_id)
    builder = InlineKeyboardBuilder()

    [
        builder.button(text=product.product_name, callback_data=f"product_{product.id}")
        for product in products
    ]

    builder.row(InlineKeyboardButton(text="Назад", callback_data="return_to_category"))

    builder.adjust(2)
    return builder.as_markup()


def generate_constructor_button(quantity: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="-", callback_data="action -")
    builder.button(text=str(quantity), callback_data=str(quantity))
    builder.button(text="+", callback_data="action +")
    builder.button(text="Положить в корзину", callback_data="put into cart")

    builder.adjust(3, 1)

    return builder.as_markup()
