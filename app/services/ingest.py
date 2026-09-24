from app.services.rag import rag_system

if __name__ == "__main__":
    rag_system.index_document(
        file_path="data/raw_docs/nusantaracare_panduan_operasional_internal_v2.md"
    )