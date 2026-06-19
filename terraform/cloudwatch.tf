resource "aws_cloudwatch_log_group" "auth" {
  name              = "/ecs/${var.project_name}/auth"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "orders" {
  name              = "/ecs/${var.project_name}/orders"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "notifications" {
  name              = "/ecs/${var.project_name}/notifications"
  retention_in_days = 30
}

resource "aws_cloudwatch_metric_alarm" "auth_cpu" {
  alarm_name          = "${var.project_name}-auth-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Auth service CPU > 80%"

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.auth.name
  }
}

resource "aws_cloudwatch_metric_alarm" "orders_cpu" {
  alarm_name          = "${var.project_name}-orders-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Orders service CPU > 80%"

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.orders.name
  }
}
