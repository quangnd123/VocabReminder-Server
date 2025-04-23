from sqlalchemy.ext.asyncio import (
    AsyncSession, create_async_engine
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import (
    Column, Integer, String, Text, BigInteger,
    ForeignKey, DateTime, PrimaryKeyConstraint
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy import select, insert

from datetime import datetime, timezone
from passlib.context import CryptContext
import uuid 


Base = declarative_base()

def gen_id():
    return str(uuid.uuid4())

class VerificationToken(Base):
    __tablename__ = "verification_token"
    identifier = Column(Text, nullable=False)
    expires = Column(DateTime(timezone=True), nullable=False)
    token = Column(Text, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('identifier', 'token'),
    )


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    email_verified = Column("emailVerified", DateTime(timezone=True), nullable=True)
    image = Column(Text, nullable=True)

    reading_languages = Column(ARRAY(String), default=list)
    learning_languages = Column(ARRAY(String), default=list)
    reminding_language = Column(String, nullable=True)
    free_llm = Column(String, nullable=True)
    unallowed_urls = Column(ARRAY(String), default=list)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column("userId", String, ForeignKey("users.id"), nullable=False)
    type = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)
    provider_account_id = Column("providerAccountId", String(255), nullable=False)
    refresh_token = Column(Text, nullable=True)
    access_token = Column(Text, nullable=True)
    expires_at = Column(BigInteger, nullable=True)
    id_token = Column(Text, nullable=True)
    scope = Column(Text, nullable=True)
    session_state = Column(Text, nullable=True)
    token_type = Column(Text, nullable=True)

    user = relationship("User", back_populates="accounts")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column("userId", String, ForeignKey("users.id"), nullable=False)
    expires = Column(DateTime(timezone=True), nullable=False)
    session_token = Column("sessionToken", String(255), nullable=False)

    user = relationship("User", back_populates="sessions")

class UserRemindersTextActivity(Base):
    __tablename__ = "user_text_reminders_activity"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column("userId", String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    sentences_num = Column(Integer, nullable=False)
    words_num = Column(Integer, nullable=False)
    related_words_num = Column(Integer, nullable=False)
    filter_related_words_num = Column(Integer, nullable=False)
    prompt_tokens_num = Column(Integer, nullable=False)
    completion_tokens_num = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=False)

class PostgreSQLDatabase:
    def __init__(self, db_url):
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # async def init_db(self):
    #     async with self.engine.begin() as conn:
    #         await conn.run_sync(Base.metadata.create_all)

    async def get_user_by_email(self, email: str):
        async with self.async_session() as session:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()

    async def update_user(self, user_id: str, **kwargs):
        async with self.async_session() as session:
            user = await session.get(User, user_id)
            if not user:
                return None

            for key, value in kwargs.items():
                setattr(user, key, value)

            await session.commit()
            await session.refresh(user)
            return user

    async def delete_user(self, user_id: str):
        async with self.async_session() as session:
            user = await session.get(User, user_id)
            if not user:
                return None

            await session.delete(user)
            await session.commit()
            return True

    async def track_user_reminders_text_activity(self, 
                                                 user_id: str, 
                                                 sentences_num: int,
                                                 words_num: int, 
                                                 related_words_num, 
                                                 filter_related_words_num: int, 
                                                 prompt_tokens_num: int,
                                                 completion_tokens_num: int,
                                                 response_time_ms):
        async with self.async_session() as session:
            user = await session.get(User, user_id)
            if not user:
                return None

            stmt = insert(UserRemindersTextActivity).values(
                user_id=user_id,
                sentences_num=sentences_num,
                words_num=words_num,
                related_words_num=related_words_num,
                filter_related_words_num=filter_related_words_num,
                prompt_tokens_num=prompt_tokens_num,
                completion_tokens_num=completion_tokens_num,
                response_time_ms=response_time_ms,
            )

            await session.execute(stmt)
            await session.commit()
            return True