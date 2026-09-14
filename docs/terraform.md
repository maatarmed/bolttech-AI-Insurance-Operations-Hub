# Terraform structure

```
infra/
  modules/vpc
  modules/security
  modules/ecr
  modules/rds
  modules/alb
  modules/iam
  modules/ecs
  envs/dev
```

`envs/dev` is the only root module. It composes the others and exports the public frontend URL, internal backend URL, ECR URLs, and ECS names.

Apply:

```bash
cd infra/envs/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

Images default to a public Python placeholder so `validate` works before the first ECR push. CI/CD overwrites `frontend_image` and `backend_image` with the built tags.

One NAT gateway is used to keep the take-home cheap. Production should use one NAT per AZ.
