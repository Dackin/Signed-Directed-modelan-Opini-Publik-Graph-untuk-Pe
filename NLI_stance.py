import pandas as pd
import os
from transformers import pipeline

# ============================================================
# NLI Zero-Shot Classification untuk Stance Detection
# Versi ultra-ringan: model kecil + proses satu-satu
# ============================================================

# 1. Load pipeline zero-shot classification (model ringan)
print("Loading model zero-shot classification ...")
classifier = pipeline(
    "zero-shot-classification",
    model="typeform/distilbert-base-uncased-mnli",
    device=-1  # CPU
)
print("Model berhasil dimuat!\n")

# 2. Konfigurasi file dan label per kebijakan
configs = [
    {
        "input": "Data/pro_pemerintah.csv",
        "output": "Data/NLI/pro_pemerintah_nli.csv",
        "candidate_labels": ["mendukung kebijakan pemerintah", "menolak kebijakan pemerintah"]
    },
    {
        "input": "Data/kontra_pemerintah.csv",
        "output": "Data/NLI/kontra_pemerintah_nli.csv",
        "candidate_labels": ["mendukung kebijakan pemerintah", "menolak kebijakan pemerintah"]
    },
    {
        "input": "Data/skenario3_polarisasi_IKN.csv",
        "output": "Data/NLI/skenario3_polarisasi_IKN_nli.csv",
        "candidate_labels": ["mendukung pembangunan IKN", "menolak pembangunan IKN"]
    },
]

# 3. Fungsi klasifikasi stance (satu per satu agar ringan)
def klasifikasi_stance(texts, candidate_labels):
    hasil = []
    total = len(texts)
    
    for i, text in enumerate(texts):
        try:
            # Potong teks terlalu panjang & pastikan string
            t = str(text)[:300] if len(str(text)) > 300 else str(text)
            if not t.strip():
                hasil.append(0)
                continue
                
            res = classifier(t, candidate_labels, multi_label=False)
            top_label = res['labels'][0]
            
            # Label pertama di candidate_labels = "mendukung" → PRO (1)
            if top_label == candidate_labels[0]:
                hasil.append(1)  # PRO
            else:
                hasil.append(0)  # KONTRA
        except Exception as e:
            print(f"  Error di tweet {i}: {e}")
            hasil.append(0)
        
        # Progress setiap 10 tweet
        if (i + 1) % 10 == 0 or (i + 1) == total:
            print(f"  Proses: {i+1}/{total} ({(i+1)*100//total}%)", flush=True)
    
    return hasil

# 4. Proses setiap file
os.makedirs("Data/NLI", exist_ok=True)

for config in configs:
    input_file = config["input"]
    output_file = config["output"]
    labels = config["candidate_labels"]
    
    print(f"\n{'='*60}")
    print(f"File  : {input_file}")
    print(f"Labels: {labels}")
    print(f"{'='*60}")
    
    df = pd.read_csv(input_file)
    df['Tweet_Text'] = df['Tweet_Text'].fillna('')
    
    # Klasifikasi
    df['Sentimen'] = klasifikasi_stance(df['Tweet_Text'].tolist(), labels)
    
    # Hitung statistik
    pro = len(df[df['Sentimen'] == 1])
    kontra = len(df[df['Sentimen'] == 0])
    total = len(df)
    
    print(f"\n  Hasil:")
    print(f"  - Total tweet : {total}")
    print(f"  - PRO (1)     : {pro} ({pro*100//total}%)")
    print(f"  - KONTRA (0)  : {kontra} ({kontra*100//total}%)")
    
    # Simpan
    df.to_csv(output_file, index=False)
    print(f"  Disimpan ke: {output_file}")

print(f"\n{'='*60}")
print("Selesai! Semua file sudah diproses.")
print("Hasil disimpan di folder Data/NLI/")
