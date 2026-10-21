
# MiniEcommerce - PWD301

A mini e-commerce application developed with Flask for the PWD301 project.

## 1. Technology Stack

- Backend: Python 3.12, Flask 3
- Frontend: HTML, CSS, Bootstrap, JavaScript, Jinja2
- ORM: SQLAlchemy
- Authentication: Flask-Login and JWT
- Security: CSRF protection and role-based access control
- Database: SQLite (local development), Microsoft SQL Server (Docker)
- Deployment: Docker, Docker Compose, Gunicorn
- Testing: pytest

## 2. Main Features

### Customer

- Browse and search products
- Filter by category and price
- Sort products and navigate pagination
- View product details
- Add products to cart
- Update and remove cart items
- Place orders and provide delivery information
- Log in and view permitted order information

### Admin

- Access the administration dashboard
- Manage products
- View and search orders
- Filter orders by status
- Update order status

### API

- Public product listing and product details
- JWT authentication
- Order listing and order details
- Role-based authorization for order management

## 3. Requirements

For local development:

- Python 3.12
- pip
- Git

For Docker deployment:

- Docker Desktop
- Docker Compose
- WSL2 on Windows

## 4. Run Locally with SQLite

Open PowerShell in the project directory.

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a local environment configuration:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and configure appropriate private values for:

```dotenv
SECRET_KEY=your-local-flask-secret
JWT_SECRET_KEY=your-local-jwt-secret
DATABASE_URL=sqlite:///dev.db
```

For a new, empty local database, initialize the schema and sample products:

```powershell
python seed.py
```

Do not use reset commands when preserving existing data.

Start Flask:

```powershell
python run.py
```

Open:

http://127.0.0.1:5000

## 5. Run with Docker and SQL Server

### Step 1: Configure environment variables

Ensure the local `.env` file exists and contains private values for:

```dotenv
SECRET_KEY=your-private-flask-secret
JWT_SECRET_KEY=your-private-jwt-secret
MSSQL_SA_PASSWORD=your-strong-sql-server-password
```

Use a strong SQL Server password that satisfies SQL Server password complexity requirements.

Never commit `.env` or real credentials to Git.

### Step 2: Build the web image

```powershell
docker compose build web
```

### Step 3: Start SQL Server

```powershell
docker compose up -d db
```

Wait until SQL Server is ready to accept connections.

### Step 4: Bootstrap the database

For a new, empty SQL Server deployment:

```powershell
docker compose run --rm --no-deps web python -m scripts.bootstrap_db
```

The bootstrap script creates `MiniEcommerceDB` if necessary and initializes the application tables.

### Step 5: Stamp the current schema revision

For a newly initialized database whose schema was created using `db.create_all()`:

```powershell
docker compose run --rm --no-deps web flask --app run:app db stamp head
```

Do not use `stamp head` as a replacement for applying migrations to an existing, outdated database schema.

### Step 6: Start the website

```powershell
docker compose up -d web
docker compose ps
```

Open the HTTP address corresponding to the published web port, typically:

http://127.0.0.1:5000

If the host port has been changed to 5050 in `docker-compose.yml`, use:

http://127.0.0.1:5050

A newly initialized SQL Server database does not contain the previously created user accounts or orders.

For an empty demo database, sample categories and products can be created with:

```powershell
docker compose run --rm --no-deps web python seed.py
```

This sample-data script does not create Admin or Customer accounts.

## 6. Migrate Existing SQLite Data to SQL Server

Use this procedure only when transferring data into an empty SQL Server database.

Create a consistent SQLite backup while the SQLite application is not performing writes:

```powershell
python -c "import sqlite3; src=sqlite3.connect('instance/dev.db'); dst=sqlite3.connect('instance/dev_backup.db'); src.backup(dst); dst.close(); src.close(); print('BACKUP OK')"
```

Stop the Docker web service:

```powershell
docker compose stop web
```

Run the migration using the read-only SQLite backup:

```powershell
docker compose run --rm --no-deps --volume "./instance/dev_backup.db:/tmp/legacy.db:ro" web python -m scripts.migrate_sqlite_to_mssql
```

The script transfers:

- DANHMUC: categories
- NGUOIDUNG: users
- SANPHAM: products
- DONHANG: orders
- CHITIETDONHANG: order items

The migration preserves existing IDs and password hashes.

The destination database must be empty. The migration script refuses to run if the destination contains records.

After a successful migration:

```powershell
docker compose up -d web
```

## 7. API Endpoints

| Method | Endpoint | Access |
|---|---|---|
| GET | `/api/health` | Public |
| GET | `/api/products` | Public |
| GET | `/api/products/<id>` | Public |
| POST | `/api/auth/token` | Public login |
| GET | `/api/orders` | JWT required |
| GET | `/api/orders/<id>` | JWT and ownership/role checks |
| PUT | `/api/orders/<id>/status` | Admin or Staff |

Example JWT login request:

```http
POST /api/auth/token
Content-Type: application/json

{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

Authenticated requests must include:

```http
Authorization: Bearer <access_token>
```

## 8. Run Tests

Activate the Python virtual environment, then run:

```powershell
python -m pytest -q
```

The pytest configuration uses an isolated SQLite test database. It does not use the production SQL Server database.

Latest verified local result:

```text
110 passed in 4.36s
```

## 9. Useful Docker Commands

View running services:

```powershell
docker compose ps
```

View web logs:

```powershell
docker compose logs --tail=100 web
```

View SQL Server logs:

```powershell
docker compose logs --tail=100 db
```

Check the current migration revision:

```powershell
docker compose exec web flask --app run:app db current
```

Stop the containers without deleting the database volume:

```powershell
docker compose down
```

**Warning:** `docker compose down -v` deletes the associated Docker volumes and may permanently remove local SQL Server data.

## 10. Security Notes

- Keep `.env` private.
- Never commit passwords, access tokens or secret keys.
- Use strong credentials outside development.
- HTML form submissions are protected by CSRF validation.
- Order APIs require JWT authentication.
- Customer access is restricted to permitted orders.
- Admin and Staff permissions are checked against database roles.
- Demo account credentials must not be used in production.

## 11. Project Structure

```text
MiniEcommerce-PWD301/
├── app/
│   ├── admin/
│   ├── api/
│   ├── auth/
│   ├── models/
│   ├── services/
│   ├── shop/
│   ├── static/
│   └── templates/
├── migrations/
├── scripts/
│   ├── bootstrap_db.py
│   └── migrate_sqlite_to_mssql.py
├── tests/
├── config.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── run.py
├── seed.py
└── README.md
```

## 12. Project Verification

The project has been manually verified with Docker and SQL Server, including:

- SQL Server database initialization
- Migration of existing SQLite records
- Product listing
- User login
- Shopping cart operations
- Checkout and order persistence
- Admin order management
- Role-based authorization
- JWT authentication and order listing

The restored demo database was verified to contain 4 categories, 20 products, 2 users, 6 orders and 8 order items immediately after migration. Subsequent test orders may change these counts.
