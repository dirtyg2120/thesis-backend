from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class UserInfoResponse(BaseModel):
    id: int
    name: str
    username: str
    created_at: datetime
    is_real: bool
    followers_count: int
    followings_count: int
    avatar: str
    banner: Optional[str]
    tweets: List[str]
