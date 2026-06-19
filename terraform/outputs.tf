output "alb_dns_name" {
  description = "Public DNS of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "ecr_auth_url" {
  description = "ECR repository URL for the Auth service"
  value       = aws_ecr_repository.auth.repository_url
}

output "ecr_orders_url" {
  description = "ECR repository URL for the Orders service"
  value       = aws_ecr_repository.orders.repository_url
}

output "ecr_notifications_url" {
  description = "ECR repository URL for the Notifications service"
  value       = aws_ecr_repository.notifications.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "redis_endpoint" {
  description = "ElastiCache Redis primary endpoint"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
  sensitive   = true
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "service_discovery_namespace" {
  description = "Cloud Map private DNS namespace"
  value       = aws_service_discovery_private_dns_namespace.main.name
}
