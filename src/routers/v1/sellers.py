from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.schemas import (
    IncomingSeller,
    ReturnedAllSellers,
    ReturnedSeller,
    ReturnedSellerWithBooks,
    UpdateSeller,
)
from src.services import SellerService

sellers_router = APIRouter(prefix="/seller", tags=["sellers"])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(payload: IncomingSeller, session: DBSession):
    new_seller = await SellerService(session).add_seller(payload)
    return new_seller


@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    sellers = await SellerService(session).get_all_sellers()
    return {"sellers": sellers}


@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller_by_id(seller_id: int, session: DBSession):
    seller = await SellerService(session).get_seller_with_books(seller_id)
    if seller is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return seller


@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, payload: UpdateSeller, session: DBSession):
    seller = await SellerService(session).update_seller(seller_id, payload)
    if seller is None:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return seller


@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    deleted = await SellerService(session).delete_seller(seller_id)
    if not deleted:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
