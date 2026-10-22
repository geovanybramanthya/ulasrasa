# Checklist Deploy UlasRasa - Aksi yang Harus Kamu Lakukan Sendiri

Semua kode sudah siap dan sudah di-commit di repo lokal. Langkah di bawah ini terikat akun milikmu (Hugging Face, GitHub, Google AI Studio), jadi harus kamu yang eksekusi. Urutannya jangan ditukar: model dulu, baru aplikasi, terakhir GitHub.

**Target akhir: 3 URL** (Space, repo model HF, GitHub) untuk dimasukkan ke slide 10 deck dan Google Form submission. Deadline: **Jumat 23 Oktober 2026 pukul 23:59 WIB**.

Folder project di PC: `C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa`

---

## Langkah A - Upload Model ke Hugging Face Hub

1. Buka https://huggingface.co - login, atau buat akun dulu bila belum punya (gratis).
2. Klik avatar kanan atas -> **New Model**. Isi:
   - Name: `ulasrasa-indobert-absa` (repo jadinya `<username-kamu>/ulasrasa-indobert-absa`)
   - License: `mit`
   - Visibility: **Public** (wajib publik supaya Space bisa memuatnya dan juri bisa membukanya)
   - Klik **Create model**.
3. Upload isi folder `models\indobert-base-absa` (folder di PC kamu, isinya file `config.json`, `model.safetensors`, file tokenizer, dll):
   - Cara web: di halaman repo model -> tab **Files and versions** -> **Add file** -> **Upload files** -> pilih SEMUA file di dalam folder itu -> **Commit changes**.
   - Cara CLI (lebih cepat untuk file ±475 MB), dari PowerShell:
     ```powershell
     py -m pip install -U huggingface_hub
     hf auth login
     cd C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa
     hf upload <username-kamu>/ulasrasa-indobert-absa models\indobert-base-absa .
     ```
     `hf auth login` akan minta token: buat di https://huggingface.co/settings/tokens (tipe **Write**).
4. Ganti README repo model dengan isi `training\model_card.md` dari project ini (di web: tab Files -> klik `README.md` -> ikon pensil -> tempel seluruh isi file -> Commit). File lokalnya bisa dibuka dari folder `training`.
5. Catat repo id persisnya: `<username-kamu>/ulasrasa-indobert-absa`. Ini dipakai di langkah B.

## Langkah B - Buat Space (Aplikasi) di Hugging Face Spaces

1. Di https://huggingface.co -> **New Space**:
   - Name: `ulasrasa` (bebas, saran: `ulasrasa-app`)
   - License: `mit`
   - SDK: **Streamlit**
   - Hardware: CPU basic (gratis)
   - Visibility: **Public**
   - Klik **Create Space**.
2. Isi file aplikasi ke Space. Dua pilihan:
   - **Pilihan 1 (upload langsung, paling simpel):** di halaman Space -> **Files and versions** -> **Add file -> Upload files**: upload `app.py`, `requirements.txt`, `README.md`, dan SELURUH folder `src\` dari project ini (pertahankan struktur foldernya). Folder `models\`, `training\venv\` TIDAK perlu diupload - model dimuat dari Hub (langkah 3).
   - **Pilihan 2 (lewat git):** clone repo Space ke PC, salin file yang sama ke dalamnya, lalu commit + push. Perintah clone ada di halaman Space (tombol titik tiga -> Clone repository).
3. Atur **Variables and secrets** Space: halaman Space -> **Settings** -> bagian *Variables and secrets* -> **New secret**:
   - `GEMINI_API_KEY` = API key Gemini kamu (secret). Cara dapatnya: buka https://aistudio.google.com -> login akun Google -> **Get API key** -> **Create API key** -> salin key-nya.
   - `ULASRASA_MODEL_REPO` = `<username-kamu>/ulasrasa-indobert-absa` (dari langkah A; boleh sebagai variable biasa, bukan secret).
   
   Tanpa secret Gemini pun aplikasi tetap jalan (otomatis jatuh ke mode template, dan caption mode di UI akan menunjukkannya), tapi untuk demo terbaik isi key ini.
4. Tunggu status build Space sampai **Running** (tab **Logs** menunjukkan progres; build pertama bisa beberapa menit karena memasang torch CPU ±200 MB).
5. **Uji alur penuh di URL Space** (formatnya `https://huggingface.co/spaces/<username-kamu>/<nama-space>`):
   - Buka URL-nya (coba juga dari jendela incognito untuk memastikan publik).
   - Tempel ulasan campuran, contoh: "Ayamnya enak banget gurih, tapi porsinya dikit banget dan kemasannya tumpah di jalan, untung mas kurirnya ramah."
   - Pastikan: analisis per aspek tampil, **Kitchen Health Score tampil dan berubah** sesuai data, **AI Kitchen Action Checklist ter-generate**, dan **caption mode** di UI menunjukkan engine/model yang benar (bukan mode darurat).
   - Coba juga tombol unduh checklist.
   
   Bila ada error, buka tab **Logs** di Space, screenshot baris error merahnya, kirim ke Muse.

## Langkah C - Push ke GitHub

Repo lokal sudah berisi commit checkpoint arsitektur final; tinggal buat repo kosong dan push.

1. Buka https://github.com/new - Name: `ulasrasa` - Visibility: **Public** - JANGAN centang "Add a README" (repo harus benar-benar kosong) -> **Create repository**.
2. Dari PowerShell, di folder project:
   ```powershell
   cd C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa
   git remote add origin https://github.com/<username-github-kamu>/ulasrasa.git
   git push -u origin main
   ```
   (Folder `models\`, `training\venv\`, dan `training\wheels\` sudah di-.gitignore, jadi tidak ikut ter-push - memang disengaja, model hidup di HF Hub.)
3. Buka halaman repo GitHub-nya, pastikan `app.py`, `src\`, `training\` (script + notebook), `evaluation\`, dan `data\` terlihat.

## Langkah D - Kumpulkan 3 URL Final

Setelah A-C beres, kumpulkan tiga URL ini:

1. URL Space: `https://huggingface.co/spaces/<username-kamu>/<nama-space>`
2. URL repo model HF: `https://huggingface.co/<username-kamu>/ulasrasa-indobert-absa`
3. URL GitHub: `https://github.com/<username-github-kamu>/ulasrasa`

Ketiganya dimasukkan ke **slide 10 deck presentasi** dan ke **Google Form "Link Pengumpulan Final Project REA AI Engineering Batch 13"** sebelum **23 Oktober 2026 pukul 23:59 WIB**. Jangan tunggu mepet - upload model ±475 MB dan build Space adalah dua langkah yang paling makan waktu.

---

## Catatan Penting (baca sebelum mulai)

- **Soal biaya Spaces:** kebijakan Hugging Face soal Space gratis untuk akun personal bisa berubah dan ada kemungkinan build Space diminta memakai plan berbayar/ZeroGPU. Ini perlu dicek langsung saat kamu eksekusi langkah B - bila Space gratis ternyata tidak bisa build, **alternatif resminya: demo lokal + video demo** (aplikasi dijalankan di PC, direkam, videonya diupload) sambil tetap menyerahkan URL repo model HF + GitHub. Jadi jangan panik dan jangan bayar apa pun tanpa mikir dulu.
- API key Gemini bersifat rahasia: masukkan HANYA di Settings Space (Secrets), jangan pernah ditulis di kode, README, atau slide.
- Bila Space error karena model tidak ditemukan, penyebab paling umum: `ULASRASA_MODEL_REPO` salah ketik atau repo model belum Public. Cek dua itu dulu.
