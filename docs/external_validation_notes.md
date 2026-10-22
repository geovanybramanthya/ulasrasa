# External Validation Set - Catatan Sumber dan Metode

File pendamping: `data/external_validation.csv` (45 ulasan)
Dibangun: 22 Oktober 2026
Status penggunaan: **HANYA untuk validasi eksternal. Bukan data training, bukan hold-out.**

---

## 1. Sumber Dataset

- **Nama:** SmSA (sentiment analysis dataset, Purwarianti & Crisdayanti, 2019), sebagaimana didistribusikan ulang dalam benchmark **IndoNLU** (Wilie et al., 2020) dan dibungkus ulang oleh **SEACrowd**.
- **URL dataset (SEACrowd):** https://huggingface.co/datasets/SEACrowd/smsa
- **URL data mentah yang diunduh:** https://github.com/IndoNLP/indonlu (folder `dataset/smsa_doc-sentiment-prosa/`, file `train_preprocess.tsv`, `valid_preprocess.tsv`, `test_preprocess.tsv`; total gabungan 12.760 kalimat).
- **Isi sumber:** komentar dan ulasan berbahasa Indonesia yang dikumpulkan (crawling) dari berbagai platform daring, lalu dianotasi sentimennya (positive / negative / neutral) oleh linguis Indonesia. Sebagian besar ulasan kuliner di dalamnya berasal dari platform ulasan restoran (ulasan tempat makan, terutama kawasan Bandung dan sekitarnya).
- **Lisensi (persis seperti tertulis di file `LICENSE` repo SEACrowd dan di skrip pemuat dataset):** **Creative Commons Attribution Share-Alike 4.0 International (CC BY-SA 4.0)**. Penggunaan untuk validasi ini mencantumkan atribusi sumber sebagaimana disyaratkan lisensi tersebut.

## 2. Cara Penyaringan

1. Gabungan ketiga split SmSA (12.760 baris) disaring dengan kata kunci inti kuliner (antara lain: makanan, restoran, resto, tempat makan, kuliner, menu, masakan, warung, kafe, porsi, hidangan, gofood, grabfood) dan dibuang konteks non-kuliner yang kentara (telekomunikasi, perbankan, film, dan sejenisnya). Tersisa kumpulan kandidat 5.113 ulasan.
2. Dari kandidat itu diambil sampel acak (seed tetap) berstrata label sentimen sumber: 90 ulasan berlabel negative, 90 berlabel positive, dan seluruh 29 berlabel neutral - total 209 ulasan yang **dibaca satu per satu secara penuh**.
3. Dari 209, dipilih 45 ulasan akhir yang memenuhi syarat:
   - benar-benar menceritakan pengalaman makanan / restoran / pesan-antar (bukan sekadar menyebut kata makanan secara metaforis, bukan berita, bukan iklan);
   - substantif (teks akhir terpendek 90 karakter; batas bawah penyaringan awal 60 karakter);
   - mengandung sekurang-kurangnya satu aspek UlasRasa yang dinyatakan eksplisit;
   - variasi sentimen dijaga (sumber positive, negative, dan neutral semuanya terwakili).
4. Pembersihan teks seperlunya: spasi digabungkan, penanda sambungan sisa crawling ("lanjutan") di akhir teks dibuang, teks dipotong maksimum 500 karakter. Perlu dicatat: SmSA didistribusikan dalam bentuk **sudah terpra-proses** oleh pembuatnya (huruf kecil, tanda baca terpisah spasi) - bentuk itulah yang dipakai di sini, tidak diubah maknanya.

## 3. Metode Anotasi

- Skema mengikuti persis konvensi dataset inti (`data/sample_reviews.csv`): 5 aspek (rasa, porsi, harga, kemasan, pelayanan), masing-masing bernilai `positive`, `negative`, `neutral`, atau `not_mentioned`.
- Aturan anotasi: aspek hanya dinilai dari apa yang **eksplisit dinyatakan teks**; aspek yang tidak disebut = `not_mentioned`; nada keseluruhan ulasan tidak dipaksakan ke aspek yang tidak dibicarakan. Penyebutan harga yang murni faktual (angka tanpa penilaian) diberi `neutral`. Penilaian campuran di dalam satu aspek mengikuti penilaian dominan yang dinyatakan penulis ulasan.
- **Anotasi dilakukan dibantu AI (Muse) mengikuti konvensi skema di atas, dengan membaca setiap ulasan secara individual. Disarankan spot-check manusia pada sampel acak (mis. 10 ulasan) sebelum set ini dipakai untuk menarik kesimpulan evaluasi.**
- Kolom `restaurant_name` diisi `IndoNLU SmSA` untuk semua baris: SmSA tidak menyediakan nama platform per baris, jadi yang dicantumkan adalah nama dataset sumbernya - bukan nama restoran karangan. Kolom `menu_item` dikosongkan karena informasi itu tidak tersedia di sumber.
- Label sentimen asli SmSA **tidak** disalin ke file ini; label aspek adalah hasil anotasi baru sesuai skema UlasRasa.

## 4. Distribusi Label Hasil Anotasi (45 ulasan)

| Aspek | positive | negative | neutral | not_mentioned |
| :--- | ---: | ---: | ---: | ---: |
| rasa | 20 | 12 | 5 | 8 |
| porsi | 2 | 5 | 2 | 36 |
| harga | 13 | 10 | 4 | 18 |
| kemasan | 1 | 0 | 0 | 44 |
| pelayanan | 8 | 13 | 0 | 24 |

## 5. Keterbatasan yang Diketahui

- Mayoritas ulasan SmSA adalah ulasan **makan di tempat (dine-in)** dari era platform ulasan restoran, bukan ulasan aplikasi pesan-antar modern. Akibatnya aspek **kemasan** nyaris tidak pernah dibahas (hanya 1 ulasan, tentang pesanan GoFood yang dikemas plastik vakum) dan aspek **porsi** jarang disebut eksplisit. Set ini kuat untuk memvalidasi aspek rasa, harga, dan pelayanan; ia **tidak cukup** untuk menyimpulkan performa aspek kemasan dan porsi secara meyakinkan.
- Teks sudah terpra-proses dari sumbernya (huruf kecil, tokenisasi tanda baca), sehingga set ini memvalidasi ketahanan model terhadap teks yang sudah dinormalisasi, bukan teks mentah persis seperti yang diketik pengguna aplikasi.
- Anotasi bersifat satu penilai (dibantu AI); belum ada pengukuran kesepakatan antar-penilai.

## 6. Pernyataan Penggunaan

Set validasi eksternal ini berdiri di luar dataset inti 100 ulasan kurasi manual. Ia tidak boleh dicampur ke data training maupun dijadikan hold-out; fungsinya semata memeriksa apakah model yang dilatih / disetel pada dataset inti tetap masuk akal ketika menghadapi ulasan asli dari sumber publik, sesuai keputusan arsitektur Q12/Q16.
