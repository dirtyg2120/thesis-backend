#!/usr/bin/env python3

import os
import sys

from dotenv import load_dotenv
from mongoengine import connect

from app.models import Operator
from app.services.auth import OperatorAuthHandler

"""
    NOTE:
    In production, run this from backend's container
"""

load_dotenv()

if len(sys.argv) < 3:
    sys.exit("Please input username and password!")

connect(
    os.environ["MONGO_DB"],
    host=os.environ["MONGO_HOST"],
    port=27017,
)

username = sys.argv[1]
hashed_password = OperatorAuthHandler().get_password_hash(sys.argv[2])
Operator(username=username, password=hashed_password).save()
