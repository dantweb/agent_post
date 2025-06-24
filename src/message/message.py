## ./agent_post/src/message/message.py

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class Message:
    id: int
    created_at: datetime
    collected_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    from_address: str
    to_address: str
    data: str

    def is_old(self, days: int = 3) -> bool:
        return self.collected_at and (datetime.now() - self.collected_at).days > days
