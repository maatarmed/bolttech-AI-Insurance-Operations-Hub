# LangGraph design

The hub is a parent `StateGraph` with four compiled subgraphs.

```
START → classify → identity | policy | claim_submit | claim_status | compose
identity → claim_status (if pending) | compose | error
policy / claim_submit / claim_status / error → compose → END
```

## State

`HubState` is the single contract. Important fields:

| Field | Role |
|---|---|
| `messages` | `add_messages` reducer, multi-turn history |
| `active_workflow` / `current_node` | UI visibility |
| `parked` | claim draft snapshot when the user switches |
| `identity_verified` | gate for claim status |
| `pending_workflow` | resume status after the identity gate |
| `claim_draft` / `missing_fields` / `awaiting_confirm` | slot filling |
| `retrieved_docs` | policy citations |

## Transitions

`classify` runs on every user turn. If the user is mid-claim and asks a policy question, the claim draft is copied into `parked` and the policy subgraph runs. “Resume the claim” restores that snapshot.

Claim status without a verified identity sets `pending_workflow=claim_status` and stores `requested_claim_number` when the user named a claim. After a successful verify, the hub continues into claim status in the same graph turn and looks up that claim.

## Session continuity

`thread_id` is the browser session UUID. Startup prefers `AsyncPostgresSaver`; if Postgres checkpoint setup fails, it falls back to `MemorySaver` so local demos still work inside one process.

## Error handling

Identity fails closed after three mismatches. Claim status refuses claims that do not belong to the verified customer. Compose never returns a stack trace. Policy answers are grounded in retrieved excerpts; if retrieval is empty the graph says it does not have that product.
