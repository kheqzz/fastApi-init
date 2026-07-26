#!/bin/bash

# FastAPI Clean Architecture Installer
# Usage: bash install.sh <project_name>
# Or one-liner:
#   curl -sL https://raw.githubusercontent.com/kheqzz/fastApi-init/main/install.sh | bash -s my_project

set -e

REPO_URL="https://github.com/kheqzz/fastApi-init.git"

# --- Argument check ---
if [ -z "$1" ]; then
    echo "❌ Error: Project name is required."
    echo ""
    echo "Usage: bash install.sh <project_name>"
    echo ""
    echo "One-liner:"
    echo "  curl -sL https://raw.githubusercontent.com/kheqzz/fastApi-init/main/install.sh | bash -s my_project"
    exit 1
fi

PROJECT_NAME="$1"
PROJECT_DIR="$(pwd)/$PROJECT_NAME"

# --- Check if target directory already exists ---
if [ -d "$PROJECT_DIR" ]; then
    echo "❌ Error: Directory '$PROJECT_DIR' already exists."
    exit 1
fi

echo "🚀 Creating new FastAPI project: $PROJECT_NAME"
echo ""

# --- Locate template source ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR=""
CLEANUP_TMP=0

# Check if running from inside the repo (local mode)
if [ -f "$SCRIPT_DIR/pyproject.toml" ] && [ -d "$SCRIPT_DIR/app" ]; then
    SOURCE_DIR="$SCRIPT_DIR"
    echo "📦 Using local template files"
else
    # Download template from GitHub
    TMP_DIR="$(mktemp -d)"
    CLEANUP_TMP=1
    echo "📥 Downloading template from GitHub..."
    if ! git clone --depth 1 "$REPO_URL" "$TMP_DIR/fastApi-init" 2>/dev/null; then
        echo "❌ Error: Failed to download template from GitHub."
        echo "   Make sure git is installed and you have internet access."
        rm -rf "$TMP_DIR"
        exit 1
    fi
    SOURCE_DIR="$TMP_DIR/fastApi-init"
    echo "✅ Template downloaded"
fi

echo ""

# --- Step 1: Create project directory ---
echo "1️⃣  Creating project directory..."
mkdir -p "$PROJECT_DIR"

# --- Step 2: Copy template files ---
echo "2️⃣  Copying project files..."
cp "$SOURCE_DIR/pyproject.toml"  "$PROJECT_DIR/"
cp "$SOURCE_DIR/.env.example"   "$PROJECT_DIR/"
cp "$SOURCE_DIR/README.md"      "$PROJECT_DIR/"
cp "$SOURCE_DIR/alembic.ini"    "$PROJECT_DIR/"

# Copy app/ directory (includes app/alembic/)
cp -r "$SOURCE_DIR/app" "$PROJECT_DIR/"

# Copy tests/
mkdir -p "$PROJECT_DIR/tests"
cp -r "$SOURCE_DIR/tests/"* "$PROJECT_DIR/tests/" 2>/dev/null || true

# --- Step 3: Initialize uv ---
echo "3️⃣  Setting up uv and installing dependencies..."
cd "$PROJECT_DIR"
uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic \
    pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart \
    2>/dev/null

# --- Step 4: Create .env ---
echo "4️⃣  Creating .env file..."
cp .env.example .env
echo "   ✅ .env created — edit it with your database URL and secret key"

# --- Step 5: Clean up temp dir ---
if [ "$CLEANUP_TMP" -eq 1 ]; then
    rm -rf "$TMP_DIR"
fi

# --- Done! ---
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Project '$PROJECT_NAME' is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Location: $PROJECT_DIR"
echo ""
echo "👉 Next steps:"
echo "   cd $PROJECT_NAME"
echo "   nano .env          # set DATABASE_URL and SECRET_KEY"
echo "   uvicorn app.main:app --reload"
echo ""
echo "🎉 Happy coding!"
