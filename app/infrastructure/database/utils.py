from typing import Iterable

from infrastructure.database.models import (
    Carts,
    Categories,
    engine,
    Finally_carts,
    Products,
    Users,
)
from sqlalchemy import (
    DECIMAL,
    delete,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import sum  # noqa: A004


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
    query = select(Carts).join(Users).where(Users.telegram == chat_id)
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


def db_get_product_by_name(product_name: str) -> Products:
    query = select(Products).where(Products.product_name == product_name)
    return db_session.scalar(query)


def db_ins_or_upd_finally_cart(cart_id, product_name, total_products, total_price):
    try:
        query = Finally_carts(
            cart_id=cart_id,
            product_name=product_name,
            quantity=total_products,
            final_price=total_price,
        )
        db_session.add(query)
        db_session.commit()
        return True
    except IntegrityError:
        db_session.rollback()
        query = (
            update(Finally_carts)
            .where(
                Finally_carts.product_name == product_name,
            )
            .where(
                Finally_carts.cart_id == cart_id,
            )
            .values(quantity=total_products, final_price=total_price)
        )
        db_session.execute(query)
        db_session.commit()
        return False


def db_get_finally_price(chat_id: int) -> DECIMAL:
    query = (
        select(sum(Finally_carts.final_price))
        .join(Carts)
        .join(Users)
        .where(Users.telegram == chat_id)
    )
    return db_session.execute(query).fetchone()[0]


def db_get_finally_cart_products(chat_id: int) -> Iterable:
    query = (
        select(
            Finally_carts.product_name,
            Finally_carts.quantity,
            Finally_carts.final_price,
            Finally_carts.cart_id,
        )
        .join(Carts)
        .join(Users)
        .where(Users.telegram == chat_id)
    )
    return db_session.execute(query).fetchall()


def db_get_product_for_delete(chat_id: int) -> Iterable:
    query = (
        select(Finally_carts.id, Finally_carts.product_name)
        .join(Carts)
        .join(Users)
        .where(Users.telegram == chat_id)
    )
    return db_session.execute(query).fetchall()


def db_delete_product(finally_id: int) -> None:
    query = delete(Finally_carts).where(Finally_carts.id == finally_id)
    db_session.execute(query)
    db_session.commit()


def db_get_user_info(chat_id: int) -> Users:
    query = select(Users).where(Users.telegram == chat_id)
    return db_session.scalar(query)


def db_clear_finally_cart(cart_id: int) -> None:
    query = delete(Finally_carts).where(Finally_carts == cart_id)
    db_session.execte(query)
    db_session.commit()
