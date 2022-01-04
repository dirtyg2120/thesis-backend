from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserInfoResponse(BaseModel):
    id : int
    name : str
    screen_name : str
    created_at : datetime
    is_real : bool
    followers_count : int 
    followings_count : int
    banner: str
    avatar : str
    tweets : List[str]