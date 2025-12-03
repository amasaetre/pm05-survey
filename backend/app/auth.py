from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud import get_user, get_user_by_email
from app.db import get_session
from app.models import User, UserRole
from app.schemas import TokenPayload, UserRead


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def _create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": subject, "exp": expire, "type": token_type}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def create_access_token(subject: str) -> str:
    return _create_token(
        subject=subject,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )


def create_refresh_token(subject: str) -> str:
    return _create_token(
        subject=subject,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token = credentials.credentials
    
    if not token:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        data = TokenPayload(**payload)
    except (JWTError, ValueError) as e:
        raise credentials_exception

    if data.type != "access":
        raise credentials_exception

    try:
        user_id = UUID(data.sub)
    except ValueError:
        raise credentials_exception

    user = await get_user(session, user_id)
    if not user:
        raise credentials_exception

    return UserRead.model_validate(user)


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> Optional[UserRead]:
    if not credentials:
        return None
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        data = TokenPayload(**payload)
        if data.type != "access":
            return None
        user_id = UUID(data.sub)
    except Exception:
        return None

    user = await get_user(session, user_id)
    if not user:
        return None
    return UserRead.model_validate(user)


async def get_current_active_user(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    return current_user


async def get_current_admin_user(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user


