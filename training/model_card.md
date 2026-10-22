---
language: id
license: mit
base_model: indobenchmark/indobert-base-p1
tags:
  - absa
  - aspect-based-sentiment-analysis
  - sentiment-analysis
  - indonesian
  - indobert
  - text-classification
pipeline_tag: text-classification
---

# UlasRasa IndoBERT ABSA (`ulasrasa-indobert-absa`)

Model klasifikasi *aspect-based sentiment analysis* (ABSA) untuk ulasan kuliner / pesan-antar berbahasa Indonesia. Model ini adalah hasil *fine-tune* dari `indobenchmark/indobert-base-p1` dan merupakan mesin analisis utama aplikasi **UlasRasa** (analisis ulasan untuk UMKM F&B).

## Tugas

Diberikan satu ulasan dan satu aspek, model memprediksi sentimen ulasan terhadap aspek tersebut ke dalam 4 kelas:

| Label ID | Label | Arti |
| :--- | :--- | :--- |
| 0 | `not_mentioned` | Aspek tidak disinggung dalam ulasan |
| 1 | `positive` | Sentimen positif terhadap aspek |
| 2 | `neutral` | Aspek disebut tanpa penilaian jelas |
| 3 | `negative` | Sentimen negatif terhadap aspek |

Lima aspek operasional yang didukung: **rasa**, **porsi**, **harga**, **kemasan**, **pelayanan**.

## Cara Pakai

Model menerima **pasangan teks**: segmen pertama adalah teks ulasan mentah, segmen kedua (`text_pair`) adalah nama aspek huruf kecil. Panjang maksimum 128 token.

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

repo = "<username>/ulasrasa-indobert-absa"
tokenizer = AutoTokenizer.from_pretrained(repo)
model = AutoModelForSequenceClassification.from_pretrained(repo)
model.eval()

review = "Ayamnya enak banget, tapi porsinya dikit dan kemasannya tumpah."
enc = tokenizer([review] * 5, ["rasa", "porsi", "harga", "kemasan", "pelayanan"],
                truncation=True, max_length=128, padding=True, return_tensors="pt")
with torch.no_grad():
    probs = torch.softmax(model(**enc).logits, dim=-1)
labels = [model.config.id2label[int(i)] for i in probs.argmax(dim=-1)]
# contoh hasil: rasa=positive, porsi=negative, harga=not_mentioned,
# kemasan=negative, pelayanan=not_mentioned
```

*Confidence* yang dipakai aplikasi adalah probabilitas *softmax* kelas terpilih (probabilitas model yang sesungguhnya, bukan heuristik).

## Hasil Evaluasi (Hold-Out Beku)

Evaluasi dilakukan pada **hold-out beku 25 ulasan** (dibekukan sebelum pengembangan apa pun, *seed* 42, daftar ID di `data/holdout_ids.json` pada repo aplikasi), memakai metrik yang sama untuk semua engine: Macro-F1 dirata-rata atas kelas yang muncul di label gold dan/atau prediksi (konvensi *scikit-learn*). Hasil lengkap tersimpan di `evaluation/evaluation_results.json` pada repo aplikasi.

**Macro-F1 keseluruhan: 0,5924** (baseline *lexicon*: 0,4778)

| Aspek | Macro-F1 IndoBERT Base | Macro-F1 Baseline Lexicon |
| :--- | ---: | ---: |
| Rasa | 0,2684 | 0,6799 |
| Porsi | 0,4672 | 0,4150 |
| Harga | 0,8003 | 0,4470 |
| Kemasan | 0,6772 | 0,4206 |
| Pelayanan | 0,7489 | 0,4264 |
| **Keseluruhan** | **0,5924** | **0,4778** |

F1 per kelas untuk IndoBERT Base (hold-out yang sama):

| Aspek | positive | neutral | negative | not_mentioned |
| :--- | ---: | ---: | ---: | ---: |
| Rasa | 0,8235 | 0,0000 | 0,2500 | 0,0000 |
| Porsi | 0,5455 | 0,0000 | 0,5000 | 0,8235 |
| Harga | 0,8182 | 0,0000 | 0,8000 | 0,7826 |
| Kemasan | 0,6667 | 0,0000 | 0,5000 | 0,8649 |
| Pelayanan | 0,8333 | 0,0000 | 0,5714 | 0,8421 |

Model pembanding dari keluarga yang sama, IndoBERT Lite (`indobenchmark/indobert-lite-base-p1`) yang dilatih dengan prosedur identik, hanya mencapai Macro-F1 0,1570 pada hold-out ini sehingga tidak dipilih.

## Data Latih - Pernyataan Kejujuran

Model dilatih pada **75 ulasan non-holdout** yang merupakan **dataset kurasi manual**: ulasan ditulis tangan meniru pola ulasan platform pesan-antar dan dianotasi manual ke 5 aspek operasional. Dataset ini **bukan** ulasan asli hasil *scraping* platform, dan tidak diklaim sebagai ulasan asli di dokumen proyek mana pun.

Dari 75 ulasan dibentuk 375 pasangan (ulasan, aspek) dengan distribusi label: `positive` 132, `not_mentioned` 170, `negative` 65, `neutral` 8. Kelas `neutral` memang sangat langka pada data latih - ini keterbatasan yang diketahui dan tercermin pada hasil evaluasi.

Proses pelatihan direplikasi pada *notebook* `training/UlasRasa_Training_Colab.ipynb` di repo aplikasi.

## Lisensi

Mengikuti lisensi model dasar `indobenchmark/indobert-base-p1`: **MIT**. Catatan tambahan: bobot model berasal dari data latih kurasi manual seperti dijelaskan di atas; tidak ada data ulasan platform proprietary di dalam data latih.

## Keterbatasan

- **Aspek rasa adalah yang terlemah** (Macro-F1 0,2684, di bawah baseline *lexicon* 0,6799): model kesulitan membedakan rasa yang "disebut" vs "tidak disebut" dan menangkap negatif rasa. Aplikasi mengatasi ini dengan tetap menyediakan engine *lexicon* sebagai pembanding/fallback.
- **Kelas `neutral` tidak pernah terprediksi dengan benar** (F1 0,0000 di semua aspek) karena contoh `neutral` pada data latih hanya 8 dari 375 pasangan.
- Hold-out hanya 25 ulasan, sehingga angka evaluasi bersifat indikatif, bukan estimasi generalisasi yang kuat.
- Model hanya terlatih pada pola ulasan kuliner Indonesia informal; performa pada domain lain (hotel, otomotif, produk umum) tidak dijamin.
- Panjang input dibatasi 128 token; ulasan yang lebih panjang terpotong.
