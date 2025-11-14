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

### Option 2: Deploy Using Pre-built Container (Docker Hub) -- NEED TO VERIFY THIS --

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

**How to Create Working Hooks:**

**IMPORTANT**: The Python S2I builder doesn't automatically execute `pre_build` and `post_build` hooks. You must create a **custom `assemble` script** that explicitly calls them.

**Step 1: Create the `.s2i/bin/` directory**

```bash
mkdir -p .s2i/bin
```

**Step 2: Create Custom Assemble Script** (`.s2i/bin/assemble`)

This is the key file that makes hooks work:

```bash
cat > .s2i/bin/assemble << 'EOF'
#!/bin/bash
# Custom S2I assemble script that calls hooks

set -e

echo "---> Running custom assemble script with hooks support"

# Run pre_build hook if it exists
if [ -f /tmp/src/.s2i/bin/pre_build ]; then
  echo "---> Executing pre_build hook..."
  /tmp/src/.s2i/bin/pre_build
fi

# Call the default Python S2I assemble script
echo "---> Calling default Python assemble script..."
/usr/libexec/s2i/assemble

# Run post_build hook if it exists
# Check both possible locations
if [ -f /tmp/src/.s2i/bin/post_build ]; then
  echo "---> Executing post_build hook..."
  /tmp/src/.s2i/bin/post_build
elif [ -f ./.s2i/bin/post_build ]; then
  echo "---> Executing post_build hook (from current dir)..."
  ./.s2i/bin/post_build
else
  echo "---> Post-build hook not found, skipping..."
fi

echo "---> Custom assemble script completed"
EOF
```

**Step 3: Create Pre-Build Hook** (`.s2i/bin/pre_build`)

```bash
cat > .s2i/bin/pre_build << 'EOF'
#!/bin/bash
# .s2i/bin/pre_build
# Runs before pip install -r requirements.txt

echo "🔧 Running pre-build hook..."

# Setup environment
export BUILD_TIME=$(date)
echo "Build started at: $BUILD_TIME"

# Verify Python version
python --version

echo "✅ Pre-build hook completed"
EOF
```

**Step 4: Create Post-Build Hook** (`.s2i/bin/post_build`)

```bash
cat > .s2i/bin/post_build << 'EOF'
#!/bin/bash
# .s2i/bin/post_build
# Runs after dependencies are installed

echo "🧪 Running post-build hook..."

# Verify all dependencies are installed
pip list

# Cleanup unnecessary files
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Post-build hook completed"
EOF
```

**Step 5: Create Custom Run Hook (Optional)** (`.s2i/bin/run`)

```bash
cat > .s2i/bin/run << 'EOF'
#!/bin/bash
# .s2i/bin/run
# Custom startup command (overrides CMD in Dockerfile)

echo "🚀 Starting Random Book Store application..."

# Start Gunicorn with custom settings
exec gunicorn \
  --bind 0.0.0.0:8080 \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  wsgi:application
EOF
```

**Step 6: Make Scripts Executable and Track in Git**

```bash
# Make all scripts executable
chmod +x .s2i/bin/*

# Add to git and update permissions
git add .s2i/
git update-index --chmod=+x .s2i/bin/assemble
git update-index --chmod=+x .s2i/bin/pre_build
git update-index --chmod=+x .s2i/bin/post_build
git update-index --chmod=+x .s2i/bin/run

# Verify git has executable permissions (should show 100755)
git ls-files --stage .s2i/bin/

# Commit and push
git commit -m "Add S2I build hooks with custom assemble script"
git push
```

**Step 7: Trigger a New Build with Hooks**

```bash
# Start a new build (hooks will run automatically)
# The repo has to be either public or accessible after authentication
oc start-build random-book-store --follow
```

**Your build output should now show:**
```
Cloning "https://github.com/your-username/random-book-store-app.git" ...
    Commit:    7090553c32713e053d3d771b30991d39ba590a4c (Add custom S2I assemble script to call hooks)
    Author:    your-username <your@email.com>
    Date:    Fri Nov 14 01:34:23 2025 +0200

STEP 9/10: RUN /tmp/scripts/assemble
---> Running custom assemble script with hooks support
---> Executing pre_build hook...
🔧 Running pre-build hook...
Build started at: Thu Nov 13 11:38:35 PM UTC 2025
Python 3.12.9
✅ Pre-build hook completed
---> Calling default Python assemble script...
---> Installing application source ...
---> Installing dependencies ...
Collecting Flask==3.0.0 (from -r requirements.txt (line 2))
  Downloading flask-3.0.0-py3-none-any.whl.metadata (3.6 kB)
...
Successfully installed APScheduler-3.10.4 Flask-3.0.0 Flask-Login-0.6.3 ...
---> Custom assemble script completed
STEP 10/10: CMD /tmp/scripts/run

Successfully pushed image-registry.openshift-image-registry.svc:5000/random-book-store-app/random-book-store@sha256:...
Push successful
```


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

#### Step 6: Set Up GitHub Webhook (Optional - Automatic Builds) #TODO: need to create secret for the hook manually

By default, S2I builds are **not triggered automatically** when you push to GitHub. You must manually run `oc start-build` each time. To enable automatic builds on `git push`, set up a webhook:

**1. Get the Webhook URL from OpenShift**

```bash
# Get the complete GitHub webhook URL with the secret
WEBHOOK_URL=$(oc describe bc/random-book-store | grep -oP 'https://[^\s]+/github' | head -1)
echo $WEBHOOK_URL
```

**Your output should look like this:**
```
https://api.crc.testing:6443/apis/build.openshift.io/v1/namespaces/random-book-store-app-2/buildconfigs/random-book-store/webhooks/abc123def456/github
```

**3. Add Webhook to GitHub Repository**

- Go to your GitHub repository: `https://github.com/<your-username>/random-book-store-app`
- Click **Settings** → **Webhooks** → **Add webhook**
- Configure the webhook:
  - **Payload URL**: Paste the **complete** webhook URL from step 1 (including the secret)
    - ⚠️ Make sure you paste the ENTIRE URL with the secret token
    - ⚠️ Do NOT manually type `<secret>` - use the actual URL from `oc describe`
  - **Content type**: `application/json`
  - **SSL verification**:
    - For **production clusters**: Enable SSL verification
    - For **local CRC/testing**: Disable SSL verification (since CRC uses self-signed certificates)
  - **Which events would you like to trigger this webhook?**: Select "Just the push event"
  - **Active**: ✅ Checked
- Click **Add webhook**

**Example webhook configuration:**
```
Payload URL: https://api.crc.testing:6443/apis/build.openshift.io/v1/namespaces/random-book-store-app-2/buildconfigs/random-book-store/webhooks/aBc123DeF456/github
Content type: application/json
SSL verification: Disable SSL verification (for local CRC)
Events: Just the push event
Active: ✓
```

**Note**: The secret in the URL (like `aBc123DeF456`) is auto-generated by OpenShift and is different for each BuildConfig.

**4. Test the Webhook**

```bash
# Make a small change and push to GitHub
echo "# Test webhook" >> README.md
git add README.md
git commit -m "Test webhook trigger"
git push

# Watch for a new build to start automatically
oc get builds -w
```

**Your output should show a new build starting:**
```
NAME                     TYPE     FROM          STATUS     STARTED
random-book-store-11     Source   Git@abc1234   Running    2 seconds ago
```

**5. Verify Webhook in GitHub**

- Go back to GitHub → Settings → Webhooks
- Click on your webhook
- Scroll to **Recent Deliveries**
- You should see a delivery with a ✅ green checkmark and response code `200`

**Troubleshooting Webhooks:**

1. **Webhook shows red X in GitHub**:
   - Check if OpenShift API is accessible from the internet (for hosted GitHub)
   - For local CRC, webhooks won't work unless CRC is publicly accessible (use `oc start-build` manually instead)

2. **No build triggered after push**:
   - Verify webhook is active in GitHub
   - Check webhook delivery logs in GitHub (Settings → Webhooks → Recent Deliveries)
   - Ensure the branch matches (webhook triggers on the branch specified in BuildConfig)

3. **SSL verification errors**:
   - For local CRC: Disable SSL verification in GitHub webhook settings
   - For production: Use valid SSL certificates

**Note for Local Development (CRC):**
GitHub webhooks typically **won't work with local CRC** because GitHub cannot reach `api.crc.testing` from the internet. For local development, manually trigger builds:

```bash
# Manual build trigger (always works)
oc start-build random-book-store --follow
```

For production OpenShift clusters with public APIs, webhooks work perfectly and enable CI/CD workflows.

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
