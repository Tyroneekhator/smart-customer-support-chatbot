from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin_user import AdminUser
from app.schemas.auth_schema import AdminLoginRequest, AdminProfileResponse, AdminTokenResponse
from app.services.auth_dependency import get_current_admin
from app.services.auth_service import auth_service


router = APIRouter(
    prefix="/api/auth",
    tags=["Admin Auth"],
)


@router.post("/login", response_model=AdminTokenResponse)
def admin_login(login_data: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = auth_service.authenticate_admin(
        db=db,
        username=login_data.username,
        password=login_data.password,
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": auth_service.create_access_token(admin),
        "token_type": "bearer",
        "expires_in_minutes": auth_service.access_token_expire_minutes,
        "admin": admin,
    }


@router.get("/me", response_model=AdminProfileResponse)
def get_logged_in_admin(current_admin: AdminUser = Depends(get_current_admin)):
    return current_admin


@router.post("/logout")
def logout_admin(current_admin: AdminUser = Depends(get_current_admin)):
    return {
        "message": f"Admin {current_admin.username} logged out successfully. Please remove the token from the frontend."
    }
