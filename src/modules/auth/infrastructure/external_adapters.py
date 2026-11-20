# modulo auth
''' Adaptadores externos: servicios técnicos que no son de negocio.
Aquí: hash de contraseñas con PBKDF2 (librería estándar, sin dependencias extra).
'''
import hashlib
import hmac
import os

_ITERACIONES = 100_000


class PasswordHasher:

    @staticmethod
    def hashear(contrasenia: str) -> str:
        salt = os.urandom(16)
        hash_bytes = hashlib.pbkdf2_hmac("sha256", contrasenia.encode(), salt, _ITERACIONES)
        return f"{salt.hex()}${hash_bytes.hex()}"

    @staticmethod
    def verificar(contrasenia: str, hash_guardado: str) -> bool:
        try:
            salt_hex, hash_hex = hash_guardado.split("$")
            salt = bytes.fromhex(salt_hex)
        except ValueError:
            return False
        nuevo = hashlib.pbkdf2_hmac("sha256", contrasenia.encode(), salt, _ITERACIONES)
        return hmac.compare_digest(nuevo.hex(), hash_hex)
