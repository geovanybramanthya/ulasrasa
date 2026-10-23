"""Peta label UI UlasRasa.

MODULE_CHOICES adalah ID modul kanonis internal (nilai session_state
``active_module_name``). Nilainya TIDAK diubah dari versi pra-perombakan
(lihat PRD Implementasi UI Bag. 1); nama tampilan pendek mengikuti
DESIGN.md Bag. 7 dan dipetakan lewat MODULE_LABELS.
"""

MODULE_CHOICES = [
    "Ringkasan Eksekutif & Health Score",
    "Deep-Dive Aspek & Sentimen",
    "AI Kitchen Action Checklist",
    "Single Review Simulator (Live Demo)",
]

# Nama tampilan pendek (DESIGN.md Bag. 7) per ID kanonis.
MODULE_LABELS = {
    "Ringkasan Eksekutif & Health Score": "Ringkasan",
    "Deep-Dive Aspek & Sentimen": "Rincian Aspek",
    "AI Kitchen Action Checklist": "Rencana Aksi",
    "Single Review Simulator (Live Demo)": "Coba Ulasan",
}

# Label tombol navigasi atas versi pra-perombakan (dipertahankan apa adanya
# selama Tahap 0; diganti pola top bar pada tahap berikutnya).
TOP_SHORT_LABELS = [
    "1. Ringkasan Eksekutif",
    "2. Deep-Dive Aspek",
    "3. Checklist & SOP",
    "4. Review Simulator",
]

DEFAULT_MODULE = MODULE_CHOICES[0]
