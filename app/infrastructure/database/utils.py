from infrastructure.database.models import (
    Carts,
    Categories,
    engine,
    Products,
    Users,
)
from sqlalchemy import (
    DECIMAL,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


with Session(engine) as session:
    db_session = session


def db_register_user(full_name: str, chat_id: int) -> bool:
    try:
        query = Users(name=full_name, telegram=chat_id)
        db_session.add(query)
        db_session.commit()
        return False
    except IntegrityError:
        db_session.rollback()
        return True


def db_update_user(chat_id: int, phone: str):
    query = update(Users).where(Users.telegram == chat_id).values(phone=phone)
    db_session.execute(query)
    db_session.commit()


def db_create_user_cart(chat_id: int) -> bool:
    try:
        subquery = db_session.scalar(select(Users).where(Users.telegram == chat_id))
        query = Carts(user_id=subquery.id)
        db_session.add(query)
        db_session.commit()
        return True
    except IntegrityError:
        db_session.rollback()
    except AttributeError:
        db_session.rollback()


def db_get_all_category():
    return db_session.scalars(select(Categories))


def db_get_product(category_id: int):
    query = select(Products).where(Products.category_id == category_id)
    return db_session.scalars(query)


def db_get_product_by_id(product_id: int):
    query = select(Products).where(Products.id == product_id)
    return db_session.scalar(query)


def db_get_user_cart(chat_id: int):
    query = select(Carts.id).join(Users).where(Users.telegram == chat_id)
    return db_session.scalar(query)


def db_update_to_cart(price: DECIMAL, cart_id: int, quantity=1) -> None:
    query = (
        update(Carts)
        .where(Carts.id == cart_id)
        .values(total_price=price, total_products=quantity)
    )

    db_session.execute(query)
    db_session.commit()


def db_get_user_cart_by_chat_id(chat_id: int):
    query = select(Carts.id).join(Users).where(Users.telegram == chat_id)
    return db_session.scalars(query)
