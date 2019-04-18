variable "name" {
}

variable "environment" {
}

variable "account_id" {
}

variable "logs_expiration_enabled" {
  default = false
}

variable "logs_expiration_days" {
  default = 30
}

data "template_file" "policy" {
  template = "${file("${path.module}/policy.json")}"

  vars = {
    bucket     = "${var.name}-${var.environment}-logs"
    account_id = "${var.account_id}"
  }
}