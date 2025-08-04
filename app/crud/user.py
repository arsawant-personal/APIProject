from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.core.logging import logger, log_database_operation, log_user_operation

@log_database_operation("SELECT")
def get_user(db: Session, user_id: int):
    logger.debug(f"🔍 Getting user by ID: {user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        log_user_operation("RETRIEVE", user.id, user.email, user.role)
    else:
        logger.warning(f"⚠️  User not found with ID: {user_id}")
    return user

@log_database_operation("SELECT")
def get_user_by_email(db: Session, email: str):
    logger.debug(f"🔍 Getting user by email: {email}")
    user = db.query(User).filter(User.email == email).first()
    if user:
        log_user_operation("RETRIEVE", user.id, user.email, user.role)
    else:
        logger.warning(f"⚠️  User not found with email: {email}")
    return user

@log_database_operation("SELECT")
def get_users(db: Session, skip: int = 0, limit: int = 100):
    logger.debug(f"🔍 Getting users with skip={skip}, limit={limit}")
    users = db.query(User).offset(skip).limit(limit).all()
    logger.info(f"📋 Retrieved {len(users)} users")
    return users

@log_database_operation("INSERT")
def create_user(db: Session, user: UserCreate):
    logger.debug(f"➕ Creating user: {user.email}, role={user.role}, tenant_id={user.tenant_id}")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role,
        tenant_id=user.tenant_id,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    log_user_operation("CREATE", db_user.id, db_user.email, db_user.role)
    return db_user

@log_database_operation("UPDATE")
def update_user(db: Session, user_id: int, user: UserUpdate):
    logger.debug(f"✏️  Updating user ID: {user_id}")
    db_user = get_user(db, user_id)
    if not db_user:
        logger.warning(f"⚠️  Cannot update user - not found with ID: {user_id}")
        return None
    
    # Prevent updating SUPER_ADMIN users
    if db_user.role == "SUPER_ADMIN":
        logger.warning(f"⚠️  Cannot update SUPER_ADMIN user with ID: {user_id}")
        return None
    
    update_data = user.dict(exclude_unset=True)
    logger.debug(f"📝 Update data: {update_data}")
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    log_user_operation("UPDATE", db_user.id, db_user.email, db_user.role)
    return db_user

@log_database_operation("DELETE")
def delete_user(db: Session, user_id: int):
    logger.debug(f"🗑️  Deleting user ID: {user_id}")
    db_user = get_user(db, user_id)
    if not db_user:
        logger.warning(f"⚠️  Cannot delete user - not found with ID: {user_id}")
        return None
    
    # Prevent deletion of SUPER_ADMIN users
    if db_user.role == "SUPER_ADMIN":
        logger.warning(f"⚠️  Cannot delete SUPER_ADMIN user with ID: {user_id}")
        return None
    
    db.delete(db_user)
    db.commit()
    log_user_operation("DELETE", db_user.id, db_user.email, db_user.role)
    return db_user 