# Quick Start Guide

Get the Random Book Store app running in minutes! Watch the catalog automatically refresh with new books every 10 minutes.

## Run Locally (Development)

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd store-app
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python wsgi.py
```

**First run output:**
```
📚 Fetching initial books from Open Library API...
✅ Successfully added 12 books from Open Library!
📚 Book refresh scheduler started (every 10 minutes)
 * Running on http://127.0.0.1:8080
```

### 5. Access the App

Open your browser to: **http://localhost:8080**

### 6. Test the App

1. Click "Register" and create an account
2. Browse the catalog (12 real books from Open Library!)
3. Add books to cart
4. View cart and checkout
5. Wait 10 minutes and refresh - see entirely new books!

## Reset Database (Optional)

Get fresh books from Open Library:

```bash
rm bookstore.db
python wsgi.py
```

---

## Deploy to OpenShift

### Option 1: Quick Deploy (Container Image)

```bash
# 1. Build container
docker build -t random-book-store:latest .

# 2. Tag for your registry
docker tag random-book-store:latest quay.io/<your-username>/random-book-store:latest

# 3. Push to registry
docker push quay.io/<your-username>/random-book-store:latest

# 4. Update image in deployment
sed -i 's|image: random-book-store:latest|image: quay.io/<your-username>/random-book-store:latest|' openshift/all-in-one.yaml

# 5. Deploy everything
oc apply -f openshift/all-in-one.yaml

# 6. Get your app URL
oc get route random-book-store
```

Visit the URL and your app is live! 🎉

### Option 2: Source-to-Image (S2I)

Let OpenShift build the container for you:

```bash
# Create app from Git
oc new-app python:3.12~https://github.com/<your-repo>/store-app --name=random-book-store

# Expose externally
oc expose svc/random-book-store

# Get URL
oc get route random-book-store
```

### Option 3: Docker Build & Deploy

```bash
# Build with Docker
docker build -t random-book-store:latest .
docker tag random-book-store:latest <registry>/random-book-store:latest
docker push <registry>/random-book-store:latest

# Update and deploy
oc apply -f openshift/all-in-one.yaml
```

---

## Verification

### Check Deployment Status

```bash
# View pods
oc get pods

# View logs
oc logs -f deployment/random-book-store

# Check route
oc get route random-book-store
```

### Test Health Endpoints

```bash
ROUTE=$(oc get route random-book-store -o jsonpath='{.spec.host}')

# Liveness probe
curl https://$ROUTE/health

# Readiness probe
curl https://$ROUTE/ready
```

---

## Next Steps

1. **Register an account** on your deployed app
2. **Browse the catalog** - See real books from Open Library
3. **Customize** - Modify code and redeploy

## Need Help?

- **Detailed deployment**: See `openshift/DEPLOYMENT.md`
- **App overview**: See `README.md`
- **Troubleshooting**: Check pod logs with `oc logs -f deployment/random-book-store`

---

**Built with ❤️ using Flask, Open Library API, APScheduler, and OpenShift**

## Configuration

### Change Refresh Interval

Set how often books refresh (default: 10 minutes):

```bash
# Refresh every 5 minutes
export BOOKS_REFRESH_INTERVAL_MINUTES=5
python wsgi.py

# Or in OpenShift
oc set env deployment/random-book-store BOOKS_REFRESH_INTERVAL_MINUTES=5
```

### Change Book Count

Set how many books to fetch (default: 12):

```bash
export BOOKS_COUNT=20
python wsgi.py
```
