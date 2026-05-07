# NEURA: Real-Time Social Listening

NEURA is an advanced, agentic social listening platform designed to monitor patient experience and safety signals across various online communities (Reddit, X, generic forums).

## Features
- **Real-Time Scraping**: Integrates with live data sources to pull unstructured patient posts.
- **LLM-Powered Analysis**: Uses Google Gemini to extract entities (drugs, symptoms), score sentiment, and flag critical adverse safety events.
- **Agentic Onboarding**: Automatically generates web scraping configurations for unknown URLs by analyzing their DOM using AI.
- **Premium Dashboard**: A sleek, zero-dependency Vanilla JS/CSS frontend interface featuring smooth animations and real-time metric counters.

## Quick Start

### Prerequisites
- Python 3.9+
- A Google Gemini API Key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/NEURA.git
cd NEURA
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the backend server:
```bash
uvicorn main:app --reload
```

4. Open the application:
Navigate to `http://localhost:8000` in your browser.

## How to Use
1. Paste your **Gemini API Key** into the Dashboard input.
2. Go to the **Projects** tab to set up monitored keywords (e.g., "Ozempic, nausea").
3. Add a **Data Source** (e.g., Reddit).
4. Run the Analysis Pipeline to see live data scraped and analyzed!
5. Test the **Agentic Onboarding** tab by passing any forum URL to generate a custom scraping JSON script.

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, SQLite
- **AI Integration**: Google GenAI (`google-genai`), BeautifulSoup4
- **Frontend**: HTML5, Vanilla JS, Custom CSS Animations
