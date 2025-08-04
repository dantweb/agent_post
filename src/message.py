## ./agent_post/src/message/message.py
import json
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class Message:
    id: int
    created_at: datetime
    from_address: str
    to_address: str
    data: str
    collected_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    metadata: Optional[dict] = None
    address_list: Optional[list[str]] = None

    def __init__(self, id: int, created_at: datetime, from_address: str, to_address: str,
                 data: str, collected_at: Optional[datetime] = None,
                 delivered_at: Optional[datetime] = None, metadata: Optional[dict] = None,
                 address_list: Optional[list[str]] = None):
        """Initialize the Message with the given parameters"""
        object.__setattr__(self, 'id', id)
        object.__setattr__(self, 'created_at', created_at)
        object.__setattr__(self, 'from_address', from_address)
        object.__setattr__(self, 'to_address', to_address)
        object.__setattr__(self, 'data', data)
        object.__setattr__(self, 'collected_at', collected_at)
        object.__setattr__(self, 'delivered_at', delivered_at)
        object.__setattr__(self, 'metadata', metadata)

        # Process to_address and set address_list
        to_list = [to_address]  # Default to single address

        # Check for common delimiters and split if found
        for delim in [';', ',', ' ']:
            if delim in to_address:
                # Split by whitespace after normalizing delimiters to spaces
                to_list = [addr.strip() for addr in
                           to_address.replace(';', ' ').replace(',', ' ').split()]
                # Remove empty items
                to_list = [addr for addr in to_list if addr]
                break

        object.__setattr__(self, 'address_list', to_list)


    def is_old(self, days: int = 3) -> bool:
        return self.collected_at and (datetime.now() - self.collected_at).days > days


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

    def __str__(self):
        """Return a JSON string representation of the message."""
        # Create a dictionary from the dataclass
        msg_dict = asdict(self)

        # Convert datetime objects to ISO format strings
        for key, value in msg_dict.items():
            if isinstance(value, datetime):
                msg_dict[key] = value.isoformat()

        # Convert to JSON string
        return json.dumps(msg_dict)

    # Optionally, you can also use the same implementation for __repr__
    __repr__ = __str__

    def to_dict(self):
        """Convert the message to a dictionary with serialized datetime values."""
        msg_dict = asdict(self)

        # Convert datetime objects to ISO format strings
        for key, value in msg_dict.items():
            if isinstance(value, datetime):
                msg_dict[key] = value.isoformat()

        return msg_dict


    def to_json(self):
        """Convert the message to a JSON string."""
        return json.dumps(self.to_dict())

    # This method allows the class to be JSON serializable
    def __json__(self):
        return self.to_dict()

