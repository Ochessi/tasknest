# TaskNest 📝

TaskNest is a task management web app designed to help users organize their tasks, categorize them, and tag them for better productivity.  
This project is built using **Django** and will expose a REST API using **Django REST Framework (DRF)**.

---

## 🚀 Week 1 Progress

### 1. Project Initialization
- Created Django project: `tasknest`
- Initialized Git repository and connected to GitHub
- Installed dependencies:
  ```bash
  pip install django djangorestframework psycopg2-binary

2. Apps Setup

Created modular Django apps:

    users → Handles authentication and user profiles

    tasks → Manages tasks and related operations

    categories → Allows task grouping by categories

    tags → Enables tagging tasks for better filtering

Added apps to INSTALLED_APPS in settings.py.
3. Database Models

Models were created based on the ERD:

User Model (Custom User)

    Extends Django’s AbstractUser

    Fields: username, email, password, date_joined

Task Model

    Belongs to a User (ForeignKey)

    Fields: title, description, is_completed, due_date, priority, created_at

    Related to categories and tags (Many-to-Many)

Category Model

    Unique category names

    Many-to-Many relationship with Task

Tag Model

    Unique tag names

    Many-to-Many relationship with Task

4. Migrations

Created and applied initial migrations:

python manage.py makemigrations
python manage.py migrate

5. Model Testing (Django Shell)


Verified relationships and data creation:

from users.models import User
from tasks.models import Task
from categories.models import Category
from tags.models import Tag

# Create user
u = User.objects.create_user(username="alice", email="alice@example.com", password="pass1234")

# Create task
t = Task.objects.create(user=u, title="Finish ERD", priority="High")

# Add category and tag
c = Category.objects.create(name="School")
tag = Tag.objects.create(name="Urgent")

t.categories.add(c)
t.tags.add(tag)

print(u.tasks.all())        # -> shows "Finish ERD"
print(t.categories.all())   # -> shows "School"
print(t.tags.all())         # -> shows "Urgent"

✅ Output confirmed that relationships and models are working correctly.


⚙️ Setup Instructions

Follow these steps to run the project locally:
1. Clone the Repository

git clone <https://github.com/Ochessi/tasknest>
cd tasknest

2. Create and Activate Virtual Environment

python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows

3. Install Dependencies

pip install -r requirements.txt

4. Configure Database

    Ensure PostgreSQL is installed and running.

    Create a database (example: tasknest_db).

    Update your settings.py:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'tasknest_db',
            'USER': '<your-username>',
            'PASSWORD': '<your-password>',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

5. Apply Migrations

python manage.py makemigrations
python manage.py migrate

6. Create Superuser (for admin access)

python manage.py createsuperuser

7. Run Development Server

python manage.py runserver

Now visit http://127.0.0.1:8000/ 🎉


📌 Next Steps (Week 2)

    Set up API endpoints using Django REST Framework

    Implement authentication (JWT)

    Write serializers and views for Users, Tasks, Categories, and Tags

    Add unit tests for API endpoints

🔗 Repository

GitHub Repo: ([https://github.com/Ochessi/tasknest](tasknest))


🛠 Tech Stack

    Python 3.x

    Django 5.x

    Django REST Framework

    PostgreSQL

    Git & GitHub

## 🔐 Authentication (JWT)
- **POST** `/api/auth/register/` → create user
- **POST** `/api/auth/token/` → obtain `{ access, refresh }`
- **POST** `/api/auth/token/refresh/` → refresh access token
- **GET** `/api/users/me/` → current user profile (auth)

## ✅ Tasks
- **GET/POST** `/api/tasks/`
- **GET/PUT/DELETE** `/api/tasks/{id}/`
- **PATCH** `/api/tasks/{id}/complete/` → `{ is_completed: true|false }`

## 🗂️ Categories
- **GET/POST** `/api/categories/`
- **GET/PUT/DELETE** `/api/categories/{id}/`

## 🏷️ Tags
- **GET/POST** `/api/tags/`
- **GET/PUT/DELETE** `/api/tags/{id}/`

> Auth: send `Authorization: Bearer <access_token>` header for all endpoints except register/token.
