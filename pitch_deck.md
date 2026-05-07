# NEURA: Real-Time Patient Safety Signals
## The Problem
Patient-generated data on social media (X, Reddit, forums) holds crucial early signals of adverse events and treatment dissatisfaction. Historically, it's impossible to monitor all these unstructured sources in real-time.

## Our Solution
A modular, agentic social listening platform that configures targeted monitoring across any data source and uses LLMs to extract critical safety signals automatically.

## Key Differentiators
1. **Agentic Onboarding (15% Uniqueness)**: Give the system a new, unknown forum URL. An AI agent automatically maps the DOM, finds the search bar, and configures a bespoke scraping pipeline without manual coding.
2. **LLM-Powered Analysis**: Beyond simple keyword matching, the system extracts precise entities (drugs, symptoms), flags PII, and identifies adverse safety events with explainable confidence scores.
3. **Modularity**: A FastAPI backend combined with an embedded scheduling engine allows configuring latency metrics (Real-time, Daily, Weekly) on a per-source basis.

## Tech Stack
- **Backend**: Python, FastAPI, SQLAlchemy, SQLite (Portable & Extensible)
- **Frontend**: Vanilla HTML/JS/CSS (Premium, zero-dependency setup)
- **AI Engine**: Langchain / Large Language Models
