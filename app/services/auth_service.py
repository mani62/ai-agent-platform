from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.models.user import User


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def register(
        self,
        db: Session,
        data: UserCreate
    ) -> User:
        existing_user = self.user_repository.get_by_email(
            db,
            data.email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        return self.user_repository.create(
            db,
            data
        )

    def login(
        self,
        db: Session,
        email: str,
        password: str
    ) -> dict:
        user = self.user_repository.get_by_email(
            db,
            email
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not verify_password(
            password,
            user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        access_token = create_access_token(
            subject=user.uuid
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }