# Bookstore Application - OpenShift Deployment

A simple Flask-based bookstore application designed for deployment on OpenShift.

## Features

- **Homepage**: Welcome page with featured books
- **Catalogue**: Browse all available books with pagination
- **User Authentication**: Register and login functionality
- **Shopping Cart**: Add/remove books, update quantities
- **Checkout**: Simple checkout process (demo only)
- **Health Checks**: Built-in liveness and readiness probes for OpenShift

## Technology Stack

- **Backend**: Python 3.12 Flask
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML/CSS with Bootstrap 5
- **WSGI Server**: Gunicorn
- **Container**: Red Hat UBI9 Python 3.12

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

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python wsgi.py
   ```

4. Access the application at `http://localhost:8080`

## OpenShift Deployment

### Method 1: Using Pre-built Container Image

1. Build the container image:
   ```bash
   podman build -t bookstore:latest .
   ```

2. Tag and push to your registry:
   ```bash
   podman tag bookstore:latest <your-registry>/bookstore:latest
   podman push <your-registry>/bookstore:latest
   ```

3. Update `openshift/deployment.yaml` with your image registry.

4. Deploy to OpenShift:
   ```bash
   oc apply -f openshift/
   ```

### Method 2: Using Source-to-Image (S2I)

1. Create a new application from source:
   ```bash
   oc new-app python:3.9~https://github.com/<your-repo>/store-app \
     --name=bookstore
   ```

2. Expose the service:
   ```bash
   oc expose svc/bookstore
   ```

3. Get the route URL:
   ```bash
   oc get route bookstore
   ```

## Configuration

### Environment Variables

- `SECRET_KEY`: Flask secret key for session management
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)
- `PORT`: Application port (default: 8080)

### Database

- **Development**: Uses SQLite (`bookstore.db`)
- **Production**: Configure `DATABASE_URL` for PostgreSQL

## Health Endpoints

- `/health` - Liveness probe (checks if app is running)
- `/ready` - Readiness probe (checks if app is ready to serve traffic)

## Project Structure

```
store-app/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── routes.py            # Application routes
│   ├── static/
│   │   └── css/
│   │       └── style.css    # Custom styles
│   └── templates/           # HTML templates
├── openshift/               # OpenShift manifests
│   ├── deployment.yaml      # Deployment configuration
│   ├── service.yaml         # Service definition
│   ├── route.yaml           # Route for external access
│   ├── secret.yaml          # Secrets
│   └── pvc.yaml            # Persistent volume claim
├── config.py               # Application configuration
├── wsgi.py                 # WSGI entry point
├── Dockerfile              # Container image definition
└── requirements.txt        # Python dependencies
```

## Sample Data

The application automatically creates sample books on first run:
- The Great Gatsby
- To Kill a Mockingbird
- 1984
- Pride and Prejudice
- The Catcher in the Rye
- The Hobbit

## Testing the Application

1. Register a new account
2. Browse the catalogue
3. Add books to cart
4. View and update cart
5. Complete checkout

## Security Notes

- Change the `SECRET_KEY` in production (use OpenShift secrets)
- The checkout process is a demo - no real payment processing
- User passwords are hashed using Werkzeug's security functions

## License

This is a demo application for educational purposes.
