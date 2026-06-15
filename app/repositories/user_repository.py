from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


class UserRepository:
    def get_by_email(
        self,
        db: Session,
        email: str
    ) -> User | None:
        return db.query(User).filter(
            User.email == email
        ).first()

    def get_by_uuid(
        self,
        db: Session,
        user_uuid: str
    ) -> User | None:
        return db.query(User).filter(
            User.uuid == user_uuid
        ).first()

    def create(
        self,
        db: Session,
        data: UserCreate
    ) -> User:
        print(data.password)
        print(len(data.password))
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=hash_password(data.password)
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user