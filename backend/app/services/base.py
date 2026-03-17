"""Generic CRUD service with tenant isolation and soft deletes."""

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar, Type

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import Base
from app.models.mixins import generate_uuid
from app.utils.numbering import generate_number

ModelT = TypeVar("ModelT", bound=Base)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class CRUDService(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    """Base CRUD service with tenant isolation and soft deletes.

    Every module in Discovery follows this exact pattern:
    - List: tenant-scoped, excludes soft-deleted
    - Create: auto-assigns tenant_id, created_by, auto-number
    - Get: by id, tenant-scoped, not deleted
    - Update: partial update with exclude_unset
    - Delete: soft delete (is_deleted=True, deleted_at=now)
    """

    def __init__(self, model: Type[ModelT], number_prefix: str | None = None):
        self.model = model
        self.number_prefix = number_prefix

    def list(
        self,
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelT]:
        query = db.query(self.model).filter(
            self.model.tenant_id == tenant_id,
        )
        # Only filter soft deletes if the model has is_deleted
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == False)
        return query.offset(skip).limit(limit).all()

    def get(self, db: Session, item_id: str, tenant_id: str) -> ModelT:
        query = db.query(self.model).filter(
            self.model.id == item_id,
            self.model.tenant_id == tenant_id,
        )
        if hasattr(self.model, "is_deleted"):
            query = query.filter(self.model.is_deleted == False)
        item = query.first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found",
            )
        return item

    def create(
        self,
        db: Session,
        payload: CreateSchemaT,
        tenant_id: str,
        user_id: str,
    ) -> ModelT:
        data = payload.model_dump()
        data["id"] = generate_uuid()
        data["tenant_id"] = tenant_id

        # Set created_by if the model has it
        if hasattr(self.model, "created_by"):
            data["created_by"] = user_id

        # Auto-number if prefix is configured and model has the right field
        if self.number_prefix:
            number_field = self._get_number_field()
            if number_field:
                data[number_field] = generate_number(
                    db, self.model, number_field, self.number_prefix, tenant_id
                )

        item = self.model(**data)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update(
        self,
        db: Session,
        item_id: str,
        payload: UpdateSchemaT,
        tenant_id: str,
    ) -> ModelT:
        item = self.get(db, item_id, tenant_id)
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    def delete(self, db: Session, item_id: str, tenant_id: str) -> ModelT:
        item = self.get(db, item_id, tenant_id)
        if hasattr(item, "is_deleted"):
            item.is_deleted = True
            item.deleted_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(item)
        else:
            # For models without soft delete (e.g. calibration), actually delete
            db.delete(item)
            db.commit()
        return item

    def _get_number_field(self) -> str | None:
        """Find the auto-number field name on the model."""
        # Convention: models use specific field names for their numbers
        number_fields = [
            "doc_number", "change_number", "capa_number", "risk_number",
            "nc_number", "deviation_number", "complaint_number", "equipment_id",
        ]
        for field in number_fields:
            if hasattr(self.model, field):
                return field
        return None
