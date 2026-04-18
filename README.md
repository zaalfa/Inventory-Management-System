# 🗃️ Inventory Management System (IMS)

Full-stack portfolio project: **Django REST Framework + React + PostgreSQL + Redis + Docker**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2, Django REST Framework, SimpleJWT |
| Real-time | Django Channels, WebSocket, Redis |
| Task Queue | Celery + Celery Beat |
| Database | PostgreSQL 16 |
| Frontend | React 18, Redux Toolkit, Tailwind CSS |
| Charts | Recharts |
| Containerization | Docker + Docker Compose |
| Testing (BE) | pytest, pytest-django, factory-boy |
| Testing (FE) | Vitest, Testing Library |
| File Storage | Cloudinary |
| Deployment | Daphne (ASGI), Nginx, Gunicorn-ready |

---

## Fitur

- ✅ JWT Authentication + Refresh Token + Blacklist
- ✅ Role-Based Access Control (Admin / Manager / Cashier)
- ✅ Product CRUD + Soft Delete + SKU Auto-Generate
- ✅ Category Management
- ✅ Atomic Stock Transactions (In / Out / Adjustment)
- ✅ Audit Trail — transaksi immutable
- ✅ Real-time Stock Alerts via WebSocket
- ✅ Celery periodic stock check
- ✅ Dashboard dengan charts (Recharts)
- ✅ Reports: Stock & Transaction dengan filter tanggal
- ✅ Export CSV (Stock & Transactions)
- ✅ Rate Limiting API
- ✅ Database Indexes untuk performa
- ✅ Full test coverage backend + frontend

---

## Struktur Project

```
ims/
├── backend/
│   ├── apps/
│   │   ├── users/          # Auth, JWT, RBAC
│   │   ├── products/       # Product & Category CRUD
│   │   ├── transactions/   # Stock transactions
│   │   ├── alerts/         # Stock alerts + WebSocket
│   │   └── reports/        # Reports + CSV export
│   ├── config/             # Django settings, URLs, ASGI, Celery
│   ├── tests/              # Test suite (130+ test cases)
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/            # Axios client + all API calls
│   │   ├── components/     # UI components + Layout
│   │   ├── hooks/          # useAuth, useAlertSocket
│   │   ├── pages/          # Dashboard, Products, Transactions, Alerts, Reports, Users
│   │   ├── store/          # Redux Toolkit slices
│   │   ├── test/           # Frontend tests (65+ test cases)
│   │   └── utils/          # Helpers (formatCurrency, etc.)
│   ├── nginx.conf
│   └── Dockerfile
└── docker-compose.yml
```

---

## Quick Start

### 1. Clone & setup env

```bash
git clone <repo>
cd ims

cp backend/.env.example backend/.env
# Edit backend/.env — ganti SECRET_KEY dan Cloudinary credentials
```

### 2. Jalankan dengan Docker

```bash
docker-compose up --build
```

Setelah semua container running:

```bash
# Seed data demo (optional)
docker-compose exec backend python manage.py seed_data
```

### 3. Buka browser

- **Frontend:** http://localhost:3000
- **Django Admin:** http://localhost:8000/admin
- **API:** http://localhost:8000/api/

---

## Demo Accounts (setelah seed_data)

| Email | Password | Role |
|---|---|---|
| admin@ims.com | Admin123! | Admin |
| manager@ims.com | Manager123! | Manager |
| cashier@ims.com | Cashier123! | Cashier |

---

## Development (tanpa Docker)

### Backend

```bash
cd backend

# Buat virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Pastikan PostgreSQL dan Redis berjalan
# Edit .env untuk koneksi lokal

python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Celery (opsional untuk alerts)

```bash
cd backend
celery -A config worker -l info
celery -A config beat -l info
```

---

## Menjalankan Tests

### Backend

```bash
cd backend
pip install -r requirements.txt

# Jalankan semua tests + coverage
pytest

# Lihat coverage report di browser
open htmlcov/index.html
```

### Frontend

```bash
cd frontend
npm install

# Jalankan semua tests
npm test

# Dengan coverage
npm run test:coverage
```

---

## API Endpoints

### Auth
```
POST   /api/auth/register/          Daftar user baru (cashier)
POST   /api/auth/login/             Login, dapat access + refresh token
POST   /api/auth/logout/            Blacklist refresh token
POST   /api/auth/token/refresh/     Refresh access token
GET    /api/auth/me/                Profil saya
PATCH  /api/auth/me/                Update profil
PUT    /api/auth/me/change-password/ Ganti password
GET    /api/auth/users/             List semua user (Admin only)
DELETE /api/auth/users/{id}/        Soft-delete user (Admin only)
POST   /api/auth/users/{id}/activate/ Aktifkan kembali user
```

### Products
```
GET    /api/products/               List produk (filter: category, low_stock, price range)
POST   /api/products/               Tambah produk (Admin)
GET    /api/products/{id}/          Detail produk
PATCH  /api/products/{id}/          Update produk (Admin)
DELETE /api/products/{id}/          Soft-delete produk (Admin)
POST   /api/products/{id}/restore/  Restore produk (Admin)
GET    /api/products/low_stock/     Daftar produk stok rendah
GET    /api/products/categories/    List kategori
POST   /api/products/categories/    Tambah kategori (Admin)
```

### Transactions
```
POST   /api/transactions/           Catat transaksi (semua role)
GET    /api/transactions/           List transaksi (Admin/Manager)
GET    /api/transactions/{id}/      Detail transaksi
```

### Alerts
```
GET    /api/alerts/                 List alerts (Admin/Manager)
POST   /api/alerts/{id}/resolve/    Resolve satu alert
POST   /api/alerts/resolve_all/     Resolve semua
GET    /api/alerts/summary/         Ringkasan alert
WS     /ws/alerts/                  WebSocket real-time alerts
```

### Reports
```
GET    /api/reports/dashboard/      Data dashboard
GET    /api/reports/stock/          Laporan stok
GET    /api/reports/transactions/   Laporan transaksi (filter: date_from, date_to, period)
GET    /api/reports/export/stock/           Download CSV stok
GET    /api/reports/export/transactions/    Download CSV transaksi
```

---

## Environment Variables

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,localhost

DB_NAME=ims_db
DB_USER=postgres
DB_PASSWORD=strongpassword
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379

CORS_ALLOWED_ORIGINS=https://yourdomain.com

CLOUDINARY_CLOUD_NAME=xxx
CLOUDINARY_API_KEY=xxx
CLOUDINARY_API_SECRET=xxx
```

---

## Deployment ke Production

1. Set `DEBUG=False` di `.env`
2. Ganti `SECRET_KEY` dengan nilai random yang kuat
3. Set `ALLOWED_HOSTS` ke domain kamu
4. Setup Cloudinary untuk image upload
5. Gunakan `docker-compose up -d --build`

Untuk cloud deployment, project ini siap di-deploy ke:
- **Railway** — connect repo, set env vars, deploy
- **Render** — Dockerfile detected otomatis
- **VPS** — Docker Compose langsung jalan

---

## License

MIT — bebas digunakan untuk portfolio dan pembelajaran.
