# RBAC_ProtoApp

A small FastAPI prototype demonstrating role-based access control (RBAC) with a minimal CRUD backend. The project contains an API for users, authentication, posts and comments, and includes security utilities, Pydantic schemas, and SQLAlchemy models.

## Contents

- `Backend/` - Python FastAPI application source
  - `main.py` - FastAPI app entrypoint
  - `routers/` - API route modules (`auth.py`, `users.py`, `posts.py`, `comments.py`)
  - `models.py` - SQLAlchemy models
  - `schemas.py` - Pydantic request/response schemas
  - `crud.py` - helper functions to interact with the DB
  - `database.py` - DB engine/session setup
  - `security.py` - password hashing and token helpers
  - `dependencies.py` - shared dependencies (current_user, role checks, etc.)
  - `requirements.txt` - Python dependencies

## Goals

- Provide an example RBAC-capable API demonstrating:
  - User registration and authentication
  - Role-based route protection
  - Basic CRUD for posts and comments
  - Clear separation of routers, models, schemas, and security logic

## Prerequisites

- Python 3.11+

## Install

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r Backend\requirements.txt
```

## Run the app

Start the FastAPI app using uvicorn from the repository root:

```powershell
uvicorn Backend.main:app --reload
```

By default uvicorn will serve on `http://127.0.0.1:8000`. If the project uses a different host/port or settings, check `Backend/main.py`.

Open the interactive docs at `http://127.0.0.1:8000/docs` (Swagger UI) or the Redoc docs at `/redoc`.

## Configuration

- The project currently uses the files in `Backend/` for DB and security configuration. If there are environment variables or a `.env` file support, set values before starting the server. Look in `Backend/database.py` and `Backend/security.py` for relevant configuration keys (database URL, secret keys, token expiration).

## API Overview

This project provides the following logical endpoints:

- Authentication (`Backend/routers/auth.py`)

  - POST /auth/register - register a new user
  - POST /auth/login - obtain access token (JWT)

- Users (`Backend/routers/users.py`)

  - GET /users/me - current user profile
  - GET /users/ - list users (admin only)
  - PATCH/PUT /users/{id} - update user (role protected)

- Posts (`Backend/routers/posts.py`)

  - GET /posts/ - list posts
  - POST /posts/ - create post (authenticated)
  - GET /posts/{id} - get post
  - PUT/PATCH /posts/{id} - update post (owner or role)
  - DELETE /posts/{id} - delete post (owner or role)

- Comments (`Backend/routers/comments.py`)
  - GET /comments/ - list comments
  - POST /comments/ - create comment (authenticated)
  - DELETE /comments/{id} - delete comment (owner or role)

Use the interactive Swagger UI to explore the exact request bodies and responses. Example curl to log in and call an authenticated endpoint:

```powershell
# Login and save token (PowerShell)
$tokenResponse = curl -Method POST -Uri http://127.0.0.1:8000/auth/login -Body (@{username='alice'; password='secret'} | ConvertTo-Json) -ContentType 'application/json'
$token = ($tokenResponse | ConvertFrom-Json).access_token

# Use token to call protected endpoint
curl -Method GET -Uri http://127.0.0.1:8000/users/me -Headers @{ Authorization = "Bearer $token" }
```

Adjust username/password and endpoints to match your implementation.

## Data models and schemas

- `models.py` - SQLAlchemy ORM models for User, Role, Post, Comment
- `schemas.py` - Pydantic models used for request validation and responses. Typical shapes include UserCreate, UserRead, Token, PostCreate, PostRead, CommentCreate, etc.

## License

This repository doesn't include an explicit license file. If you want permissive usage, add an `LICENSE` file (e.g., MIT) and note it here.

## Next steps

- Wire up a persistent database (Postgres or SQLite for quick starts). Ensure `Backend/database.py` points to the correct database URL.
- Add role management endpoints (assign roles to users).
- Harden security: refresh tokens, revoke tokens, rate limiting.

---

## How RBAC (Role-Based Access Control) works in this project

This project uses a simple, explicit RBAC implementation built from three pieces: the database models, JWT-based authentication, and FastAPI dependency helpers that enforce role checks.

- Models: `Backend/models.py`

  - Users and Roles have a many-to-many relationship via the `user_roles` association table. A `User` has a `roles` relationship which contains `Role` objects with a `name` attribute (e.g. `admin`, `author`, `user`).

- Authentication & tokens: `Backend/security.py`

  - When a user logs in, the token endpoint issues a JWT access token. The token payload includes a `sub` claim set to the username. The token is created with `create_access_token(...)` and validated with `decode_token(...)`.
  - The token is used by the `OAuth2PasswordBearer` scheme; `dependencies.get_current_user` decodes the token, extracts the `sub` username, and loads the `User` from the database.

- Role enforcement helpers: `Backend/dependencies.py`
  - `require_role(*allowed_roles)` returns a dependency that checks whether the current user's assigned roles include any of the allowed roles. It raises HTTP 403 if the user lacks the role.
  - `is_admin_or_owner(post_id, ...)` is a more specialized dependency used by post modification routes. It permits the action if either:
    - the current user has the `admin` role, or
    - the current user has the `author` role and is the owner (author) of the post being modified.

How the pieces interact in a request:

1. Client includes the JWT `Authorization: Bearer <token>` header.
2. FastAPI's dependency `get_current_user` decodes the token and returns the `User` object from the DB (so subsequent checks can inspect `user.roles`).
3. A route can require a role using `Depends(require_role("admin"))` (or several roles). If the user doesn't have a matching role, the dependency raises 403.
4. For ownership checks (posts/comments) the route can use `Depends(is_admin_or_owner)` which performs both existence and permission checks and returns the post and user context when allowed.

Design notes:

- Roles are stored in the DB as simple strings. This is flexible but not hierarchical. If you need role hierarchies (e.g., `admin` implies `author`), either assign both roles to admin accounts or enhance the logic.
- The JWT only contains the username (`sub`) and expiration; role membership is looked up from the database for each request. This keeps tokens small and allows role changes to take effect immediately (no token revocation required for role changes), but it does add a DB lookup per authenticated request.
- For higher scale, you could embed role claims into the token (with care for revocation) or cache role lookups.
