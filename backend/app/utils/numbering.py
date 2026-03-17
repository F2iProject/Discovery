"""Auto-number generator for Discovery modules."""

from typing import Type

from sqlalchemy.orm import Session

from app.database import Base


def generate_number(
    db: Session,
    model: Type[Base],
    field_name: str,
    prefix: str,
    tenant_id: str,
) -> str:
    """Generate the next sequential number for a module within a tenant.

    Pattern: PREFIX-0001, PREFIX-0002, etc.
    Counts existing records (including soft-deleted) to avoid number reuse.
    """
    query = db.query(model).filter(model.tenant_id == tenant_id)

    # Count ALL records (including deleted) to prevent number reuse
    count = query.count()
    next_num = count + 1

    return f"{prefix}-{next_num:04d}"
