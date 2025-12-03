from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import auth as auth_utils
from app.core.config import settings
from app.crud import create_user, get_user_by_email
from app.db import get_session
from app.models import User, UserRole
from app.schemas import TokenPair, UserCreate, UserLogin, UserRead


router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    existing = await get_user_by_email(session, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=auth_utils.get_password_hash(user_in.password),
        role=UserRole.user,
    )
    user = await create_user(session, user)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenPair)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user = await get_user_by_email(session, form_data.username)
    if not user or not auth_utils.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    access = auth_utils.create_access_token(str(user.id))
    refresh = auth_utils.create_refresh_token(str(user.id))
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
):
    from jose import JWTError, jwt

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Missing user ID in token")
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    access = auth_utils.create_access_token(user_id)
    new_refresh = auth_utils.create_refresh_token(user_id)
    return TokenPair(access_token=access, refresh_token=new_refresh)


@router.get("/me", response_model=UserRead)
async def read_me(current_user: UserRead = Depends(auth_utils.get_current_user)):
    return current_user


