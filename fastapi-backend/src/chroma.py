import chromadb

client = chromadb.HttpClient(host="vector-backend", port=8000, ssl=False)
print(client)
