# Kuber_Ai  — Gold Investment Chatbot

## Problem Statement
The task is to create a chatbot that can handle user queries related to gold investing. The chatbot provides clear, friendly, and accurate responses, guiding users on digital gold investment options, current gold prices, and basic financial advice. The bot also guides users on investing in digital gold.

---

## Tech Stack
- **Programming Language:** Python  
- **Frontend/UI:** Streamlit  
- **Backend/Database:** Supabase (PostgreSQL)  
- **Language Model:** Groq LLM (via LangChain-Groq)  
- **Environment Management:** Python 3.11, python-dotenv  

---

## Setup Instructions

### 1. Clone Repository
git clone <your-repo-url>
cd KUBER_Ai


### 2. Create Virtual Environment
python -m venv venv
source venv/bin/activate    macOS/Linux
venv\Scripts\activate        --Windows

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Set Up Environment Variables by creating a .env file in the root directory:
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-key>
GROK_API_KEY=<your-groq-api-key> 

### Execute the following queries in Supabase(PostgreSQL) SQL editor to set up the database schema:
### --For saving the message history
create table if not exists chat_history (
  id uuid primary key default gen_random_uuid(),
  session_id text not null,
  role text not null,       -- 'human' or 'ai'
  content text not null,
  created_at timestamp with time zone default now()
);

### For handling the large data we can create a B-Tree index on the session_id column:
create index if not exists idx_chat_history_session on chat_history(session_id);

### For saving the gold_investors data
create table if not exists gold_investors (
    id uuid primary key default gen_random_uuid(),
    session_id text not null,
    name text not null,
    phone text not null,
    amount numeric not null,
    created_at timestamp with time zone default now()
);

### Usage
Login: Enter your first name and phone number to start a session.
Chat: Ask questions about gold or investments.
Invest: When prompted, click “Invest Now” to navigate to the investment page.
Dynamic Investment Calculation: Enter the amount to invest and see the equivalent grams of digital gold in real time.
Confirm Investment: Saves your investment to Supabase for record-keeping.

### Folder Structure
.
├── app.py                 # Main chat interface
├── pages/
│   └── investment.py      # Investment page
├── chatbot/
│   ├── llm_handler.py     # Intent & LLM handling
│   └── supabase_history.py# Supabase client & chat history
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md
