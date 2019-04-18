resource "aws_route53_zone" "main" {
  name    = "${var.name}"
  vpc {
    vpc_id = "${var.vpc_id}"
  }
  comment = ""
}
