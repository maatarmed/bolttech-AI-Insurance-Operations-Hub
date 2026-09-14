terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project = "ai-insurance-ops-hub"
      Env     = "dev"
    }
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

module "vpc" {
  source = "../../modules/vpc"
  name   = var.name
  azs    = slice(data.aws_availability_zones.available.names, 0, 2)
}

module "security" {
  source = "../../modules/security"
  name   = var.name
  vpc_id = module.vpc.vpc_id
}

module "ecr" {
  source = "../../modules/ecr"
  name   = var.name
}

module "rds" {
  source             = "../../modules/rds"
  name               = var.name
  subnet_ids         = module.vpc.data_subnet_ids
  security_group_ids = [module.security.rds_sg_id]
  username           = var.db_username
  password           = var.db_password
}

module "alb" {
  source             = "../../modules/alb"
  name               = var.name
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids
  public_sg_id       = module.security.alb_public_sg_id
  internal_sg_id     = module.security.alb_internal_sg_id
}

module "iam" {
  source = "../../modules/iam"
  name   = var.name
}

locals {
  database_url = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${module.rds.address}:${module.rds.port}/ops_hub"
  backend_url  = "http://${module.alb.internal_alb_dns}"
}

module "ecs" {
  source             = "../../modules/ecs"
  name               = var.name
  private_subnet_ids = module.vpc.private_subnet_ids
  frontend_sg_id     = module.security.frontend_sg_id
  backend_sg_id      = module.security.backend_sg_id
  frontend_image     = var.frontend_image
  backend_image      = var.backend_image
  frontend_tg_arn    = module.alb.frontend_tg_arn
  backend_tg_arn     = module.alb.backend_tg_arn
  execution_role_arn = module.iam.execution_role_arn
  task_role_arn      = module.iam.task_role_arn
  backend_url        = local.backend_url
  database_url       = local.database_url
  openai_api_key     = var.openai_api_key
}
