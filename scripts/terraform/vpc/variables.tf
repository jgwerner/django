variable "cidr" {
  description = "The CIDR block for the VPC."
}

variable "external_subnets" {
  description = "List of external subnets"
  type        = "list"
}

variable "internal_subnets" {
  description = "List of internal subnets"
  type        = "list"
}

variable "environment" {
  description = "Environment tag, e.g prod"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = "list"
}

variable "name" {
  description = "Name tag, e.g stack"
  default     = "stack"
}

variable "use_nat_instances" {
  description = "If true, use EC2 NAT instances instead of the AWS NAT gateway service."
  default     = false
}

variable "nat_instance_type" {
  description = "Only if use_nat_instances is true, which EC2 instance type to use for the NAT instances."
  default     = "t2.nano"
}

variable "use_eip_with_nat_instances" {
  description = "Only if use_nat_instances is true, whether to assign Elastic IPs to the NAT instances. IF this is set to false, NAT instances use dynamically assigned IPs."
  default     = false
}

# This data source returns the newest Amazon NAT instance AMI
data "aws_ami" "nat_ami" {
  owners      = ["amazon"]
  most_recent = true

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }

  filter {
    name   = "name"
    values = ["amzn-ami-vpc-nat*"]
  }
}

variable "nat_instance_ssh_key_name" {
  description = "Only if use_nat_instance is true, the optional SSH key-pair to assign to NAT instances."
  default     = ""
}