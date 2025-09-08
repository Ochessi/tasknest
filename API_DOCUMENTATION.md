# TaskNest API Documentation

TaskNest is a comprehensive task management REST API built with Django REST Framework. It provides user authentication, task management, categorization, and tagging functionality.

## Base URL
```
http://localhost:8000/api/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register/
```
**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123"
}
```
**Response:**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
}
```

#### Login (Get Token)
```http
POST /api/auth/token/
```
**Request Body:**
```json
{
    "username": "john_doe",
    "password": "securepassword123"
}
```
**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh Token
```http
POST /api/auth/token/refresh/
```
**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## User Endpoints

#### Get User Profile
```http
GET /api/users/me/
```
**Response:**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "date_joined": "2025-01-01T00:00:00Z"
}
```

#### Update User Profile
```http
PUT /api/users/me/
PATCH /api/users/me/
```

#### Get Dashboard Data
```http
GET /api/users/dashboard/
```
**Response:**
```json
{
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "date_joined": "2025-01-01T00:00:00Z"
    },
    "stats": {
        "total_tasks": 10,
        "completed_tasks": 6,
        "pending_tasks": 4,
        "high_priority_tasks": 2,
        "completion_rate": 60.0
    }
}
```

## Task Endpoints

#### List Tasks
```http
GET /api/tasks/
```
**Query Parameters:**
- `is_completed`: Filter by completion status (true/false)
- `priority`: Filter by priority (Low, Medium, High)
- `due_date`: Filter by due date
- `search`: Search in title and description
- `ordering`: Order by fields (created_at, updated_at, due_date, priority)

**Response:**
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Complete project documentation",
            "description": "Write comprehensive API documentation",
            "is_completed": false,
            "due_date": "2025-01-15",
            "priority": "High",
            "categories": ["Work", "Documentation"],
            "tags": ["urgent", "api"],
            "created_at": "2025-01-01T10:00:00Z",
            "updated_at": "2025-01-01T10:00:00Z"
        }
    ]
}
```

#### Create Task
```http
POST /api/tasks/
```
**Request Body:**
```json
{
    "title": "New Task",
    "description": "Task description",
    "priority": "Medium",
    "due_date": "2025-01-20",
    "category_ids": [1, 2],
    "tag_ids": [1, 3]
}
```

#### Get Task
```http
GET /api/tasks/{id}/
```

#### Update Task
```http
PUT /api/tasks/{id}/
PATCH /api/tasks/{id}/
```

#### Delete Task
```http
DELETE /api/tasks/{id}/
```

#### Mark Task as Complete/Incomplete
```http
PATCH /api/tasks/{id}/complete/
```
**Request Body:**
```json
{
    "is_completed": true
}
```

#### Get Completed Tasks
```http
GET /api/tasks/completed/
```

#### Get Pending Tasks
```http
GET /api/tasks/pending/
```

#### Get Task Statistics
```http
GET /api/tasks/stats/
```
**Response:**
```json
{
    "total_tasks": 10,
    "completed_tasks": 6,
    "pending_tasks": 4,
    "high_priority_tasks": 2,
    "completion_rate": 60.0
}
```

## Category Endpoints

#### List Categories
```http
GET /api/categories/
```
**Response:**
```json
{
    "count": 3,
    "results": [
        {
            "id": 1,
            "name": "Work",
            "description": "Work-related tasks",
            "created_at": "2025-01-01T00:00:00Z",
            "task_count": 5
        }
    ]
}
```

#### Create Category
```http
POST /api/categories/
```
**Request Body:**
```json
{
    "name": "Personal",
    "description": "Personal tasks and activities"
}
```

#### Get Category Tasks
```http
GET /api/categories/{id}/tasks/
```

## Tag Endpoints

#### List Tags
```http
GET /api/tags/
```
**Response:**
```json
{
    "count": 5,
    "results": [
        {
            "id": 1,
            "name": "urgent",
            "color": "#ff0000",
            "created_at": "2025-01-01T00:00:00Z",
            "task_count": 3
        }
    ]
}
```

#### Create Tag
```http
POST /api/tags/
```
**Request Body:**
```json
{
    "name": "important",
    "color": "#ff9900"
}
```

#### Get Tag Tasks
```http
GET /api/tags/{id}/tasks/
```

## Error Responses

The API returns standard HTTP status codes and error messages:

```json
{
    "detail": "Authentication credentials were not provided."
}
```

Common status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Usage Examples

### Complete Workflow Example

1. **Register a new user:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "password123"}'
```

2. **Get authentication token:**
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'
```

3. **Create a category:**
```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Work", "description": "Work tasks"}'
```

4. **Create a tag:**
```bash
curl -X POST http://localhost:8000/api/tags/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "urgent", "color": "#ff0000"}'
```

5. **Create a task:**
```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Complete project", "priority": "High", "category_ids": [1], "tag_ids": [1]}'
```

6. **Get user dashboard:**
```bash
curl -X GET http://localhost:8000/api/users/dashboard/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Admin Interface

Access the Django admin interface at:
```
http://localhost:8000/admin/
```

Default superuser credentials:
- Username: admin
- Password: (set during superuser creation)

The admin interface provides full CRUD operations for all models with enhanced filtering and search capabilities.
