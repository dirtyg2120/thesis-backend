from datetime import datetime

from pydantic import BaseModel


class TweetInfoResponse(BaseModel):
    id: int
    text: str
    created_at: datetime
