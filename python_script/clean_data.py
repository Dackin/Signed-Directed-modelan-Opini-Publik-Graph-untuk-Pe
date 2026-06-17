import pandas as pd

def clean_twitter_data(input_csv, output_csv):
    print("Membaca data awal...")
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: File {input_csv} tidak ditemukan.")
        return

    awal = len(df)
    print(f"Jumlah baris awal: {awal}")

    # 1. Menghapus Duplikat
    # Terkadang ada tweet yang persis sama terekam dua kali
    df.drop_duplicates(subset=['Tweet_Text', 'Author_Username'], inplace=True)
    setelah_duplikat = len(df)
    print(f"Data setelah hapus duplikat: {setelah_duplikat} (dihapus {awal - setelah_duplikat})")

    # 2. Filtering Keyword (Sesuai diskusimu)
    # Ubah teks ke huruf kecil semua (lower) agar pencarian kata tidak sensitif huruf besar/kecil
    df['text_lower'] = df['Tweet_Text'].astype(str).str.lower()
    
    # Kumpulan keyword yang dianggap valid (topik IKN)
    keywords = ['ikn', 'ibu kota', 'nusantara', 'investor', 'anggaran', 'pindah ibu kota']
    
    # Buat fungsi untuk mengecek apakah ada keyword di teks
    def contains_keyword(text):
        return any(kw in text for kw in keywords)
    
    # Terapkan filter keyword
    has_keyword_mask = df['text_lower'].apply(contains_keyword)
    
    # --- PILIHAN STRATEGI ---
    # STRATEGI 1: Hapus SEMUA yang tidak punya keyword (Strict)
    # df_bersih = df[has_keyword_mask].copy()

    # STRATEGI 2 (Rekomendasi SNA): Hapus yang tidak punya keyword KECUALI dia Reply/Quote/Mention
    # Karena kalau dia Reply/Quote, dia tetap membentuk "Garis/Edge" di jaringan (Graf)
    has_edge_mask = df['Reply_To'].notna() | df['Quote_Tweet_Of'].notna() | df['Mentions'].notna()
    
    # Kita simpan baris yang PUNYA KEYWORD *ATAU* PUNYA KONEKSI INTERAKSI
    df_bersih = df[has_keyword_mask | has_edge_mask].copy()

    # 3. Membersihkan kolom yang kosong (opsional)
    # Mengisi nilai NaN/Kosong di kolom edge dengan string kosong agar rapi
    cols_to_fill = ['Mentions', 'Reply_To', 'Quote_Tweet_Of']
    for c in cols_to_fill:
        df_bersih[c] = df_bersih[c].fillna('')

    # Hapus kolom bantuan
    df_bersih.drop(columns=['text_lower'], inplace=True)

    akhir = len(df_bersih)
    print(f"Data setelah filter keyword/SNA: {akhir} (dihapus {setelah_duplikat - akhir})")

    # Simpan hasil
    df_bersih.to_csv(output_csv, index=False)
    print(f"\nData bersih berhasil disimpan di: {output_csv}")

if __name__ == "__main__":
    clean_twitter_data("scraping_ikn_gabungan.csv", "data_siap_sna_ikn.csv")
