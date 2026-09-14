# AWS architecture and networking

This is designed as an internal operations platform. The UI is reachable for a demo. The API and database are not.

```
Internet
  → public ALB :80
      → frontend Fargate (private subnet, no public IP)
          → internal ALB :80
              → backend Fargate :8000 (private)
                  → RDS Postgres (data subnets, 5432 from backend SG only)
                  → OpenAI / Bedrock via NAT
```

VPC `10.40.0.0/16`, two AZs, three tiers:

| Tier | Purpose |
|---|---|
| Public | public ALB, NAT, internet gateway |
| App private | both ECS services, internal ALB |
| Data private | RDS, no internet route |

Security groups are the service boundary. Frontend accepts 8501 only from the public ALB. The internal ALB accepts 80 only from the frontend SG. Backend accepts 8000 only from the internal ALB. RDS accepts 5432 only from the backend SG.

Frontend-to-backend communication is server-side HTTP to the internal ALB DNS (`BACKEND_URL`). The browser never sees the backend.

Demo compromise: the public ALB is HTTP:80 open to `0.0.0.0/0` so an assessor can open the console. A production insurer would use an internal ALB, VPN/SSO, HTTPS, and an IP allowlist.
