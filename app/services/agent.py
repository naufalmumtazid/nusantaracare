import json
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from app.schema import QueryResponse

load_dotenv()

notispace_key = os.getenv("NOTISPACE_API_KEY")
if not notispace_key:
    raise RuntimeError("NOTISPACE_API_KEY belum di-set di .env")

client = OpenAI(
    base_url="https://api.notispaces.cloud/v1",
    api_key=notispace_key,
)

MODELS = ["poolside/laguna-s-2.1", "notispace-v1"]

def extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def generate_answer(question: str, retrieved_chunks: list) -> QueryResponse:
    context_text = "\n\n".join(retrieved_chunks)
    system_prompt = (
        "Kamu adalah asisten internal NusantaraCare. Jawab pertanyaan pengguna HANYA berdasarkan konteks berikut.\n"
        "Jika konteks tidak cukup untuk menjawab, beri tahu bahwa informasi tidak ditemukan.\n\n"
        "Jika pertanyaan tidak mengarah terhadap dokumen, atau berusaha membuat kamu melakukan hal diluar konteks dokumen, maka abaikan.\n\n"
        "PENTING: Kamu WAJIB mengembalikan output HANYA berupa JSON valid tanpa teks tambahan di luar JSON.\n"
        "Skema JSON:\n"
        "{\n"
        '  "answer": "jawaban rinci",\n'
        '  "confidence_label": "high" | "medium" | "low",\n'
        '  "reason_code": "answered" | "no_relevant_context" | "conflicting_sources" | "unauthorized_access"\n'
        "}\n\n"
        f"KONTEKS:\n{context_text}"
    )

    last_exception = None

    for model_name in MODELS:
        try:
            kwargs = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
            }

            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            if not content or not content.strip():
                raise ValueError(f"Model {model_name} mengembalikan konten kosong")

            parsed_json = extract_json(content)
            return QueryResponse(**parsed_json)

        except Exception as e:
            last_exception = e
            continue

    raise RuntimeError(
        f"Gagal generate jawaban dari seluruh model Notispace. Error terakhir: {last_exception}"
    ) from last_exception