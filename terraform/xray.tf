resource "aws_cloudwatch_log_group" "xray" {
  name              = "/ecs/${var.project_name}/xray-daemon"
  retention_in_days = 30
}

locals {
  xray_sidecar = {
    name      = "xray-daemon"
    image     = "amazon/aws-xray-daemon"
    essential = false
    portMappings = [{
      containerPort = 2000
      protocol      = "udp"
    }]
    environment = [
      { name = "AWS_REGION", value = var.aws_region }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/${var.project_name}/xray-daemon"
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "xray"
      }
    }
  }
}
