output "alb_public_sg_id" {
  value = aws_security_group.alb_public.id
}

output "frontend_sg_id" {
  value = aws_security_group.frontend.id
}

output "alb_internal_sg_id" {
  value = aws_security_group.alb_internal.id
}

output "backend_sg_id" {
  value = aws_security_group.backend.id
}

output "rds_sg_id" {
  value = aws_security_group.rds.id
}
