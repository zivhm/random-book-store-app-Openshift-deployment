# OpenShift Deployment Guide

Complete guide for deploying the Random Book Store application to OpenShift 4.x.

This application fetches real book data from Open Library API and automatically refreshes with new random books every 10 minutes, providing a dynamic e-commerce demonstration.

## Prerequisites

- **OpenShift cluster access** (4.x or later)
- **oc CLI** installed and logged in: `oc login`
- **Container build tool**: `docker`
- **Container registry**: Docker Hub, or OpenShift internal registry
- **Git repository** (optional, for S2I deployments)

## Deployment Options

### Option 1: Local OpenShift Build (Recommended)

This method builds the container directly in OpenShift without needing external registry access. **Best for local development and testing.**

#### Prerequisites

- Local OpenShift cluster (CRC, MicroShift, or local cluster)
- Sufficient disk space (~10GB free)

#### Step 1: Login to OpenShift

```bash
oc login -u kubeadmin https://api.crc.testing:6443
```

**Your output should look like this:**

```
Logged into "https://api.crc.testing:6443" as "kubeadmin" using existing credentials.

You have access to 65 projects, the list has been suppressed. You can list all projects with 'oc projects'

Using project "default".
```

#### Step 2: Create Project and Build

```bash
# Navigate to your source code directory
cd /path/to/random-store-app

# Create new project
oc new-project random-book-store-app

# Create a build configuration from local source
oc new-build --name=random-book-store --binary --strategy=docker
```

**Your output should look like this:**
```
    * A Docker build using binary input will be created
      * The resulting image will be pushed to image stream tag "random-book-store:latest"
      * A binary build was created, use 'oc start-build --from-dir' to trigger a new build

--> Creating resources with label build=random-book-store ...
    imagestream.image.openshift.io "random-book-store" created
    buildconfig.build.openshift.io "random-book-store" created
--> Success
```

```bash
# Start the build from your local directory
oc start-build random-book-store --from-dir=. --follow
```

**Your output should look like this:**
```
Uploading directory "." as binary input for the build ...
..
Uploading finished
build.build.openshift.io/random-book-store-1 started
Receiving source from STDIN as archive ...
.
.
.
Writing manifest to image destination
Successfully pushed image-registry.openshift-image-registry.svc:5000/random-book-store-app/random-book-store@sha256:abc123def456...
Push successful
```

This will:
- Upload your local code to OpenShift
- Build the container image using your Dockerfile
- Store the image in the internal registry

#### Step 3: Create Secret

```bash
# Create secret for Flask session management
oc create secret generic random-book-store-secret \
  --from-literal=secret-key=$(openssl rand -hex 32)
```

**Your output should look like this:**
```
secret/random-book-store-secret created
```

#### Step 4: Deploy Application

```bash
# Create persistent storage
oc apply -f openshift/pvc.yaml
```

**Your output should look like this:**
```
persistentvolumeclaim/random-book-store-pvc created
```

```bash
# Create the application from the built image
oc new-app random-book-store \
  --name=random-book-store
```
**Your output should look like this:**
```
--> Found image 416c233 (4 minutes old) in image stream "random-book-store-app/random-book-store" under tag "latest" for "random-book-store"
--> Creating resources ...
    deployment.apps "random-book-store" created
    service "random-book-store" created
--> Success
    Application is not exposed. You can expose services to the outside world by executing one or more of the commands below:
     'oc expose service/random-book-store' 
    Run 'oc status' to view your app.
```

```bash
# Add the secret as environment variable
  oc set env deployment/random-book-store \
    --from secret/random-book-store-secret
```

**Your output should look like this:**
```
deployment.apps/random-book-store updated
```

```bash
# Mount persistent volume for database
oc set volume deployment/random-book-store \
  --add --name=data \
  --type=persistentVolumeClaim \
  --claim-name=random-book-store-pvc \
  --mount-path=/opt/app-root/src/data
```

**Your output should look like this:**
```
deployment.apps/random-book-store volume updated
```

```bash
# Add resource limits (important for local clusters)
oc set resources deployment/random-book-store \
  --requests=memory=258Mi,cpu=100m,ephemeral-storage=500Mi \
  --limits=memory=512Mi,cpu=500m,ephemeral-storage=1Gi
```

**Your output should look like this:**
```
deployment.apps/random-book-store resource requirements updated
```

#### Step 5: Expose and Access

```bash
# Create route for external access
oc expose svc/random-book-store
```

**Your output should look like this:**
```
route.route.openshift.io/random-book-store exposed
```

```bash
# Get the application URL
oc get route random-book-store
```

**Your output should look like this:**
```
NAME                HOST/PORT                                                  PATH   SERVICES            PORT       TERMINATION   WILDCARD
random-book-store   random-book-store-random-book-store-app.apps-crc.testing          random-book-store   8080-tcp                 None
```

```bash
# Test the application
ROUTE=$(oc get route random-book-store -o jsonpath='{.spec.host}')
echo "Application URL: http://$ROUTE"
curl http://$ROUTE/health
```

**Your output should look like this:**
```
Application URL: http://random-book-store-random-book-store-app.apps-crc.testing
```

#### Step 6: Monitor Deployment

```bash
# Watch pods start
oc get pods -w

# Check events
oc get events --sort-by='.lastTimestamp' | tail -10
```

**Your output should look like this:**
```
34m         Normal    SuccessfulCreate        replicaset/random-book-store-6bbccd98d8       Created pod: random-book-store-6bbccd98d8-gkd5n
34m         Normal    ScalingReplicaSet       deployment/random-book-store                  Scaled up replica set random-book-store-6bbccd98d8 from 0 to 1
34m         Normal    Scheduled               pod/random-book-store-6bbccd98d8-gkd5n        Successfully assigned random-book-store-app/random-book-store-6bbccd98d8-gkd5n to crc
34m         Normal    AddedInterface          pod/random-book-store-6bbccd98d8-gkd5n        Add eth0 [5.160.243.162/23] from ovn-kubernetes
34m         Normal    ScalingReplicaSet       deployment/random-book-store                  Scaled down replica set random-book-store-79f4dbc748 from 1 to 0
34m         Normal    SuccessfulDelete        replicaset/random-book-store-79f4dbc748       Deleted pod: random-book-store-79f4dbc748-thb55
34m         Normal    Killing                 pod/random-book-store-79f4dbc748-thb55        Stopping container random-book-store
33m         Normal    Pulled                  pod/random-book-store-6bbccd98d8-gkd5n        Container image "image-registry.openshift-image-registry.svc:5000/random-book-store-app/random-book-store@sha256:abc123def456..." already present on machine
33m         Normal    Created                 pod/random-book-store-6bbccd98d8-gkd5n        Created container random-book-store
33m         Normal    Started                 pod/random-book-store-6bbccd98d8-gkd5n        Started container random-book-store
```

#### Updating Your Application

When you make code changes, rebuild and redeploy:

```bash
# Rebuild from local source
oc start-build random-book-store --from-dir=. --follow

# Trigger a new deployment (automatic after build completes)
oc rollout status deployment/random-book-store
```

---

### Option 2: Deploy Using Pre-built Container (Docker Hub)

This method uses Docker Hub to store your container image. **Best for production deployments or sharing images.**

#### Prerequisites

- Docker Hub account (free at https://hub.docker.com)
- Docker logged in: `docker login`

#### Step 1: Build the Container Image

```bash
# Navigate to your source code directory
cd /path/to/store-app

# Build the container image
docker build -t random-book-store:latest .
```

**Your output should look like this:**
```
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [1/8] FROM registry.access.redhat.com/ubi9/python-312:latest
 => [2/8] USER root
 => [3/8] WORKDIR /opt/app-root/src
 => [4/8] COPY requirements.txt .
 => [5/8] RUN pip install --no-cache-dir -r requirements.txt
 => [6/8] COPY . .
 => [7/8] RUN chown -R 1001:0 /opt/app-root/src && chmod -R g=u /opt/app-root/src
 => exporting to image
 => => naming to docker.io/library/random-book-store:latest
```

#### Step 2: Tag and Push to Docker Hub

```bash
# Login to Docker Hub (if not already logged in)
docker login

# Tag image with your Docker Hub username
docker tag random-book-store:latest <your-dockerhub-username>/random-book-store:latest

# Push to Docker Hub
docker push <your-dockerhub-username>/random-book-store:latest
```

**Your output should look like this:**
```
Login Succeeded

The push refers to repository [docker.io/your-username/random-book-store]
a1b2c3d4e5f6: Pushed
7g8h9i0j1k2l: Pushed
3m4n5o6p7q8r: Pushed
latest: digest: sha256:abc123def456... size: 2421
```

#### Step 3: Create Project and Deploy

```bash
# Create new project
oc new-project random-book-store-app

# Create secret
oc create secret generic random-book-store-secret \
  --from-literal=secret-key=$(openssl rand -hex 32)

# Create persistent storage
oc apply -f openshift/pvc.yaml

# Deploy from Docker Hub image
oc new-app <your-dockerhub-username>/random-book-store:latest \
  --name=random-book-store

# Configure environment and storage
oc set env deployment/random-book-store \
  --from secret/random-book-store-secret

oc set volume deployment/random-book-store \
  --add --name=data \
  --type=persistentVolumeClaim \
  --claim-name=random-book-store-pvc \
  --mount-path=/opt/app-root/src/data

oc set resources deployment/random-book-store \
  --requests=memory=256Mi,cpu=150m \
  --limits=memory=512Mi,cpu=500m

# Expose the service
oc expose svc/random-book-store
```

**Your output should look like this:**
```
project.project.openshift.io/random-book-store-app created
secret/random-book-store-secret created
persistentvolumeclaim/random-book-store-pvc created
--> Found container image abc1234 (10 minutes old) from docker.io for "your-username/random-book-store:latest"
--> Creating resources ...
    deployment.apps "random-book-store" created
    service "random-book-store" created
--> Success
route.route.openshift.io/random-book-store exposed
```

#### Step 4: Verify Deployment

```bash
# Get the application URL
oc get route random-book-store

# Check pod status
oc get pods

# View logs
oc logs -f deployment/random-book-store
```

**Your output should look like this:**
```
NAME                 HOST/PORT                                               PATH   SERVICES            PORT   TERMINATION   WILDCARD
random-book-store    random-book-store-random-book-store-app.apps.example.com       random-book-store   8080   edge          None

NAME                                 READY   STATUS    RESTARTS   AGE
random-book-store-7b8f9d6c4d-x5k2m   1/1     Running   0          1m
```

#### Updating Your Application

When you make code changes:

```bash
# Rebuild and push
docker build -t random-book-store:latest .
docker tag random-book-store:latest <your-dockerhub-username>/random-book-store:latest
docker push <your-dockerhub-username>/random-book-store:latest

# Trigger redeployment in OpenShift
oc rollout restart deployment/random-book-store
oc rollout status deployment/random-book-store
```

---

### Option 3: Deploy Using Source-to-Image (S2I)

This method lets OpenShift build the container image from source code in Git.

#### Step 1: Push Code to Git Repository

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-git-repo-url>
git push -u origin main
```

#### Step 2: Create Application from Source

```bash
# Create new project
oc new-project random-book-store-app

# Create secret for session management
oc create secret generic random-book-store-secret \
  --from-literal=secret-key=$(openssl rand -hex 32)

# Create application from Git repository using Python 3.12
oc new-app python:3.12-ubi9~<your-git-repo-url> \
  --name=random-book-store \
  --env SECRET_KEY=$(oc get secret random-book-store-secret -o jsonpath='{.data.secret-key}' | base64 -d)
```

**Your output should look like this:**
```
--> Found image d00084d (2 months old) in image stream "openshift/python" under tag "3.12-ubi9" for "python:3.12-ubi9"
--> Creating resources ...
    imagestream.image.openshift.io "random-book-store" created
    buildconfig.build.openshift.io "random-book-store" created
    deployment.apps "random-book-store" created
    service "random-book-store" created
--> Success
    Build scheduled, use 'oc logs -f buildconfig/random-book-store' to track its progress.
    Application is not exposed. You can expose services to the outside world by executing one or more of the commands below:
     'oc expose service/random-book-store' 
    Run 'oc status' to view your app.
```

#### S2I Build Hooks (Optional but Recommended)

S2I supports custom build hooks that run during the build process. **Hooks are useful for:**
- Running database migrations
- Installing additional system packages
- Running tests before deployment
- Custom initialization tasks

**Supported Hook Types:**

| Hook | When It Runs | Use Case |
|------|--------------|----------|
| `pre_build` | Before installing dependencies | Install system packages, setup configs |
| `post_build` | After build, before image creation | Run tests, cleanup, optimize |
| `assemble` | Custom build logic | Override default build process |
| `run` | Container startup | Custom startup commands |

**How to Create Hooks:**

1. Create a `.s2i/bin/` directory in your repository root:

```bash
mkdir -p .s2i/bin
chmod +x .s2i/bin/*  # Make scripts executable
```

2. Add hook scripts to `.s2i/bin/`

**Example: Pre-Build Hook** (`.s2i/bin/pre_build`)

```bash
#!/bin/bash
# .s2i/bin/pre_build
# Runs before pip install -r requirements.txt

echo "🔧 Running pre-build hook..."

# Install additional system packages if needed
# (requires escalated permissions in BuildConfig)
# yum install -y some-package

# Setup environment
export BUILD_TIME=$(date)
echo "Build started at: $BUILD_TIME"

# Verify Python version
python --version

echo "✅ Pre-build hook completed"
```

**Example: Post-Build Hook** (`.s2i/bin/post_build`)

```bash
#!/bin/bash
# .s2i/bin/post_build
# Runs after dependencies are installed

echo "🧪 Running post-build hook..."

# Run tests (optional - comment out if you don't want tests during build)
# python -m pytest tests/ || exit 1

# Initialize database schema (if needed)
# python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Verify all dependencies are installed
pip list

# Cleanup unnecessary files
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Post-build hook completed"
```

**Example: Custom Run Hook** (`.s2i/bin/run`)

```bash
#!/bin/bash
# .s2i/bin/run
# Custom startup command (overrides CMD in Dockerfile)

echo "🚀 Starting Random Book Store application..."

# Run database migrations (if you add them later)
# python manage.py db upgrade

# Start Gunicorn with custom settings
exec gunicorn \
  --bind 0.0.0.0:8080 \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  wsgi:application
```

**Add Hooks to Your Repository:**

```bash
# Commit and push
git add .s2i/
git commit -m "Add S2I build hooks"
git push
```

**Trigger a New Build with Hooks:**

```bash
# Start a new build (hooks will run automatically)
# The repo has to be either public or accessible after authentication
oc start-build random-book-store --follow 

# Watch build logs to see hooks in action
oc logs -f buildconfig/random-book-store
```

**Your build output should now show:**
```
Cloning "https://github.com/your-username/random-book-store-app.git" ...
---> Installing application source...
🔧 Running pre-build hook...
Python 3.12.1
pip 24.0 from /opt/app-root/lib/python3.12/site-packages/pip (python 3.12)
✅ Pre-build hook completed
---> Installing dependencies ...
Collecting Flask==3.0.0
...
Successfully installed Flask-3.0.0 ...
🧪 Running post-build hook...
Flask                         3.0.0
gunicorn                      21.2.0
...
✅ Post-build hook completed
Build complete, pushing image ...
Push successful
```

**Common Issues:**

1. **Hooks not executing**: Ensure scripts are executable (`chmod +x .s2i/bin/*`)
2. **Permission errors**: Some system operations require BuildConfig changes
3. **Hook fails build**: Hooks that exit with non-zero status will fail the build

#### Step 3: Create Persistent Storage (Optional)

```bash
oc apply -f openshift/pvc.yaml
oc set volume deployment/random-book-store \
  --add --name=data \
  --type=persistentVolumeClaim \
  --claim-name=random-book-store-pvc \
  --mount-path=/opt/app-root/src/data
```

#### Step 4: Expose the Service

```bash
# Create route with TLS
oc create route edge random-book-store \
  --service=random-book-store \
  --insecure-policy=Redirect

# Or apply the route manifest
oc apply -f openshift/route.yaml
```

#### Step 5: Get Application URL

```bash
oc get route random-book-store -o jsonpath='{.spec.host}'
```

---

## Post-Deployment Configuration

### Update Secret Key (Important for Production!)

**Before deploying to production**, change the default secret key:

```bash
# Generate a secure random key
SECRET_KEY=$(openssl rand -hex 32)

# Update the secret
oc patch secret random-book-store-secret \
  -p "{\"stringData\":{\"secret-key\":\"$SECRET_KEY\"}}"

# Restart pods to apply changes
oc rollout restart deployment/random-book-store
```

Alternatively, edit `openshift/secret.yaml` before deploying and replace the default value.

### Scale the Application

```bash
oc scale deployment/random-book-store --replicas=3

# Scale down
oc scale deployment/random-book-store --replicas=1
```

### View Logs

```bash
# View logs from all pods
oc logs -l app=random-book-store

oc logs -f deployment/random-book-store

# View logs from specific pod
oc logs <pod-name>
```

### Access the Application

```bash
# Get the route URL
oc get route random-book-store

# The URL will be something like:
# https://random-book-store-<project-name>.apps.<cluster-domain>
```

## Monitoring

### Check Health Endpoints

```bash
# Get route host
ROUTE_HOST=$(oc get route random-book-store -o jsonpath='{.spec.host}')

# Check liveness
curl https://$ROUTE_HOST/health

# Check readiness
curl https://$ROUTE_HOST/ready
```

### View Resource Usage

```bash
# View pod resource usage
oc adm top pods -l app=random-book-store

# View node resource usage
oc adm top nodes
```

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod
oc describe pod <pod-name>

# Check events
oc get events --sort-by='.lastTimestamp'

# Check logs
oc logs <pod-name>
```

### Permission Issues

OpenShift runs containers with random UIDs. Ensure:
- Container runs as non-root (UID 1001)
- Files have proper group permissions (GID 0)
- Ports are non-privileged (>= 1024)

```bash
# Check security context
oc describe pod <pod-name> | grep -A 10 "Security Context"
```

### Database Issues

```bash
# Check if PVC is bound
oc get pvc random-book-store-pvc

# Check volume mount
oc describe pod <pod-name> | grep -A 5 "Mounts"
```

## Cleanup

### Delete All Resources

```bash
# Using individual manifests
oc delete -f openshift/

# Or using all-in-one manifest
oc delete -f openshift/all-in-one.yaml

# Delete the project entirely
oc delete project random-book-store-app
```

### Delete Specific Resources

```bash
# Delete deployment
oc delete deployment random-book-store

# Delete service
oc delete svc random-book-store

# Delete route
oc delete route random-book-store

# Delete PVC (this will delete data!)
oc delete pvc random-book-store-pvc

# Delete secret
oc delete secret random-book-store-secret
```

## Production Considerations

### 1. Database (PostgreSQL Recommended)

For production, replace SQLite with PostgreSQL:

```bash
# Deploy PostgreSQL from template
oc new-app postgresql-persistent \
  --param DATABASE_NAME=random_book_store \
  --param DATABASE_USER=random_book_store \
  --param DATABASE_PASSWORD=$(openssl rand -base64 32)

# Update deployment with PostgreSQL connection
oc set env deployment/random-book-store \
  DATABASE_URL="postgresql://random_book_store:password@postgresql:5432/random_book_store"
```

### 2. Scaling and Resources

**Horizontal Scaling:**
```bash
oc scale deployment/random-book-store --replicas=3
```

**Autoscaling:**
```bash
oc autoscale deployment/random-book-store \
  --min=2 --max=10 --cpu-percent=75
```

**Resource Tuning:**
Edit `openshift/deployment.yaml` and adjust:
- `requests`: Guaranteed resources
- `limits`: Maximum resources allowed

### 3. Monitoring and Logging

- **Built-in Health Checks**: Already configured (`/health`, `/ready`)
- **Prometheus Metrics**: Available via OpenShift monitoring
- **Logs**: Access with `oc logs -f deployment/random-book-store`
- **Events**: Monitor with `oc get events --sort-by='.lastTimestamp'`

### 4. Persistent Storage

The application uses a PVC for SQLite database:
- **Storage Class**: Adjust in `openshift/pvc.yaml` based on your cluster
- **Backups**: Schedule regular database backups
- **Size**: Default is 1Gi, increase if needed

### 5. TLS/SSL

Routes use edge TLS termination by default:
- Certificates managed by OpenShift
- HTTP automatically redirects to HTTPS
- Custom certificates: Update `openshift/route.yaml`

## Additional Resources

- [OpenShift Documentation](https://docs.openshift.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Open Library API](https://openlibrary.org/developers/api)
- [Python S2I Builder](https://github.com/sclorg/s2i-python-container)
- [Red Hat UBI Images](https://catalog.redhat.com/software/containers/search)

## Support

For issues or questions:
1. Check pod logs: `oc logs -f deployment/random-book-store`
2. Review events: `oc get events`
3. Check pod status: `oc describe pod <pod-name>`
4. Test health endpoints: `/health` and `/ready`
