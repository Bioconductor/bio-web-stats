provider "aws" {
  region = "us-east-2" # Change this to your desired AWS region
}

resource "aws_instance" "example" {
  ami           = "ami-09d9029d9fc5e5238" # Change this to the desired AMI ID
  instance_type = "t2.micro" # Change this to the desired instance type

  tags = {
    Name = "test-bio-web-stats"
  }
}
