from datetime import datetime

from pydantic import BaseModel


class TweetInfoResponse(BaseModel):
    id: str
    text: str
    created_at: datetime
