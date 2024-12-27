import hmac
import hashlib

def create_HMAC(password, salt):
    hmac_sha256 = hmac.new(password.encode("utf-8"), salt.encode("utf-8"), hashlib.sha256)
    return hmac_sha256.hexdigest()