from pydantic import BaseModel
from typing import Dict, Optional, Any


class ExecuteRequestData(BaseModel):
    url: str
    method: str
    headers: Dict[str, str] = {}
    data: Optional[Any] = None
