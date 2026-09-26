# Nusantara Care

## 1. Problem & Success Criteria
To solve the problem, we need to understand what's the problem first instead of just jumping into the solution.
And then, we need to define the success criteria for the solution.

Problem :
1. Employee faces the trouble to find the answer because of the spreading and massive documents
2. Employee faces the issue about they can't use the semantic keyword (so they have to use literal search)
3. AI can compose the story that unbased from the knowledge base

So the solution is to build an RAG (Retrieval-Augmented Generation) system that provides a knowledge-based response to the employee's query.

And the success criteria is to provide a knowledge-based response to the employee's query, with a human-like response that is easy to understandm and also based on real data. Also to eliminate the injection attacks, the system must be has the limit to it, for example like preventing the system from executing arbitrary code, or limiting the system to only respond to queries that are within the scope of the knowledge base.

## 2. Knowledge Base Understanding
The documents contain the nusantaracare protocol due to operationa internal services. And it's unique because it contains the different version on the same file. The rule is diffrentiate between two of them. The 1.4 version is just 3 days on tool submission and 2.0 is 5 days.

## 3. RAG Design & Data Preparation
Chunking: use MarkdownHeaderTextSplitter to separate the data by the "#" icon and the headings
Metadata per chunk: doc_id, doc_version, is_active, h2, h3, chunk_id.
Vector database: ChromaDB
Retrieval: top-k, filtering
Prompt: intstruction “jawab hanya dari konteks” and instruction to avoid prompt injection
Dokumen nonaktif/konflik: The data that contains 1.4 version will be not included in the chromadb database

## 4. Kesimpulan & Dokumentasi
NusantaraCare created an internal system where employees or internal staff can ask questions regarding operational guidelines. For the RAG pipeline, I used MarkdownHeaderTextSplitter instead of splitting chunks by character length to avoid cutting off critical document context. The architecture is fairly simple and aligns with the material provided.

Flow:
Request -> RAG -> LLM -> Schema -> Output

Before running the application, populate the document data using:

```Bash
python app/services/ingest.py
```

For local development, run the service using:

```Bash
PYTHONPATH=. fastapi dev app/main.py
```

This is an example of the request

```Bash
curl -X POST "http://localhost:8000/api/v1/ask" \
     -H "Content-Type: application/json" \
     -d '{
           "question": "Bagaimana prosedur pengajuan cuti tahunan?"
         }'
```

Conclusion:
This RAG system still requires several adjustments, such as more comprehensive test cases and additional enhancements. Furthermore, the model capabilities are currently limited due to using a free tier.
