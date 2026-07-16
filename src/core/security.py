from datetime import datetime, timedelta, timezone
import jwt
import uuid
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from pydantic import BaseModel
from src.core.config import SECRET
class JWTPayload(BaseModel):
    id: uuid.UUID
    role: str


hasher = PasswordHash((BcryptHasher(),))

def hash_password(password: str) -> str:
    return hasher.hash(password=password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hasher.verify(plain_password, hashed_password) 

def create_jwt(payload: JWTPayload):

    payload_dict = {"id": str(payload.id),"role":payload.role}   
    if not payload_dict.get("id") or not payload_dict.get("role"):
        raise ValueError("Invalid payload values passed: 'id' and 'role' are required.")
    if "exp" not in payload_dict:
        payload_dict["exp"] = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(payload_dict, SECRET, algorithm="HS256")

    return token

def decode_jwt(token: str) -> JWTPayload:
    try:
        decoded_payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        
        return JWTPayload(
            id=uuid.UUID(decoded_payload["id"]),
            role=decoded_payload["role"]
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token.")