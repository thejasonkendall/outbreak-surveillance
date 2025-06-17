#!/bin/bash
# scripts/start_server.sh

set -e

echo "Starting Health Intelligence application..."

# Navigate to application directory
cd /opt/health-intelligence

# Set environment variables
export AWS_DEFAULT_REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)
export HOSTNAME=$(hostname)

# Get environment variables from AWS Systems Manager Parameter Store
export DATABASE_URL=$(aws ssm get-parameter --name "/health-intelligence/database-url" --with-decryption --query 'Parameter.Value' --output text --region $AWS_DEFAULT_REGION)
export NEWS_API_KEY=$(aws ssm get-parameter --name "/health-intelligence/news-api-key" --with-decryption --query 'Parameter.Value' --output text --region $AWS_DEFAULT_REGION)
export ANTHROPIC_API_KEY=$(aws ssm get-parameter --name "/health-intelligence/anthropic-api-key" --with-decryption --query 'Parameter.Value' --output text --region $AWS_DEFAULT_REGION)
export ECR_API_REPO=$(aws ssm get-parameter --name "/health-intelligence/ecr-api-repo" --query 'Parameter.Value' --output text --region $AWS_DEFAULT_REGION)
export ECR_DASHBOARD_REPO=$(aws ssm get-parameter --name "/health-intelligence/ecr-dashboard-repo" --query 'Parameter.Value' --output text --region $AWS_DEFAULT_REGION)

# Login to ECR for both repositories
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $ECR_API_REPO
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $ECR_DASHBOARD_REPO

# Create CloudWatch log group if it doesn't exist
aws logs create-log-group --log-group-name /aws/ec2/health-intelligence --region $AWS_DEFAULT_REGION 2>/dev/null || true

# Pull the latest images
docker-compose pull

# Start the application
docker-compose up -d

# Wait for health check
echo "Waiting for application to be healthy..."
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "Application is healthy!"
        break
    fi
    echo "Waiting for application... ($counter/$timeout)"
    sleep 5
    counter=$((counter + 5))
done

if [ $counter -ge $timeout ]; then
    echo "Application failed to become healthy within $timeout seconds"
    docker-compose logs
    exit 1
fi

echo "Health Intelligence application started successfully!"