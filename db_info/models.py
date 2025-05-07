from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, DeclarativeBase
from sqlalchemy import Integer, Column, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    ...

class Chat(Base):
    __tablename__ = 'chat'
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_name: Mapped[str] = mapped_column(String(20), nullable=False)
    chat_admins: Mapped[list["Admin"]] = relationship(back_populates="chat", lazy="selectin")  # Має співпадати з Admin.chat в back_populates
    is_muted: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        info = f'<ID чату: {self.id}, Посилання на табличку адімнів: {self.chat_admins}>'
        return info


class Admin(Base):
    __tablename__ = 'admins'
    admin_id: Mapped[int] = mapped_column(primary_key=True)
    admin_tag: Mapped[str] = mapped_column(nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    chat: Mapped["Chat"] = relationship(back_populates="chat_admins")  # ✅ Має співпадати з chat_admins в Chat.chat_admins

    def __repr__(self):
        return f'ID адміна: {self.admin_id} ID його чату: {self.chat_id}'


'''Use-Case:
1. Зберігати дані про чати і стан бота
2. Тегати адмінів через БД (по можлиовсті))
'''






