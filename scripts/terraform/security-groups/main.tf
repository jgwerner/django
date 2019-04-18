resource "aws_security_group" "rds" {
  name        = "${var.name}-rds"
  description = "Allows traffic to RDS from other security groups"
  vpc_id      = "${var.vpc_id}"

  ingress {
    from_port       = "${var.port}"
    to_port         = "${var.port}"
    protocol        = "TCP"
    security_groups = ["${var.ingress_allow_security_groups}"]
  }

  ingress {
    from_port   = "${var.port}"
    to_port     = "${var.port}"
    protocol    = "TCP"
    cidr_blocks = ["${var.ingress_allow_cidr_blocks}"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name = "RDS (${var.name})"
  }
}

resource "aws_security_group" "internal_elb" {
  name        = "${format("%s-%s-internal-elb", var.name, var.environment)}"
  vpc_id      = "${var.vpc_id}"
  description = "Allows internal ELB traffic"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["${var.cidr}"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }

  tags {
    Name        = "${format("%s internal elb", var.name)}"
    Environment = "${var.environment}"
  }
}

resource "aws_security_group" "external_elb" {
  name        = "${format("%s-%s-external-elb", var.name, var.environment)}"
  vpc_id      = "${var.vpc_id}"
  description = "Allows external ELB traffic"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }

  tags {
    Name        = "${format("%s external elb", var.name)}"
    Environment = "${var.environment}"
  }
}

resource "aws_security_group" "external_ssh" {
  name        = "${format("%s-%s-external-ssh", var.name, var.environment)}"
  description = "Allows ssh from the world"
  vpc_id      = "${var.vpc_id}"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }

  tags {
    Name        = "${format("%s external ssh", var.name)}"
    Environment = "${var.environment}"
  }
}

resource "aws_security_group" "internal_ssh" {
  name        = "${format("%s-%s-internal-ssh", var.name, var.environment)}"
  description = "Allows ssh from bastion"
  vpc_id      = "${var.vpc_id}"

  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = ["${aws_security_group.external_ssh.id}"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "tcp"
    cidr_blocks = ["${var.cidr}"]
  }

  lifecycle {
    create_before_destroy = true
  }

  tags {
    Name        = "${format("%s internal ssh", var.name)}"
    Environment = "${var.environment}"
  }
}