variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-west-1"
}

variable "username" {
  description = "Username prefix for resource naming"
  type        = string
  default     = "lukebowm"
}

variable "environment" {
  description = "Environment (dev, prod)"
  type        = string
  default     = "dev"
}
