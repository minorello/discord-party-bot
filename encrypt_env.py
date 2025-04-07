from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import base64

# Configuração fixa de salt
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

# Solicita senha e gera chave
senha = getpass("Digite uma senha para criptografar: ")
key = derive_key(senha, salt)
fernet = Fernet(key)

# Lê o conteúdo do .env original
with open(".env", "rb") as file:
    conteudo = file.read()

# Criptografa e salva como .env.enc
criptografado = fernet.encrypt(conteudo)
with open(".env.enc", "wb") as file:
    file.write(criptografado)

print("✅ .env criptografado e salvo como .env.enc!")
