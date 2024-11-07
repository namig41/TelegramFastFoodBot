from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from infrastructure.database.utils import (
    db_get_all_category,
    gb_get_product,
)


def generate_category_menu() -> InlineKeyboardMarkup:
    categories = db_get_all_category()
    builder = InlineKeyboardBuilder()

    builder.button(text="Ваша корзина", callback_data="Ваша корзинка")
    [
        builder.button(
            text=category.category_name, callback_data=f"category_{category.id}",
        )
        for category in categories
    ]

    builder.adjust(1, 2)
    return builder.as_makrup()


def show_product_by_category(category_id: int) -> InlineKeyboardMarkup:
    products = gb_get_product(category_id)
    builder = InlineKeyboardBuilder()

    [
        builder.button(text=product.product_name, callback_data=f"product_{product.id}")
        for product in products
    ]

    builder.row(InlineKeyboardButton(text="Назад", callback_data="return_to_category"))

    builder.adjust(2)
    return builder.as_makrup()
