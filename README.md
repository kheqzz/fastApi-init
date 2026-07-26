# FastAPI Clean Architecture

Boilerplate/initiator FastAPI production-ready with Clean Architecture.

## Features

- Clean Architecture (repository / service / router / schema)
- Async SQLAlchemy 2.x as ORM
- Alembic for database migration
- Pydantic v2 for validation & serialization
- JWT authentication with python-jose
- Password hashing with passlib[bcrypt]

## Quick Start

### One-liner (recommended)

Just copy-paste this line in your terminal:

```bash
curl -sL https://raw.githubusercontent.com/kheqzz/fastApi-init/main/install.sh | bash -s my_project
```

> Works on **bash**, **zsh**, and **fish** shell.

That's it! The installer will:
1. Download the latest project template from GitHub
2. Create your new FastAPI project
3. Install all dependencies
4. Create a ready-to-use `.env` file

After installation, you will be located in your new project directory. Edit `.env` and you can start developing immediately.

### Alternative: Clone first (if you prefer)

```bash
# Clone the repo
git clone https://github.com/kheqzz/fastApi-init.git
cd fastApi-init

# Run the installer
chmod +x install.sh
./install.sh my_project

# Go to your project
cd my_project

# Edit .env with your database URL and secret key
uvicorn app.main:app --reload
```

## What the Installer Does

1. Copies all template files into your new project folder
2. Initializes `uv` and installs all dependencies
3. Sets up Alembic with async support
4. Creates `.env` from `.env.example`
5. Prints next steps for you

## Development

```bash
# Run development server
uvicorn app.main:app --reload

# Generate migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Run tests
uv run pytest
```

## Project Structure

```
project_root/
├── alembic.ini
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── core/                    # Config, security, exceptions
│   ├── db/                      # Database session & dependencies
│   ├── models/                  # SQLAlchemy ORM models
│   ├── schemas/                 # Pydantic schemas
│   ├── repositories/            # Data access layer
│   ├── services/                # Business logic
│   ├── api/v1/endpoints/        # API routes
│   ├── alembic/                 # Alembic migration files
│   └── utils/                   # Helpers (pagination, etc.)
├── tests/
├── .env
├── .env.example
├── pyproject.toml
└── README.md
```

See `CLAUDE.md` for detailed documentation.

## License

MIT
