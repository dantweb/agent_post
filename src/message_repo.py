# src/message_repo.py

import os
import uuid
from typing import List

from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.message import Message

load_dotenv()

Base = declarative_base()
DB_URL = os.getenv('DATABASE_URL')

class MessageModel(Base):
    __tablename__ = 'messages'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    from_address = Column(String, nullable=False)
    to_address = Column(String, nullable=False)
    data = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)


class MessageRepository:
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = DB_URL
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save(self, message: Message):
        session = self.Session()
        try:
            # Normalize id
            if not message.id:
                message.id = str(uuid.uuid4())
            else:
                message.id = str(message.id)

            msg_model = MessageModel(
                id=message.id,
                from_address=message.from_address,
                to_address=message.to_address,
                data=message.data,
                created_at=message.created_at
            )
            session.add(msg_model)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def find_all(self):
        session = self.Session()
        try:
            models = session.query(MessageModel).all()
            messages = [
                Message(
                    id=m.id,
                    from_address=m.from_address,
                    to_address=m.to_address,
                    data=m.data,
                    created_at=m.created_at,
                )
                for m in models
            ]
            return messages
        finally:
            session.close()

    def get_messages_for_the_given_agents(self, agents_of_user: List[str]):
        session = self.Session()
        try:
            if not agents_of_user:
                return []

            # Filter only messages where from_address or to_address matches any of the agent addresses
            models = (
                session.query(MessageModel)
                .filter(
                    or_(
                        MessageModel.from_address.in_(agents_of_user),
                        MessageModel.to_address.in_(agents_of_user),
                    )
                )
                .order_by(MessageModel.created_at.asc())
                .all()
            )

            messages = [
                Message(
                    id=m.id,
                    from_address=m.from_address,
                    to_address=m.to_address,
                    data=m.data,
                    created_at=m.created_at,
                )
                for m in models
            ]

            return messages
        finally:
            session.close()

message_repo = MessageRepository()