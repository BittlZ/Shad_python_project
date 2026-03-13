import pytest
from fastapi import status
from icecream import ic
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller

API_V1_URL_PREFIX = "/api/v1/books"


# Тест на ручку создающую книгу
@pytest.mark.asyncio()
async def test_create_book(db_session, async_client):
    seller = Seller(
        first_name="Тест",
        last_name="Продавец",
        e_mail="test@example.com",
        password="secret",
    )
    db_session.add(seller)
    await db_session.flush()

    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 2025,
        "seller_id": seller.id,
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_book_id = result_data.pop("id", None)
    assert resp_book_id is not None, "Book id not returned from endpoint"

    assert result_data == {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 2025,
        "seller_id": seller.id,
    }


@pytest.mark.asyncio()
async def test_create_book_without_seller_id(async_client):
    """Без seller_id создание книги не допускается."""
    data = {
        "title": "Clean Code",
        "author": "R. Martin",
        "count_pages": 200,
        "year": 2024,
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio()
async def test_create_book_with_old_year(db_session, async_client):
    seller = Seller(
        first_name="Тест",
        last_name="Продавец",
        e_mail="old@example.com",
        password="secret",
    )
    db_session.add(seller)
    await db_session.flush()

    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 1986,
        "seller_id": seller.id,
    }
    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Тест на ручку получения списка книг
@pytest.mark.asyncio()
async def test_get_books(db_session, async_client):
    # Создаем продавца и книги вручную, а не через ручку
    seller = Seller(
        first_name="Список",
        last_name="Книг",
        e_mail="list@test.com",
        password="x",
    )
    db_session.add(seller)
    await db_session.flush()
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2021, pages=104, seller_id=seller.id)
    book_2 = Book(author="Lermontov", title="Mziri", year=2021, pages=108, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["books"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2021,
                "id": book.id,
                "pages": 104,
                "seller_id": seller.id,
            },
            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 2021,
                "id": book_2.id,
                "pages": 108,
                "seller_id": seller.id,
            },
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio()
async def test_get_single_book(db_session, async_client):
    seller = Seller(
        first_name="Один",
        last_name="Продавец",
        e_mail="one@test.com",
        password="x",
    )
    db_session.add(seller)
    await db_session.flush()
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)
    book_2 = Book(author="Lermontov", title="Mziri", year=1997, pages=104, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "pages": 104,
        "id": book.id,
        "seller_id": seller.id,
    }


@pytest.mark.asyncio()
async def test_get_single_book_with_wrong_id(db_session, async_client):
    seller = Seller(first_name="X", last_name="X", e_mail="x@x.com", password="x")
    db_session.add(seller)
    await db_session.flush()
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/426548")

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Тест на ручку обновления книги
@pytest.mark.asyncio()
async def test_update_book(db_session, async_client):
    seller = Seller(
        first_name="Обнов",
        last_name="Книги",
        e_mail="upd@test.com",
        password="x",
    )
    db_session.add(seller)
    await db_session.flush()
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    data = {
        "title": "Mziri",
        "author": "Lermontov",
        "pages": 250,
        "year": 2024,
        "id": book.id,
        "seller_id": seller.id,
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{book.id}",
        json=data,
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Book, book.id)
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.pages == 250
    assert res.year == 2024
    assert res.seller_id == seller.id
    assert res.id == book.id


@pytest.mark.asyncio()
async def test_delete_book(db_session, async_client):
    seller = Seller(first_name="Del", last_name="Book", e_mail="del@test.com", password="x")
    db_session.add(seller)
    await db_session.flush()
    book = Book(author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()
    ic(book.id)

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    all_books = await db_session.execute(select(Book))
    res = all_books.scalars().all()

    assert len(res) == 0


@pytest.mark.asyncio()
async def test_delete_book_with_invalid_book_id(db_session, async_client):
    seller = Seller(first_name="X", last_name="X", e_mail="xx@test.com", password="x")
    db_session.add(seller)
    await db_session.flush()
    book = Book(author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{book.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
