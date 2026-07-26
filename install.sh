#!/bin/bash

# FastAPI Project Installer
# Usage: ./install.sh <project_name>
# Example: ./install.sh my_api

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -z "$1" ]; then
    echo "❌ Error: Project name is required."
    echo "Usage: $0 <project_name>"
    echo "Example: $0 my_api"
    exit 1
fi

PROJECT_NAME="$1"
PROJECT_DIR="$(pwd)/$PROJECT_NAME"

# Check if target directory already exists
if [ -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Directory '$PROJECT_DIR' already exists."
    exit 1
fi

echo "🚀 Creating new FastAPI project: $PROJECT_NAME"

# 1. Create project directory
echo "1️⃣ Creating project directory..."
mkdir -p "$PROJECT_DIR"

# 2. Copy template files into the new directory
echo "2️⃣ Copying project files..."
cp "$SCRIPT_DIR/pyproject.toml" "$PROJECT_DIR/"
cp "$SCRIPT_DIR/.env.example"  "$PROJECT_DIR/"
cp "$SCRIPT_DIR/README.md"     "$PROJECT_DIR/"
cp "$SCRIPT_DIR/alembic.ini"   "$PROJECT_DIR/"

# Copy the app/ directory (includes app/alembic/)
cp -r "$SCRIPT_DIR/app" "$PROJECT_DIR/"

# Copy tests/
mkdir -p "$PROJECT_DIR/tests"
cp -r "$SCRIPT_DIR/tests/"* "$PROJECT_DIR/tests/" 2>/dev/null || true

# 3. Initialize uv in the new project directory
echo "3️⃣ Initializing uv..."
cd "$PROJECT_DIR"
if [ ! -f "pyproject.toml" ]; then
    uv init
fi

# 4. Add project dependencies
echo "4️⃣ Adding dependencies..."
uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic \
    pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart

# 5. Initialize Alembic (if alembic directory is empty or missing)
if [ ! -f "$PROJECT_DIR/app/alembic/env.py" ]; then
    echo "5️⃣ Setting up Alembic..."
    uv run alembic init -t async alembic
else
    echo "5️⃣ Alembic already initialized. Skipping..."
fi

# 6. Create .env file from example if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "6️⃣ Creating .env file from .env.example..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "✅ .env file created. Please edit it with your database URL and settings."
else
    echo "✅ .env file already exists. Skipping creation."
fi

# 7. Show next steps
echo ""
echo "7️⃣ ✅ Setup complete!"
echo ""
echo "📁 Project created at: $PROJECT_DIR"
echo ""
echo "💡 Next steps:"
echo "   cd $PROJECT_NAME"
echo "   • Edit .env with your database URL and secret keys"
echo "   • Run migrations: alembic upgrade head"
echo "   • Start development server: uvicorn app.main:app --reload"
echo ""
echo "🎉 Happy coding!"
