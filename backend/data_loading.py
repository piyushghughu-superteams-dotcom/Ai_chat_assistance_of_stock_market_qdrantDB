from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer
import csv

client = QdrantClient(host="localhost", port=6333)

def create_embeded_text(symbol, name, sector, price, marketcap, pe_ratio, dividend_yield, description):
    return f"Symbol:{symbol} | Name:{name} | Sector:{sector} | Price:{price} | MarketCap:{marketcap} | PE_Ratio:{pe_ratio} | Dividend_Yield:{dividend_yield} | Description:{description}"

if not client.collection_exists("stock"):
    client.create_collection(
        collection_name="stock",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
model = SentenceTransformer('all-MiniLM-L6-v2')

csv_file = "../data/stock_data.csv"


def get_embedding(text):
    vectors = model.encode(text)
    return vectors.tolist()

points = []
with open(csv_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for i, row in enumerate(reader):
        embedded_text = create_embeded_text(
            row['Symbol'],
            row['Name'],
            row['Sector'],
            row['Price'],
            row['MarketCap'],
            row['PE_Ratio'],
            row['Dividend_Yield'],
            row['Description']
        )
        vector = get_embedding(embedded_text)
        points.append({
            "id": i,
            "vector": vector,
            "payload": {
                "embedded_text": embedded_text,
                "Symbol": row['Symbol'],
                "Name": row['Name'],
                "Sector": row['Sector'],
                "Price": row['Price'],
                "MarketCap": row['MarketCap'],
                "PE_Ratio": row['PE_Ratio'],
                "Dividend_Yield": row['Dividend_Yield'],
                "Description": row['Description'],
            }
        })

# Insert into Qdrant
client.upsert(
    collection_name="stock",
    points=points
)
