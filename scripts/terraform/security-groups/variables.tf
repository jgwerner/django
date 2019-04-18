/**
 * Creates basic security groups to be used by instances and ELBs.
 */

variable "name" {
  description = "The name of the security groups serves as a prefix, e.g illumidesk"
}

variable "vpc_id" {
  description = "The VPC ID"
}

variable "environment" {
  description = "The environment, used for tagging, e.g prod"
}

variable "cidr" {
  description = "The cidr block to use for internal security groups"
}

variable "ingress_allow_cidr_blocks" {
  description = "A list of CIDR blocks to allow traffic from"
  type        = "list"
  default     = []
}

variable "ingress_allow_security_groups" {
  description = "A list of security group IDs to allow traffic from"
  type        = "list"
  default     = []
}

variable "port" {
  description = "Port for database to listen on"
  default     = 5432
}
