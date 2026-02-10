import pandas as pd
import joblib
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import os

# 1. Uygulamayı (Garsonu) Başlat
app = FastAPI(title="NYC Taxi Fare Prediction API", version="1.0")

# ---------------------------------------------------------
# 2. Modeli ve Encoder'ı Hafızaya Yükle (Başlangıçta 1 Kere)
# ---------------------------------------------------------
print("⏳ Model ve Encoder yükleniyor...")

# Path configurations
# This file is in app/, so go up one level to find 'models/' directory in root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'xgb_model.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'models', 'encoder.pkl')

try:
    # Eğitilmiş modeli yükle
    model = joblib.load(MODEL_PATH)
    
    # Eğitilmiş OneHotEncoder'ı yükle (Sütun isimlerini biliyor)
    encoder = joblib.load(ENCODER_PATH)
    
    print(f"✅ BAŞARILI: Model ve Encoder kullanıma hazır! ({MODEL_PATH})")
except Exception as e:
    print(f"❌ HATA: Dosyalar bulunamadı! {e}")
    print(f"Aranan yol: {MODEL_PATH}")
    print("Lütfen önce src/model.py dosyasını çalıştırıp .joblib dosyalarını oluşturun.")
    model, encoder = None, None

# ---------------------------------------------------------
# 3. Veri Şablonu (Kullanıcıdan Ne İstiyoruz?)
# ---------------------------------------------------------
class TaxiInput(BaseModel):
    trip_distance: float  # Mesafe (Mil)
    trip_duration: float  # Süre (Dakika)
    trip_hours: int       # Saat (0-23)
    day_name: str              # Gün (Örn: "Monday")
    is_tolls: int         # Köprü (0 veya 1)


@app.get("/")
def ana_sayfa():
    return {"message": "API ayakta! Tahmin için /docs adresine git."}

# ---------------------------------------------------------
# 4. Tahmin Endpoint'i (Sipariş Alma Noktası)
# ---------------------------------------------------------
@app.post("/predict")
def predict_fare(input_data: TaxiInput):
    # Eğer model yüklenmediyse hata dön
    if not model or not encoder:
        return {"error": "Model sunucuda yüklü değil, tahmin yapılamaz."}

    # A. Gelen veriyi Sözlükten -> DataFrame'e çevir
    input_df = pd.DataFrame([input_data.dict()])

    try:
        # B. ENCODING İŞLEMİ (OneHot Dönüşümü) 🛠️
        # 1. Sadece 'day' sütununu alıp encoder'a sokuyoruz
        encoded_array = encoder.transform(input_df[['day_name']])
        
        # 2. Eğer sparse matrix (sıkıştırılmış) dönerse, normal array'e çevir
        if hasattr(encoded_array, "toarray"):
            encoded_array = encoded_array.toarray()
            
        # 3. Yeni sütun isimlerini al (day_Monday, day_Tuesday vb.)
        encoded_columns = encoder.get_feature_names_out(['day_name'])
        
        # 4. Bu array'den yeni bir DataFrame oluştur
        encoded_df = pd.DataFrame(encoded_array, columns=encoded_columns)
        
        # C. BİRLEŞTİRME (Concatenation) 🧩
        input_df = input_df.drop(columns=['day_name']) # String olanı at
        final_df = pd.concat([input_df, encoded_df], axis=1) # Sayısal olanları ekle
        
        # D. SÜTUN SIRALAMASI (Güvenlik Önlemi) 🛡️
        if hasattr(model, "feature_names_in_"):
            final_df = final_df[model.feature_names_in_]

        # E. TAHMİN YAP 🎯
        prediction = model.predict(final_df)
        tahmini_fiyat = float(prediction[0])

        return {
            "tahmin": round(tahmini_fiyat, 2), # 2 basamak yuvarla
            "para_birimi": "USD"
        }

    except Exception as e:
        return {"error": f"Bir hata oluştu: {str(e)}"}

# ---------------------------------------------------------
# 5. Çalıştırma Komutu (Not olarak)
# ---------------------------------------------------------
# Terminale şunu yazarak çalıştır:
# uvicorn app.api:app --reload
