
from dataclasses import dataclass, field
from typing import Optional
import uuid

@dataclass(frozen=True)
class Customer:
    name: str
    document_id: str
    email: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
