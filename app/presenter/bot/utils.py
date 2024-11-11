def text_for_caption(name, description, price):
    text = f"<b>{name}</b>\n\n"
    text += f"<b>Ингридиенты: </b>{description}"
    text += f"<b>Цена: </b>{price} сум"

    return text
