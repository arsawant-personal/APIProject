# SaaS Admin Console

A modern, responsive admin console built with Bootstrap 5 for managing your SaaS API.

## Features

- 🔐 **Secure Authentication** - JWT-based login with token refresh
- 🏢 **Tenant Management** - Create and manage tenants
- 📊 **Dashboard Analytics** - Real-time statistics and metrics
- 🎨 **Modern UI** - Bootstrap 5 with custom styling
- 📱 **Responsive Design** - Works on desktop and mobile
- 🔄 **Real-time Updates** - Live data from your API

## Quick Start

### 1. Start the Admin Console Server

```bash
cd admin_console
python server.py
```

The admin console will be available at: http://localhost:8080

### 2. Login Credentials

- **Email**: `admin@yourcompany.com`
- **Password**: `your-super-admin-password`

These credentials correspond to the super admin user created in your SaaS API.

### 3. Make Sure Your API is Running

Ensure your SaaS API is running at http://localhost:8000:

```bash
# In your main project directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Features

### Tenant Management
- ✅ **List All Tenants** - View all tenants in a responsive table
- ✅ **Create New Tenant** - Add new tenants with name, domain, and status
- ✅ **Real-time Stats** - See total tenants, active tenants, and activity
- 🔄 **Edit Tenant** - Coming soon
- 🔄 **Delete Tenant** - Coming soon

### Authentication
- ✅ **JWT Login** - Secure authentication with your API
- ✅ **Token Refresh** - Automatic token refresh when expired
- ✅ **Session Management** - Persistent login sessions
- ✅ **Secure Logout** - Proper token cleanup

### UI/UX
- ✅ **Modern Design** - Bootstrap 5 with custom gradients
- ✅ **Responsive Layout** - Works on all screen sizes
- ✅ **Loading States** - Visual feedback during operations
- ✅ **Toast Notifications** - Success/error messages
- ✅ **Smooth Animations** - CSS transitions and animations

## File Structure

```
admin_console/
├── index.html          # Main HTML file
├── styles.css          # Custom CSS styles
├── script.js           # JavaScript functionality
├── server.py           # Simple HTTP server
└── README.md           # This file
```

## API Integration

The admin console connects to your SaaS API endpoints:

- **Authentication**: `/api/v1/auth/token`
- **Tenants**: `/api/v1/admin/tenants/`
- **Users**: `/api/v1/admin/users/` (coming soon)

## Customization

### Styling
Edit `styles.css` to customize:
- Color scheme
- Typography
- Animations
- Layout

### Functionality
Edit `script.js` to add:
- New API endpoints
- Additional features
- Custom validations

## Browser Compatibility

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

## Security Notes

- The admin console uses JWT tokens for authentication
- Tokens are stored in localStorage (consider httpOnly cookies for production)
- CORS is enabled for development (configure properly for production)
- All API calls include proper authorization headers

## Development

### Adding New Features

1. **Add new sections** in `index.html`
2. **Style them** in `styles.css`
3. **Add functionality** in `script.js`
4. **Connect to API** using the existing patterns

### API Endpoints

To add new API endpoints:

1. Create the endpoint in your FastAPI app
2. Add the corresponding function in `script.js`
3. Update the UI to use the new functionality

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure your API has CORS configured
2. **Authentication Failed**: Check that your API is running and credentials are correct
3. **Network Errors**: Verify the API_BASE_URL in script.js matches your API

### Debug Mode

Open browser developer tools (F12) to see:
- Network requests
- Console logs
- JavaScript errors

## Production Deployment

For production deployment:

1. **Configure CORS** properly in your API
2. **Use HTTPS** for all communications
3. **Implement proper session management**
4. **Add rate limiting**
5. **Set up monitoring and logging**

## License

This admin console is part of your SaaS API project. 