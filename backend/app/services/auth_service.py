import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.admin_user import AdminUser


PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 200_000
JWT_ALGORITHM = "HS256"


class AuthService:
    def __init__(self):
        self.secret_key = os.getenv(
            "ADMIN_SECRET_KEY",
            "change-this-development-secret-key-before-deployment",
        )
        self.access_token_expire_minutes = int(
            os.getenv("ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES", "120")
        )

    def hash_password(self, password: str, salt: Optional[str] = None) -> str:
        if salt is None:
            salt = secrets.token_hex(16)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            PBKDF2_ITERATIONS,
        ).hex()

        return f"{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${salt}${password_hash}"

    def verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            algorithm, iterations, salt, expected_hash = stored_hash.split("$", 3)
        except ValueError:
            return False

        if algorithm != PBKDF2_ALGORITHM:
            return False

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()

        return hmac.compare_digest(calculated_hash, expected_hash)

    def authenticate_admin(
        self,
        db: Session,
        username: str,
        password: str,
    ) -> Optional[AdminUser]:
        identifier = username.strip()

        admin = (
            db.query(AdminUser)
            .filter(
                or_(
                    AdminUser.username == identifier,
                    AdminUser.email == identifier,
                )
            )
            .first()
        )

        if not admin or not admin.is_active:
            return None

        if not self.verify_password(password, admin.password_hash):
            return None

        return admin

    def create_access_token(self, admin: AdminUser) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_token_expire_minutes
        )

        header = {
            "alg": JWT_ALGORITHM,
            "typ": "JWT",
        }
        payload = {
            "sub": str(admin.id),
            "username": admin.username,
            "role": "admin",
            "exp": int(expires_at.timestamp()),
        }

        encoded_header = self._base64url_encode_json(header)
        encoded_payload = self._base64url_encode_json(payload)
        signing_input = f"{encoded_header}.{encoded_payload}"
        signature = self._sign(signing_input)

        return f"{signing_input}.{signature}"

    def decode_access_token(self, token: str) -> Dict[str, Any]:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired admin token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            encoded_header, encoded_payload, received_signature = token.split(".")
        except ValueError as exc:
            raise credentials_exception from exc

        signing_input = f"{encoded_header}.{encoded_payload}"
        expected_signature = self._sign(signing_input)

        if not hmac.compare_digest(received_signature, expected_signature):
            raise credentials_exception

        try:
            payload = self._base64url_decode_json(encoded_payload)
        except (ValueError, json.JSONDecodeError) as exc:
            raise credentials_exception from exc

        expires_at = payload.get("exp")

        if expires_at is None or int(expires_at) < int(datetime.now(timezone.utc).timestamp()):
            raise credentials_exception

        if payload.get("role") != "admin":
            raise credentials_exception

        return payload

    def _sign(self, signing_input: str) -> str:
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            signing_input.encode("utf-8"),
            hashlib.sha256,
        ).digest()

        return self._base64url_encode_bytes(signature)

    def _base64url_encode_json(self, value: Dict[str, Any]) -> str:
        json_bytes = json.dumps(value, separators=(",", ":")).encode("utf-8")
        return self._base64url_encode_bytes(json_bytes)

    def _base64url_encode_bytes(self, value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")

    def _base64url_decode_json(self, value: str) -> Dict[str, Any]:
        padding = "=" * (-len(value) % 4)
        decoded = base64.urlsafe_b64decode(f"{value}{padding}")
        return json.loads(decoded.decode("utf-8"))


auth_service = AuthService()


def seed_default_admin(db: Session) -> None:
    existing_admin_count = db.query(AdminUser).count()

    if existing_admin_count > 0:
        return

    username = os.getenv("ADMIN_USERNAME", "admin")
    email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    password = os.getenv("ADMIN_PASSWORD", "Admin123!")

    admin = AdminUser(
        username=username.strip(),
        email=email.strip() or None,
        password_hash=auth_service.hash_password(password),
        is_active=True,
    )

    db.add(admin)
    db.commit()
