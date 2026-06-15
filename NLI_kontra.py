import pandas as pd
import os
from transformers import pipeline

# ============================================================
# NLI Zero-Shot - Model Besar (mDeBERTa multilingual)
# Proses: kontra_pemerintah.csv saja
# ============================================================

print("Loading model mDeBERTa-v3-base multilingual NLI ...")
classifier = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
    device=-1  # CPU
)
print("Model berhasil dimuat!\n")

# Konfigurasi
input_file = "Data/pro_pemerintah.csv"
output_file = "Data/NLI/pro_pemerintah_nli.csv"
candidate_labels = [
    "kebijakan ini bermanfaat bagi rakyat",
    "kebijakan ini merugikan atau tidak efektif"
]

print(f"{'='*60}")
print(f"File  : {input_file}")
print(f"Labels: {candidate_labels}")
print(f"{'='*60}")

df = pd.read_csv(input_file)
df['Tweet_Text'] = df['Tweet_Text'].fillna('')

hasil = []
total = len(df)

for i, text in enumerate(df['Tweet_Text']):
    try:
        t = str(text)[:300] if len(str(text)) > 300 else str(text)
        if not t.strip():
            hasil.append(0)
            continue
        
        res = classifier(t, candidate_labels, multi_label=False)
        top_label = res['labels'][0]
        
        if top_label == candidate_labels[0]:
            hasil.append(1)  # PRO
        else:
            hasil.append(0)  # KONTRA
    except Exception as e:
        print(f"  Error di tweet {i}: {e}")
        hasil.append(0)
    
    if (i + 1) % 10 == 0 or (i + 1) == total:
        print(f"  Proses: {i+1}/{total} ({(i+1)*100//total}%)", flush=True)

df['Sentimen'] = hasil

pro = len(df[df['Sentimen'] == 1])
kontra = len(df[df['Sentimen'] == 0])

print(f"\n  Hasil:")
print(f"  - Total tweet : {total}")
print(f"  - PRO (1)     : {pro} ({pro*100//total}%)")
print(f"  - KONTRA (0)  : {kontra} ({kontra*100//total}%)")

os.makedirs("Data/NLI", exist_ok=True)
df.to_csv(output_file, index=False)
print(f"  Disimpan ke: {output_file}")
print("Selesai!")
