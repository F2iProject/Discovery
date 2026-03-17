"""Seed script: creates a default tenant and admin user.

Usage: python -m scripts.seed
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.tenant import Tenant
from app.models.user import User
from app.models.mixins import generate_uuid
from app.core.security import get_password_hash

# Import all models so tables are registered
from app.models import *  # noqa


def seed():
    """Create default tenant and admin user if they don't exist."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if any tenant exists
        existing = db.query(Tenant).first()
        if existing:
            print(f"Database already seeded. Tenant: {existing.name}")
            return

        # Create tenant
        tenant = Tenant(
            id=generate_uuid(),
            name="My Lab",
            slug="my-lab",
        )
        db.add(tenant)
        db.flush()

        # Create admin user
        user = User(
            id=generate_uuid(),
            email="admin@discovery.local",
            hashed_password=get_password_hash("discovery"),
            full_name="Lab Admin",
            role="admin",
            is_active=True,
            tenant_id=tenant.id,
        )
        db.add(user)
        db.commit()

        print("Database seeded successfully!")
        print(f"  Tenant: {tenant.name} ({tenant.slug})")
        print(f"  Admin:  {user.email} / discovery")
        print()
        print("Change the password after first login.")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
