from passlib.context import CryptContext


# creating a daefault(what we want to use) algorithm that we want to use (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#hashing password in database
def hash(password: str):
    return pwd_context.hash(password)


#comparing hashed pass and login password for validation
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
