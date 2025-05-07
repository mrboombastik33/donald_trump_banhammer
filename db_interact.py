from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from db_info.models import Chat, Admin

async def orm_add_chat(session: AsyncSession, data: dict):
    obj = Chat(
        id=data["id"],
        chat_name=data["chat_name"],
        chat_admins=[Admin(**admin_data) for admin_data in data["chat_admins"]],
        is_muted=False
    )
    session.add(obj)
    await session.commit()

async def orm_select_chats(session: AsyncSession):
    query = select(Chat).order_by(Chat.id)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_select_chat_id(session: AsyncSession, chat_id: int):
    query = select(Chat).where(Chat.id == chat_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def orm_check_mute(session: AsyncSession, chat_id: int):
    query = select(Chat.is_muted).where(Chat.id == chat_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def orm_update_chat_status(session: AsyncSession, chat_id: int):
    query = update(Chat).where(Chat.id == chat_id).values(is_muted=not Chat.is_muted)
    await session.execute(query)
    await session.commit()
