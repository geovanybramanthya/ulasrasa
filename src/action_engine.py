"""Mesin generatif rekomendasi evaluasi dapur dan action checklist operasional.

Urutan generasi (keputusan arsitektur Q2/Q9/Q15):
1. LLM Gemini (key env GEMINI_API_KEY)
2. LLM Groq (key env GROQ_API_KEY)
3. Katalog template terstruktur (fallback terakhir, deterministik)

LLM hanya menerima payload JSON teragregasi (skor aspek kritis + contoh
ulasan negatif per aspek), tidak pernah seluruh ulasan mentah, dan hanya
boleh memakai fakta dari payload itu. Hasil LLM di-cache per hash payload.
Kegagalan panggil/parse LLM tidak pernah diteruskan ke pengguna: engine
selalu turun ke provider berikutnya atau ke template.
"""

import hashlib
import json
import os
from typing import Dict, Any, List, Optional, Tuple, Union

import requests

try:
    from .preprocessing import ASPECT_KEYWORDS
except Exception:  # pragma: no cover - fallback bila struktur paket berubah
    ASPECT_KEYWORDS = {}

GEMINI_DEFAULT_MODEL = "gemini-3.5-flash"
GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
LLM_TIMEOUT_SECONDS = 30
LLM_TEMPERATURE = 0.3
MAX_SAMPLES_PER_ASPECT = 5
CRITICAL_SCORE_THRESHOLD = 70.0

_PROMPT_INSTRUCTION = """Kamu adalah konsultan operasional dapur untuk restoran Indonesia.
Tugasmu: susun analisis akar masalah, checklist tindakan dapur, dan rekomendasi SOP
berdasarkan DATA AGREGAT keluhan pelanggan berikut.

ATURAN KETAT:
- Gunakan HANYA fakta yang ada di DATA. Dilarang menyebutkan menu, bahan, peralatan,
  harga, atau masalah apa pun yang tidak muncul di DATA.
- Semua keluaran berbahasa Indonesia, konkret, dan bisa dieksekusi staf dapur hari ini juga.
- Balas HANYA dengan JSON valid (tanpa markdown, tanpa teks tambahan) ber-skema persis:
  {"root_cause_analysis": ["..."], "kitchen_action_checklist": ["..."], "sop_recommendations": ["..."]}
- root_cause_analysis: satu string per aspek kritis di DATA.
- kitchen_action_checklist: langkah tindakan konkret per aspek kritis.
- sop_recommendations: satu string SOP per aspek kritis.

DATA:
"""


class ActionPlanEngine:
    """Menghasilkan analisis akar masalah dan checklist tindakan dapur."""

    def __init__(self, api_key: Optional[str] = None, provider: str = "gemini"):
        self.api_key = api_key
        self.provider = provider
        # Cache hasil LLM tervalidasi: hash payload -> (data LLM, nama provider)
        self._llm_cache: Dict[str, Tuple[Dict[str, List[str]], str]] = {}

    # ------------------------------------------------------------------
    # Resolusi API key (dibaca saat pemanggilan, tidak pernah hardcoded)
    # ------------------------------------------------------------------
    def _provider_keys(self) -> Tuple[Optional[str], Optional[str]]:
        gemini_key = os.getenv("GEMINI_API_KEY") or (
            self.api_key if self.provider == "gemini" else None
        )
        groq_key = os.getenv("GROQ_API_KEY") or (
            self.api_key if self.provider == "groq" else None
        )
        return gemini_key, groq_key

    # ------------------------------------------------------------------
    # Payload teragregasi untuk LLM
    # ------------------------------------------------------------------
    def _map_complaints_to_aspects(
        self,
        sample_complaints: List[str],
        aspect_names: List[str],
    ) -> Dict[str, List[str]]:
        """Petakan contoh keluhan ke aspek kritis via kecocokan kata kunci aspek.

        Keterbatasan: call site di app.py menggabungkan contoh keluhan semua
        aspek menjadi satu list datar (label aspek hilang), jadi pemetaan di
        sini direkonstruksi secara heuristik dari kata kunci aspek. Keluhan
        yang tidak cocok aspek mana pun menjadi cadangan umum.
        """
        assigned: Dict[str, List[str]] = {name: [] for name in aspect_names}
        general_pool: List[str] = []
        complaints = [c.strip() for c in (sample_complaints or []) if isinstance(c, str) and c.strip()]

        for complaint in complaints:
            lowered = complaint.lower()
            best_aspect, best_score = None, 0
            for aspect in aspect_names:
                keywords = ASPECT_KEYWORDS.get(aspect, [aspect])
                score = sum(1 for kw in keywords if kw in lowered)
                if score > best_score:
                    best_aspect, best_score = aspect, score
            if best_aspect is not None:
                assigned[best_aspect].append(complaint)
            else:
                general_pool.append(complaint)

        for aspect in aspect_names:
            samples = assigned[aspect][:MAX_SAMPLES_PER_ASPECT]
            if not samples:
                samples = general_pool[:MAX_SAMPLES_PER_ASPECT]
            assigned[aspect] = samples
        return assigned

    def _build_llm_payload(
        self,
        restaurant_name: str,
        evaluation_results: Dict[str, Any],
        critical_aspects: List[Any],
        sample_complaints: Union[List[str], Dict[str, List[str]]],
    ) -> Dict[str, Any]:
        aspect_names = [name for name, _ in critical_aspects]
        if isinstance(sample_complaints, dict):
            # Pemetaan eksak dari call site: {aspek: [teks keluhan, ...]}
            # tanpa heuristik kata kunci.
            samples_by_aspect = {
                name: [
                    str(c).strip()
                    for c in (sample_complaints.get(name) or [])
                    if isinstance(c, str) and str(c).strip()
                ][:MAX_SAMPLES_PER_ASPECT]
                for name in aspect_names
            }
        else:
            samples_by_aspect = self._map_complaints_to_aspects(
                sample_complaints, aspect_names
            )
        return {
            "restaurant_name": restaurant_name,
            "kitchen_health_score": evaluation_results.get("kitchen_health_score", 0.0),
            "critical_aspects": [
                {
                    "aspect": aspect_name,
                    "satisfaction_score": data.get("satisfaction_score", 100.0),
                    "negative_count": int(data.get("negative", 0)),
                    "sample_negative_reviews": samples_by_aspect.get(aspect_name, []),
                }
                for aspect_name, data in critical_aspects
            ],
        }

    # ------------------------------------------------------------------
    # Panggilan LLM (REST via requests, tanpa SDK tambahan)
    # ------------------------------------------------------------------
    def _call_gemini(self, api_key: str, prompt: str) -> Optional[Dict[str, List[str]]]:
        model = os.getenv("GEMINI_MODEL", GEMINI_DEFAULT_MODEL)
        response = requests.post(
            GEMINI_API_URL.format(model=model),
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": LLM_TEMPERATURE,
                    "responseMimeType": "application/json",
                },
            },
            timeout=LLM_TIMEOUT_SECONDS,
        )
        if response.status_code != 200:
            return None
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return self._parse_and_validate(text)

    def _call_groq(self, api_key: str, prompt: str) -> Optional[Dict[str, List[str]]]:
        model = os.getenv("GROQ_MODEL", GROQ_DEFAULT_MODEL)
        response = requests.post(
            GROQ_API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "temperature": LLM_TEMPERATURE,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": "Kamu adalah konsultan operasional dapur. Balas hanya JSON valid sesuai skema yang diminta."},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=LLM_TIMEOUT_SECONDS,
        )
        if response.status_code != 200:
            return None
        text = response.json()["choices"][0]["message"]["content"]
        return self._parse_and_validate(text)

    @staticmethod
    def _parse_and_validate(text: Any) -> Optional[Dict[str, List[str]]]:
        """Parse teks respons LLM dan validasi skema tetap. None bila tidak sah."""
        if not isinstance(text, str):
            return None
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").strip()
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        try:
            data = json.loads(cleaned)
        except (ValueError, TypeError):
            return None
        if not isinstance(data, dict):
            return None
        validated: Dict[str, List[str]] = {}
        for key in ("root_cause_analysis", "kitchen_action_checklist", "sop_recommendations"):
            value = data.get(key)
            if not isinstance(value, list):
                return None
            items = [str(item).strip() for item in value if isinstance(item, str) and item.strip()]
            validated[key] = items
        if not validated["kitchen_action_checklist"]:
            return None
        return validated

    def _try_llm_generation(
        self, payload: Dict[str, Any]
    ) -> Optional[Tuple[Dict[str, List[str]], str]]:
        """Coba Gemini -> Groq. Kembalikan (data tervalidasi, provider) atau None."""
        cache_key = hashlib.sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        if cache_key in self._llm_cache:
            return self._llm_cache[cache_key]

        gemini_key, groq_key = self._provider_keys()
        prompt = _PROMPT_INSTRUCTION + json.dumps(payload, ensure_ascii=False, indent=2)

        attempts = []
        if gemini_key:
            attempts.append(("gemini", lambda: self._call_gemini(gemini_key, prompt)))
        if groq_key:
            attempts.append(("groq", lambda: self._call_groq(groq_key, prompt)))

        for provider_name, call in attempts:
            try:
                result = call()
            except Exception:
                result = None
            if result:
                self._llm_cache[cache_key] = (result, provider_name)
                return result, provider_name
        return None

    # ------------------------------------------------------------------
    # API utama
    # ------------------------------------------------------------------
    def generate_action_plan(
        self,
        restaurant_name: str,
        evaluation_results: Dict[str, Any],
        sample_complaints: Union[List[str], Dict[str, List[str]]]
    ) -> Dict[str, Any]:
        """Menghasilkan action plan operasional dapur berbasis data evaluasi.

        sample_complaints boleh berupa list string datar (perilaku lama,
        dipetakan heuristik per aspek) atau dict {aspek: [teks, ...]}
        (pemetaan eksak dari call site).
        """
        # Identifikasi aspek dengan skor kepuasan terendah
        breakdown = evaluation_results.get("aspect_breakdown", {})
        sorted_aspects = sorted(
            breakdown.items(),
            key=lambda x: x[1].get("satisfaction_score", 100.0)
        )

        critical_aspects = [item for item in sorted_aspects if item[1].get("satisfaction_score", 100.0) < CRITICAL_SCORE_THRESHOLD]
        if not critical_aspects and sorted_aspects:
            critical_aspects = [sorted_aspects[0]]
        khs = evaluation_results.get("kitchen_health_score", 0.0)

        # Rencana dasar selalu dihitung lokal & deterministik
        # (priority_risk_areas + summary_note tidak berasal dari LLM).
        plan = self._generate_structured_recommendation(
            restaurant_name=restaurant_name,
            critical_aspects=critical_aspects,
            sample_complaints=sample_complaints,
            khs=khs
        )

        payload = self._build_llm_payload(
            restaurant_name, evaluation_results, critical_aspects, sample_complaints
        )
        llm_result = self._try_llm_generation(payload)

        if llm_result:
            llm_data, provider_name = llm_result
            for key in ("root_cause_analysis", "kitchen_action_checklist", "sop_recommendations"):
                if llm_data.get(key):
                    plan[key] = llm_data[key]
            plan["generation_mode"] = "llm"
            plan["llm_provider"] = provider_name
        else:
            plan["generation_mode"] = "template"
            plan["llm_provider"] = None

        return plan

    def _generate_structured_recommendation(
        self,
        restaurant_name: str,
        critical_aspects: List[Any],
        sample_complaints: List[str],
        khs: float
    ) -> Dict[str, Any]:
        """Template generator operasional dapur standar industri F&B."""
        
        checklist_items = []
        root_causes = []
        sop_recommendations = []
        
        aspect_action_catalog = {
            "kemasan": {
                "root_cause": "Kerapian penutupan wadah berkuah tidak terstandarisasi, bahan kemasan tipis tidak tahan uap panas atau guncangan pengantaran kurir.",
                "checklist": [
                    "Wajib gunakan isolasi / sealing tape silang pada setiap tutup mangkok makanan berkuah sebelum dimasukkan ke kantong plastik.",
                    "Pisahkan kuah dan kondimen kering ke dalam wadah terpisah (double packaging).",
                    "Gunakan kardus tebal bersertifikasi food-grade khusus pesanan gorengan agar minyak tidak merembes."
                ],
                "sop": "SOP Pengemasan Anti-Bocor: Koki wajib melakukan tilt-test 5 derajat sebelum pesanan diserahkan ke driver."
            },
            "pelayanan": {
                "root_cause": "Bottleneck pada antrean kitchen order saat jam sibuk dan miskomunikasi pengecekan kelengkapan pesanan (alat makan/sambal).",
                "checklist": [
                    "Terapkan sistem double-check tiket pesanan: Koki centang checklist menu, staf kasir verifikasi sebelum stapler struk.",
                    "Siapkan pre-pack sendok, garpu, dan sambal dalam pouch higienis di awal shift kerja.",
                    "Batasi estimasi slot terima pesanan delivery maksimal 12 menit per batch."
                ],
                "sop": "SOP Dispatch & Packing: Verifikasi 3 poin (Jumlah item, Catatan kustom pelanggan, Kelengkapan sendok) oleh staf expediter."
            },
            "porsi": {
                "root_cause": "Penakaran bahan baku (nasi dan lauk) masih mengandalkan perkiraan manual juru masak tanpa timbangan digital.",
                "checklist": [
                    "Wajib sediakan timbangan digital per workstation dapur (target berat nasi: 180-200 gram per porsi).",
                    "Gunakan centong ukur berstandar volume untuk porsi sambal dan sayuran pelengkap.",
                    "Audit acak 3 porsi per shift kerja oleh kepala dapur (Head Chef)."
                ],
                "sop": "SOP Standard Yield & Portioning: Timbangan presisi untuk semua protein hewani dan takaran karbohidrat."
            },
            "rasa": {
                "root_cause": "Variasi takaran bumbu dasar harian dan waktu simmering kuah yang tidak seragam antar juru masak.",
                "checklist": [
                    "Pusatkan preparasi bumbu dasar (pre-mix seasoning) dengan resep gramasi baku harian.",
                    "Lakukan blind tasting 1 sendok kuah sebelum jam operasional resto dimulai.",
                    "Gunakan timer digital untuk kontrol suhu penggorengan dan kematangan protein."
                ],
                "sop": "SOP Kalibrasi Rasa Dapur: Validasi kualitas rasa oleh penanggung jawab shift sebelum buka order pertama."
            },
            "harga": {
                "root_cause": "Ketidaksesuaian persepsi nilai (perceived value) pelanggan terhadap harga jual di aplikasi pesan-antar.",
                "checklist": [
                    "Tambahkan nilai tambah visual berupa garnish, kondimen gratis (lalapan/kerupuk), atau upgrade kemasan premium.",
                    "Evaluasi margin fee aplikasi delivery agar tidak menaikkan harga menu melebihi batas psikologis konsumen.",
                    "Buat paket bundling hemat untuk meningkatkan persepsi nilai ekonomis pelanggan."
                ],
                "sop": "SOP Pricing & Value Perception: Review berkala harga jual dibanding benchmark kompetitor radius 3 km."
            }
        }
        
        for aspect_name, data in critical_aspects:
            catalog = aspect_action_catalog.get(aspect_name)
            if catalog:
                root_causes.append(f"Aspek {aspect_name.capitalize()}: {catalog['root_cause']}")
                checklist_items.extend(catalog["checklist"])
                sop_recommendations.append(catalog["sop"])
                
        # Jika tidak ada aspek kritis terdeteksi
        if not checklist_items:
            checklist_items = [
                "Pertahankan konsistensi takaran resep saat ini.",
                "Lakukan monitoring review harian untuk mendeteksi anomali komplain sedini mungkin."
            ]
            root_causes = ["Secara keseluruhan operasional dapur berada pada standar optimal."]
            sop_recommendations = ["SOP Quality Assurance berkala setiap awal pekan."]

        return {
            "restaurant_name": restaurant_name,
            "overall_health_score": khs,
            "priority_risk_areas": [a[0].capitalize() for a in critical_aspects],
            "root_cause_analysis": root_causes,
            "kitchen_action_checklist": checklist_items,
            "sop_recommendations": sop_recommendations,
            "summary_note": f"Analisis UlasRasa untuk {restaurant_name}: Ditemukan {len(critical_aspects)} area perhatian utama dengan Kitchen Health Score {khs:.1f}%. Perbaikan pada checklist prioritas di atas diproyeksikan mereduksi komplain hingga 30-40%."
        }
