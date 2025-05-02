from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from app.core.config import get_settings

settings = get_settings()

class JWTService:
    def __init__(self):
        self.secret_key = settings.TOKEN_SIGNING_KEY
        self.algorithm = "HS256"
        self.access_token_expiration = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def extract_user_name(self, token: str) -> str:
        return self.extract_claim(token, "sub")

    def generate_token(self, user_details: Dict[str, Any]) -> str:
        claims = {
            "id": user_details.get("id"),
            "email": user_details.get("email"),
            "role": user_details.get("role")
        }
        return self.generate_token_with_claims(claims, user_details)

    def is_token_valid(self, token: str, user_details: Dict[str, Any]) -> bool:
        username = self.extract_user_name(token)
        return username == user_details.get("username") and not self.is_token_expired(token)

    def extract_claim(self, token: str, claim: str) -> Any:
        claims = self.extract_all_claims(token)
        return claims.get(claim)

    def generate_token_with_claims(self, claims: Dict[str, Any], user_details: Dict[str, Any]) -> str:
        to_encode = claims.copy()
        to_encode.update({
            "sub": user_details.get("username"),
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expiration)
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def is_token_expired(self, token: str) -> bool:
        expiration = self.extract_claim(token, "exp")
        if expiration is None:
            return True
        return datetime.fromtimestamp(expiration) < datetime.utcnow()

    def extract_all_claims(self, token: str) -> Dict[str, Any]:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return self.extract_all_claims(token)
        except Exception:
            return None 