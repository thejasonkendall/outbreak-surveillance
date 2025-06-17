#!/bin/bash
# terraform/user-data/codedeploy-user-data.sh

exec > >(tee /var/log/user-data.log) 2>&1

echo "Starting user data script for CodeDeploy at $(date)"

# Update system packages
yum update -y

# Install required packages
yum install -y \
    docker \
    aws-cli \
    ruby \
    wget \
    curl \
    htop

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start and enable Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install CodeDeploy agent
cd /home/ec2-user
wget https://aws-codedeploy-${aws_region}.s3.${aws_region}.amazonaws.com/latest/install
chmod +x ./install
./install auto

# Start and enable CodeDeploy agent
service codedeploy-agent start
chkconfig codedeploy-agent on

# Ensure SSM agent is running
yum install -y amazon-ssm-agent
systemctl enable amazon-ssm-agent
systemctl start amazon-ssm-agent

# Create application directory
mkdir -p /opt/health-intelligence
chown ec2-user:ec2-user /opt/health-intelligence

# Copy dashboard and nginx config from the deployment package
# These will be provided by the deployment package
mkdir -p /opt/health-intelligence/dashboard
mkdir -p /opt/health-intelligence/nginx

# Create CloudWatch log group
aws logs create-log-group --log-group-name /aws/ec2/health-intelligence --region ${aws_region} 2>/dev/null || true

# Verify installations
docker --version
docker-compose --version
service codedeploy-agent status

echo "User data script completed successfully at $(date)"