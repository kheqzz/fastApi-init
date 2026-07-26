# CLAUDE.md

Dokumen ini adalah panduan kerja untuk Claude (atau siapa pun) saat membangun/mengembangkan project ini. Tujuannya: **inisialisasi project FastAPI dengan struktur Clean Architecture, async SQLAlchemy, dan Alembic untuk migration**, konsisten di setiap sesi.

---

## 1. Tujuan Project

Boilerplate/initiator FastAPI production-ready dengan:
- Clean Architecture (pemisahan repository / service / router / schema)
- Async SQLAlchemy 2.x sebagai ORM
- Alembic untuk database migration
- Pydantic v2 untuk validasi & serialisasi
- Siap dikembangkan jadi REST API skala menengah-besar

---

## 2. Tech Stack

| Layer | Teknologi |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x (async, `asyncpg` / `aiomysql` sesuai DB) |
| Migration | Alembic (async engine) |
| Validasi | Pydantic v2 (`BaseModel`, `pydantic-settings`) |
| DB Driver | PostgreSQL (default) via `asyncpg` — ganti sesuai kebutuhan |
| Auth | JWT (`python-jose` / `pyjwt`) + `passlib[bcrypt]` |
| Server | `uvicorn` (dev), `gunicorn + uvicorn.workers` (prod) |
| Env Management | `pydantic-settings` + `.env` |
| Dependency Manager | `uv` atau `poetry` (pilih salah satu, konsisten) |
| Testing | `pytest` + `pytest-asyncio` + `httpx.AsyncClient` |

---

## 3. Struktur Folder (Clean Architecture)

```
project_root/
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── app/
│   ├── main.py                      # entrypoint FastAPI app
│   ├── core/
│   │   ├── config.py                 # Settings (pydantic-settings)
│   │   ├── security.py               # JWT, hashing password
│   │   ├── exceptions.py             # custom exception classes
│   │   └── logging.py
│   ├── db/
│   │   ├── base.py                   # Base declarative class
│   │   ├── session.py                # async engine & sessionmaker
│   │   └── dependencies.py           # get_db() dependency
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── __init__.py               # import semua model (wajib utk alembic autogenerate)
│   │   └── user.py
│   ├── schemas/                      # Pydantic schemas (request/response)
│   │   └── user.py
│   ├── repositories/                 # akses data murni (query DB), tidak ada business logic
│   │   ├── base.py                   # generic CRUD repository
│   │   └── user_repository.py
│   ├── services/                     # business logic, orkestrasi antar repository
│   │   └── user_service.py
│   ├── api/
│   │   ├── deps.py                   # dependency injection (get_current_user, dll)
│   │   └── v1/
│   │       ├── router.py             # gabungan semua router v1
│   │       └── endpoints/
│   │           └── user.py
│   └── utils/
│       └── pagination.py
├── tests/
│   ├── conftest.py
│   └── test_user.py
├── .env
├── .env.example
├── pyproject.toml
└── README.md
```

**Alur dependency (satu arah, jangan dibalik):**
`endpoint (router)` → `service` → `repository` → `model`
`schema` dipakai di layer `endpoint` (request/response), boleh dipakai `service` untuk return type, **tidak boleh** dipakai di `repository`.

---

## 4. Aturan & Konvensi Coding

### Umum
- Semua I/O ke database **wajib async** (`AsyncSession`, `await session.execute(...)`).
- Jangan taruh query SQLAlchemy langsung di endpoint/router — selalu lewat `repository`.
- Jangan taruh business logic (validasi kompleks, kalkulasi, kombinasi beberapa repository) di `repository` — itu tugas `service`.
- Endpoint hanya bertugas: terima request → panggil service → return response. Tidak ada logic di endpoint.

### Repository Pattern
- Buat `BaseRepository` generic (pakai `Generic[ModelType]`) untuk CRUD dasar: `get`, `get_all`, `create`, `update`, `delete`.
- Repository spesifik (`UserRepository`) inherit dari `BaseRepository`, tambahkan query custom di sini.

### Service Layer
- Service menerima `AsyncSession` atau `repository` via dependency injection (constructor/`Depends`), bukan buat session sendiri.
- Semua exception bisnis (misal "email sudah terdaftar") di-raise di service pakai custom exception class dari `core/exceptions.py`, ditangkap oleh exception handler global di `main.py`.

### Schema (Pydantic v2)
- Pisahkan schema per keperluan: `UserCreate`, `UserUpdate`, `UserOut`/`UserRead`.
- Gunakan `model_config = ConfigDict(from_attributes=True)` untuk schema yang di-return dari ORM object.

### Model (SQLAlchemy)
- Semua model wajib inherit dari `Base` di `db/base.py`.
- **Wajib** import setiap model baru ke `app/models/__init__.py` — kalau tidak, Alembic autogenerate tidak akan mendeteksi perubahan.
- Gunakan `Mapped[]` dan `mapped_column()` (SQLAlchemy 2.0 style), bukan `Column()` lama.

### Naming Convention
- File & folder: `snake_case`
- Class: `PascalCase`
- Function/variable: `snake_case`
- Endpoint path: `kebab-case` (misal `/user-profile`)

---

## 5. Alembic Setup (Async)

`alembic/env.py` harus dikonfigurasi untuk async engine:

```python
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from alembic import context

from app.core.config import settings
from app.db.base import Base
from app.models import *  # noqa — wajib, agar semua model ter-load

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

### Perintah Alembic yang sering dipakai
```bash
# generate migration baru otomatis dari perubahan model
alembic revision --autogenerate -m "deskripsi perubahan"

# jalankan migration ke versi terbaru
alembic upgrade head

# rollback satu step
alembic downgrade -1

# lihat history migration
alembic history

# lihat versi saat ini
alembic current
```

**Aturan wajib:** setiap kali menambah/mengubah model, selalu jalankan `alembic revision --autogenerate` lalu **review dulu file migration yang dihasilkan** sebelum `upgrade head` — autogenerate tidak selalu 100% akurat (index, enum, rename kolom sering meleset).

---

## 6. Environment Variables (`app/core/config.py`)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Clean Architecture"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
```

`.env.example` harus selalu disinkronkan setiap kali ada variable baru.

---

## 7. Perintah Setup Project dari Nol

```bash
# 1. init dependency manager (pilih salah satu)
uv init
uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic \
       pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart

# 2. init alembic
alembic init -t async alembic

# 3. jalankan server dev
uvicorn app.main:app --reload

# 4. generate migration pertama
alembic revision --autogenerate -m "init tables"
alembic upgrade head
```

---

## 8. Testing

- Gunakan `pytest-asyncio` dengan `asyncio_mode = auto` di `pyproject.toml`.
- Gunakan test database terpisah (jangan pakai DB development).
- `httpx.AsyncClient(app=app, base_url="http://test")` untuk test endpoint.
- Struktur test mengikuti struktur `app/` (1 file model/service → 1 file test).

---

## 9. Checklist Sebelum Commit

- [ ] Model baru sudah di-import di `app/models/__init__.py`
- [ ] Migration sudah di-generate dan direview manual
- [ ] Tidak ada query SQLAlchemy langsung di router/endpoint
- [ ] Business logic tidak bocor ke repository
- [ ] Schema request/response sudah dipisah (`Create`/`Update`/`Out`)
- [ ] `.env.example` sudah update kalau ada env var baru
- [ ] Endpoint baru sudah didaftarkan di `api/v1/router.py`

---

## 10. Catatan Tambahan

- Gunakan `Depends()` untuk semua dependency (session DB, current user, repository, service) — jangan instansiasi manual di dalam function endpoint.
- Semua response error sebaiknya konsisten formatnya (pakai exception handler global, bukan `HTTPException` tersebar di service).
- Kalau butuh pagination, gunakan helper generic di `utils/pagination.py`, jangan duplikasi logic di tiap endpoint.
