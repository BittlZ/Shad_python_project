from pydantic import BaseModel, ConfigDict, EmailStr

from .books import ReturnedBook

__all__ = [
    "BaseSeller",
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedSellerWithBooks",
    "ReturnedAllSellers",
    "UpdateSeller",
]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr


class IncomingSeller(BaseSeller):
    password: str


# Ответ API: без пароля (безопасность). from_attributes для сериализации из ORM.
class ReturnedSeller(BaseSeller):
    model_config = ConfigDict(from_attributes=True)
    id: int


class UpdateSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr


# Один продавец с полным списком его книг (GET by id).
class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBook] = []


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]
