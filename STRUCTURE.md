# Repository Structure

Clean, production-ready repository for the Random Book Store application and OpenShift deployment.

## Overview

**Random Book Store** is a Flask-based e-commerce application that:
- **Auto-refreshes** with new random books every 10 minutes (configurable)
- Fetches real book data from Open Library API
- Provides user authentication and shopping cart functionality
- Follows OpenShift security best practices
- Can be deployed via container image or Source-to-Image (S2I)

```
store-app/
├── app/                          # Application code
│   ├── __init__.py              # App factory, database initialization
│   ├── models.py                # Database models (User, Book, CartItem)
│   ├── openlibrary.py           # Open Library API integration
│   ├── routes.py                # Flask routes and views
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css        # Custom styles
│   │   └── images/
│   │       └── book-placeholder.svg  # Default book cover
│   └── templates/               # Jinja2 HTML templates
│       ├── base.html            # Base template
│       ├── index.html           # Homepage
│       ├── catalog.html         # Book catalog
│       ├── book_detail.html     # Book details
│       ├── cart.html            # Shopping cart
│       ├── checkout.html        # Checkout page
│       ├── login.html           # Login page
│       └── register.html        # Registration page
│
├── .s2i/                         # Source-to-Image build hooks
│   └── bin/
│       ├── assemble              # Custom build script
│       ├── pre_build             # Pre-build hook
│       ├── post_build            # Post-build hook
│       └── run                   # Container startup script
│
├── openshift/                    # OpenShift deployment manifests
│   ├── all-in-one.yaml          # Single file deployment
│   ├── deployment.yaml          # Deployment configuration
│   ├── service.yaml             # Service definition
│   ├── route.yaml               # Route (external access)
│   ├── secret.yaml              # Secrets
│   ├── pvc.yaml                 # Persistent volume claim
│   └── DEPLOYMENT.md            # Detailed deployment guide
│
├── config.py                     # Application configuration
├── wsgi.py                       # WSGI entry point (OpenShift S2I)
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container image definition
├── .dockerignore                 # Docker build exclusions
├── .gitignore                    # Git exclusions
├── README.md                     # Main documentation
├── QUICKSTART.md                 # Quick start guide
└── STRUCTURE.md                  # This file - repository structure
```

## What's Excluded (via .gitignore)

- Python cache: `__pycache__/`, `*.pyc`
- Virtual environments: `.venv/`, `venv/`, `env/`
- Database files: `*.db`, `*.sqlite3`
- IDE files: `.vscode/`, `.idea/`
- Environment files: `.env`
- Development tools: `uv.lock`, `.python-version`, `pyproject.toml`
- Test scripts: `test_*.py`
- Local scripts: `reset_database.sh`
- Claude artifacts: `.claude/`

## File Descriptions

### Application Code (`app/`)
- **`__init__.py`**: Flask app factory, initializes database, fetches books from Open Library
- **`models.py`**: SQLAlchemy models for User, Book, and CartItem
- **`openlibrary.py`**: API integration module for fetching trending books
- **`routes.py`**: All Flask routes including health checks (`/health`, `/ready`)
- **`templates/`**: Jinja2 HTML templates with Bootstrap 5 styling
- **`static/`**: CSS and SVG placeholder for book covers

### S2I Build Hooks (`.s2i/`)
- **`assemble`**: Custom build script that calls pre/post build hooks
- **`pre_build`**: Runs before pip install (verify Python version, setup environment)
- **`post_build`**: Runs after dependencies installed (cleanup, list packages)
- **`run`**: Custom container startup script with Gunicorn configuration

### OpenShift Deployment (`openshift/`)
- **`all-in-one.yaml`**: Complete deployment in single file (easiest option)
- **`deployment.yaml`**: Pod deployment with health probes and resource limits
- **`service.yaml`**: ClusterIP service on port 8080
- **`route.yaml`**: External access with TLS edge termination
- **`secret.yaml`**: Flask SECRET_KEY (change for production!)
- **`pvc.yaml`**: 1Gi persistent volume for SQLite database
- **`DEPLOYMENT.md`**: Comprehensive deployment guide

### Root Files
- **`config.py`**: App configuration with environment variable support
- **`wsgi.py`**: WSGI entry point, S2I compatible
- **`requirements.txt`**: Python dependencies (Flask, SQLAlchemy, requests, etc.)
- **`Dockerfile`**: Multi-stage build with UBI9 Python 3.12
- **`README.md`**: Complete application documentation
- **`QUICKSTART.md`**: Quick deployment instructions
- **`STRUCTURE.md`**: This file

## What's Included

✅ **Production-ready code**: No test files or development artifacts
✅ **OpenShift compliant**: Non-root, health checks, resource limits
✅ **Real data**: Open Library API integration
✅ **Complete docs**: README, QUICKSTART, DEPLOYMENT guides
✅ **Deployment options**: Container build, S2I, or all-in-one YAML

## What's Excluded

❌ Development tools (pytest, coverage, etc.)
❌ Test scripts and fixtures
❌ Database files (*.db)
❌ Python cache (__pycache__)
❌ Virtual environments (.venv)
❌ IDE configurations

This keeps the repository clean, lightweight, and focused on what's essential for deployment.
