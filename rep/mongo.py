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


class Family(Document):
    token = StringField(required=True, primary_key=True)
    categories = ListField(StringField())
    pending = ListField(StringField())
    name = StringField()


class User(Document):
    username = StringField(required=True, primary_key=True)
    password = StringField(required=True, min_length=8)
    email = StringField(required=True)
    name = StringField()
    role_in_family = IntField(min_value=0, max_value=4)
    family = ReferenceField(Family, reverse_delete_rule=CASCADE)

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
            return False
        except jwt.InvalidTokenError:
            return False


class Category(Document):
    id = StringField(primary_key=True)
    name = StringField(required=True, min_length=3, max_length=25)
    description = StringField(max_length=100, required=True)
    owner = ReferenceField('User', reverse_delete_rule=CASCADE, required=True)


class Spend(Document):
    id = IntField(primary_key=True)
    date = StringField(required=True)
    price = IntField(required=True)
    category = ReferenceField('Category', reverse_delete_rule=CASCADE, required=True)
    owner = ReferenceField('User', reverse_delete_rule=CASCADE, required=True)


class BlackList(Document):
    token = StringField(required=True)
    blacklisted_on = DateTimeField(required=True)
