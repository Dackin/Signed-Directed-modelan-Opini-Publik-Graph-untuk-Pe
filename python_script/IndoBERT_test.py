import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 1. Baca file CSV kamu
df = pd.read_csv('Data/pro_pemerintah.csv')

# Pastikan tidak ada teks yang kosong/NaN
df['Tweet_Text'] = df['Tweet_Text'].fillna('')

# 2. Panggil model dan tokenizer IndoBERT
# Menggunakan model yang sudah dilatih khusus untuk Analisis Sentimen bahasa Indonesia
model_name = "w11wo/indonesian-roberta-base-sentiment-classifier" 
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# 3. Fungsi untuk memproses teks per kelompok (batch) agar cepat & hemat memori
def proses_indobert_batch(texts, batch_size=32):
    hasil_prediksi = []
    
    for i in range(0, len(texts), batch_size):
        batch_tweets = texts[i:i+batch_size].tolist()
        
        # Tokenisasi teks sekaligus dalam satu batch
        inputs = tokenizer(batch_tweets, padding=True, truncation=True, max_length=128, return_tensors="pt")
        
        # Prediksi menggunakan model
        with torch.no_grad():
            outputs = model(**inputs)
            # Mengambil indeks dengan skor tertinggi sebagai hasil label/sentimen
            predictions = torch.argmax(outputs.logits, dim=-1)
            hasil_prediksi.extend(predictions.tolist())
            
    # Pemetaan label dari angka ke angka target (1: Positif, 0: Negatif, Netral diabaikan/dibuang)
    label_map = {0: 1, 1: 'Netral', 2: 0}
    hasil_prediksi_teks = [label_map.get(label, 'Tidak Diketahui') for label in hasil_prediksi]
            
    return hasil_prediksi_teks

# 4. Jalankan prosesnya ke kolom Tweet_Text
df['Sentimen'] = proses_indobert_batch(df['Tweet_Text'], batch_size=32)

# 5. Filter hanya yang Positif (1) dan Negatif (0) (hapus Netral)
df_filtered = df[df['Sentimen'].isin([1, 0])]

# 6. Simpan kembali seluruh data beserta kolom baru ke CSV baru
df_filtered.to_csv('pro_pemerintah_indobert.csv', index=False)
print("Selesai! Hasil disimpan di 'pro_pemerintah_indobert.csv'")