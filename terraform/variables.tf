variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "health-intelligence"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "demo"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_password" {
  description = "RDS password"
  type        = string
  sensitive   = true
}

variable "api_instance_type" {
  description = "EC2 instance type for API servers"
  type        = string
  default     = "t3.micro"
}

variable "news_api_key" {
  description = "NewsAPI key"
  type        = string
  sensitive   = true
}

variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
}


