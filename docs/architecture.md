# Architecture Reference

## Full Enterprise Architecture

The complete solution architecture for the AI-Driven Prior Authorization system is documented in the solutions-architecture-agent repository:

- **Proposal**: [solutions-architecture-agent/outputs/eng-2026-004/proposal.md](https://github.com/praeducer/solutions-architecture-agent)
- **Implementation Spec**: [solutions-architecture-agent/outputs/eng-2026-004/plans/implementation-prompt.md](https://github.com/praeducer/solutions-architecture-agent)

## Demo vs Production

| Aspect | Demo (This Repo) | Production (Full Architecture) |
|--------|-------------------|-------------------------------|
| **API Gateway** | FastAPI direct | Amazon API Gateway + WAF |
| **Event Bus** | Kafka (Docker, single node) | Amazon MSK (multi-AZ) |
| **AI Engine** | Amazon Bedrock (Claude) | Autonomize AI PA Copilot + Bedrock |
| **Database** | PostgreSQL (Docker) | Amazon RDS (Multi-AZ) |
| **Audit** | PostgreSQL table | DynamoDB (append-only) |
| **Clinical Data** | Mock FHIR R4 server | AWS HealthLake + EMR endpoints |
| **Eligibility** | Mock Facets API | TriZetto Facets integration |
| **Guidelines** | Mock InterQual API | InterQual/MCG live APIs |
| **Ingestion** | Portal only | Portal + Fax OCR + X12 278 EDI |
| **Security** | None (demo) | Zero-trust, HIPAA, encryption |
| **Deployment** | Docker Compose (local) | EKS + Fargate (multi-AZ) |
| **Observability** | Console logs | CloudWatch + OpenTelemetry |

## Key Design Decisions

1. **Event-driven architecture** — Kafka decouples ingestion from processing, enabling async PA handling
2. **Mock services** — Simulate external APIs to demonstrate integration patterns without vendor dependencies
3. **AI determination** — Amazon Bedrock provides clinical decision support with confidence scoring
4. **Audit trail** — Every determination is logged with full context for compliance demonstration
