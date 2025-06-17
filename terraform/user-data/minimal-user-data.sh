# #!/bin/bash
# exec > >(tee /var/log/user-data.log) 2>&1

# echo "Starting user data script at $(date)"

# # Update system packages
# yum update -y

# # Install SSM agent explicitly (should be pre-installed but let's make sure)
# yum install -y amazon-ssm-agent

# # Install basic tools
# yum install -y curl wget htop

# # Ensure SSM agent is running
# systemctl enable amazon-ssm-agent
# systemctl start amazon-ssm-agent

# # Create simple health check with nginx
# yum install -y nginx

# # Create simple health response
# echo '{"status": "healthy"}' > /usr/share/nginx/html/health

# # Configure nginx to listen on port 8000
# cat > /etc/nginx/conf.d/health.conf << 'EOF'
# server {
#     listen 8000;
#     location /health {
#         root /usr/share/nginx/html;
#         try_files /health =404;
#         add_header Content-Type application/json;
#     }
# }
# EOF

# # Start nginx
# systemctl enable nginx
# systemctl start nginx

# echo "User data script completed at $(date)"