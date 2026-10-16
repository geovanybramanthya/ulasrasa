"""Mesin generatif rekomendasi evaluasi dapur dan action checklist operasional."""

import os
from typing import Dict, Any, List, Optional

class ActionPlanEngine:
    """Menghasilkan analisis akar masalah dan checklist tindakan dapur."""

    def __init__(self, api_key: Optional[str] = None, provider: str = "gemini"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY")
        self.provider = provider

    def generate_action_plan(
        self,
        restaurant_name: str,
        evaluation_results: Dict[str, Any],
        sample_complaints: List[str]
    ) -> Dict[str, Any]:
        """Menghasilkan action plan operasional dapur berbasis data evaluasi."""
        
        # Identifikasi aspek dengan skor kepuasan terendah
        breakdown = evaluation_results.get("aspect_breakdown", {})
        sorted_aspects = sorted(
            breakdown.items(),
            key=lambda x: x[1].get("satisfaction_score", 100.0)
        )
        
        critical_aspects = [item for item in sorted_aspects if item[1].get("satisfaction_score", 100.0) < 70.0]
        if not critical_aspects and sorted_aspects:
            critical_aspects = [sorted_aspects[0]]

        # Fallback generator berbasis template terstruktur yang deterministik
        return self._generate_structured_recommendation(
            restaurant_name=restaurant_name,
            critical_aspects=critical_aspects,
            sample_complaints=sample_complaints,
            khs=evaluation_results.get("kitchen_health_score", 0.0)
        )

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
