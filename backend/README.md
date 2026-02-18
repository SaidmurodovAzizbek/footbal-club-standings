# FCS Backend

⚽ **Football Club Standings** - Futbol ligalari, turni jadvallar va jonli natijalar API.

## Texnologiyalar

- **FastAPI** - Asinxron Python web framework
- **SQLAlchemy** - ORM (async)
- **PostgreSQL** / SQLite - Ma'lumotlar bazasi
- **Redis** - Kesh (jonli o'yinlar)
- **Alembic** - Database migratsiyalar

## Ishga tushirish

### 1. Virtual muhit yaratish

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# yoki
source venv/bin/activate  # Linux/Mac
```

### 2. Dependency-larni o'rnatish

```bash
pip install -r requirements.txt
```

### 3. Environment sozlash

`.env.example` ni `.env` ga nusxalang va sozlamalarni o'zgartiring:

```bash
cp .env.example .env
```

### 4. Database migratsiya

```bash
alembic upgrade head
```

### 5. Serverni ishga tushirish

```bash
uvicorn app.main:app --reload --port 8000
```

### 6. API hujjatlari

Brauzerda oching: [http://localhost:8000/docs](http://localhost:8000/docs)

## API Endpoints

| Endpoint | Method | Ta'rif |
|---|---|---|
| `/api/v1/leagues` | GET | Barcha ligalar |
| `/api/v1/leagues/{id}` | GET | Liga tafsilotlari |
| `/api/v1/clubs` | GET | Klublar ro'yxati |
| `/api/v1/clubs/{id}` | GET | Klub tafsilotlari |
| `/api/v1/matches` | GET | O'yinlar ro'yxati |
| `/api/v1/matches/live` | GET | Jonli o'yinlar |
| `/api/v1/standings/league/{id}` | GET | Liga jadvali |

## Loyiha strukturasi

```
backend/
├── app/
│   ├── main.py          # FastAPI entry point
│   ├── core/            # Konfiguratsiya, DB, security
│   ├── models/          # SQLAlchemy modellar
│   ├── schemas/         # Pydantic v2 schemaiar
│   ├── api/v1/          # REST API endpointlar
│   ├── services/        # Tashqi API klientlar
│   └── tasks/           # Background sync tasks
├── alembic/             # Migratsiyalar
├── requirements.txt
└── .env
```
