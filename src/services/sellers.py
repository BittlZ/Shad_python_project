__all__ = ["SellerService"]

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.sellers import Seller
from src.schemas.sellers import IncomingSeller, UpdateSeller


class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_seller(self, payload: IncomingSeller) -> Seller:
        new_seller = Seller(
            first_name=payload.first_name,
            last_name=payload.last_name,
            e_mail=payload.e_mail,
            password=payload.password,
        )
        self.session.add(new_seller)
        await self.session.flush()
        return new_seller

    async def get_all_sellers(self) -> list[Seller]:
        query = select(Seller)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_seller_by_id(self, seller_id: int) -> Seller | None:
        return await self.session.get(Seller, seller_id)

    async def get_seller_with_books(self, seller_id: int) -> Seller | None:
        """Продавец с подгруженным списком книг (для GET по id)."""
        query = select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def update_seller(self, seller_id: int, payload: UpdateSeller) -> Seller | None:
        if seller := await self.session.get(Seller, seller_id):
            seller.first_name = payload.first_name
            seller.last_name = payload.last_name
            seller.e_mail = payload.e_mail
            await self.session.flush()
            return seller
        return None

    async def delete_seller(self, seller_id: int) -> bool:
        if seller := await self.session.get(Seller, seller_id):
            await self.session.delete(seller)
            return True
        return False
