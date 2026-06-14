# Panduan Scraping dan Cleaning Data X (Twitter) untuk Social Network Analysis (SNA)

Proyek ini berisi dua skrip utama yang digunakan untuk mengumpulkan data dari platform X (Twitter) dan membersihkannya agar siap digunakan untuk *Social Network Analysis* (SNA).

## Daftar Isi
1. [Persiapan dan Prasyarat](#persiapan-dan-prasyarat)
2. [Tahap 1: Penggunaan script.py (Scraping Data)](#tahap-1-penggunaan-scriptpy-scraping-data)
3. [Tahap 2: Penggunaan clean_data.py (Membersihkan Data)](#tahap-2-penggunaan-clean_datapy-membersihkan-data)

---

## Persiapan dan Prasyarat

Sebelum menjalankan kedua skrip ini, pastikan Anda telah melakukan hal-hal berikut:

1. **Instalasi Python**
   Pastikan Anda sudah menginstal Python (disarankan versi 3.8 ke atas).

2. **Instalasi Dependensi (Library)**
   Buka terminal/command prompt dan instal library yang dibutuhkan, yaitu `playwright` (untuk scraping) dan `pandas` (untuk pengolahan data):
   ```bash
   pip install playwright pandas
   playwright install chromium
   ```

3. **Mengekspor Cookies Akun X (Twitter)**
   Agar skrip scraping dapat berjalan dan tidak terblokir, kita membutuhkan session login Twitter yang aktif:
   * Login ke akun X/Twitter Anda melalui browser (contoh: Google Chrome).
   * Gunakan ekstensi browser (seperti **EditThisCookie**, **Cookie-Editor**, atau sejenisnya) untuk mengekspor cookie sesi tersebut ke dalam format JSON.
   * Buat file baru bernama `cookies.json` di dalam folder yang sama dengan file `script.py` dan tempelkan isinya ke file tersebut.

---

## Tahap 1: Penggunaan `script.py` (Scraping Data)

File `script.py` bertugas mencari tweet berdasarkan *keyword* tertentu. Skrip ini akan melakukan scroll layar otomatis secara berulang dan mengambil elemen seperti teks tweet, penulis, jumlah *likes/retweets*, serta interaksi (mention, reply, quote) untuk kebutuhan SNA.

### Cara Penggunaan:
1. Buka file `script.py`.
2. Anda bisa mengubah nama file CSV output dengan mengedit variabel ini (sekitar baris ke-35):
   ```python
   csv_filename = "hasil_scraping_sna_2.csv"
   ```
3. Di bagian **paling bawah** skrip, tentukan **kata kunci pencarian** (keyword) dan **jumlah maksimal scroll** layar yang diinginkan:
   ```python
   scrape_with_cookies("pemblokiran judol komdigi", max_scrolls=70)
   ```
   * *Catatan: 1 scroll umumnya akan memuat sekitar beberapa tweet baru.*
4. Jalankan skrip di terminal:
   ```bash
   python script.py
   ```
5. Tunggu prosesnya selesai. Setelah selesai, skrip akan membuat file CSV baru yang memuat seluruh tweet yang berhasil ditarik (contohnya `hasil_scraping_sna_2.csv`).

---

## Tahap 2: Penggunaan `clean_data.py` (Membersihkan Data)

Data mentah hasil scraping kadang memiliki tweet duplikat atau tweet yang tidak terlalu relevan. File `clean_data.py` akan:
* Menghapus baris yang ganda (duplikat).
* Menyaring tweet dengan mencocokkannya menggunakan daftar *keyword*.
* **Strategi Khusus SNA:** Skrip ini dirancang untuk tetap menyimpan tweet yang tidak memiliki *keyword* ASALKAN tweet tersebut merupakan bentuk interaksi (Reply, Quote, atau Mention). Ini sangat penting agar relasi jaringan (*edge*) pada graf (SNA) tidak terputus.

### Cara Penggunaan:
1. Buka file `clean_data.py`.
2. Di bagian **paling bawah**, pastikan argumen fungsi `clean_twitter_data` merujuk ke nama file hasil scraping yang tepat (input) dan nama file bersih (output):
   ```python
   # Ganti "hasil_scraping_sna.csv" sesuai dengan output dari script.py
   clean_twitter_data("hasil_scraping_sna_2.csv", "data_siap_sna.csv")
   ```
3. Jika diperlukan, Anda dapat memodifikasi daftar *keyword* (sekitar baris ke-25):
   ```python
   keywords = ['judol', 'judi online', 'judi', 'komdigi']
   ```
4. Jalankan pembersihan di terminal:
   ```bash
   python clean_data.py
   ```
5. Output di terminal akan melaporkan berapa jumlah data awal, berapa yang dihapus karena duplikat, dan jumlah data final.
6. Anda akan mendapatkan file baru (contoh: `data_siap_sna.csv`). File inilah yang siap untuk Anda impor ke dalam *software* seperti **Gephi** atau diproses dengan **NetworkX** untuk dianalisis lebih jauh (Social Network Analysis).
