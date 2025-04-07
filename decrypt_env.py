from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import base64

# Mesmo salt usado na criptografia
salt = b"mysalt_12345678"

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)

# Solicita a senha e tenta descriptografar
senha = getpass("Digite a senha para descriptografar: ")
key = derive_key(senha, salt)
fernet = Fernet(key)

try:
    with open(".env.enc", "rb") as file:
        encrypted = file.read()

    decrypted = fernet.decrypt(encrypted)

    with open(".env", "wb") as file:
        file.write(decrypted)

    print("✅ Descriptografado com sucesso e salvo como .env!")

except Exception as e:
    print("❌ Erro ao descriptografar:", str(e))
