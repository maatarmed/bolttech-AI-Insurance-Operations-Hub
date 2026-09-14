# CI/CD design

GitHub Actions has two workflows.

**CI** (`ci.yml`) on every push/PR:

- Python 3.12, `ruff`, `pytest`
- `terraform fmt -check`, `init -backend=false`, `validate`

**Deploy** (`deploy.yml`) on `main` only when `AWS_ROLE_ARN` is configured:

- OIDC into AWS (no long-lived keys)
- Build and push frontend/backend images to ECR
- `terraform apply`
- Force new ECS deployments for both services

Required GitHub configuration:

- Variables: `AWS_ROLE_ARN`, `AWS_REGION`, `ECR_FRONTEND`, `ECR_BACKEND`, `ECS_CLUSTER`, `ECS_FRONTEND`, `ECS_BACKEND`
- Secrets: `DB_PASSWORD`, `OPENAI_API_KEY`
