variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "cloud-native-ms"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

variable "auth_task_cpu" {
  description = "CPU units for the Auth service Fargate task"
  type        = number
  default     = 256
}

variable "auth_task_memory" {
  description = "Memory (MB) for the Auth service Fargate task"
  type        = number
  default     = 512
}

variable "orders_task_cpu" {
  description = "CPU units for the Orders service Fargate task"
  type        = number
  default     = 256
}

variable "orders_task_memory" {
  description = "Memory (MB) for the Orders service Fargate task"
  type        = number
  default     = 512
}

variable "notifications_task_cpu" {
  description = "CPU units for the Notifications service Fargate task"
  type        = number
  default     = 256
}

variable "notifications_task_memory" {
  description = "Memory (MB) for the Notifications service Fargate task"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of tasks per ECS service"
  type        = number
  default     = 2
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}
