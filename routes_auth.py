from fastapi import APIRouter, HTTPException, status, Depends
from models import UserCreate, LoginRequest, Token, UserResponse
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user_id,
)
from database import cosmos_db
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_200_OK)
async def register(user_data: UserCreate):
    """
    Register a new user account
    """
    try:
        # Check if user already exists
        logger.info(f"Registration attempt for email: {user_data.email}")
        existing_user = cosmos_db.get_user_by_email(user_data.email)
        if existing_user:
            logger.warning(f"Registration failed: Email already exists {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        # Create user document
        user_id = str(uuid.uuid4())
        user_doc = {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": get_password_hash(user_data.password),
            "created_at": datetime.utcnow().isoformat(),
        }

        # Save to database
        created_user = cosmos_db.create_user(user_doc)
        logger.info(f"User created successfully: {user_data.email}")

        # Generate JWT token
        access_token = create_access_token(
            data={"sub": user_id, "email": user_data.email}
        )

        # Prepare response
        user_response = UserResponse(
            id=created_user["id"],
            username=created_user["username"],
            email=created_user["email"],
            createdAt=created_user["created_at"],
        )

        return Token(token=access_token, user=user_response)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Registration validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register user: {str(e)}",
        )


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(login_data: LoginRequest):
    """
    Authenticate user and receive access token
    """
    try:
        # Get user by email
        logger.info(f"Login attempt for email: {login_data.email}")
        user = cosmos_db.get_user_by_email(login_data.email)
        if not user:
            logger.warning(f"Login failed: User not found for email {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Verify password
        if not verify_password(login_data.password, user["hashed_password"]):
            logger.warning(f"Login failed: Invalid password for email {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Generate JWT token
        access_token = create_access_token(
            data={"sub": user["id"], "email": user["email"]}
        )

        # Prepare response
        user_response = UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            createdAt=user["created_at"],
        )

        logger.info(f"Login successful for user: {user['email']}")
        return Token(token=access_token, user=user_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to login: {str(e)}",
        )
