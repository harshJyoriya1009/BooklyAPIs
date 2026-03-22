from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from app.config import Config
from itsdangerous import URLSafeTimedSerializer
import jwt, uuid, logging

password_context = CryptContext(schemes=["bcrypt"])

ACCESS_TOKEN_EXPIRY = 3600


def generate_hash_pasword(password: str) -> str:
    hash = password_context.hash(password)
    return hash


def verify_hash_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)


def create_access_token(user_data: dict, expiry_time: timedelta = None, refresh: bool = False):
    payload = {}

    payload['user'] = user_data

    expire = datetime.now(timezone.utc) + (
        expiry_time if expiry_time is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )

    payload['exp'] = expire
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh

    token = jwt.encode(
        payload=payload,
        key=Config.jwt_secret,
        algorithm=Config.jwt_algorithm
    )

    return token


def decode_access_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.jwt_secret,
            algorithms=[Config.jwt_algorithm]
        )
        return token_data

    except jwt.ExpiredSignatureError as e:
        logging.exception("Token expired")
        return None

    except jwt.InvalidTokenError as e:
        logging.exception("Invalid token")
        return None

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
    

    
token_serializer = URLSafeTimedSerializer(
        secret_key=Config.jwt_secret,
        salt="email-verification"
    )
def create_url_safe_token(data: dict):
    token = token_serializer.dumps(data)
    return token

def decode_url_safe_token(token:str):
    try:
        token_data = token_serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(str(e))