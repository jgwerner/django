
/**
 * This module is used to set configuration defaults for the AWS infrastructure.
 * It doesn't provide much value when used on its own because terraform makes it
 * hard to do dynamic generations of things like subnets, for now it's used as
 * a helper module for the illumidesk deployment.
 *
 * Usage:
 *
 *     module "defaults" {
 *       source = "./defaults"
 *       region = "us-east-1"
 *       cidr   = "10.0.0.0/16"
 *     }
 *
 */

variable "region" {
  description = "The AWS region"
}

variable "cidr" {
  description = "The CIDR block to provision for the VPC"
}

variable "default_ecs_ami" {
  default = {
    us-east-2	      =	"ami-0aa9ee1fc70e57450"
    us-east-1	      =	"ami-007571470797b8ffa"
    us-west-2	      =	"ami-0302f3ec240b9d23c"
    us-west-1	      =	"ami-0935a5e8655c6d896"
    eu-west-3	      =	"ami-0b419de35e061d9df"
    eu-west-2	      =	"ami-0380c676fcff67fd5"
    eu-west-1	      =	"ami-0b8e62ddc09226d0a"
    eu-central-1	  =	"ami-01b63d839941375df"
    eu-north-1	    =	"ami-03f8f3eb89dcfe553"
    ap-northeast-2	=	"ami-0c57dafd95a102862"
    ap-northeast-1	=	"ami-086ca990ae37efc1b"
    ap-southeast-2	=	"ami-0d28e5e0f13248294"
    ap-southeast-1	=	"ami-0627e2913cf6756ed"
    ca-central-1	  =	"ami-0835b198c8a7aced4"
    ap-south-1	    =	"ami-05de310b944d67cde"
    sa-east-1	      =	"ami-09987452123fadc5b"
  }
}

# http://docs.aws.amazon.com/ElasticLoadBalancing/latest/DeveloperGuide/enable-access-logs.html#attach-bucket-policy
variable "default_log_account_ids" {
  default = {
    us-east-1      = "127311923021"
    us-east-2	     = "033677994240"
    us-west-1      = "027434742980"
    us-west-2      = "797873946194"
    ca-central-1   = "985666609251"
    eu-west-1      = "156460612806"
    eu-central-1   = "054676820928"
    ap-southeast-1 = "114774131450"
    ap-southeast-2 = "783225319266"
    ap-northeast-1 = "582318560864"
    ap-northeast-2 = "600734575887"
    ap-northeast-3 = "383597477331"
    ap-south-1     = "718504428378"
    sa-east-1      = "507241528517"
  }
}

output "domain_name_servers" {
  value = "${cidrhost(var.cidr, 2)}"
}

output "ecs_ami" {
  value = "${lookup(var.default_ecs_ami, var.region)}"
}

output "s3_logs_account_id" {
  value = "${lookup(var.default_log_account_ids, var.region)}"
}