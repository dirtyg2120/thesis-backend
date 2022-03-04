from mongoengine import Document, StringField


class Operator(Document):
    username = StringField(primary_key=True)
    password = StringField(required=True)

    meta = {"collection": "operators"}
