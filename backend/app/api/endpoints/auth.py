"""Auth endpoints — login, register, me."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
async def register():
    """Register a new user."""
    # TODO: implement
    return {"message": "not implemented"}


@router.post("/login")
async def login():
    """Login and receive JWT token."""
    # TODO: implement
    return {"message": "not implemented"}


@router.get("/me")
async def me():
    """Get current user."""
    # TODO: implement
    return {"message": "not implemented"}
