from passlib.context import CryptContext


#creating a daefault(what we want to use) algorithm that we want to use (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)





