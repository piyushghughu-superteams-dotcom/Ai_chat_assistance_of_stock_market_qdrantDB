import os
import json
from groq import Groq
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Literal

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
google_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class ParsedQuery(BaseModel):
    stocks_mentioned: List[str] = Field(
        default_factory=list,
        description="listing of stock tickers or company names mentioned in the query"
    )
    date_range: str = Field(
        default="none",
        description="Date range mentioned in the query (e.g., 'last week', '2023', 'none')"
    )
    if_vector_or_live: Literal["vector", "live"] = Field(
        description="Whether to use vector search or live data"
    )


PARSE_SYSTEM_PROMPT = """
You are a financial assistant that parses user queries to extract structured information. 
Return ONLY valid JSON in this structure:
{
  "stocks_mentioned": ["ticker1", "ticker2"],
  "date_range": "string or none",
  "if_vector_or_live": "vector" or "live"
}
No extra text, no explanations.
"""

SYSTEM_PROMPT = """
Convert the Python dictionary payload(s) into a clean, human-readable answer.
- If multiple answers are returned, format them as a bullet list.
- Clearly label values like Price, MarketCap, PE_Ratio, and Dividend_Yield.
- Respond in plain English, not JSON or dict format.
"""

SYSTEM_PROMPT2 = """
You are a financial assistant with expertise in stocks, money, and finance.
Instructions:
1. If the user asks about any stock, finance, or money-related query:
   - Fetch the most recent market data available.
   - Always return the following details (if available):
        • Current Price
        • Market Cap
        • PE Ratio
        • Dividend Yield
2. If any information is missing, explicitly say: "Data not available".
3. Keep responses concise, professional, and informative.
4. Always relate your answer directly to the user query.
5. Ensure your response mentions:
   - current_price
   - market_cap
   - pe_ratio
   - dividend_yield
6. Always try to give answer based on the latest market data.
"""

RELEVANCE_PROMPT = """
Given the user query and the retrieved data, determine if the data is relevant and sufficient to fully answer the query.
Respond only with 'yes' or 'no'.
"""


def parse_query(user_query: str) -> dict:
    """
    Parse the user query into stocks, date_range, and routing.
    Uses Groq LLM and strictly parses JSON manually.
    Fills defaults if fields are missing or None.
    """
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": PARSE_SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ],
        model="llama-3.1-8b-instant"
    )

    raw_output = response.choices[0].message.content.strip()
    
    try:
        parsed_args = json.loads(raw_output)
    except json.JSONDecodeError:
        print("Failed to parse JSON from LLM:", raw_output)
        parsed_args = {}

    stocks = parsed_args.get("stocks_mentioned") or []
    date_range = parsed_args.get("date_range") or "none"
    routing = parsed_args.get("if_vector_or_live") or "vector"

    validated = ParsedQuery(
        stocks_mentioned=stocks,
        date_range=date_range,
        if_vector_or_live=routing
    )

    return validated.model_dump()



def get_response(text: dict) -> str:
    result = ""
    stream = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(text)}
        ],
        model="llama-3.1-8b-instant",
        stream=True
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            result += chunk.choices[0].delta.content
    return result


def get_finance_response(user_query: str) -> str:
    try:
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        response = google_client.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT2,
                thinking_config=types.ThinkingConfig(thinking_budget=2500),
                tools=[grounding_tool]
            ),
            contents=user_query
        )
        return response.text
    except Exception as e:
        print("Error fetching finance data:", e)
        return "Error fetching live data."


def is_relevant(user_query: str, payload: dict) -> bool:
    prompt = f"User query: {user_query}\nRetrieved data: {json.dumps(payload)}"
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": RELEVANCE_PROMPT},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.1-8b-instant",
    )
    answer = response.choices[0].message.content.strip().lower()
    return answer == 'yes'
