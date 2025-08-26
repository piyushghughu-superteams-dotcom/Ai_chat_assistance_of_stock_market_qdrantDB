from qdrant_client import QdrantClient
from llm import get_response, get_finance_response, parse_query, is_relevant
from sentence_transformers import SentenceTransformer

client = QdrantClient(host="localhost", port=6333)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Ask user
user_query = input("Enter your query: ")


parsed_query = parse_query(user_query)
stocks = parsed_query["stocks_mentioned"]
date_range = parsed_query["date_range"]
routing = parsed_query["if_vector_or_live"]

print(f"\nParsed Query: {parsed_query}")

if routing == "live":
    print("\n> Fetching live data...\n")
    print(get_finance_response(user_query))
else:
    # Vector search
    query_vector = model.encode(user_query).tolist()
    query_filter = None
    if date_range != "none":
        query_filter = {"must": [{"key": "date", "match": {"value": date_range}}]}

    query_points = client.query_points(
        collection_name="stock",
        query=query_vector,
        limit=5,
        with_payload=True,
        query_filter=query_filter
    )

    best_response = None
    best_score = float('-inf')
    for point in query_points.points:
        score = point.score
        payload = point.payload
        if score > best_score:
            best_score = score
            best_response = payload

    if not best_response or not is_relevant(user_query, best_response):
        print("\n> No good match in database. Fetching live data...\n")
        print(get_finance_response(user_query))
    else:
        print("\n> Found in database:\n")
        print(get_response(best_response))
        print(f"\n(Qdrant match score: {best_score:.2f})")