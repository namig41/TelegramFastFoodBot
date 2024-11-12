from pydantic_settings import BaseSettings


class Config(BaseSettings):
    TELEGRAM_TOKEN: str
    PAYMENT_TOKEN: str
    MANAGER_ID: int
    DB_USER: str
    DB_PASSWORD: str
    DB_ADDRESS: str
    DB_NAME: str


config = Config()
