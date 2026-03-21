# Chakra — AI Safety & Alignment Platform

Chakra is a deployable, zero-trust AI safety platform built around **four core pillars** for testing, auditing, and protecting Large Language Models.

## The Four Pillars

### 🔴 1. AI Red Team Simulator
A sandbox where developers can test LLMs against prompt injection, jailbreaks, PII leaks, social engineering, and harmful content scenarios.
- **Built-in attack suites** organized by category (injection, jailbreak, PII, social engineering, benign)
- **Configurable categories** — select which attack types to include in each run
- **Detection rate metrics** and per-category breakdowns

### 📊 2. Trustworthiness Scorecard
A dashboard that measures model safety, bias, and compliance based on inputs and outputs.
- **Three dimensions**: Safety (injection/jailbreak prevention), Bias (over-flagging analysis), Compliance (PII/regulatory handling)
- **Composite trust score** computed from dimensional metrics
- **Baseline vs. protected** comparisons

### ⚙️ 3. Ethics Layer Plugin
A middleware tool that sits between user prompts and model responses, filtering unsafe or misleading outputs.
- **Multi-stage pipeline**: Heuristic Analysis → ML Classifier → Vector Similarity → Policy Engine
- **Pipeline trace**: Step-by-step breakdown of how each stage contributed to the decision
- **Configurable per-tenant policies** with tunable thresholds

### 📋 4. LLM Audit API
An API that logs and explains decisions made by the model to support transparency and regulatory auditing.
- **Decision traces** showing exactly which guardrail stage flagged what
- **Full audit history** with prompt snippets, risk scores, labels, and explanations
- **Regulatory compliance** support (EU AI Act, GDPR, NIST AI RMF, SOC 2)

## Architecture

```text
       [ Client / App ]
              │ (HTTP/REST)
              ▼
    [ Chakra Gateway API ]
              │
    ┌─────────┼─────────────────────┐
    │         │                     │
    ▼         ▼                     ▼
 [Red Team] [Ethics Layer]    [Audit API]
              │
              ▼
 [ Guardrail Engine Pipeline ]
   ├─ Heuristics (Regex + Stealthy Patterns)
   ├─ ML Classifier (Transformers)
   ├─ Vector Search (FAISS)
   └─ Policy Engine (Per-Tenant)
              │
              ▼
    [Trustworthiness Scorecard]
```

## Getting Started

### Run Locally
```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000/** for the dashboard.

### Run via Docker
```bash
docker-compose up -d --build
```

### Run Tests
```bash
pytest tests/ -v
```

## API Endpoints

| Pillar | Endpoint | Method | Description |
|---|---|---|---|
| Ethics Layer | `/v1/filter` | POST | Evaluate a prompt through the guardrail pipeline |
| Red Team | `/v1/redteam/run` | POST | Run adversarial attack suite |
| Scorecard | `/v1/scorecard` | GET | Get trustworthiness metrics |
| Audit API | `/v1/audit/logs` | GET | Query decision audit logs |
| System | `/health` | GET | Health check |

## Documentation
- [Framework, Ethics & Use Cases](docs/framework_and_ethics.md)
- [Evaluation Results](docs/evaluation_results.md)
- [Evaluation Dataset](data/evaluation_dataset.json)
