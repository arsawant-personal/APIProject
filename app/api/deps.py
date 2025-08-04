from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token, verify_password
from app.crud import user as user_crud, token as token_crud
from app.models.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = user_crud.get_user_by_email(db=db, email=email)
    if user is None:
        raise credentials_exception
    
    return user

def get_current_super_admin(current_user = Depends(get_current_user)):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def get_current_api_user_or_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Authenticate either a user token or an API token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # First, try to authenticate as a user token
    try:
        payload = verify_token(token)
        if payload is not None:
            email: str = payload.get("sub")
            if email is not None:
                user = user_crud.get_user_by_email(db=db, email=email)
                if user is not None:
                    # Check if user has appropriate role
                    if user.role in [UserRole.API_USER, UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN]:
                        return user
    except:
        pass
    
    # If user token fails, try API token
    try:
        api_token = token_crud.verify_token(db, token)
        if api_token is not None:
            # Get the user associated with this token (if any)
            if api_token.user_id:
                user = user_crud.get_user(db, user_id=api_token.user_id)
                if user is not None:
                    return user
            else:
                # Create a mock user for tokens without user association
                from app.models.user import User
                mock_user = User(
                    id=None,  # Use None to avoid foreign key constraint
                    email="api-token@system",
                    full_name="API Token User",
                    role=UserRole.API_USER,
                    tenant_id=api_token.tenant_id,
                    is_active=True
                )
                return mock_user
    except:
        pass
    
    raise credentials_exception

def get_current_api_user_with_scope(required_scope: str):
    """Dependency that requires a specific scope for API tokens"""
    def _get_user_with_scope(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        scope_exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Token does not have required scope: {required_scope}",
        )
        
        # First, try to authenticate as a user token
        try:
            payload = verify_token(token)
            if payload is not None:
                email: str = payload.get("sub")
                if email is not None:
                    user = user_crud.get_user_by_email(db=db, email=email)
                    if user is not None:
                        # Check if user has appropriate role
                        if user.role in [UserRole.API_USER, UserRole.TENANT_ADMIN, UserRole.SUPER_ADMIN]:
                            return user
        except:
            pass
        
        # If user token fails, try API token
        try:
            api_token = token_crud.verify_token(db, token)
            if api_token is not None:
                # Check if token has required scope
                import json
                token_scopes = json.loads(api_token.scopes)
                if required_scope not in token_scopes:
                    raise scope_exception
                
                # Get the user associated with this token (if any)
                if api_token.user_id:
                    user = user_crud.get_user(db, user_id=api_token.user_id)
                    if user is not None:
                        return user
                else:
                    # Create a mock user for tokens without user association
                    from app.models.user import User
                    mock_user = User(
                        id=None,  # Use None to avoid foreign key constraint
                        email="api-token@system",
                        full_name="API Token User",
                        role=UserRole.API_USER,
                        tenant_id=api_token.tenant_id,
                        is_active=True
                    )
                    return mock_user
        except HTTPException:
            raise
        except:
            pass
        
        raise credentials_exception
    
    return _get_user_with_scope 