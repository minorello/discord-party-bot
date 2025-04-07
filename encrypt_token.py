import os
import base64
import getpass
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv

def generate_key(password: bytes, salt: bytes) -> bytes:
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    return base64.urlsafe_b64encode(kdf.derive(password))

# Criação do .env criptografado
def encrypt_token():
    token = input("Digite seu token do Discord: ").strip()
    password = getpass.getpass("Digite uma senha para criptografar: ").encode()

    salt = os.urandom(16)
    key = generate_key(password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(token.encode())

    with open(".env", "w") as fenv:
        fenv.write(f"SALT={base64.urlsafe_b64encode(salt).decode()}\n")
        fenv.write(f"TOKEN_ENCRYPTED={encrypted.decode()}\n")

    print("[✓] Token criptografado e salvo com sucesso!")

if __name__ == "__main__":
    encrypt_token()
