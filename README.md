# AI-First CRM — HCP Module (Log Interaction Screen)

A pharmaceutical CRM module featuring an AI-powered split-screen interface for logging HCP interactions. Field reps interact **only through the chat** — the AI assistant fills and updates the form automatically.

## Tech Stack
| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, Redux Toolkit |
| Styling | Vanilla CSS, Google Inter |
| Backend | Python 3.11+, FastAPI |
| AI Agent | LangGraph |
| LLM (primary) | `llama-3.3-70b-versatile` via Groq (best tool-calling support) |
| LLM (reference) | `gemma2-9b-it` via Groq (mentioned in task requirements) |
| Database | PostgreSQL (via Docker) |
| ORM | SQLAlchemy |

## LangGraph Tools (5)
1. **`log_interaction`** — LLM extracts HCP name, date, topics, sentiment, materials from free text
2. **`edit_interaction`** — LLM identifies specific fields to update without touching others
3. **`search_hcp`** — LLM parses search intent; queries HCP database
4. **`suggest_follow_up`** — LLM analyzes the logged interaction and generates next-step recommendations
5. **`get_interaction_summary`** — LLM generates a professional written CRM-ready summary

## Prerequisites
- Node.js 18+
- Python 3.11+
- Docker (for PostgreSQL)
- A Groq API key from https://console.groq.com/

## Setup & Run

### Step 1: Start the database
```bash
docker-compose up -d
```

### Step 2: Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Seed the database with sample HCPs and materials
python seed.py

# Start the API server
uvicorn main:app --reload --port 8000
```

### Step 3: Frontend setup
```bash
cd frontend
npm install
npm run dev
```

### Step 4: Open the app
Navigate to **http://localhost:5173**

## Usage Examples

### Log a new interaction
Type in the chat:
> "Today I met with Dr. Smith and discussed ProduX efficacy. Sentiment was positive and I shared the brochures."

→ The AI will extract all fields and populate the form automatically.

### Edit a specific field
Type in the chat:
> "Sorry, the name was actually Dr. John and the sentiment was negative."

→ Only `hcp_name` and `sentiment` will update. All other fields remain unchanged.

### Search for an HCP
> "Find cardiologists in New York"

### Get follow-up suggestions
> "What should I do next with this HCP?"

### Generate a summary
> "Generate a summary of this interaction"

## Environment Variables (backend/.env)
```
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://crm_user:crm_pass@localhost:5432/crm_db
```
