"""Document endpoints — CRUD."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_documents(db: Session = Depends(get_db)):
    """List all documents."""
    # TODO: implement with tenant filtering
    return []


@router.post("/")
async def create_documents(db: Session = Depends(get_db)):
    """Create a new document."""
    # TODO: implement
    return {"message": "not implemented"}


@router.get("/{item_id}")
async def get_documents(item_id: str, db: Session = Depends(get_db)):
    """Get a single document by ID."""
    # TODO: implement
    raise HTTPException(status_code=404, detail="Not found")


@router.patch("/{item_id}")
async def update_documents(item_id: str, db: Session = Depends(get_db)):
    """Update a document."""
    # TODO: implement
    return {"message": "not implemented"}


@router.delete("/{item_id}")
async def delete_documents(item_id: str, db: Session = Depends(get_db)):
    """Soft-delete a document."""
    # TODO: implement
    return {"message": "not implemented"}
