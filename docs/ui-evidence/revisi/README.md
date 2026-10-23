# Harness Verifikasi - Revisi Mayor UI UlasRasa

Folder bukti BARU untuk revisi landing + penataan widget. Harness di sini
TIDAK mengubah kode aplikasi; ia hanya mengukur keadaan app apa adanya
(termasuk FAIL selama landing belum dibangun).

Baseline angka: `../baseline.json` (teraudit) - KHS Semua Outlet 67,27
(WASPADA); Ayam Geprek Sambal Korek Barokah 55,84 (KRITIS); Bakso Rusuk
Solo Pak Ndut 68,24 (WASPADA); Bebek Goreng Madura Cak Roni 83,00 (PRIMA);
Kopi Susu Senja & Toast 59,55 (KRITIS). Tampilan app 1 desimal, jadi
perbandingan memakai pembulatan 1 desimal + kata status.

## Cara menjalankan (di PC, Python proyek = `py` 3.14 saja)

Semua harness Playwright menyalakan server Streamlit detached sendiri di
port 8525 bila belum ada yang menjawab (dan mematikannya di akhir);
muat model IndoBERT ±18-30 detik per muat halaman - beri waktu.

```powershell
cd C:\Users\geova\Downloads\BOOTCAMP\PROJECTS\ulasrasa
py docs/ui-evidence/revisi/font_sweep_open_states.py --tag awal
py docs/ui-evidence/revisi/account_parity.py --tag awal
py docs/ui-evidence/revisi/journey_revisi.py --tag awal
py docs/ui-evidence/revisi/apptest_revisi.py
```

Server manual (opsional): `powershell -File docs/ui-evidence/revisi/start_server_revisi.ps1 -Port 8525`,
lalu arahkan harness dengan `--url http://localhost:8525`.

## Isi

| File | Fungsi |
|---|---|
| `_revisi_common.py` | Helper bersama: baseline, server detached, JS sapuan font (pola audit-fix3), baca hero KHS, deteksi/klik landing. |
| `font_sweep_open_states.py` | Sapuan computed font (termasuk SVG `<text>`) pada: (a) landing/keadaan awal, (b) panel Ganti Data terbuka, (c) expander Input Ulasan terbuka, (d) popover selectbox terbuka, (e) keempat modul normal. Target: 0 "Source Sans". Output `font_sweep_open_states_<tag>.json`. |
| `account_parity.py` | Klik tombol "Masuk Dashboard" pada kartu tiap akun (4 resto + Benchmark) dari landing, baca KHS + status hero, bandingkan ke baseline. Klik gagal = FAIL jujur + diagnostik angka tercetak di kartu landing (tidak dihitung PASS). Output `account_parity_<tag>.json`. |
| `journey_revisi.py` | Journey 7 langkah: landing -> Ayam -> Ganti Akun -> panel -> unggah `test_upload_3.csv` -> Preset lagi -> tambah ulasan (total +1). Output `journey_revisi_<tag>.json`. |
| `apptest_revisi.py` | AppTest: landing tanpa state akun (`active_account=None`); dashboard Ayam + Benchmark di modul Ringkasan (seed `active_account`, meniru `core.enter_account`). Output `apptest_revisi_result.json`. |
| `test_upload_3.csv` | CSV uji 3 baris, hanya kolom `review_text` (memicu resto fallback "Outlet Kustom"). |
| `start_server_revisi.ps1` | Server detached manual, pola `../start_server.ps1`. |

Hasil lari awal (`--tag awal`) tersimpan sebagai `*_awal.json` + `*.log`
di folder ini: dijalankan terhadap implementasi landing final
(HEAD `662cb9c`, branch `revisi-landing`) pada 2026-10-23 malam, saat
`src/ui/theme.py` masih memuat perubahan belum ter-commit milik pekerja
tema/widget. Hasilnya: font sweep 0 "Source Sans" di 8 keadaan,
account parity 5/5 PASS, journey 7/7 PASS, AppTest 4/4 PASS.
Koordinator: jalankan ulang sesudah tema final ter-commit untuk
verifikasi penutup.
