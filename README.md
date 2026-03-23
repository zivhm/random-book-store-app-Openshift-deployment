# Random Book Store - OpenShift Deployment

A dynamic Flask-based bookstore that automatically refreshes with random books from Open Library every 10 minutes, designed for deployment on OpenShift.

## Features

- Auto-Refreshing Catalog: Books automatically refresh every 10 minutes (configurable) with new random selections from Open Library
- Real Book Data: Fetches actual books from Open Library API with covers, titles, authors, and ISBNs
- Homepage: Welcome page with featured books and cover images
- Book Catalog: Browse all available books with pagination and cover art
- Book Details: Individual book pages with large cover images from Open Library
- User Authentication: Secure register and login with password hashing
- Shopping Cart: Add/remove books, update quantities (with thumbnails)
- Checkout: Simple checkout process (demo only, no payment processing)
- Health Checks: Built-in liveness and readiness probes for Kubernetes/OpenShift

## Book Data Source & Auto-Refresh

The application uses the **Open Library API** (https://openlibrary.org) to dynamically populate the catalog:

### Initial Load
- On first run: Automatically fetches 12 trending books from multiple subjects
- Real data: Actual book titles, authors, ISBNs, publication dates, and cover images
- Cover images: Served from Open Library's CDN (`covers.openlibrary.org`)

### Automatic Refresh
- Every 10 minutes (configurable): Background scheduler fetches fresh random books

### Configuration
Set via environment variables:
- `BOOKS_REFRESH_INTERVAL_MINUTES=10` - Refresh every 10 minutes (default)
- `BOOKS_COUNT=12` - Number of books to fetch (default)

## Testing the Application

1. Register a new account
2. Browse the catalog
3. Add books to cart
4. View and update cart
5. Complete checkout


## Screenshots

### Book Catalog

![Book Catalog](docs/images/catalog.png)

### Shopping Cart

![Shopping Cart](docs/images/cart.png)

## Technology Stack

- Backend: Python 3.12, Flask 3.0, Flask-Login, Flask-SQLAlchemy
- Scheduler: APScheduler for automatic book rotation
- Database: SQLite (development) / PostgreSQL (production ready)
- Frontend: HTML5, CSS3, Bootstrap 5, Jinja2 templates
- API Integration: Open Library API for real book data
- WSGI Server: Gunicorn (production)
- Container: Red Hat UBI9 Python 3.12
- Deployment: OpenShift 4.x / Kubernetes 1.24+

## Project Structure

```
store-app/
├── app/
│   ├── __init__.py          # Application factory, database init
│   ├── models.py            # Database models (User, Book, CartItem)
│   ├── openlibrary.py       # Open Library API integration
│   ├── routes.py            # Flask routes and views
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Custom styles
│   │   └── images/
│   │       └── book-placeholder.svg  # Fallback book cover
│   └── templates/           # Jinja2 HTML templates
│       ├── base.html        # Base layout
│       ├── index.html       # Homepage
│       ├── catalog.html     # Book catalog
│       ├── book_detail.html # Book details
│       ├── cart.html        # Shopping cart
│       ├── checkout.html    # Checkout
│       ├── login.html       # Login
│       └── register.html    # Registration
├── openshift/               # OpenShift/Kubernetes manifests
│   ├── all-in-one.yaml      # Single-file deployment
│   ├── deployment.yaml      # Deployment config
│   ├── service.yaml         # Service definition
│   ├── route.yaml           # Route (external access)
│   ├── secret.yaml          # Application secrets
│   └── pvc.yaml             # Persistent volume claim
├── docs/                    # Documentation
│   ├── DEPLOYMENT.md        # Detailed deployment guide
│   ├── QUICKSTART.md        # Quick start guide
│   └── images/              # Screenshots and images
│       ├── catalog.png      # Catalog page screenshot
│       └── cart.png         # Shopping cart screenshot
├── config.py                # Application configuration
├── wsgi.py                  # WSGI entry point (S2I compatible)
├── Dockerfile               # Container image definition
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── .dockerignore            # Docker ignore rules
└── .gitignore               # Git ignore rules

```

## Database Schema

Simple SQLite/PostgreSQL schema with three tables:

```
┌─────────────────┐
│      User       │
├─────────────────┤
│ id (PK)         │
│ username        │
│ password_hash   │
└─────────────────┘

┌─────────────────────┐
│        Book         │
├─────────────────────┤
│ id (PK)             │
│ title               │
│ author              │
│ isbn                │
│ description         │
│ price               │
│ stock               │
│ cover_image         │
│ published_date      │
└─────────────────────┘

┌─────────────────────┐
│      CartItem       │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK → User) │
│ book_id (FK → Book) │
│ quantity            │
└─────────────────────┘
```

**Relationships:**

- User → CartItem (one-to-many)
- Book → CartItem (one-to-many)
