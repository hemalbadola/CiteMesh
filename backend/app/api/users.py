"""User management API endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select

from ..core.firebase_auth import FirebaseUser, get_current_user
from ..db import get_session
from ..models import Profile, User, UserRead, UserRole

router = APIRouter()


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    full_name: Optional[str] = None
    display_name: Optional[str] = None
    role: Optional[UserRole] = None


class ProfileUpdate(BaseModel):
    """Schema for updating user profile details."""

    bio: Optional[str] = None
    affiliation: Optional[str] = None
    avatar_url: Optional[str] = None


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Get the current authenticated user's profile."""
    return current_user.db_user


@router.put("/me", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdate,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update the current user's profile."""
    db_user = current_user.db_user

    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name
    if user_update.display_name is not None:
        db_user.display_name = user_update.display_name
    if user_update.role is not None:
        db_user.role = user_update.role

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: FirebaseUser = Depends(get_current_user),
):
    """Get a user by ID."""
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.get("/me/profile")
async def get_current_user_profile_details(
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get the current user's extended profile."""
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authenticated user is missing a database id",
        )

    statement = select(Profile).where(Profile.user_id == current_user.id)
    profile = session.exec(statement).first()

    if not profile:
        # Create profile if it doesn't exist
        profile = Profile(user_id=current_user.id)
        session.add(profile)
        session.commit()
        session.refresh(profile)

    return profile


@router.put("/me/profile")
async def update_current_user_profile(
    profile_update: ProfileUpdate,
    current_user: FirebaseUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update the current user's extended profile."""
    if current_user.id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authenticated user is missing a database id",
        )

    statement = select(Profile).where(Profile.user_id == current_user.id)
    profile = session.exec(statement).first()

    if not profile:
        profile = Profile(user_id=current_user.id)

    if profile_update.bio is not None:
        profile.bio = profile_update.bio
    if profile_update.affiliation is not None:
        profile.affiliation = profile_update.affiliation
    if profile_update.avatar_url is not None:
        profile.avatar_url = profile_update.avatar_url

    session.add(profile)
    session.commit()
    session.refresh(profile)

    return profile
