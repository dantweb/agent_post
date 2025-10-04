##filepath: ./src/message.py
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import json


@dataclass
class Message:
    from_address: str
    to_address: str
    data: str
    id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        else:
            self.id = str(self.id)  # convert int or UUID to string

    @property
    def address_list(self) -> List[str]:
        """Process to_address and return address_list"""
        to_list = [self.to_address]  # Default to single address

        # Check for common delimiters and split if found
        for delim in [';', ',', ' ']:
            if delim in self.to_address:
                # Split by whitespace after normalizing delimiters to spaces
                to_list = [addr.strip() for addr in
                           self.to_address.replace(';', ' ').replace(',', ' ').split()]
                # Remove empty items
                to_list = [addr for addr in to_list if addr]
                break

        return to_list

    def is_old(self, days: int = 3) -> bool:
        return self.created_at and (datetime.now() - self.created_at).days > days

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

    def to_dict(self):
        """Convert the message to a dictionary with serialized datetime values."""
        result = {
            "id": str(self.id) if self.id else None,  # Convert UUID to string
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'from_address': self.from_address,
            'to_address': self.to_address,
            'data': self.data,
        }
        return result

    def to_json(self):
        """Convert the message to a JSON string."""
        return json.dumps(self.to_dict())

    def __str__(self):
        """Return a JSON string representation of the message."""
        return self.to_json()

    # Optionally, you can also use the same implementation for __repr__
    __repr__ = __str__

    # This method allows the class to be JSON serializable
    def __json__(self):
        return self.to_dict()


    def set_created_at(self):
        self.created_at = datetime.now()

