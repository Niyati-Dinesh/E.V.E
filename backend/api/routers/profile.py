# api/routers/profile.py
"""
Profile endpoints — all require an authenticated session.
GET  /api/profile          → fetch current user's profile
PUT  /api/profile          → update full_name and/or bio
POST /api/profile/avatar   → upload a new avatar (multipart)
"""

import os
import uuid
import shutil
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel

from api.routers.auth import get_current_user
from core.database import get_profile, upsert_profile, update_profile_avatar

router = APIRouter(prefix="/api/profile", tags=["profile"])

# Directory where avatars are stored locally.

AVATAR_DIR = Path("static/avatars")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB


# ── Schemas ────────────────────────────────────────────────────────────────

class ProfileOut(BaseModel):
    user_id:   int
    full_name: Optional[str] = None
    bio:       Optional[str] = None
    pfp_url:   Optional[str] = None
    email:     Optional[str] = None   # joined from users table


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio:       Optional[str] = None


# ── Helpers ────────────────────────────────────────────────────────────────

def _row_to_out(row, user_id: int, email: str) -> dict:
    """Convert a DB row (RealDictRow or None) to a plain dict for the response."""
    if row is None:
        # No profile row yet — return empty profile with the session user_id
        return {"user_id": user_id, "full_name": None, "bio": None, "pfp_url": None, "email": email}
    return {
        "user_id":   row["user_id"],
        "full_name": row["full_name"],
        "bio":       row["bio"],
        "pfp_url":   row["pfp_url"],
        "email":     email,
    }


# ── Routes ─────────────────────────────────────────────────────────────────

@router.get("", response_model=ProfileOut)
def read_profile(current_user: dict = Depends(get_current_user)):
    """Return the authenticated user's profile (may have null fields if never set)."""
    user_id = current_user["user_id"]
    email   = current_user["email"]
    row = get_profile(user_id)
    return _row_to_out(row, user_id, email)


@router.put("", response_model=ProfileOut)
def write_profile(
    body: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Create or update full_name and/or bio for the authenticated user."""
    user_id = current_user["user_id"]
    email   = current_user["email"]

    row = upsert_profile(
        user_id   = user_id,
        full_name = body.full_name,
        bio       = body.bio,
    )
    return _row_to_out(row, user_id, email)


@router.post("/avatar", response_model=ProfileOut)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload a new profile picture.
    Accepts JPEG / PNG / WebP / GIF, max 2 MB.
    Saves to static/avatars/ and stores the URL in profiles.pfp_url.
    """
    user_id = current_user["user_id"]
    email   = current_user["email"]

    # ── Validate mime type
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP, or GIF images are allowed.")

    # ── Read and validate size
    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Image must be under 2 MB.")

    # ── Save with a unique filename
    ext      = Path(file.filename).suffix.lower() or ".jpg"
    filename = f"{user_id}_{uuid.uuid4().hex}{ext}"
    dest     = AVATAR_DIR / filename

    with open(dest, "wb") as f:
        f.write(contents)


    pfp_url = f"http://localhost:8000/static/avatars/{filename}"

    row = update_profile_avatar(user_id, pfp_url)
    return _row_to_out(row, user_id, email)