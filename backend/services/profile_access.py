"""Load the one saved user. There are no accounts — the id is always 'default'."""

from backend.database import SessionLocal, init_db
from backend.models.user_profile import UserProfile

DEFAULT_USER_ID = "default"


def load_saved_profile(user_id: str = DEFAULT_USER_ID):
    """Read the profile the web app already saved. Do not invent figures."""
    init_db()
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise RuntimeError("No saved profile. Complete Financial Reality Intake first.")
        db.refresh(profile)
        db.expunge(profile)
        return profile
    finally:
        db.close()
