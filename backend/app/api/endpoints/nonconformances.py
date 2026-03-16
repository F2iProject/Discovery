"""Non-Conformance endpoints — CRUD."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_nonconformances(db: Session = Depends(get_db)):
    """List all non-conformances."""
    # TODO: implement with tenant filtering
    return []


@router.post("/")
async def create_nonconformances(db: Session = Depends(get_db)):
    """Create a new non-conformance."""
    # TODO: implement
    return {"message": "not implemented"}


@router.get("/{item_id}")
async def get_nonconformances(item_id: str, db: Session = Depends(get_db)):
    """Get a single non-conformance by ID."""
    # TODO: implement
    raise HTTPException(status_code=404, detail="Not found")


@router.patch("/{item_id}")
async def update_nonconformances(item_id: str, db: Session = Depends(get_db)):
    """Update a non-conformance."""
    # TODO: implement
    return {"message": "not implemented"}


@router.delete("/{item_id}")
async def delete_nonconformances(item_id: str, db: Session = Depends(get_db)):
    """Soft-delete a non-conformance."""
    # TODO: implement
    return {"message": "not implemented"}
