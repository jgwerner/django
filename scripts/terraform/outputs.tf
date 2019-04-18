// The region in which the infra lives.
output "region" {
  value = "${var.region}"
}

// The bastion host IP.
output "bastion_ip" {
  value = "${module.bastion.external_ip}"
}

// The internal route53 zone ID.
output "zone_id" {
  value = "${module.dns.zone_id}"
}

// Security group for internal ELBs.
output "internal_elb" {
  value = "${module.security_groups.internal_elb}"
}

// Security group for external ELBs.
output "external_elb" {
  value = "${module.security_groups.external_elb}"
}

// Comma separated list of internal subnet IDs.
output "internal_subnets" {
  value = "${module.vpc.internal_subnets}"
}

// Comma separated list of external subnet IDs.
output "external_subnets" {
  value = "${module.vpc.external_subnets}"
}

// ECS Service IAM role.
output "iam_role" {
  value = "${module.iam_role.arn}"
}

// Default ECS role ID. Useful if you want to add a new policy to that role.
output "iam_role_default_ecs_role_id" {
  value = "${module.iam_role.default_ecs_role_id}"
}

// S3 bucket ID for ELB logs.
output "log_bucket_id" {
  value = "${module.s3_logs.id}"
}

// The internal domain name, e.g "illumidesk.local".
output "domain_name" {
  value = "${module.dns.name}"
}

// The illumidesk environment, e.g "dev".
output "environment" {
  value = "${var.environment}"
}

// The default ECS cluster name.
output "cluster" {
  value = "${module.ecs_cluster.name}"
}

// The VPC availability zones.
output "availability_zones" {
  value = "${module.vpc.availability_zones}"
}

// The VPC security group ID.
output "vpc_security_group" {
  value = "${module.vpc.security_group}"
}

// The VPC ID.
output "vpc_id" {
  value = "${module.vpc.id}"
}

// The default ECS cluster security group ID.
output "ecs_cluster_security_group_id" {
  value = "${module.ecs_cluster.security_group_id}"
}

// Comma separated list of internal route table IDs.
output "internal_route_tables" {
  value = "${module.vpc.internal_rtb_id}"
}

// The external route table ID.
output "external_route_tables" {
  value = "${module.vpc.external_rtb_id}"
}
