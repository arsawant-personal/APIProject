# SaaS API Project - Multi-Tenant API Infrastructure

A complete multi-tenant SaaS API infrastructure built with FastAPI, PostgreSQL, and a unified Bootstrap admin console. This project provides a robust foundation for building SaaS applications with comprehensive tenant management, user authentication, role-based access control, and external API access.

## 🏗️ Architecture Overview

### Core Components
- **FastAPI Backend**: High-performance API server with automatic documentation
- **PostgreSQL Database**: Multi-tenant data storage with proper isolation
- **Unified Console**: Single web interface for all user types
- **External APIs**: Tenant-facing APIs with authentication and access control
- **Comprehensive Logging**: Detailed logging system with configurable levels

### User Types & Access Control
- **Super Admin**: Full system access, can create tenants and users
- **Tenant Admin**: Manages their tenant and users
- **API User**: Access to external APIs only
- **Regular User**: Basic tenant access

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL
- Git

### Database Setup
```bash
# Start PostgreSQL (macOS)
brew services start postgresql

# Create database
createdb saas_db
```

### 1. Clone and Setup
```bash
git clone https://github.com/arsawant-personal/APIProject.git
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

### 4. Environment Setup
```bash
# Copy environment file
cp env.example .env

# Update DATABASE_URL in .env to use your system username:
# DATABASE_URL=postgresql://amit@localhost/saas_db
```

### 5. Database Migrations
```bash
# Run migrations
alembic upgrade head
```

### 6. Start All Services
```bash
# Basic startup
python manage_servers.py start

# With detailed logging
python manage_servers.py start --debug --detailed

# With file logging
python manage_servers.py start --log-file

# All logging options
python manage_servers.py start --debug --detailed --log-file
```

## 📋 Access URLs & Credentials

### 🌐 Application URLs
- **SaaS API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **External API Documentation**: http://localhost:8000/external/docs
- **Unified Console**: http://localhost:8082

### 🔑 Login Credentials

#### Unified Console Login
- **Super Admin**: `admin@yourcompany.com` / `your-super-admin-password`
- **Tenant Users**: Automatically routed based on role

#### API Authentication
- **Super Admin Token**: Available in `.env` file
- **API User Tokens**: Generated through unified console

## 🛠️ Server Management

### Start All Services
```bash
# Basic startup
python manage_servers.py start

# With detailed logging
python manage_servers.py start --debug --detailed

# With file logging
python manage_servers.py start --log-file

# All logging options
python manage_servers.py start --debug --detailed --log-file
```

### Stop All Services
```bash
python manage_servers.py stop
```

### Check Server Status
```bash
python manage_servers.py status
```

### Restart All Services
```bash
python manage_servers.py restart
```

## 🌐 External APIs

### Available Endpoints
The following external APIs are available for authenticated API users:

#### Health Check
```bash
GET /api/v1/external/health
```
**Purpose**: Verify service health and authentication
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-02T23:38:39.362006",
  "user_id": 12,
  "tenant_id": 16,
  "message": "Service is running normally"
}
```

#### Service Status
```bash
GET /api/v1/external/status
```
**Purpose**: Get service information and user context
**Response**:
```json
{
  "service": "SaaS API",
  "version": "1.0.0",
  "status": "operational",
  "timestamp": "2025-08-02T23:38:39.362006",
  "user": {
    "id": 12,
    "email": "user@example.com",
    "tenant_id": 16
  }
}
```

#### User Profile
```bash
GET /api/v1/external/profile
```
**Purpose**: Get current user profile information
**Response**:
```json
{
  "id": 12,
  "email": "user@example.com",
  "full_name": "Demo API User",
  "role": "API_USER",
  "tenant_id": 16,
  "is_active": true,
  "created_at": "2025-08-02T23:38:39.362006",
  "updated_at": "2025-08-02T23:38:39.362006"
}
```

#### Tenant Information
```bash
GET /api/v1/external/tenant
```
**Purpose**: Get tenant information for current user
**Response**:
```json
{
  "id": 16,
  "name": "Demo Company",
  "domain": "demo.example.com",
  "is_active": true,
  "created_at": "2025-08-02T23:38:39.362006",
  "updated_at": "2025-08-02T23:38:39.362006"
}
```

#### Ping
```bash
GET /api/v1/external/ping
```
**Purpose**: Simple connectivity test
**Response**:
```json
{
  "pong": true,
  "timestamp": "2025-08-02T23:38:39.362006",
  "user_id": 12
}
```

#### Echo
```bash
POST /api/v1/external/echo
```
**Purpose**: Test endpoint that echoes back data
**Request Body**:
```json
{
  "test": "message",
  "number": 42,
  "boolean": true
}
```
**Response**:
```json
{
  "message": {"test": "message", "number": 42, "boolean": true},
  "user_id": 12,
  "tenant_id": 16,
  "timestamp": "2025-08-02T23:38:39.362006",
  "echo": true
}
```

### Authentication
All external APIs require Bearer token authentication:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/external/health
```

### Access Control
- **API Users**: Can access all external endpoints
- **Tenant Admins**: Can access all external endpoints
- **Super Admins**: Can access all external endpoints
- **Regular Users**: Cannot access external endpoints

### Testing External APIs
```bash
# Test all external APIs
python test_external_apis.py

# Test specific functionality
python test_api_access.py
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

## 📊 Logging System

### Comprehensive Logging
- **API Request/Response Logging**: Track all API calls with timing
- **Database Operation Logging**: Monitor all CRUD operations
- **Authentication Logging**: Track login attempts and token operations
- **Function Call Logging**: Detailed function execution tracking
- **Error Logging**: Comprehensive error tracking with context

### Logging Levels
- **DEBUG**: Detailed function calls and database operations
- **INFO**: API requests, user operations, authentication
- **WARNING**: Non-critical issues and warnings
- **ERROR**: Errors with full context and stack traces

### Logging Options
```bash
# Basic logging (default)
python manage_servers.py start

# Debug level logging
python manage_servers.py start --debug

# Detailed function call logging
python manage_servers.py start --detailed

# File logging
python manage_servers.py start --log-file

# All options combined
python manage_servers.py start --debug --detailed --log-file
```

### Log Output Examples
```
2025-08-02 14:06:39,798 | INFO | 🌐 API REQUEST: POST /api/v1/auth/token
2025-08-02 14:06:39,832 | INFO | 👤 USER RETRIEVE: ID=1, Email=admin@yourcompany.com, Role=UserRole.SUPER_ADMIN
2025-08-02 14:06:40,094 | INFO | 🔑 TOKEN CREATE: User=admin@yourcompany.com, Type=ACCESS
2025-08-02 14:06:40,095 | INFO | ✅ API RESPONSE: 200 (0.297s)
```

## 🧪 Testing

### Test API Access
```bash
python test_api_access.py
```

### Test External APIs
```bash
python test_external_apis.py
```

### Test Token Generation
```bash
python test_token_generation.py
```

### Test User Creation
```bash
python test_user_creation.py
```

### Test Database Connection
```bash
python test_db.py
```

### Reset Database to Initial State
```bash
# Interactive reset (with confirmation prompt)
python reset_database.py

# Automated reset (skip confirmation)
python reset_database.py --confirm
```

**⚠️ WARNING**: The reset script will:
- Delete ALL data in the database
- Remove ALL users, tenants, and products
- **PRESERVE** database schema and structure
- Create only the super admin user

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
├── unified_console/            # Unified web interface
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

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:8082 | xargs kill -9

# Restart services
python manage_servers.py restart
```

### Database Connection Issues
```bash
# Check PostgreSQL status
brew services list | grep postgresql

# Restart PostgreSQL
brew services restart postgresql

# Verify DATABASE_URL in .env uses your system username
# DATABASE_URL=postgresql://amit@localhost/saas_db
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

### SQLAlchemy Relationship Issues
```bash
# If you see "Mapper has no property" errors:
# 1. Check that all relationships are properly defined
# 2. Ensure models are imported in __init__.py
```

## 🔄 Development Workflow

### Making Changes
1. **Create Feature Branch**: `git checkout -b feature-name`
2. **Make Changes**: Edit files as needed
3. **Test Changes**: Run appropriate test scripts
4. **Commit Changes**: `git commit -m "feat: description"`
5. **Push Changes**: `git push origin feature-name`
6. **Create PR**: Use GitHub CLI or web interface

### Code Quality
- **Type Hints**: All functions should have type hints
- **Docstrings**: All functions should have docstrings
- **Error Handling**: Proper exception handling
- **Logging**: Appropriate logging levels
- **Testing**: Test new features

### Database Changes
1. **Create Migration**: `alembic revision --autogenerate -m "description"`
2. **Review Migration**: Check generated migration file
3. **Apply Migration**: `alembic upgrade head`
4. **Test Changes**: Verify functionality

## 📈 Performance Considerations

### Database Optimization
- **Indexes**: Proper database indexes for queries
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Minimize N+1 queries

### API Performance
- **Caching**: Consider Redis for caching
- **Pagination**: Implement pagination for large datasets
- **Rate Limiting**: Protect against abuse
- **Compression**: Enable gzip compression

### Monitoring
- **Health Checks**: Regular health check endpoints
- **Metrics**: Application metrics collection
- **Logging**: Comprehensive logging for debugging
- **Alerting**: Set up monitoring alerts

## 🔮 Future Enhancements

### Planned Features
- **Redis Integration**: Caching and session management
- **Email Service**: User notifications and alerts
- **File Upload**: Document and file management
- **Audit Logging**: Comprehensive audit trails
- **API Rate Limiting**: Protect against abuse
- **Webhook Support**: External integrations
- **Multi-Factor Authentication**: Enhanced security
- **SSO Integration**: Single sign-on support

### Scalability Improvements
- **Horizontal Scaling**: Load balancer support
- **Database Sharding**: Multi-database support
- **Microservices**: Service decomposition
- **Containerization**: Docker support
- **Kubernetes**: Orchestration support

## 📞 Support

### Getting Help
- **Documentation**: Check this README and API docs
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Testing**: Run test scripts to verify functionality

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using FastAPI, PostgreSQL, and Bootstrap** 