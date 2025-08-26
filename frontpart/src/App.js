import React, { useState } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [chatLog, setChatLog] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = { role: 'user', content: query };
    setChatLog((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });

      const data = await response.json();

      let resultText = '';
      if (data.message) {
        resultText = data.message;
        if (data.source === "qdrant") {
          resultText += `\n\n(Qdrant match score: ${data.score?.toFixed(2)})`;
        } else if (data.source === "live") {
          resultText += `\n\n(Fetched from live finance API)`;
        }
      } else if (data.error) {
        resultText = '❌ Error: ' + data.error;
      } else {
        resultText = '❌ No results found.';
      }

      const botMessage = { role: 'bot', content: resultText };
      setChatLog((prev) => [...prev, botMessage]);
    } catch (error) {
      setChatLog((prev) => [
        ...prev,
        { role: 'bot', content: '❌ Error connecting to backend.' }
      ]);
    }

    setQuery('');
    setLoading(false);
  };

  const handleQuickQuery = (quickQuery) => setQuery(quickQuery);

  return (
    <div className="app-container">
      <h2>💰 AI Wealth Management Advisor</h2>
      <div className="chat-box">
        {chatLog.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div>
            {msg.content.split("\n").map((line, idx) => (
              line.trim().startsWith("*") ? (
                <li key={idx}>{line.replace("*", "").trim()}</li>
            ) : (
            <p key={idx}>{line}</p>
          )
        ))}
      </div>
          </div>
        ))}
        {loading && <div className="message bot">🤔 Analyzing your financial query...</div>}
      </div>

      <form className="input-form" onSubmit={handleQuery}>
        <input
          type="text"
          placeholder="Ask about investments, stocks, or finance..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}

export default App;
