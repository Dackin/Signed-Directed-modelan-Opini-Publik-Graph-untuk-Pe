# Pemodelan Graf Opini Publik (Twitter/X)

Repositori ini memuat *pipeline* lengkap untuk menganalisis dan memodelkan opini publik dari media sosial X (Twitter) terkait kebijakan pemerintah ke dalam bentuk Jaringan Graf Interaktif (*Interactive Graph Network*). 

Projek ini menggabungkan teknik **Natural Language Processing (NLP)** untuk analisis sentimen (*stance detection*) dan **Teori Graf (Graph Theory)** untuk memetakan aktor, peran, dan polarisasi interaksi antar pengguna.

---

## 📂 Struktur Direktori Utama

Pipa pemrosesan data (*Data Pipeline*) dibagi ke dalam beberapa skrip Python berurutan dan satu antarmuka web untuk visualisasi akhir:

```text
graf-pemodelan-opini-publik/
│
├── Data/                       # Folder penyimpanan data mentah (CSV)
├── Data/NLI/                   # Folder data yang telah diberi label sentimen
├── graf_json/                  # Output data graf dalam format JSON
├── python_script/              # Kumpulan skrip pemrosesan utama
│   ├── scrap_X_script.py       # 1. Scraper Data Twitter
│   ├── clean_data.py           # 2. Pembersihan Data Teks
│   ├── NLI_stance.py           # 3. Prediksi Sentimen (Pro/Kontra)
│   └── graph_builder.py        # 4. Pembentukan Jaringan Graf
│
├── index.html                  # 5. Visualisasi Web Interaktif (Frontend)
└── README.md                   # Dokumentasi Projek
```

---

## ⚙️ Alur Kerja Sistem (*Workflow*)

Proyek ini dijalankan secara berurutan mengikuti langkah-langkah berikut:

### 1. Ekstraksi Data (`scrap_X_script.py`)
Skrip ini digunakan untuk mengambil data *tweet* mentah dari X (Twitter) berdasarkan kata kunci (*keywords*) kebijakan pemerintah tertentu. Data yang ditarik mencakup *Username*, *Tweet Text*, *Mentions*, *Reply To*, *Quote Tweet*, dan matriks interaksi lainnya.

### 2. Pembersihan Data (`clean_data.py`)
Data Twitter sangat bising (*noisy*). Skrip ini bertanggung jawab untuk memproses teks sebelum dianalisis oleh AI. Pembersihan meliputi penghapusan URL, *mentions*, karakter khusus, dan normalisasi bahasa/kata gaul (*slang*).

### 3. Prediksi Sentimen & Stance (`NLI_stance.py`)
Tahap pemrosesan NLP. Skrip ini menggunakan model **Natural Language Inference (NLI)** (seperti IndoBERT) untuk membaca teks tweet yang sudah bersih dan memprediksi apakah pengguna tersebut **Pro (Mendukung)** atau **Kontra (Menolak)** terhadap kebijakan pemerintah. Hasilnya akan menghasilkan data baru dengan kolom tambahan `Sentimen`.

### 4. Pemodelan Teori Graf (`graph_builder.py`)
Skrip inti untuk analisis jaringan menggunakan *library* `NetworkX`. 
*   **Nodes:** Ekstraksi *Username* sebagai titik jaringan.
*   **Edges:** Membangun garis interaksi berdasarkan kolom *Mentions* dan *Replies*.
*   **Atribut:** Menambahkan warna (Sentimen Pro/Kontra) dan melakukan klasifikasi peran (Pemerintah, Media, Influencer, Komunitas, Masyarakat) menggunakan algoritma *Top-Down Heuristics*.
*   **Output:** Mengonversi struktur graf menjadi format `JSON` yang siap dibaca oleh Web.

### 5. Visualisasi Interaktif (`index.html`)
Antarmuka web interaktif (Frontend) yang membaca file `JSON` dari skrip sebelumnya. Visualisasi ini dibangun untuk memudahkan analisis tingkat makro. Pengguna dapat men-*zoom*, menggeser *node*, melihat detail klasifikasi pengguna saat *hover*, serta memfilter graf berdasarkan skenario (Pro, Kontra, IKN).

---

## 🚀 Cara Menjalankan Projek

Pastikan Anda memiliki Python versi 3.x dan telah menginstal semua pustaka yang dibutuhkan (pandas, networkx, dsb).

1. **Scraping Data:**
   ```bash
   python python_script/scrap_X_script.py
   ```
2. **Bersihkan Data:**
   ```bash
   python python_script/clean_data.py
   ```
3. **Jalankan Prediksi AI:**
   ```bash
   python python_script/NLI_stance.py
   ```
4. **Bangun Graf JSON:**
   ```bash
   python python_script/graph_builder.py
   ```
5. **Lihat Visualisasi:**
   Buka file `index.html` menggunakan peramban web (Google Chrome / Firefox) untuk berinteraksi dengan graf secara visual.

---
*Dikembangkan untuk Projek Pemodelan Opini Publik - Teori Graf.*
