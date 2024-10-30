from typing import Optional
from dataclasses import dataclass


@dataclass
class Request:
    id: str
    url: str
    method: str
    headers: Optional[dict]
    body: Optional[dict] = None

    def slug_id(self):
        return self.id.lower().replace(" ", "-")