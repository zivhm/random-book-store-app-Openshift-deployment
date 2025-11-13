# OpenShift Deployment Guide

This guide provides step-by-step instructions for deploying the Bookstore application to OpenShift.

## Prerequisites

- Access to an OpenShift cluster
- `oc` CLI tool installed and configured
- `podman` or `docker` for building container images
- Access to a container registry (e.g., Quay.io, Docker Hub, or OpenShift internal registry)

## Deployment Options

### Option 1: Deploy Using Pre-built Container (Recommended)

This method gives you full control over the container image.

#### Step 1: Build the Container Image

```bash
# Build using podman
podman build -t bookstore:latest .

# Or using docker
docker build -t bookstore:latest .
```

#### Step 2: Tag and Push to Registry

```bash
# Example with Quay.io
podman tag bookstore:latest quay.io/<your-username>/bookstore:latest
podman push quay.io/<your-username>/bookstore:latest

# Example with OpenShift internal registry
oc create imagestream bookstore
podman tag bookstore:latest default-route-openshift-image-registry/<your-project>/bookstore:latest
podman push default-route-openshift-image-registry/<your-project>/bookstore:latest
```

#### Step 3: Update Deployment Manifest

Edit `openshift/deployment.yaml` and update the image reference:

```yaml
spec:
  template:
    spec:
      containers:
      - name: bookstore
        image: quay.io/<your-username>/bookstore:latest  # Update this
```

Or use the all-in-one manifest (`openshift/all-in-one.yaml`) and update the image there.

#### Step 4: Deploy to OpenShift

```bash
# Create a new project (optional)
oc new-project bookstore-app

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
oc get deployment bookstore

# Check service
oc get svc bookstore

# Get the application URL
oc get route bookstore
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
oc new-project bookstore-app

# Create secret for session management
oc create secret generic bookstore-secret \
  --from-literal=secret-key=$(openssl rand -hex 32)

# Create application from Git repository using Python 3.12
oc new-app python:3.12~<your-git-repo-url> \
  --name=bookstore \
  --env SECRET_KEY=$(oc get secret bookstore-secret -o jsonpath='{.data.secret-key}' | base64 -d)

# Or if using a specific branch
oc new-app python:3.12~<your-git-repo-url>#<branch-name> --name=bookstore
```

#### Step 3: Create Persistent Storage (Optional)

```bash
oc apply -f openshift/pvc.yaml
oc set volume deployment/bookstore \
  --add --name=data \
  --type=persistentVolumeClaim \
  --claim-name=bookstore-pvc \
  --mount-path=/opt/app-root/src/data
```

#### Step 4: Expose the Service

```bash
# Create route with TLS
oc create route edge bookstore \
  --service=bookstore \
  --insecure-policy=Redirect

# Or apply the route manifest
oc apply -f openshift/route.yaml
```

#### Step 5: Get Application URL

```bash
oc get route bookstore -o jsonpath='{.spec.host}'
```

## Post-Deployment Configuration

### Update Secret Key (Important!)

```bash
# Generate a secure random key
SECRET_KEY=$(openssl rand -hex 32)

# Update the secret
oc patch secret bookstore-secret \
  -p "{\"stringData\":{\"secret-key\":\"$SECRET_KEY\"}}"

# Restart pods to pick up new secret
oc rollout restart deployment/bookstore
```

### Scale the Application

```bash
# Scale up
oc scale deployment/bookstore --replicas=3

# Scale down
oc scale deployment/bookstore --replicas=1
```

### View Logs

```bash
# View logs from all pods
oc logs -l app=bookstore

# Follow logs in real-time
oc logs -f deployment/bookstore

# View logs from specific pod
oc logs <pod-name>
```

### Access the Application

```bash
# Get the route URL
oc get route bookstore

# The URL will be something like:
# https://bookstore-<project-name>.apps.<cluster-domain>
```

## Monitoring

### Check Health Endpoints

```bash
# Get route host
ROUTE_HOST=$(oc get route bookstore -o jsonpath='{.spec.host}')

# Check liveness
curl https://$ROUTE_HOST/health

# Check readiness
curl https://$ROUTE_HOST/ready
```

### View Resource Usage

```bash
# View pod resource usage
oc adm top pods -l app=bookstore

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
oc get pvc bookstore-pvc

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
oc delete project bookstore-app
```

### Delete Specific Resources

```bash
# Delete deployment
oc delete deployment bookstore

# Delete service
oc delete svc bookstore

# Delete route
oc delete route bookstore

# Delete PVC (this will delete data!)
oc delete pvc bookstore-pvc

# Delete secret
oc delete secret bookstore-secret
```

## Production Considerations

1. **Database**: Use PostgreSQL instead of SQLite
   - Deploy PostgreSQL database
   - Update `DATABASE_URL` environment variable

2. **Secrets**: Use OpenShift secrets for sensitive data
   - Never commit secrets to Git
   - Rotate secrets regularly

3. **Resource Limits**: Adjust based on load
   - Monitor resource usage
   - Scale horizontally as needed

4. **Persistent Storage**: Plan for data persistence
   - Regular backups
   - Appropriate storage class

5. **Monitoring**: Set up monitoring and alerts
   - Prometheus metrics
   - Logging aggregation

6. **TLS/SSL**: Ensure secure communication
   - Use edge termination for routes
   - Keep certificates up to date

## Additional Resources

- [OpenShift Documentation](https://docs.openshift.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Python S2I Builder](https://github.com/sclorg/s2i-python-container)
