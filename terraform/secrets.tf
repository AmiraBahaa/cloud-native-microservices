resource "aws_secretsmanager_secret" "jwt_secret" {
  name        = "/${var.project_name}/${var.environment}/jwt-secret"
  description = "JWT signing secret for the Auth service"

  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id     = aws_secretsmanager_secret.jwt_secret.id
  secret_string = "REPLACE_WITH_STRONG_SECRET_BEFORE_DEPLOY"

  lifecycle {
    ignore_changes = [secret_string]
  }
}
