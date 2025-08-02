from app.core.database import engine
from app.models import user, tenant, product
from sqlalchemy import text

print('Testing database connection...')
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('Database connection successful!')
except Exception as e:
    print(f'Database connection failed: {e}') 