from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

auth_service = AuthService()

@router.post(
    "/register",
    response_model=UserRead
)
def register(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    return auth_service.register(
        db,
        data
    )

@router.post(
    "/login",
    response_model=Token
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return auth_service.login(
        db,
        form_data.username,
        form_data.password
    )