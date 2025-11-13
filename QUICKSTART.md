# Quick Start Guide

## Run Locally (Development)

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python wsgi.py
   ```

4. **Access the app**: Open browser to `http://localhost:8080`

## Deploy to OpenShift (Quick Method)

### Using Pre-built Image

```bash
# 1. Build container
podman build -t bookstore:latest .

# 2. Tag for your registry
podman tag bookstore:latest <registry>/bookstore:latest

# 3. Push to registry
podman push <registry>/bookstore:latest

# 4. Update image in deployment.yaml or all-in-one.yaml

# 5. Deploy
oc apply -f openshift/all-in-one.yaml

# 6. Get URL
oc get route bookstore
```

### Using Source-to-Image (S2I)

```bash
# 1. Create app from Git using Python 3.12
oc new-app python:3.12~<your-git-repo-url> --name=bookstore

# 2. Expose service
oc expose svc/bookstore

# 3. Get URL
oc get route bookstore
```

## Default Test Account

After deployment, register a new account or use these steps:

1. Click "Register"
2. Create username/password
3. Login and start shopping!

## Health Checks

- Liveness: `http://<app-url>/health`
- Readiness: `http://<app-url>/ready`

For detailed instructions, see:
- `README.md` - Application overview
- `openshift/DEPLOYMENT.md` - Detailed deployment guide
