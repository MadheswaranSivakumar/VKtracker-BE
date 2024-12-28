import hmac
import hashlib

def hash_password(password, secrete_key):
    """Hash a password using HMAC and SHA256."""
    return hmac.new(password.encode(), bytes.fromhex(secrete_key), hashlib.sha256).hexdigest()