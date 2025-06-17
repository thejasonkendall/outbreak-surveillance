#!/bin/bash
# Update system and install Docker
yum update -y
yum install -y docker aws-cli

# Ensure SSM agent is running (should be pre-installed on Amazon Linux 2)
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent
systemctl status amazon-ssm-agent

# Start Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create application directory
mkdir -p /opt/health-intelligence
cd /opt/health-intelligence

# # Create docker-compose file for production
# cat > docker-compose.yml << COMPOSEEOF
# version: '3.8'
# services:
#   api:
#     image: ${ecr_api_repo}:latest
#     ports:
#       - "8000:8000"
#     environment:
#       - DATABASE_URL=postgresql://postgres:${db_password}@${db_endpoint}:5432/health_intelligence
#       - NEWS_API_KEY=${news_api_key}
#       - ANTHROPIC_API_KEY=${anthropic_api_key}
#       - ENVIRONMENT=production
#     restart: unless-stopped
#     logging:
#       driver: awslogs
#       options:
#         awslogs-group: /aws/ec2/health-intelligence
#         awslogs-region: ${aws_region}
#         awslogs-stream: api-\$HOSTNAME
# COMPOSEEOF

# # Create startup script that will be called on refresh
# cat > start-app.sh << STARTEOF
# #!/bin/bash
# cd /opt/health-intelligence

# # Login to ECR
# aws ecr get-login-password --region ${aws_region} | docker login --username AWS --password-stdin ${ecr_api_repo}

# # Pull latest image
# docker-compose pull

# # Stop and start with new image
# docker-compose down
# docker-compose up -d

# # Wait for health check
# sleep 30
# curl http://localhost:8000/health || echo "Health check failed"
# STARTEOF

# chmod +x start-app.sh

# # Create CloudWatch log group
# aws logs create-log-group --log-group-name /aws/ec2/health-intelligence --region ${aws_region} || true

# # Initial login to ECR and start
# aws ecr get-login-password --region ${aws_region} | docker login --username AWS --password-stdin ${ecr_api_repo}
# docker pull ${ecr_api_repo}:latest || echo "Could not pull image, will use simple health check"

# # Start the application
# docker pull ${ecr_api_repo}:latest; then
# echo "Starting real application from ECR..."
# docker-compose up -d


# echo "Health Intelligence API server setup complete!"