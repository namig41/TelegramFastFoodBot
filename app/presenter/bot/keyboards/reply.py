from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder,
    ReplyKeyboardMarkup,
)


def share_phone_button() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Отправить свой контакт", request_contact=True)

    return builder.as_markup(resize_keyboard=True)
