"""Firebase Authentication middleware for FastAPI."""
import base64
import json
import os
from datetime import datetime
from typing import Optional

import firebase_admin  # type: ignore[import-not-found]
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth, credentials  # type: ignore[import-not-found]
from sqlmodel import Session, select

from ..db import get_session
from ..models import User, UserRole

# Initialize Firebase Admin SDK
try:
    firebase_admin.get_app()
except ValueError:
    # App not initialized, initialize it
    # Priority 1: Base64 encoded service account (for cloud deployment)
    encoded_service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT_BASE64")
    if encoded_service_account:
        try:
            service_account_json = base64.b64decode(encoded_service_account).decode('utf-8')
            service_account_dict = json.loads(service_account_json)
            cred = credentials.Certificate(service_account_dict)
        except Exception as e:
            raise ValueError(f"Failed to decode Firebase service account from base64: {e}")
    
    # Priority 2: Service account file path
    else:
        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")
        if service_account_path and os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
        else:
            # Priority 3: Default application credentials (Cloud Run, etc.)
            cred = credentials.ApplicationDefault()
    
    # Initialize with explicit project ID
    firebase_admin.initialize_app(cred, {
        'projectId': os.getenv("FIREBASE_PROJECT_ID", "citemesh")
    })

security = HTTPBearer()


class FirebaseUser:
    """Authenticated Firebase user with database record."""

    def __init__(self, firebase_uid: str, email: Optional[str], db_user: User):
        self.firebase_uid = firebase_uid
        self.email = email
        self.db_user = db_user
        self.id = db_user.id
        self.role = db_user.role


async def verify_firebase_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> FirebaseUser:
    """
    Verify Firebase ID token and return authenticated user.
    
    This dependency extracts the Bearer token from the Authorization header,
    verifies it with Firebase, and ensures the user exists in the database.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(token)
        firebase_uid = decoded_token["uid"]
        email = decoded_token.get("email")

    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get or create user in database
    statement = select(User).where(User.firebase_uid == firebase_uid)
    db_user = session.exec(statement).first()

    if not db_user:
        # Create new user
        db_user = User(
            firebase_uid=firebase_uid,
            email=email,
            display_name=decoded_token.get("name"),
            photo_url=decoded_token.get("picture"),
            role=UserRole.student,  # Default role
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

    # Update last login
    db_user.last_login_at = datetime.utcnow()
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return FirebaseUser(firebase_uid=firebase_uid, email=email, db_user=db_user)


# Dependency for routes that require authentication
async def get_current_user(
    user: FirebaseUser = Depends(verify_firebase_token),
) -> FirebaseUser:
    """Get the current authenticated user."""
    if not user.db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return user


# Dependency for routes that require specific roles
def require_role(*allowed_roles: UserRole):
    """
    Dependency factory that creates a dependency requiring specific roles.
    
    Usage:
        @app.get("/admin-only")
        async def admin_route(user: FirebaseUser = Depends(require_role(UserRole.admin))):
            ...
    """

    async def role_checker(user: FirebaseUser = Depends(get_current_user)) -> FirebaseUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in allowed_roles]}",
            )
        return user

    return role_checker
