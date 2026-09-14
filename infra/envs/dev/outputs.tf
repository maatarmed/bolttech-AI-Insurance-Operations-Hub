output "frontend_url" {
  value = "http://${module.alb.public_alb_dns}"
}

output "internal_backend_url" {
  value = "http://${module.alb.internal_alb_dns}"
}

output "ecr_frontend" {
  value = module.ecr.frontend_url
}

output "ecr_backend" {
  value = module.ecr.backend_url
}

output "ecs_cluster" {
  value = module.ecs.cluster_name
}

output "frontend_service" {
  value = module.ecs.frontend_service_name
}

output "backend_service" {
  value = module.ecs.backend_service_name
}
