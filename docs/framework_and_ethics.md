# Chakra AI Safety Platform — Framework, Ethics & Use Cases

## 1. The Four Pillars

Chakra is built around four interconnected capabilities:

| Pillar | Purpose |
|---|---|
| **🔴 AI Red Team Simulator** | Proactively test LLMs against known and novel attack patterns |
| **📊 Trustworthiness Scorecard** | Quantify model safety, bias, and compliance across dimensions |
| **⚙️ Ethics Layer Plugin** | Real-time middleware filtering between users and LLMs |
| **📋 LLM Audit API** | Transparent, explainable decision logging for regulatory compliance |

---

## 2. Framework Architecture

### Ethics Layer Pipeline (Pillar 3)

Every prompt passes through a multi-stage guardrail pipeline:

| Stage | Method | Purpose |
|---|---|---|
| **Heuristic Analysis** | Regex + keyword + stealthy pattern matching | Detect direct injections, PII, social engineering, authority impersonation |
| **ML Classifier** | DistilBERT fine-tuned model | Detect jailbreak and adversarial intent semantically |
| **Vector Similarity** | FAISS index | Match against curated attack vector database |
| **Policy Engine** | Configurable per-tenant thresholds | Apply block/warn/allow/sanitize decisions |

Each stage records a **pipeline trace** — a structured log of its contribution to the final decision. This trace powers the Audit API's explainability.

### Red Team Simulator (Pillar 1)

Built-in attack suites organized by category:
- **Injection**: Direct instruction overrides ("ignore previous instructions")
- **Jailbreak**: Persona/mode switching ("DAN mode", "developer mode")
- **PII Leak**: Sensitive data exposure (SSN, email, credit card)
- **Social Engineering**: Flattery manipulation, authority impersonation, academic framing
- **Benign**: Control prompts to measure false positive rate

### Trustworthiness Scorecard (Pillar 2)

Three computed dimensions:
- **Safety** (0-10): Based on block rate — measures injection/jailbreak prevention effectiveness
- **Bias** (0-10): Based on warn rate — measures over-flagging of ambiguous content
- **Compliance** (0-10): Based on sanitize rate — measures PII/regulatory handling

### LLM Audit API (Pillar 4)

Every evaluation produces an immutable audit record containing:
- Timestamp, tenant, session identifiers
- The action taken and risk score
- Labels that triggered the decision
- **Decision trace**: Per-stage breakdown of which guardrail flagged what and why
- Latency metrics

---

## 3. Ethical Considerations

### Transparency
- Every decision includes a human-readable explanation and full pipeline trace
- No "black box" filtering — operators can inspect exactly why a prompt was flagged

### Fairness & Bias
- ML classifiers are monitored for false positives using benign control prompts
- Per-tenant thresholds allow tuning sensitivity to avoid over-blocking

### User Autonomy
- Blocked prompts return clear explanations, never silently modify user intent
- Sanitization is reserved exclusively for PII protection

### Accountability
- Immutable audit trail with decision traces supports regulatory compliance
- Red-team testing enables proactive vulnerability assessment

### Limitations
- Guardrails are defense-in-depth, not a substitute for responsible model training
- Novel attacks may evade detection; continuous retraining is essential
- Over-aggressive thresholds can harm usability

---

## 4. Use Cases

| Use Case | Pillars Used |
|---|---|
| **Enterprise LLM Deployment** | Ethics Layer + Audit API |
| **Pre-deployment Safety Testing** | Red Team Simulator + Scorecard |
| **Regulatory Compliance Auditing** | Audit API + Scorecard |
| **Multi-Tenant SaaS AI Platforms** | All four pillars |
| **AI Safety Research** | Red Team + Scorecard |

---

## 5. Regulatory Alignment

| Regulation | Chakra Feature |
|---|---|
| EU AI Act (High-Risk AI) | Audit logging, explainability, red-team testing |
| GDPR | PII detection & redaction, data minimization |
| NIST AI RMF | Risk scoring, continuous monitoring, red-teaming |
| SOC 2 Type II | Immutable audit trail, access control |
