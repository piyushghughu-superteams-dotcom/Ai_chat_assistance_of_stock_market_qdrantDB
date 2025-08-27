<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>💰 AI Wealth Management Advisor</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 2rem;
      line-height: 1.6;
      background: #f9f9f9;
      color: #222;
    }
    h1, h2, h3 {
      color: #0d6efd;
    }
    pre, code {
      background: #eee;
      padding: 0.5rem;
      border-radius: 6px;
      display: block;
      overflow-x: auto;
    }
    .box {
      background: #fff;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 1rem;
      margin: 1rem 0;
      box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    ul {
      margin-left: 1.2rem;
    }
  </style>
</head>
<body>

<h1>💰 AI Wealth Management Advisor</h1>
<p>
  An <strong>AI-powered financial assistant</strong> that answers natural language queries about
  <strong>stocks, investments, and finance</strong>.  
</p>
<p>
It uses a <strong>hybrid retrieval approach</strong>:
<ul>
  <li><strong>Qdrant Vector Database</strong> → stock knowledge from CSV dataset.</li>
  <li><strong>Google Gemini API</strong> → fetches live market data.</li>
  <li><strong>Groq LLM (Llama 3.1)</strong> → query parsing, relevance check, and response formatting.</li>
  <li><strong>FastAPI + React</strong> → smooth chat UI for user interaction.</li>
</ul>
</p>

<hr>

<h2>🚀 Features</h2>
<ul>
  <li>Ask questions in plain English about stocks, PE ratio, market cap, or dividend yield.</li>
  <li>Smart routing between <strong>local Qdrant DB</strong> and <strong>live Gemini finance API</strong>.</li>
  <li>LLM-powered <em>query parsing</em> (stock symbols, date range, routing decision).</li>
  <li>React frontend chat interface.</li>
</ul>

<hr>

<h2>🏗️ Project Structure</h2>
<pre>
project-root/
│── backend/
│   ├── data_loading.py      # Load CSV stock data → embeddings → Qdrant
│   ├── llm.py               # Groq + Gemini logic
│   ├── query_engine.py      # CLI query tester
│   ├── main.py              # FastAPI backend
│   ├── requirements.txt     # Python deps
│   └── .env                 # API keys
│
│── frontend/
│   ├── src/App.js           # React chat UI
│   ├── src/App.css          # Styling
│   └── package.json
│
│── data/
│   └── stock_data.csv       # Stock dataset
│
└── README.html              # This file
</pre>

<hr>

<h2>⚡ Tech Stack</h2>
<ul>
  <li><strong>Backend</strong>: FastAPI, Groq API, Gemini API, Qdrant Client, SentenceTransformers</li>
  <li><strong>Database</strong>: Qdrant (Vector DB)</li>
  <li><strong>Frontend</strong>: React</li>
  <li><strong>Embeddings</strong>: all-MiniLM-L6-v2</li>
</ul>

<hr>

<h2>🔑 Setup Instructions</h2>

<h3>1️⃣ Start Qdrant with Docker</h3>
<pre>docker run -p 6333:6333 qdrant/qdrant</pre>

<h3>2️⃣ Backend Setup</h3>
<pre>
cd backend
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
</pre>

<h4>requirements.txt</h4>
<pre>
fastapi
uvicorn
qdrant-client
sentence-transformers
python-dotenv
groq
google-genai
pydantic
</pre>

<h4>Create <code>.env</code> file:</h4>
<pre>
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
</pre>

<h3>3️⃣ Load Stock Data</h3>
<pre>python data_loading.py</pre>

<h3>4️⃣ Start Backend</h3>
<pre>uvicorn main:app --reload</pre>
<p>API runs at <code>http://localhost:8000</code></p>

<h3>5️⃣ Frontend Setup</h3>
<pre>
cd frontend
npm install
npm start
</pre>
<p>Frontend runs at <code>http://localhost:3000</code></p>

<hr>

<h2>💡 Usage</h2>
<p>Ask questions like:</p>
<ul>
  <li>"Show me the PE ratio of TCS"</li>
  <li>"Which companies have the highest dividend yield?"</li>
  <li>"What is the current stock price of Reliance?"</li>
</ul>

<div class="box">
  <strong>Example Response (from Qdrant)</strong>
  <pre>
Infosys Ltd (INFY)
- Price: 1530.25
- MarketCap: 6.5T
- PE_Ratio: 27.5
- Dividend_Yield: 2.1%

(Qdrant match score: 0.92)
  </pre>
</div>

<div class="box">
  <strong>Example Response (from Live Gemini API)</strong>
  <pre>
Reliance Industries Ltd (RELIANCE)
- Current Price: ₹2745
- Market Cap: ₹18.5T
- PE Ratio: 23.1
- Dividend Yield: 0.34%

(Fetched from live finance API)
  </pre>
</div>

<hr>

<h2>🔄 How It Works (Flow)</h2>
<pre>
User Query → FastAPI (/query) → parse_query() [Groq LLM]
        ├── if_vector_or_live == "vector" → Embed → Qdrant search
        │       ├── If relevant → get_response() [Groq LLM formats payload]
        │       └── Else → fallback to Gemini live data
        └── if_vector_or_live == "live" → get_finance_response() [Gemini]
</pre>

<hr>

<h2>✨ Future Improvements</h2>
<ul>
  <li>Support multiple datasets</li>
  <li>Better date filtering in Qdrant</li>
  <li>Add authentication for API</li>
  <li>Deploy on cloud (AWS/GCP/Azure)</li>
</ul>

<hr>

<h2>👨‍💻 Author</h2>
<p>Built with ❤️ by <strong>Piyush Ghughu</strong></p>

</body>
</html>
