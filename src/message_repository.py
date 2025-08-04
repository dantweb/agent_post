from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from message import Message

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
            # Create a clean dictionary of just the fields MessageModel expects
            message_dict = {
                'id': message.id,
                'created_at': message.created_at,
                'collected_at': message.collected_at,
                'delivered_at': message.delivered_at,
                'from_address': message.from_address,
                'to_address': message.to_address,
                'data': message.data
            }

            message_model = MessageModel(**message_dict)  # Only include fields that exist in MessageModel
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
            return [
                Message(
                    id=msg.id,
                    created_at=msg.created_at,
                    collected_at=msg.collected_at,
                    delivered_at=msg.delivered_at,
                    from_address=msg.from_address,
                    to_address=msg.to_address,
                    data=msg.data
                ) for msg in messages
            ]
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
            return [
                Message(
                    id=msg.id,
                    created_at=msg.created_at,
                    collected_at=msg.collected_at,
                    delivered_at=msg.delivered_at,
                    from_address=msg.from_address,
                    to_address=msg.to_address,
                    data=msg.data
                ) for msg in messages
            ]
        except SQLAlchemyError as e:
            raise Exception(f"Error retrieving messages: {e}")
        finally:
            session.close()


    def __eq__(self, other):
        if not isinstance(other, Message):
            return False
        return (
                self.id == other.id and
                self.from_address == other.from_address and
                self.to_address == other.to_address and
                self.data == other.data
            # Intentionally not comparing datetime fields as they might have microsecond differences
        )
