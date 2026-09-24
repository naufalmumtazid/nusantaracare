import os
import chromadb
import yaml
from langchain_text_splitters import MarkdownHeaderTextSplitter
import json

chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(name="policies")


class RAGPipeline:
	def __init__(self, collection):
		self.collection = collection

		self.headers_to_split = [
			("##", "h2"),
			("###", "h3"),
		]

		self.splitter = MarkdownHeaderTextSplitter(headers_to_split_on=self.headers_to_split, strip_headers=False)

	def _parse_formatter(self, content: str):
		if content.startswith("---"):
			parts = content.split("---", 2)
			if len(parts) >= 3:
				yaml_text = parts[1]
				body_text = parts[2]
				metadata = yaml.safe_load(yaml_text) or {}
				return metadata, body_text
		return {}, content

	def index_document(self, file_path: str):
		print(f"Memproses Dokumen: {file_path}")

		if not os.path.exists(file_path):
			print(f"[Error] File tidak ditemukan di path: {file_path}")
			return

		with open(file_path, "r", encoding="utf-8") as f:
			content = f.read()

		base_metadata, body_text = self._parse_formatter(content)
		docs = self.splitter.split_text(body_text)

		documents = []
		metadatas = []
		ids = []

		for idx, doc in enumerate(docs):
			documents.append(doc.page_content)

			h2 = doc.metadata.get("h2", "")
			h3 = doc.metadata.get("h3", "")

			is_active = bool(base_metadata.get("is_active", True))
			doc_version = str(base_metadata.get("doc_version", "2.0"))

			if "v1.4" in h3.lower() or "v1.4" in doc.page_content.lower() or "nonaktif" in h3.lower():
					is_active = False
					doc_version = "1.4"

			chunk_meta = {
					"doc_id": str(base_metadata.get("doc_id", "DOC")),
					"doc_version": doc_version,
					"is_active": is_active,
					"h2": h2,
					"h3": h3,
					"chunk_id": f"chunk_{idx}",
			}

			metadatas.append(chunk_meta)
			ids.append(f"{base_metadata.get('doc_id', 'DOC')}_v2_{idx}")

		self.collection.upsert(
			documents=documents,
			metadatas=metadatas,
			ids=ids
		)

		print(f"Data berhasil ditambahkan di db")

	def query_rag(self, user_question: str) -> dict:
		results = self.collection.query(
			query_texts=[user_question], n_results=1, where={
				"$and": [
							{"is_active": True},
							{"doc_version": "2.0"}
					]
			}
		)
		return results


rag_system = RAGPipeline(collection=collection)