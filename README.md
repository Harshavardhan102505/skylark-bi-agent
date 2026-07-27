# Skylark Drones - Business Intelligence AI Agent

## Architecture Overview
The system uses an OpenAI GPT-4o agent connected via Function Calling to a custom Monday.com GraphQL client. Data fetched from boards is passed through an in-memory `DataResilienceEngine` before LLM synthesis.

## Setup & Local Run
1. Clone repository: `git clone <repo-url>`
2. Install dependencies: `pip install -r requirements.txt`
3. Add credentials in `.env`:
   - `GROQ_API_KEY`
   - `MONDAY_API_TOKEN`
   - `DEALS_BOARD_ID`
   - `WORK_ORDERS_BOARD_ID`
4. Run locally: `streamlit run app.py`
