from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import NoResultFound

from .models import User
from .schemas import UserCreateModel
from .utils import generate_password_hash, verify_password


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        try:
            statement = select(User).where(User.email == email)
            result = await session.exec(statement)
            user = result.one()
            return user
        except NoResultFound:
            return None

    async def user_exists(self, email, session: AsyncSession):
        user = await self.get_user_by_email(email, session)

        return True if user is not None else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password_hash(user_data_dict["password"])
        session.add(new_user)
        await session.commit()
        # await session.refresh(new_user)
        return new_user
