from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

from src.message import Message

Base = declarative_base()


class MessageModel(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    collected_at = Column(DateTime)
    delivered_at = Column(DateTime)
    from_address = Column(String)
    to_address = Column(String)
    data = Column(String)


class MessageRepository:
    def __init__(self, db_url: str = None):
        self.engine = create_engine(db_url or 'sqlite:///:memory:')  # Use in-memory SQLite if no URL provided
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save(self, message: Message) -> None:
        session = self.Session()
        try:
            message_model = MessageModel(**message.__dict__)  # convert from Message to MessageModel
            session.add(message_model)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error saving message: {e}")
        finally:
            session.close()

    def find_all(self) -> list[Message]:
        session = self.Session()
        try:
            messages = session.query(MessageModel).all()
            return [Message(**msg.__dict__) for msg in messages]  # convert from MessageModel to Message
        except SQLAlchemyError as e:
            raise Exception(f"Error retrieving messages: {e}")
        finally:
            session.close()

    def delete(self, message: Message) -> None:
        session = self.Session()
        try:
            message_model = session.query(MessageModel).filter_by(id=message.id).first()
            if message_model:
                session.delete(message_model)
                session.commit()
            else:
                raise Exception("Message not found")
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error deleting message: {e}")
        finally:
            session.close()

    def find_by_address(self, address: str) -> list[Message]:
        session = self.Session()
        try:
            messages = session.query(MessageModel).filter(
                (MessageModel.from_address.like(f'%{address}%')) |
                (MessageModel.to_address.like(f'%{address}%'))
            ).all()
            return [Message(**msg.__dict__) for msg in messages]
        except SQLAlchemyError as e:
            raise Exception(f"Error retrieving messages: {e}")
        finally:
            session.close()
