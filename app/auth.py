from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt

# As chaves SECRET_KEY e ALGORITHM devem ser configuradas como variáveis de ambiente
# para melhor segurança. Por exemplo, você pode usar o pacote python-dotenv para isso.
SECRET_KEY = "umasecretmuitosecreta"  # Mude para uma chave real em produção
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 100

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
