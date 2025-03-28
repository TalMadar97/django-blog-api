# Django Blog API

A RESTful API for a blog platform built with Django REST Framework.

## Features

- User authentication with JWT
- CRUD operations for blog posts
- Image upload support
- API documentation with drf-spectacular
- PostgreSQL database
- CORS support

## Requirements

- Python 3.8+
- PostgreSQL
- Django 4.0+

## Installation

1. Clone the repository

```bash
git clone <your-repo-url>
cd django-blog-api
```

2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set up environment variables
   Create a `.env` file in the project root with:

```
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
```

5. Run migrations

```bash
python manage.py migrate
```

## Running the Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## API Documentation

- API Schema: `/api/schema/`
- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

## Deployment

This project is configured for deployment on Render.com with the following features:

- PostgreSQL database with SSL connection
- CORS configuration for frontend access
- Static files served through Render

## Frontend Integration

The API is configured to work with the React frontend at:

- Development: `http://localhost:3000`
- Production: `https://myblog-sd38.onrender.com`
