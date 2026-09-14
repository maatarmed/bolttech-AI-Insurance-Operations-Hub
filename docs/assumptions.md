# Assumptions, tradeoffs, future work

## Assumptions

- Users are internal operations staff, not policyholders.
- Identity is knowledge-based: name + date of birth + policy number against seeded customers. No document KYC.
- All data is fictional.
- The default LLM is OpenAI `gpt-4o-mini`. If `OPENAI_API_KEY` is empty, the hub still runs: intent is rule-based and policy answers are the retrieved excerpts.
- Single region, single `dev` environment.

## Tradeoffs

| Choice | Alternative | Why |
|---|---|---|
| Supervisor + subgraphs | Four apps or one giant node | Shows transitions and reuses the identity gate |
| Keyword retrieval + optional LLM | Always-on pgvector embeddings | Works offline; still grounded |
| Postgres checkpointer with memory fallback | Redis | One data store; local resilience |
| Streamlit | Next.js | Fast workflow visibility, matches the preferred stack |
| Public HTTP ALB for UI | VPN-only internal ALB | Assessors can open the demo |
| One NAT | NAT per AZ | Cost for a take-home |
| Task env vars for secrets | Secrets Manager | Faster first apply; documented as a follow-up |

## Future improvements

- HTTPS listeners + ACM
- Secrets Manager and IAM least-privilege for Bedrock
- Cognito or SSO in front of the public ALB
- pgvector embeddings and retrieval grading as a dedicated node
- Human-in-the-loop `interrupt()` before high-value claim payouts
- WAF, VPC flow logs, and private DNS
