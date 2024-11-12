from infrastructure.database.utils import db_get_finally_cart_products


def text_for_caption(name, description, price):
    text = f"<b>{name}</b>\n\n"
    text += f"<b>Ингридиенты: </b>{description}"
    text += f"<b>Цена: </b>{price} сум"

    return text


def counting_products_from_cart(chat_id, user_text):
    products = db_get_finally_cart_products(chat_id)
    if products:
        text = f"{user_text}\n\n"
        total_products = 0
        total_price = 0
        count = 0

        for name, quantity, price, cart_id in products:
            count += 1
            total_products += quantity
            total_price += price
            text += f"{count}. {name}\nКоличество: {quantity}\nСтоимость: {price}\n\n"

        text += f"Общее количество продуктов: {total_products}\nОбщая стоимость корзины: {total_price}"

        return count, text, total_price, cart_id
