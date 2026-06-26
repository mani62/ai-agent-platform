from datetime import datetime, timezone
from typing import Generic, TypeVar
from sqlalchemy.orm import Session
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(
            self,
            model: type[ModelType],
    ):
        self.model = model

    def get_by_uuid(
        self,
        db: Session,
        uuid: str
    ) -> ModelType | None:
        return db.query(self.model).filter(
            self.model.uuid == uuid,
            self.model.deleted_at.is_(None)
        ).first()
    
    def get_all(
        self,
        db: Session,
    ) -> list[ModelType]:
        return db.query(self.model).filter(
            self.model.deleted_at.is_(None)
        ).all()
    
    def save(
        self,
        db: Session,
        obj: ModelType
    ) -> ModelType:
        db.commit()
        db.refresh(obj)

        return obj
    
    def create(
        self,
        db: Session,
        obj: ModelType
    ) -> ModelType:
        db.add(obj)
        db.commit()
        db.refresh(obj)

        return obj

    def soft_delete(
        self,
        db: Session,
        obj: ModelType
    ) -> ModelType:
        obj.deleted_at = datetime.now(timezone.utc)

        db.commit()
    


