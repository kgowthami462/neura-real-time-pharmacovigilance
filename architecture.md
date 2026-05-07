# System Architecture

```mermaid
graph TD
    UI[Frontend Dashboard (HTML/JS/CSS)] -->|REST API| API[FastAPI Backend]
    
    subgraph Backend Services
        API --> DB[(SQLite Database)]
        API --> Scheduler[Background Scheduler]
        Scheduler --> Crawler[Crawler Engine]
        Crawler --> Analyzer[LLM Analysis Pipeline]
    end
    
    subgraph Crawler Engine
        Crawler --> Reddit[Reddit Scraper]
        Crawler --> X[X API Client]
        Crawler --> Agentic[Agentic Web Crawler]
    end
    
    subgraph Data Sources
        Reddit --> Web1(Reddit.com)
        X --> Web2(X / Twitter)
        Agentic --> Web3(Unknown Medical Forums)
    end
    
    Analyzer --> DB
    Crawler --> DB
```

## Flow Description
1. User configures a **Project** (keywords) and **Sources** via the Dashboard.
2. The **Scheduler** triggers the **Crawler Engine** based on the configured latency (Real-time, Daily, Weekly).
3. The **Crawler Engine** acquires unstructured text and saves it to the Database as `AcquiredData`.
4. The **LLM Analysis Pipeline** processes the raw text, extracting sentiments, entities, and adverse event flags, saving to `AnalysisResults`.
5. The **Dashboard** polls the REST API to visualize the signals in real-time.
