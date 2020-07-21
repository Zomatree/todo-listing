import jwt
import binascii
from Crypto.Random import get_random_bytes


def generate(userid, key=None):
    payload = {"id": userid}
    key = key or binascii.hexlify(get_random_bytes(64))
    return jwt.encode(payload, key, algorithm='HS512'), key.decode()


def get_user_id(token):
    payload = jwt.decode(token, verify=False, algorithms=['HS512'])
    return payload['id']