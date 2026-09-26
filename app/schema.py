from typing import Literal
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(
        description="Pertanyaan pengguna terkait panduan operasional NusantaraCare"
    )


class QueryResponse(BaseModel):
    answer: str = Field(
        description="Jawaban langsung dan rinci berdasarkan konteks dokumen v2.0 yang aktif"
    )
    confidence_label: Literal["high", "medium", "low"] = Field(
        description="Tingkat keyakinan: 'high' jika dokumen sangat relevan, 'medium' jika cukup relevan, 'low' jika informasi tidak ditemukan atau kurang spesifik"
    )
    reason_code: Literal[
        "answered",
        "no_relevant_context",
        "conflicting_sources",
        "unauthorized_access",
    ] = Field(
        description=(
            "Kode alasan respons: 'answered' jika berhasil dijawab, "
            "'no_relevant_context' jika di luar cakupan, "
            "'conflicting_sources' jika isi dokumen bertentangan, "
            "'unauthorized_access' jika akses ditolak"
        )
    )