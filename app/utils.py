from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # -> specify default hashing algorith passlib (in thus case bcryp)


def hash(password: str):
    return pwd_context.hash(password)



def Verify(plain_password, hash_password):
    return pwd_context.verify(plain_password, hash_password)