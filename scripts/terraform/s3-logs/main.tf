resource "aws_s3_bucket" "logs" {
  bucket = "${var.name}-${var.environment}-logs"

  lifecycle_rule {
    id = "logs-expiration"
    prefix = ""
    enabled = "${var.logs_expiration_enabled}"

    expiration {
      days = "${var.logs_expiration_days}"
    }
  }

  tags {
    Name        = "${var.name}-${var.environment}-logs"
    Environment = "${var.environment}"
  }

  policy = "${data.template_file.policy.rendered}"
}
