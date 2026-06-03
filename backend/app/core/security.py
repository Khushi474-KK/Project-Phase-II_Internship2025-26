"""
Firebase-only authentication system.
All authentication is handled by Firebase on the frontend.
Backend only verifies Firebase ID tokens.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from app.core.database import get_db
from app.models.user import User
from datetime import datetime
import os
import uuid

# Initialize Firebase Admin SDK with service account
try:
    firebase_admin.get_app()
    print("✓ Firebase Admin SDK already initialized")
except ValueError:
    # Use service account key file
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    print("✓ Firebase Admin SDK initialized with service account")
    print("✓ Project: smart-camera-auth")
    print("✓ Authentication: Firebase ONLY (no backend login/register)")

# HTTP Bearer token scheme
security = HTTPBearer()

def verify_firebase_token(token: str) -> dict:
    """
    Verify Firebase ID token and return decoded token.
    
    Args:
        token: Firebase ID token from frontend
        
    Returns:
        dict: Decoded token containing uid, email, etc.
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_or_create_user(decoded_token: dict, db: Session) -> User:
    """
    Get existing user or create new user from Firebase token.
    Implements proper account linking based on email.
    
    IMPORTANT: Preserves existing username during account linking.
    
    Logic:
    1. Try to find user by firebase_uid
    2. If not found, try to find by email
    3. If found by email, link the Firebase UID (account linking)
       - PRESERVE existing username (do NOT overwrite)
    4. If not found at all, create new user
    
    Args:
        decoded_token: Decoded Firebase token
        db: Database session
        
    Returns:
        User: User object from database
    """
    uid = decoded_token.get("uid")
    email = decoded_token.get("email", "")
    name = decoded_token.get("name", "") or decoded_token.get("email", "").split("@")[0]
    email_verified = decoded_token.get("email_verified", False)
    picture = decoded_token.get("picture", "")
    
    # Get provider info
    firebase_providers = decoded_token.get("firebase", {}).get("sign_in_provider", "")
    provider = "google" if "google" in firebase_providers else "password"
    
    print(f"\n{'='*60}")
    print(f"Authentication Request:")
    print(f"  Provider: {provider}")
    print(f"  Email: {email}")
    print(f"  Firebase UID: {uid}")
    print(f"  Email Verified: {email_verified}")
    print(f"  Display Name from Token: {name}")
    print(f"{'='*60}\n")
    
    # Step 1: Try to find user by Firebase UID
    user = db.query(User).filter(User.firebase_uid == uid).first()
    
    if user:
        print(f"✓ Existing user found by Firebase UID: {email}")
        print(f"  User ID: {user.id}")
        print(f"  Username: {user.username} (preserved)")
        return user
    
    # Step 2: Try to find user by email (for account linking)
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Account linking: User exists with this email but different Firebase UID
        print(f"✓ Existing user found by email: {email}")
        print(f"  Linking {provider} account to existing user")
        print(f"  User ID: {user.id}")
        print(f"  Username: {user.username} (PRESERVED - not changed)")
        print(f"  Previous Firebase UID: {user.firebase_uid}")
        print(f"  New Firebase UID: {uid}")
        
        # Update Firebase UID and auth provider
        # IMPORTANT: Do NOT update username - preserve existing username
        user.firebase_uid = uid
        user.auth_provider = provider
        
        # Update profile picture if from Google and not already set
        if provider == "google" and picture:
            print(f"  Profile picture available: {picture}")
        
        db.commit()
        db.refresh(user)
        
        print(f"✓ Account linked successfully!")
        print(f"  Username remains: {user.username}")
        return user
    
    # Step 3: Create new user (no existing account found)
    print(f"✓ No existing user found")
    print(f"  Creating new user for: {email}")
    
    # Generate unique username for new users
    base_username = name
    username = base_username
    counter = 1
    
    # Ensure username is unique
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1
        print(f"  Username '{base_username}' taken, trying '{username}'")
    
    user = User(
        firebase_uid=uid,
        email=email,
        username=username,
        auth_provider=provider,
        hashed_password=None,  # No password - Firebase handles auth
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"✓ New user created:")
    print(f"  User ID: {user.id}")
    print(f"  Email: {email}")
    print(f"  Username: {username}")
    print(f"  Provider: {provider}")
    
    return user

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from Firebase token.
    This is the main dependency for protected routes.
    
    Args:
        credentials: HTTP Bearer credentials containing Firebase token
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    # Verify Firebase token
    decoded_token = verify_firebase_token(token)
    
    # Get or create user in database (with account linking)
    user = get_or_create_user(decoded_token, db)
    
    # Update last login time ONLY, do NOT regenerate session_id
    # Session ID should only be generated on actual login, not on every API call
    user.last_login = datetime.utcnow()
    
    # If no session_id exists, generate one (first time or after logout)
    if not user.login_session_id:
        from app.models.photo import Photo
        from datetime import date
        
        today = date.today()
        today_str = today.strftime("%b %d, %Y")  # e.g., "Mar 10, 2026"
        
        # Get all sessions for this user today
        existing_sessions = db.query(Photo.session_id).filter(
            Photo.user_id == user.id
        ).distinct().all()
        
        # Count sessions from today
        today_session_count = 0
        for (session_id,) in existing_sessions:
            if session_id and today_str in session_id:
                today_session_count += 1
        
        # Next session number for today
        next_session_num = today_session_count + 1
        user.login_session_id = f"session_{next_session_num} {today_str}"
        
        print(f"✓ Generated new login session ID: {user.login_session_id}")
    
    db.commit()
    
    return user
