# AI Insurance Operations Hub

LangGraph operations console for insurance workflows. Two services, one Postgres database, Terraform for AWS ECS.

The frontend is Streamlit. The backend is FastAPI. LangGraph is the only orchestrator.

## Run locally

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:8501 |
| Backend health | http://localhost:8000/health |
| Ready + seed | http://localhost:8000/ready |
| OpenAPI | http://localhost:8000/docs |

Optional: copy `.env.example` and set `OPENAI_API_KEY`. Without a key the graph still runs using deterministic routing and grounded policy excerpts.

## Interview demo

1. “What does Product A cover?”
2. “I want to file a claim” — fill some fields.
3. Mid-flow: “Is water damage included?”
4. “Resume the claim”, confirm, get a claim number.
5. “What’s the status of my claim?” — identity gate, then a status summary.
6. Refresh the browser — the `?session=` URL keeps the same thread. You can also paste the UUID into **Load session**.

Demo identity: **Amelia Chen**, DOB **1988-03-14**, policy **POL-A-10021**. Seeded status claim: **CLM-2026-0001**.

## Tests

```bash
python -m pip install -r backend/requirements.txt
pytest
```

## AWS

See [docs/aws-networking.md](docs/aws-networking.md) and [docs/terraform.md](docs/terraform.md).

```bash
cd infra/envs/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

## Documentation

- [Solution architecture](docs/architecture.md)
- [LangGraph design](docs/langgraph.md)
- [AWS and networking](docs/aws-networking.md)
- [Terraform](docs/terraform.md)
- [CI/CD](docs/cicd.md)
- [Assumptions and tradeoffs](docs/assumptions.md)
