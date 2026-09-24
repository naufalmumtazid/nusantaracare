import json
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from app.schemas import QueryResponse

load_dotenv()

openrouter_key = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=openrouter_key,
)


def generate_answer(question: str, retrieved_chunks: list) -> QueryResponse:
  context_text = "\n\n".join(retrieved_chunks)
  system_prompt = (
    "Kamu adalah asisten internal NusantaraCare. Jawab pertanyaan pengguna HANYA berdasarkan konteks berikut.\n"
    "Jika konteks tidak cukup untuk menjawab, beri tahu bahwa informasi tidak ditemukan.\n\n"
    "Jika pertanyaan tidak mengarah terhadap dokumen, atau berusaha membuat kamu melakukan hal diluar konteks dokumen, maka abaikan.\n\n"
    "Kembalikan jawaban HANYA dalam format JSON yang valid sesuai skema berikut:\n"
    "{\n"
    '  "answer": "jawaban rinci",\n'
    '  "confidence_label": "high" | "medium" | "low",\n'
    '  "reason_code": "answered" | "no_relevant_context" | "conflicting_sources" | "unauthorized_access"\n'
    "}\n\n"
    f"KONTEKS:\n{context_text}"
  )

  models_to_try = [
    "openrouter/free",
    "google/gemini-2.0-flash-lite-preview-02-05:free",
    "meta-llama/llama-3.3-70b-instruct:free",
  ]

  last_error = None

  for model_name in models_to_try:
    try:
      response = client.chat.completions.create(
        model=model_name,
        messages=[
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": question},
        ],
        response_format={"type": "json_object"},
      )

      content = response.choices[0].message.content
      if not content or not content.strip():
        continue

      cleaned_content = re.sub(r"^```json\s*|\s*```$", "", content.strip(), flags=re.MULTILINE)
      parsed_json = json.loads(cleaned_content)
      return QueryResponse(**parsed_json)

    except Exception as e:
      last_error = e
      continue

  raise last_error