# Random Book Store - OpenShift Deployment

A dynamic Flask-based bookstore that automatically refreshes with random books from Open Library every 10 minutes, designed for deployment on OpenShift.

## Features

- **🔄 Auto-Refreshing Catalog**: Books automatically refresh every 10 minutes (configurable) with new random selections from Open Library
- **📚 Real Book Data**: Fetches actual books from Open Library API with covers, titles, authors, and ISBNs
- **🏠 Homepage**: Welcome page with featured books and cover images
- **📖 Book Catalog**: Browse all available books with pagination and cover art
- **🔍 Book Details**: Individual book pages with large cover images from Open Library
- **🔐 User Authentication**: Secure register and login with password hashing
- **🛒 Shopping Cart**: Add/remove books, update quantities (with thumbnails)
- **💳 Checkout**: Simple checkout process (demo only, no payment processing)
- **❤️ Health Checks**: Built-in liveness and readiness probes for Kubernetes/OpenShift

## Technology Stack

- **Backend**: Python 3.12, Flask 3.0, Flask-Login, Flask-SQLAlchemy
- **Scheduler**: APScheduler for automatic book rotation
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: HTML5, CSS3, Bootstrap 5, Jinja2 templates
- **API Integration**: Open Library API for real book data
- **WSGI Server**: Gunicorn (production)
- **Container**: Red Hat UBI9 Python 3.12
- **Deployment**: OpenShift 4.x / Kubernetes 1.24+

## OpenShift Compliance

This application follows OpenShift security and deployment best practices:

- ✅ Runs as **non-root user** (UID 1001)
- ✅ Uses **non-privileged port** 8080
- ✅ Implements **health check endpoints** (`/health`, `/ready`)
- ✅ Proper **file permissions** for random UID assignment (GID 0)
- ✅ Uses **Red Hat UBI** base image
- ✅ Includes **resource limits** and **security context**

## Local Development

### Prerequisites

- Python 3.12+ (3.11+ supported)
- pip

### Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python wsgi.py
   ```

   On first run, the app will:
   - Create the database
   - Fetch 12 real books from Open Library API
   - Populate the catalog with actual book data and covers

4. **Access the application:** Open your browser to `http://localhost:8080`

### Reset Database (Get Fresh Books)

To reset the database and fetch new books from Open Library:

```bash
rm random-book-store.db
python wsgi.py
```

## OpenShift Deployment

### Method 1: Using Pre-built Container Image

1. Build the container image:
   ```bash
   docker build -t random-book-store:latest .
   ```

2. Tag and push to your registry:
   ```bash
   docker tag random-book-store:latest <your-registry>/random-book-store:latest
   docker push <your-registry>/random-book-store:latest
   ```

3. Update `openshift/deployment.yaml` with your image registry.

4. Deploy to OpenShift:
   ```bash
   oc apply -f openshift/
   ```

### Method 2: Using Source-to-Image (S2I)

1. Create a new application from source:
   ```bash
   oc new-app python:3.12~https://github.com/<your-repo>/store-app \
     --name=random-book-store
   ```

2. Expose the service:
   ```bash
   oc expose svc/random-book-store
   ```

3. Get the route URL:
   ```bash
   oc get route random-book-store
   ```

See `openshift/DEPLOYMENT.md` for detailed deployment instructions.

## Configuration

### Environment Variables

- `SECRET_KEY`: Flask secret key for session management
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)
- `PORT`: Application port (default: 8080)
- `BOOKS_REFRESH_INTERVAL_MINUTES`: How often to fetch new books (default: 10)
- `BOOKS_COUNT`: Number of books to fetch (default: 12)

### Database

- **Development**: Uses SQLite (`random-book-store.db`)
- **Production**: Configure `DATABASE_URL` for PostgreSQL

## Health Endpoints

- `/health` - Liveness probe (checks if app is running)
- `/ready` - Readiness probe (checks if app is ready to serve traffic)

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
│   ├── pvc.yaml            # Persistent volume claim
│   └── DEPLOYMENT.md        # Detailed deployment guide
├── config.py               # Application configuration
├── wsgi.py                 # WSGI entry point (S2I compatible)
├── Dockerfile              # Container image definition
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── QUICKSTART.md           # Quick start guide
└── STRUCTURE.md            # Repository structure
```

## Book Data Source & Auto-Refresh

The application uses the **Open Library API** (https://openlibrary.org) to dynamically populate the catalog:

### Initial Load
- **On first run**: Automatically fetches 12 trending books from multiple subjects
- **Real data**: Actual book titles, authors, ISBNs, publication dates, and cover images
- **Cover images**: Served from Open Library's CDN (`covers.openlibrary.org`)

### Automatic Refresh (New!)
- **Every 10 minutes** (configurable): Background scheduler fetches fresh random books
- **Complete rotation**: Old books are replaced with entirely new selections
- **Always fresh**: Visitors see different books on each visit
- **No downtime**: Refresh happens in the background

### Book Selection
- **Diverse catalog**: Random selection from fiction, sci-fi, mystery, romance, fantasy, history, biography, and science
- **Quality filtering**: Only books with ISBNs and cover images
- **No duplicates**: Deduplication ensures variety
- **Demo pricing**: Prices ($9.99-$24.99) and stock (5-30 units) are randomized for demonstration

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

## Security Notes

- **Production secrets**: Always change `SECRET_KEY` in production (see `openshift/secret.yaml`)
- **Password security**: User passwords are hashed using Werkzeug's `generate_password_hash`
- **No payment processing**: Checkout is demonstration only, no real transactions
- **HTTPS recommended**: Use TLS/SSL for production deployments
- **OpenShift SCC**: Runs with restricted security context (non-root, no privilege escalation)

## Contributing

This is a demo application for educational purposes. Feel free to fork and modify for your needs.

## Additional Resources

- [Open Library API Documentation](https://openlibrary.org/developers/api)
- [OpenShift Documentation](https://docs.openshift.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/5.3/)

## License

MIT License - Free to use for educational and demonstration purposes.
