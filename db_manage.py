import datetime
from sqlalchemy import String, Integer, Text, ForeignKey, select, update, delete, Boolean, TIMESTAMP, text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from config import DB_PASS, DB_NAME, DB_HOST, DB_USER

DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

engine = create_async_engine(url=DATABASE_URL)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'User'
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    telegram_id: Mapped[str] = mapped_column(primary_key=True, type_=String(45), nullable=False, unique=True)
    city: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    currency: Mapped[str] = mapped_column(String(45), nullable=False)
    language: Mapped[str] = mapped_column(String(45), nullable=False)
    is_blocked: Mapped[bool] = mapped_column(nullable=False, default=False)
    reserve_time_minute: Mapped[datetime.time] = mapped_column(nullable=False,
                                                               default=datetime.time(hour=0, minute=10, second=0))
    anti_sniper: Mapped[datetime.time] = mapped_column(nullable=False,
                                                       default=datetime.time(hour=0, minute=10, second=0))

    def __repr__(self):
        return f'<User {self.telegram_id}>'


class Lot(Base):
    __tablename__ = 'Lot'
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement=True)
    owner_telegram_id: Mapped[str] = mapped_column(ForeignKey('User.telegram_id'), nullable=False)
    bidder_telegram_id: Mapped[str] = mapped_column(String(45), nullable=True)
    last_bid: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    photo_id: Mapped[str] = mapped_column(String(255), nullable=True)
    video_id: Mapped[str] = mapped_column(String(255), nullable=True)
    start_price: Mapped[int] = mapped_column(Integer, nullable=False)
    price_steps: Mapped[str] = mapped_column(String(255), nullable=True)
    lot_time_living: Mapped[int] = mapped_column(Integer, nullable=False)
    bid_time: Mapped[str] = mapped_column(TIMESTAMP,
                                          server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    create_time: Mapped[str] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    lot_link: Mapped[str] = mapped_column(String(255), nullable=True)
    message_id: Mapped[str] = mapped_column(String(45), nullable=True)


async def add_new_user(telegram_id, language):
    async with async_session() as session:
        new_user = User
        stmt = insert(new_user).values(
            telegram_id=telegram_id,
            language=language
        ).on_duplicate_key_update(
            language=language
        ).prefix_with('IGNORE')
        await session.execute(stmt)
        await session.commit()


async def update_user_sql(telegram_id, **kwargs):
    async with async_session() as session:
        stmt = update(User).where(User.telegram_id == telegram_id).values(kwargs)
        await session.execute(stmt)
        await session.commit()


async def update_lot_sql(lot_id, **kwargs):
    async with async_session() as session:
        stmt = update(Lot).where(Lot.id == lot_id).values(kwargs)
        await session.execute(stmt)
        await session.commit()


async def create_lot(fsm_data, owner_id):
    async with async_session() as session:
        new_lot = Lot(
            owner_telegram_id=owner_id,
            description=fsm_data.get('description'),
            start_price=fsm_data.get('price'),
            lot_time_living=fsm_data.get('lot_time_living'),
            photo_id=fsm_data.get('photo'),
            video_id=fsm_data.get('video'),
            price_steps=fsm_data.get('price_steps')
        )
        session.add(new_lot)
        await session.commit()
        await session.refresh(new_lot)
        return str(new_lot.id)


async def get_lot(lot_id):
    async with async_session() as session:
        stmt = select(Lot).where(Lot.id == lot_id)
        execute = await session.execute(stmt)
        res = execute.fetchone()
        if res:
            return res[0]


async def get_user_lots(user_id):
    async with async_session() as session:
        stmt = select(Lot).where(Lot.owner_telegram_id == user_id)
        res = await session.execute(stmt)
        return res.fetchall()


async def delete_lot_sql(lot_id):
    async with async_session() as session:
        stmt = delete(Lot).where(Lot.id == lot_id)
        await session.execute(stmt)
        await session.commit()


async def make_bid_sql(lot_id, price, bidder_id):
    async with async_session() as session:
        stmt = update(Lot).where(Lot.id == lot_id).values(last_bid=price, bidder_telegram_id=bidder_id)
        await session.execute(stmt)
        await session.commit()


async def get_last_bid(lot_id):
    async with async_session() as session:
        stmt = select(Lot).where(Lot.id == lot_id)
        res = await session.execute(stmt)
        return res.fetchone()[0]


async def get_user(user_id):
    async with async_session() as session:
        stmt = select(User).where(User.telegram_id == user_id)
        res = await session.execute(stmt)
        return res.fetchone()[0]


async def on_startup(dp):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
