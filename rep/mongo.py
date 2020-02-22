import datetime
from enum import Enum

import jwt
from mongoengine import *

connect('spends')


class Role(Enum):
    NOT_IN_A_FAMILY = 0
    IN_A_FAMILY = 1
    READ = 2
    MANAGER = 3
    OWNER = 4


class User(Document):
    username = StringField(required=True, primary_key=True)
    password = StringField(required=True, min_length=8)
    email = StringField(required=True)
    name = StringField()
    role_in_family = IntField(min_value=0, max_value=4)

    def encode_token(self, username):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=1, minutes=0, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': username
            }
            return jwt.encode(
                payload,
                'xxxyyyzzz',
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_token(auth_token):
        try:
            payload = jwt.decode(auth_token, 'xxxyyyzzz')
            blacklisted_query_set = BlackList.objects(token=auth_token)
            if len(blacklisted_query_set) == 0:
                return payload['sub']
            else:
                return False
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class Category(Document):
    id = StringField(primary_key=True)
    name = StringField(required=True, min_length=3, max_length=15)
    description = StringField(max_length=50, required=True)
    owner = ReferenceField('User', reverse_delete_rule=CASCADE, required=True)


class Family(Document):
    token = StringField(required=True, primary_key=True)
    members = ListField(ReferenceField(User, reverse_delete_rule=CASCADE))
    categories = ListField(StringField())


class Spend(Document):
    id = IntField(primary_key=True)
    date = StringField(required=True)
    price = IntField(required=True)
    category = ReferenceField('Category', reverse_delete_rule=CASCADE, required=True)
    owner = ReferenceField('User', reverse_delete_rule=CASCADE, required=True)


class BlackList(Document):
    token = StringField(required=True)
    blacklisted_on = DateTimeField(required=True)
