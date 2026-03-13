"""Тесты эндпоинтов продавцов. Данные создаём через ORM, чтобы не зависеть от POST-ручки."""

import pytest
from fastapi import status

from src.models.books import Book
from src.models.sellers import Seller

API_V1_SELLER_PREFIX = "/api/v1/seller"


@pytest.mark.asyncio()
async def test_create_seller(async_client):
    data = {
        "first_name": "Иван",
        "last_name": "Петров",
        "e_mail": "ivan@example.com",
        "password": "secret123",
    }
    response = await async_client.post(f"{API_V1_SELLER_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert "id" in result
    assert result["first_name"] == "Иван"
    assert result["last_name"] == "Петров"
    assert result["e_mail"] == "ivan@example.com"
    assert "password" not in result, "Поле password не должно возвращаться в ответе"


@pytest.mark.asyncio()
async def test_get_all_sellers(db_session, async_client):
    seller1 = Seller(
        first_name="Анна",
        last_name="Сидорова",
        e_mail="anna@test.com",
        password="pwd1",
    )
    seller2 = Seller(
        first_name="Борис",
        last_name="Козлов",
        e_mail="boris@test.com",
        password="pwd2",
    )
    db_session.add_all([seller1, seller2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_SELLER_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "sellers" in data
    assert len(data["sellers"]) == 2
    for seller in data["sellers"]:
        assert "password" not in seller, "В списке продавцов не должно быть поля password"
    ids = {s["id"] for s in data["sellers"]}
    assert ids == {seller1.id, seller2.id}


@pytest.mark.asyncio()
async def test_get_seller_by_id(db_session, async_client):
    seller = Seller(
        first_name="Мария",
        last_name="Иванова",
        e_mail="maria@example.com",
        password="hidden",
    )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_SELLER_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["id"] == seller.id
    assert result["first_name"] == "Мария"
    assert result["last_name"] == "Иванова"
    assert result["e_mail"] == "maria@example.com"
    assert "password" not in result, "При просмотре продавца password не должен возвращаться"
    assert "books" in result
    assert result["books"] == []


@pytest.mark.asyncio()
async def test_get_seller_by_id_with_books(db_session, async_client):
    seller = Seller(
        first_name="Олег",
        last_name="Книжников",
        e_mail="oleg@books.com",
        password="secret",
    )
    db_session.add(seller)
    await db_session.flush()
    book1 = Book(
        title="Первый том",
        author="Автор",
        year=2023,
        pages=100,
        seller_id=seller.id,
    )
    book2 = Book(
        title="Второй том",
        author="Автор",
        year=2024,
        pages=200,
        seller_id=seller.id,
    )
    db_session.add_all([book1, book2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_SELLER_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["id"] == seller.id
    assert "password" not in result
    assert len(result["books"]) == 2
    titles = {b["title"] for b in result["books"]}
    assert titles == {"Первый том", "Второй том"}
    for b in result["books"]:
        assert b["seller_id"] == seller.id


@pytest.mark.asyncio()
async def test_get_seller_by_id_not_found(db_session, async_client):
    seller = Seller(
        first_name="Х",
        last_name="Х",
        e_mail="x@x.com",
        password="x",
    )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_SELLER_PREFIX}/{seller.id + 999}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):
    seller = Seller(
        first_name="Старое",
        last_name="Имя",
        e_mail="old@mail.com",
        password="dontchange",
    )
    db_session.add(seller)
    await db_session.flush()

    data = {
        "first_name": "Новое",
        "last_name": "Фамилия",
        "e_mail": "new@mail.com",
    }
    response = await async_client.put(f"{API_V1_SELLER_PREFIX}/{seller.id}", json=data)

    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result["first_name"] == "Новое"
    assert result["last_name"] == "Фамилия"
    assert result["e_mail"] == "new@mail.com"
    assert "password" not in result


@pytest.mark.asyncio()
async def test_update_seller_not_found(async_client):
    data = {
        "first_name": "Н",
        "last_name": "Ф",
        "e_mail": "n@f.com",
    }
    response = await async_client.put(f"{API_V1_SELLER_PREFIX}/99999", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_delete_seller(db_session, async_client):
    seller = Seller(
        first_name="На",
        last_name="Удаление",
        e_mail="del@me.com",
        password="x",
    )
    db_session.add(seller)
    await db_session.flush()
    sid = seller.id

    response = await async_client.delete(f"{API_V1_SELLER_PREFIX}/{sid}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()
    deleted = await db_session.get(Seller, sid)
    assert deleted is None


@pytest.mark.asyncio()
async def test_delete_seller_cascades_books(db_session, async_client):
    seller = Seller(
        first_name="С",
        last_name="Книгами",
        e_mail="with@books.com",
        password="x",
    )
    db_session.add(seller)
    await db_session.flush()
    book = Book(
        title="Книга продавца",
        author="Автор",
        year=2024,
        pages=50,
        seller_id=seller.id,
    )
    db_session.add(book)
    await db_session.flush()
    bid, sid = book.id, seller.id

    response = await async_client.delete(f"{API_V1_SELLER_PREFIX}/{sid}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()
    assert await db_session.get(Seller, sid) is None
    assert await db_session.get(Book, bid) is None, "Книги продавца должны удаляться каскадно"


@pytest.mark.asyncio()
async def test_delete_seller_not_found(async_client):
    response = await async_client.delete(f"{API_V1_SELLER_PREFIX}/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
