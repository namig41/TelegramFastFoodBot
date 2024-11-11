from sqlalchemy import (
    BigInteger,
    create_engine,
    DECIMAL,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
)

from settings.config import config


DB_USER: str = config.DB_USER
DB_PASSWORD: str = config.DB_PASSWORD
DB_ADDRESS: str = config.DB_ADDRESS
DB_NAME: str = config.DB_NAME

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_NAME}",
)


class Base(DeclarativeBase):
    pass


class Users(Base):

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    name: Mapped[str] = mapped_column(String(50))
    telegram: Mapped[int] = mapped_column(BigInteger, unique=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)

    carts: Mapped["Carts"] = relationship("Carts", back_populates="user_cart")

    def __str__(self):
        return self.name


class Carts(Base):

    __tablename__ = "carts"
    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    total_price: Mapped[int] = mapped_column(DECIMAL(12, 2), default=0)
    total_products: Mapped[int] = mapped_column(default=0)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    user_cart: Mapped[Users] = relationship(back_populates="carts")
    finally_id: Mapped[int] = relationship("Finally_carts", back_populates="user_cart")

    def __str__(self):
        return str(self.id)


class Finally_carts(Base):

    __tablename__ = "finally_carts"
    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    product_name: Mapped[str] = mapped_column(String(50))
    final_price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2))
    quantity: Mapped[int]

    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    user_cart: Mapped[Carts] = relationship(back_populates="finally_id")

    __table_args__ = (UniqueConstraint("cart_id", "product_name"),)

    def __str__(self):
        return str(self.id)


class Categories(Base):

    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    category_name: Mapped[str] = mapped_column(String(20), unique=True)

    products: Mapped["Products"] = relationship(
        "Products",
        back_populates="product_category",
    )  # Исправлено на 'Products'

    def __str__(self):
        return self.category_name


class Products(Base):

    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)  # noqa: A003
    product_name: Mapped[str] = mapped_column(String(20), unique=True)
    description: Mapped[str]
    image: Mapped[str] = mapped_column(String(100))
    price: Mapped[DECIMAL] = mapped_column(DECIMAL(12, 2))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    product_category: Mapped[Categories] = relationship(
        "Categories",
        back_populates="products",
    )

    def __str__(self):
        return self.product_name


def main():
    Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)

    categories = ("Лаваши", "Донары", "Хот-Доги", "Десерты", "Соусы")

    products = (
        (
            1,
            "Мини лаваш",
            20000,
            "Мясо, тесто, помидоры",
            "app/resources/media/lavash/lavash_1.jpg",
        ),
        (
            1,
            "Мини говяжий",
            24000,
            "Мясо, тесто, помидоры",
            "app/resources/media/lavash/lavash_2.jpg",
        ),
        (
            1,
            "Мини с сыром",
            24000,
            "Мясо, тесто, помидоры",
            "app/resources/media/lavash/lavash_3.jpg",
        ),
        (
            2,
            "Гамбургер",
            18000,
            "Мясо, тесто, помидоры",
            "app/resources/media/donar/donar_1.jpg",
        ),
        (
            2,
            "Дамбургер",
            22000,
            "Мясо, тесто, помидоры",
            "app/resources/media/donar/donar_2.jpg",
        ),
        (
            2,
            "Чисбургер",
            19000,
            "Мясо, тесто, помидоры",
            "app/resources/media/donar/donar_3.jpg",
        ),
    )

    with Session(engine) as session:
        for category in categories:
            query = Categories(category_name=category)
            session.add(query)
            session.commit()

        for product in products:
            query = Products(
                category_id=product[0],
                product_name=product[1],
                price=product[2],
                description=product[3],
                image=product[4],
            )
            session.add(query)
            session.commit()


if __name__ == "__main__":
    main()
