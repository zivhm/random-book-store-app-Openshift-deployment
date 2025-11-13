# Use Red Hat Universal Base Image for Python 3.12
FROM registry.access.redhat.com/ubi9/python-312:latest

# OpenShift runs containers with random UIDs, so we need to set proper permissions
# The primary group is always root (GID 0)
USER root

# Set working directory
WORKDIR /opt/app-root/src

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set proper permissions for OpenShift
# OpenShift assigns random UID but always uses GID 0 (root group)
RUN chown -R 1001:0 /opt/app-root/src && \
    chmod -R g=u /opt/app-root/src

# Switch to non-root user (required by OpenShift)
USER 1001

# Expose port 8080 (non-privileged port)
EXPOSE 8080

# Set environment variables
ENV FLASK_APP=wsgi.py \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "wsgi:application"]
