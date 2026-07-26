"""
Handles encrypting/decrypting photos so nothing sits on disk as a plain
viewable image file. Key is generated once and kept in the app's PRIVATE
storage (user_data_dir) which other apps cannot read without root.
"""
import os
from cryptography.fernet import Fernet

APP_DIR = None
_fernet = None


def _key_path():
    return os.path.join(APP_DIR, ".vaultkey")


def _load_or_create_key():
    path = _key_path()
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(path, "wb") as f:
        f.write(key)
    return key


def init(app_private_dir):
    """Call once at app startup with app.user_data_dir"""
    global APP_DIR, _fernet
    APP_DIR = app_private_dir
    _fernet = Fernet(_load_or_create_key())


def encrypt_file(src_path, dst_path):
    with open(src_path, "rb") as f:
        data = f.read()
    token = _fernet.encrypt(data)
    with open(dst_path, "wb") as f:
        f.write(token)


def decrypt_bytes(enc_path):
    with open(enc_path, "rb") as f:
        token = f.read()
    return _fernet.decrypt(token)
