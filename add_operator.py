#!/usr/bin/env python3

import os
import sys

from dotenv import load_dotenv
from pymongo import MongoClient  # type: ignore

from app.services.auth import OperatorAuthHandler

load_dotenv()

if len(sys.argv) < 3:
    sys.exit("Please input username and password!")

client = MongoClient(host=os.environ["MONGO_HOST"], port=int(os.environ["MONGO_PORT"]))
db = client[os.environ["MONGO_DB"]]
operators = db.operators

username = sys.argv[1]
hashed_password = OperatorAuthHandler().get_password_hash(sys.argv[2])
operators.insert_one({"username": username, "password": hashed_password})
