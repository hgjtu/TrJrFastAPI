# Travel Journal Web Service

A FastAPI-based web service for a travel journal application that allows users to share their travel experiences through posts with images. The service includes role-based access control, post moderation, and image storage capabilities.

## Features

- **Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (User, Moderator, Admin)
  - Secure password handling
  - User registration and login

- **User Management**
  - User profile management
  - Profile image upload
  - Password change functionality
  - Role management

- **Post Management**
  - Create, read, update, and delete posts
  - Post moderation system
  - Post likes functionality
  - Post status tracking (Pending, Approved, Rejected)
  - Post resubmission for rejected posts

- **Image Management**
  - Image upload and storage using MinIO
  - Image retrieval and base64 encoding
  - Default images for users and posts
  - Image reset functionality

- **Moderation System**
  - Post approval/rejection by moderators
  - Post status tracking
  - Moderator-specific endpoints

- **Admin Features**
  - Admin rights management
  - User role management

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/tr_jr_db
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=1234
TOKEN_SIGNING_KEY=Jssu8aTdbT8hjeZ610Z0IGeHfDQvr6EE6Gj56JWM1E80b4t2l2GC62PRMKTYEHDS
MINIO_URL=http://127.0.0.1:9000
MINIO_BUCKET=tr-jr-bucket
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

## Configuration

The application uses the following configuration:

- Port: 8010
- API Base Path: /api/v1
- Database: PostgreSQL
- File Storage: MinIO
- JWT Token Expiration: 20 days
- Max File Size: 10MB
- Max Request Size: 10MB

## Prerequisites

- Python 3.8+
- pip (Python package installer)
- MinIO server for image storage
- SQLite database (or other supported database)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd travel-journal-web-service
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create the `.env` file with your configuration

5. Run the application:
```bash
uvicorn app.main:app --reload --port 8010
```

The API will be available at `http://localhost:8010/api/v1`

## Project Structure

```
app/
├── api/
│   └── v1/
│       └── endpoints/
│           ├── auth.py
│           ├── post.py
│           └── user.py
├── core/
│   ├── auth_service.py
│   ├── user_service.py
│   ├── post_service.py
│   ├── moderator_service.py
│   ├── admin_service.py
│   ├── jwt_service.py
│   ├── minio_service.py
│   ├── exceptions.py
│   └── security.py
├── models/
│   ├── base.py
│   ├── post.py
│   ├── user.py
│   └── enums.py
├── schemas/
│   ├── auth.py
│   ├── post.py
│   └── user.py
├── db/
│   └── database.py
└── main.py
```

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation: `http://localhost:8010/docs`
- ReDoc documentation: `http://localhost:8010/redoc`

## API Endpoints

### Authentication
- POST `/api/v1/auth/sign-up` - Register a new user
- POST `/api/v1/auth/sign-in` - Login user
- PUT `/api/v1/auth/change-password` - Change user password

### Users
- GET `/api/v1/users/me` - Get current user profile
- PUT `/api/v1/users/me` - Update current user profile
- PUT `/api/v1/users/me/image` - Update user profile image
- DELETE `/api/v1/users/me/image` - Reset user profile image

### Posts
- GET `/api/v1/posts` - Get paginated posts
- POST `/api/v1/posts` - Create a new post
- GET `/api/v1/posts/{post_id}` - Get specific post
- PUT `/api/v1/posts/{post_id}` - Update post
- DELETE `/api/v1/posts/{post_id}` - Delete post
- POST `/api/v1/posts/{post_id}/like` - Like post
- DELETE `/api/v1/posts/{post_id}/like` - Unlike post
- PUT `/api/v1/posts/{post_id}/image` - Update post image
- DELETE `/api/v1/posts/{post_id}/image` - Reset post image
- POST `/api/v1/posts/{post_id}/resubmit` - Resubmit rejected post

### Moderator
- PUT `/api/v1/moderator/posts/{post_id}/decision` - Approve or reject post

### Admin
- POST `/api/v1/admin/grant-admin` - Grant admin rights to user

## Error Handling

The service uses custom exceptions for better error handling:
- `ResourceNotFoundException` - For 404 errors
- `UnauthorizedException` - For 401/403 errors
- `BadRequestException` - For 400 errors
- `StorageUnavailableException` - For 503 errors

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 