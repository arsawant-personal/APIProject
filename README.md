# SaaS API Project - Multi-Tenant API Infrastructure

A complete multi-tenant SaaS API infrastructure built with FastAPI, PostgreSQL, and Bootstrap admin console. This project provides a foundation for building SaaS applications with tenant management, user authentication, and API access control.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL
- Git

### 1. Clone and Setup
```bash
git clone https://github.com/arsawant-github/APIProject.git
cd APIProject
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Start PostgreSQL (macOS)
brew services start postgresql

# Create database
createdb saas_db

# Set up environment
cp env.example .env
# Edit .env with your database URL (see Environment Variables section)
```

### 5. Database Migrations
```bash
# Run migrations
alembic upgrade head
```

### 6. Start All Services
```bash
python manage_servers.py start
```

## 📋 Access URLs & Credentials

### 🌐 Application URLs
- **SaaS API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Admin API Documentation**: http://localhost:8000/admin/docs
- **External API Documentation**: http://localhost:8000/external/docs
- **Admin Console**: http://localhost:8080

### 🔑 Login Credentials

#### Admin Console Login
- **Email**: `admin@yourcompany.com`
- **Password**: `your-super-admin-password`

#### API Authentication
- **Super Admin Token**: Available in `.env` file
- **API User Tokens**: Generated through admin console

## 🛠️ Server Management

### Start All Services
```bash
python manage_servers.py start
```

### Stop All Services
```bash
python manage_servers.py stop
```

### Restart All Services
```bash
python manage_servers.py restart
```

### Check Service Status
```bash
python manage_servers.py status
```

### Manual Port Cleanup (if needed)
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:8080 | xargs kill -9
```

## 🏗️ Architecture Overview

### Multi-Tenant Structure
- **Tenants**: Isolated customer environments
- **Users**: Belong to specific tenants
- **Products**: Tenant-specific features
- **API Users**: External API access with bearer tokens

### User Roles
1. **SUPER_ADMIN**: Full system access, can manage all tenants
2. **TENANT_ADMIN**: Manage users within their tenant
3. **USER**: Regular tenant user
4. **API_USER**: External API access with bearer tokens

## 📚 API Documentation

### Admin APIs (Super Admin Only)
- **Base URL**: `http://localhost:8000/api/v1/admin`
- **Documentation**: http://localhost:8000/admin/docs

#### Tenant Management
- `POST /admin/tenants/` - Create new tenant
- `GET /admin/tenants/` - List all tenants
- `GET /admin/tenants/{tenant_id}` - Get tenant details
- `PUT /admin/tenants/{tenant_id}` - Update tenant

#### User Management
- `POST /admin/users/` - Create new user
- `GET /admin/users/` - List all users
- `GET /admin/users/{user_id}` - Get user details
- `PUT /admin/users/{user_id}` - Update user
- `DELETE /admin/users/{user_id}` - Delete user
- `POST /admin/users/{user_id}/generate-token` - Generate bearer token for API user

### External APIs (API Users)
- **Base URL**: `http://localhost:8000/api/v1/external`
- **Documentation**: http://localhost:8000/external/docs

#### Health Check
- `GET /external/health` - Health check endpoint

### Authentication APIs
- **Base URL**: `http://localhost:8000/api/v1/auth`
- `POST /auth/token` - Login and get access token
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info

## 🎛️ Admin Console Features

### Dashboard
- Overview of tenants and users
- Quick statistics

### Tenant Management
- **Create Tenant**: Add new customer environments
- **List Tenants**: View all tenants with details
- **Edit Tenant**: Modify tenant information

### User Management
- **Create User**: Add users to specific tenants
- **List Users**: View all users across tenants
- **Edit User**: Modify user information
- **Delete User**: Remove users from system
- **Generate API Token**: Create bearer tokens for API users

### API Token Generation
- Generate bearer tokens for API users
- Copy tokens to clipboard
- View token usage examples

## 🔧 Environment Variables

Create `.env` file from `env.example`:

```bash
# Database
DATABASE_URL=postgresql://amit@localhost/saas_db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Super Admin
SUPER_ADMIN_EMAIL=admin@yourcompany.com
SUPER_ADMIN_PASSWORD=your-super-admin-password

# Redis (optional)
REDIS_URL=redis://localhost:6379
```

## 🧪 Testing

### Test API Access
```bash
python test_api_access.py
```

### Test Token Generation
```bash
python test_token_generation.py
```

### Test User Creation
```bash
python test_user_creation.py
```

## 📁 Project Structure

```
APIProject/
├── app/                          # Main application
│   ├── api/v1/                  # API endpoints
│   │   ├── admin.py            # Admin APIs
│   │   ├── auth.py             # Authentication APIs
│   │   ├── external.py         # External APIs
│   │   └── api.py              # API router
│   ├── core/                   # Core configuration
│   │   ├── config.py           # Settings
│   │   ├── database.py         # Database setup
│   │   └── security.py         # JWT authentication
│   ├── crud/                   # Database operations
│   │   ├── tenant.py           # Tenant CRUD
│   │   └── user.py             # User CRUD
│   ├── models/                 # SQLAlchemy models
│   │   ├── tenant.py           # Tenant model
│   │   └── user.py             # User model
│   ├── schemas/                # Pydantic schemas
│   │   ├── tenant.py           # Tenant schemas
│   │   └── user.py             # User schemas
│   └── main.py                 # FastAPI app
├── admin_console/              # Admin web interface
│   ├── index.html              # Main console page
│   ├── script.js               # Console JavaScript
│   ├── style.css               # Console styles
│   └── server.py               # Console server
├── alembic/                    # Database migrations
│   └── versions/               # Migration files
├── scripts/                    # Utility scripts
├── venv/                       # Virtual environment
├── manage_servers.py           # Server management
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🔒 Security Features

### Authentication
- JWT-based authentication
- Bearer token support
- Role-based access control
- Token expiration

### Multi-Tenancy
- Tenant isolation
- User role management
- API access control

### API Security
- CORS configuration
- Input validation
- SQL injection protection
- Rate limiting ready

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:8080 | xargs kill -9

# Restart services
python manage_servers.py restart
```

### Database Connection Issues
```bash
# Check PostgreSQL status
brew services list | grep postgresql

# Restart PostgreSQL
brew services restart postgresql
```

### Migration Issues
```bash
# Reset migrations (WARNING: This will delete data)
alembic downgrade base
alembic upgrade head
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 🔄 Development Workflow

### Adding New Features
1. Update models in `app/models/`
2. Create schemas in `app/schemas/`
3. Add CRUD operations in `app/crud/`
4. Create API endpoints in `app/api/v1/`
5. Update admin console if needed
6. Add tests
7. Create database migration

### Database Changes
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

### Code Style
- Use Black for Python formatting
- Follow PEP 8 guidelines
- Add type hints
- Write docstrings

## 📈 Production Deployment

### Environment Setup
1. Use production PostgreSQL instance
2. Set strong SECRET_KEY
3. Enable HTTPS
4. Configure CORS properly
5. Set up monitoring and logging

### Security Checklist
- [ ] Change default passwords
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS
- [ ] Configure firewall rules
- [ ] Set up backup strategy
- [ ] Implement rate limiting
- [ ] Add audit logging

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check server logs
4. Create GitHub issue

---

**Last Updated**: January 2025
**Version**: 1.0.0
**Status**: Baseline - Ready for Development 