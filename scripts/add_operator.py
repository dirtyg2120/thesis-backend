#!/usr/bin/env python3

import os
import sys

from dotenv import load_dotenv
from pymongo import MongoClient  # type: ignore

load_dotenv()

if len(sys.argv) < 3:
    sys.exit("Please input username and password!")

client = MongoClient(host=os.environ["MONGO_HOST"], port=int(os.environ["MONGO_PORT"]))
db = client[os.environ["MONGO_DB"]]
operators = db.operators
operators.insert_one({"username": sys.argv[1], "password": sys.argv[2]})
