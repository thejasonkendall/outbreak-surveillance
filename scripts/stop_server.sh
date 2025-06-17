#!/bin/bash
# scripts/stop_server.sh

set -e

echo "Stopping Health Intelligence application..."

# Navigate to application directory
cd /opt/health-intelligence 2>/dev/null || {
    echo "Application directory not found, nothing to stop"
    exit 0
}

# Stop and remove containers
if [ -f docker-compose.yml ]; then
    docker-compose down --remove-orphans 2>/dev/null || true
fi

# Clean up any remaining containers
docker ps -q --filter "name=health_" | xargs -r docker stop
docker ps -aq --filter "name=health_" | xargs -r docker rm

echo "Application stopped successfully!"