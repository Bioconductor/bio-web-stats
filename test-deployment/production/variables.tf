# development/variables.tf
variable "aws_region" {
  type    = string
  default = "us-east-2"
}

variable "ami_id" {
  type    = string
  default = "ami-09d9029d9fc5e5238"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}
