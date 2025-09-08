from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static

# Admin site customization
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'TaskNest Admin')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'TaskNest Admin Portal')
admin.site.index_title = getattr(settings, 'ADMIN_SITE_INDEX_TITLE', 'Welcome to TaskNest Administration')

# Schema View for Swagger/OpenAPI - Best Practices
schema_view = get_schema_view(
    openapi.Info(
        title="📋 TaskNest API",
        default_version='v1.0',
        description="""
# 🚀 **TaskNest API v1.0**

A modern, scalable task management platform built with Django REST Framework and comprehensive role-based access control.

## 🏗️ **Architecture Overview**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Django 5.2 + DRF | RESTful API with advanced features |
| **Database** | PostgreSQL/SQLite | Robust data storage with advanced querying |
| **Authentication** | JWT (SimpleJWT) | Secure token-based authentication |
| **Documentation** | OpenAPI 3.0 | Interactive API documentation |
| **Filtering** | Django Filters | Advanced data querying and filtering |

## 🔐 **Access Control Matrix**

| Endpoint Type | Authentication | User Role | Description |
|---------------|----------------|-----------|-------------|
| **Public** | ❌ None | 👥 Everyone | Basic API info, health checks |
| **Authenticated** | ✅ JWT Token | 👤 Registered Users | Task management, categories, tags |
| **Admin** | ✅ JWT Token | 👑 Administrators | System management, full access |

## 🚀 **Quick Start Guide**

### 1. **Authentication Flow**
```bash
# Register new account
POST /api/auth/register/
{
  "username": "your_username",
  "email": "your_email@example.com",
  "password": "your_password"
}

# Login to get JWT tokens
POST /api/auth/login/
{
  "username": "your_username",
  "password": "your_password"
}

# Response includes access and refresh tokens
{
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### 2. **Using JWT in Swagger**
1. Click the **🔒 Authorize** button at the top
2. Enter your JWT token (without "Bearer" prefix)
3. Click **Authorize**
4. The system automatically adds the "Bearer " prefix

### 3. **Token Refresh**
```bash
POST /api/auth/token/refresh/
{
  "refresh": "your_refresh_token"
}
```

## 📊 **API Categories**

- **🔐 Authentication**: Registration, login, password management
- **👤 User Management**: Profile management, account settings
- **📋 Tasks**: Core task CRUD operations with filtering and search
- **🏷️ Categories**: Task categorization and organization
- **🔖 Tags**: Task tagging system for flexible organization
- **👑 Admin**: System administration and user management

## 🔒 **Security Features**

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Granular permission system
- **Input Validation**: Comprehensive data sanitization
- **CORS Protection**: Cross-origin request security
- **HTTPS Ready**: Production security compliance

## 📈 **Performance Features**

- **Database Optimization**: Advanced querying with Django ORM
- **Pagination**: Efficient data retrieval (10 items per page)
- **Filtering & Search**: Advanced data querying capabilities
- **Ordering**: Flexible result sorting

## 🛠️ **Development & Testing**

- **Unit Tests**: Comprehensive test coverage
- **Integration Tests**: API endpoint testing
- **Documentation**: Auto-generated OpenAPI specs

## 📚 **Additional Resources**

- **GitHub Repository**: [TaskNest Platform](https://github.com/yourusername/tasknest)
- **API Status**: [Health Check Endpoint](/health/)
- **Support**: support@tasknest.com

---

        """,
        terms_of_service="https://tasknest.com/terms/",
        contact=openapi.Contact(
            name="TaskNest Support Team",
            email="support@tasknest.com",
            url="https://tasknest.com/support"
        ),
        license=openapi.License(
            name="MIT License",
            url="https://opensource.org/licenses/MIT"
        ),
        version="1.0.0",
        x_logo={
            "url": "https://via.placeholder.com/200x200/3B82F6/FFFFFF?text=📋",
            "backgroundColor": "#3B82F6"
        }
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

# Health check view
@csrf_exempt
def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': '2025-09-08T15:08:25+03:00',
        'service': 'TaskNest API',
        'version': '1.0.0'
    })

urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Home
    path('', lambda request: HttpResponse('''
        <div style="text-align: center; padding: 50px; font-family: Arial, sans-serif;">
            <h1 style="color: #3B82F6;">📋 TaskNest API v1.0</h1>
            <p style="font-size: 18px; color: #6B7280;">
                A modern, scalable task management platform with comprehensive role-based access control
            </p>
            <div style="margin: 30px 0;">
                <a href="/api/docs/" style="background: #3B82F6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 0 10px;">
                    📚 Swagger UI
                </a>
                <a href="/api/redoc/" style="background: #10B981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 0 10px;">
                    📖 ReDoc
                </a>
            </div>
            <div style="background: #F3F4F6; padding: 20px; border-radius: 8px; max-width: 700px; margin: 0 auto;">
                <h3 style="color: #374151;">🚀 Quick Start Guide</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; text-align: left; color: #6B7280;">
                    <div>
                        <h4 style="color: #3B82F6;">🔐 Authentication</h4>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li>Register at <code>/api/auth/register/</code></li>
                            <li>Login at <code>/api/auth/login/</code></li>
                            <li>Use JWT tokens for protected endpoints</li>
                        </ul>
                    </div>
                    <div>
                        <h4 style="color: #10B981;">📋 Task Management</h4>
                        <ul style="margin: 0; padding-left: 20px;">
                            <li><strong>Tasks:</strong> Create, update, delete tasks</li>
                            <li><strong>Categories:</strong> Organize with categories</li>
                            <li><strong>Tags:</strong> Flexible tagging system</li>
                            <li><strong>Search:</strong> Advanced filtering & search</li>
                        </ul>
                    </div>
                </div>
            </div>
            <div style="margin-top: 30px; padding: 20px; background: #EFF6FF; border-radius: 8px; max-width: 700px; margin-left: auto; margin-right: auto;">
                <h3 style="color: #1E40AF;">💡 Pro Tips</h3>
                <p style="color: #374151; margin: 0;">
                    <strong>JWT Authentication:</strong> In Swagger, click "Authorize" and enter your token without the "Bearer" prefix - it's added automatically! 🎯
                </p>
            </div>
            <div style="margin-top: 20px; padding: 15px; background: #F0FDF4; border-radius: 8px; max-width: 700px; margin-left: auto; margin-right: auto;">
                <h4 style="color: #166534; margin: 0 0 10px 0;">🔗 API Endpoints</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px; color: #374151;">
                    <div><strong>Auth:</strong> <code>/api/auth/</code></div>
                    <div><strong>Tasks:</strong> <code>/api/tasks/</code></div>
                    <div><strong>Categories:</strong> <code>/api/categories/</code></div>
                    <div><strong>Tags:</strong> <code>/api/tags/</code></div>
                    <div><strong>Users:</strong> <code>/api/users/</code></div>
                    <div><strong>Admin:</strong> <code>/admin/</code></div>
                </div>
            </div>
        </div>
    '''), name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', csrf_exempt(schema_view.with_ui('redoc', cache_timeout=0)), name='schema-redoc'),
    
    # API Endpoints
    path('api/auth/', include('users.auth_urls')),
    path('api/users/', include('users.user_urls')),
    path('api/tasks/', include('tasks.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/tags/', include('tags.urls')),
    
    # JSON Schema
    re_path(r'^api/schema(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
