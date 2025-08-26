from fastapi import FastAPI
from llm import get_response, get_finance_response, parse_query, is_relevant
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

app = FastAPI()


origins = ["http://192.168.0.186:3000", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


qdrant = QdrantClient(host="localhost", port=6333)
embedder = SentenceTransformer("all-MiniLM-L6-v2")


class QueryRequest(BaseModel):
    query: str

# Response models
class ParsedQueryModel(BaseModel):
    stocks_mentioned: List[str]
    date_range: str
    if_vector_or_live: str

class QueryResponse(BaseModel):
    message: str
    source: str
    score: Optional[float] = None
    parsed_query: ParsedQueryModel

@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):
    # Parse the query using LLM
    parsed_query_dict = parse_query(req.query)
    parsed_query = ParsedQueryModel(**parsed_query_dict)
    
    routing = parsed_query.if_vector_or_live
    stocks = parsed_query.stocks_mentioned
    date_range = parsed_query.date_range

    # this is doing the live geminii search
    if routing == "live":
        return QueryResponse(
            message=get_finance_response(req.query),
            source="live",
            parsed_query=parsed_query
        )

    #it will perform vector search
    vector = embedder.encode(req.query).tolist()
    query_filter = None
    if date_range != "none":
        query_filter = {"must": [{"key": "date", "match": {"value": date_range}}]}

    results = qdrant.query_points(
        collection_name="stock",
        query=vector,
        limit=5,
        with_payload=True,
        query_filter=query_filter
    )

    best = max(results.points, key=lambda p: p.score, default=None)

    if not best or not is_relevant(req.query, best.payload):
        return QueryResponse(
            message=get_finance_response(req.query),
            source="live",
            parsed_query=parsed_query
        )

    return QueryResponse(
        message=get_response(best.payload),
        source="qdrant",
        score=best.score,
        parsed_query=parsed_query
    )
