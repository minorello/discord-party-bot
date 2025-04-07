from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import base64

# Mesmo salt da outra criptografia
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

# Solicita senha e criptografa o .gitignore
senha = getpass("Digite a senha para criptografar o .gitignore: ")
key = derive_key(senha, salt)
fernet = Fernet(key)

try:
    with open(".gitignore", "rb") as file:
        conteudo = file.read()

    encrypted = fernet.encrypt(conteudo)

    with open(".gitignore.enc", "wb") as file:
        file.write(encrypted)

    print("✅ .gitignore criptografado com sucesso para .gitignore.enc!")

except Exception as e:
    print("❌ Erro ao criptografar:", str(e))
