variable "aws_region" {
  type    = string
  default = "ap-southeast-1"
}

variable "name" {
  type    = string
  default = "ops-hub-dev"
}

variable "db_username" {
  type    = string
  default = "hub"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "openai_api_key" {
  type      = string
  default   = ""
  sensitive = true
}

variable "frontend_image" {
  type    = string
  default = "public.ecr.aws/docker/library/python:3.12-slim"
}

variable "backend_image" {
  type    = string
  default = "public.ecr.aws/docker/library/python:3.12-slim"
}
