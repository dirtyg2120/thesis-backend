from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TwitterUser(BaseModel):
    twitter_id: str
    name: str
    username: str
    created_at: datetime
    followers_count: int
    followings_count: int
    avatar: str
    banner: Optional[str]
