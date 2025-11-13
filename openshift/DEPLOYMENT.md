# OpenShift Deployment Guide

Complete guide for deploying the Random Book Store application to OpenShift 4.x.

This application fetches real book data from Open Library API and automatically refreshes with new random books every 10 minutes, providing a dynamic e-commerce demonstration.

## Prerequisites

- **OpenShift cluster access** (4.x or later)
- **oc CLI** installed and logged in: `oc login`
- **Container build tool**: `docker`
- **Container registry**: Quay.io, Docker Hub, or OpenShift internal registry
- **Git repository** (optional, for S2I deployments)

## Deployment Options

### Option 1: Deploy Using Pre-built Container (Recommended)

This method gives you full control over the container image.

#### Step 1: Build the Container Image

```bash
docker build -t random-book-store:latest .
```

#### Step 2: Tag and Push to Registry

```bash
# Example with Quay.io
docker tag random-book-store:latest quay.io/<your-username>/random-book-store:latest
docker push quay.io/<your-username>/random-book-store:latest

# Example with OpenShift internal registry
oc create imagestream random-book-store
docker tag random-book-store:latest default-route-openshift-image-registry/<your-project>/random-book-store:latest
docker push default-route-openshift-image-registry/<your-project>/random-book-store:latest
```

#### Step 3: Update Deployment Manifest

Edit `openshift/deployment.yaml` and update the image reference:

```yaml
spec:
  template:
    spec:
      containers:
      - name: random-book-store
        image: quay.io/<your-username>/random-book-store:latest  # Update this
```

Or use the all-in-one manifest (`openshift/all-in-one.yaml`) and update the image there.

#### Step 4: Deploy to OpenShift

```bash
# Create a new project (optional)
oc new-project random-book-store-app

# Deploy using individual manifests
oc apply -f openshift/secret.yaml
oc apply -f openshift/pvc.yaml
oc apply -f openshift/deployment.yaml
oc apply -f openshift/service.yaml
oc apply -f openshift/route.yaml

# OR deploy using all-in-one manifest
oc apply -f openshift/all-in-one.yaml
```

#### Step 5: Verify Deployment

```bash
# Check pods
oc get pods

# Check deployment
oc get deployment random-book-store

# Check service
oc get svc random-book-store

# Get the application URL
oc get route random-book-store
```

### Option 2: Deploy Using Source-to-Image (S2I)

This method lets OpenShift build the container image from source code.

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
oc new-app python:3.12~<your-git-repo-url> \
  --name=random-book-store \
  --env SECRET_KEY=$(oc get secret random-book-store-secret -o jsonpath='{.data.secret-key}' | base64 -d)

# Or if using a specific branch
oc new-app python:3.12~<your-git-repo-url>#<branch-name> --name=random-book-store
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

### 2. Security Best Practices

- **Secrets Management**
  - Never commit secrets to Git
  - Use OpenShift secrets (`oc create secret`)
  - Rotate secrets regularly
  - Use different secrets per environment

- **Network Policies**
  - Restrict pod-to-pod communication
  - Limit external access

- **RBAC**
  - Use service accounts with minimal permissions
  - Avoid using cluster-admin

### 3. Scaling and Resources

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

### 4. Monitoring and Logging

- **Built-in Health Checks**: Already configured (`/health`, `/ready`)
- **Prometheus Metrics**: Available via OpenShift monitoring
- **Logs**: Access with `oc logs -f deployment/random-book-store`
- **Events**: Monitor with `oc get events --sort-by='.lastTimestamp'`

### 5. Persistent Storage

The application uses a PVC for SQLite database:
- **Storage Class**: Adjust in `openshift/pvc.yaml` based on your cluster
- **Backups**: Schedule regular database backups
- **Size**: Default is 1Gi, increase if needed

### 6. TLS/SSL

Routes use edge TLS termination by default:
- Certificates managed by OpenShift
- HTTP automatically redirects to HTTPS
- Custom certificates: Update `openshift/route.yaml`

## Performance Tips

1. **Use Gunicorn workers**: Already configured (4 workers)
2. **Enable HTTP caching**: Add caching headers for static assets
3. **CDN**: Use CDN for static files in production
4. **Database indexing**: Add indexes for frequently queried fields
5. **Connection pooling**: Configure for PostgreSQL

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
