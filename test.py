import joblib
import pandas as pd
import numpy as np
import os

BASE_DIR = "C:/Users/ert/nyc_taxi_project/models"

def load_models():
    model_path = os.path.join(BASE_DIR, 'xgb_model.pkl')
    encoder_path = os.path.join(BASE_DIR, 'encoder.pkl')
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model dosyası bulunamadı: {model_path}")
    if not os.path.exists(encoder_path):
        raise FileNotFoundError(f"Encoder dosyası bulunamadı: {encoder_path}. Lütfen önce model.py dosyasını çalıştırın.")

    model = joblib.load(model_path)
    encoder = joblib.load(encoder_path)
    return model, encoder

def make_custom_prediction(model, encoder, trip_distance, trip_duration, trip_hours, is_tolls, day_name):
    # 1. Sayısal verileri hazırla: [Mesafe, Süre, Saat, Tolls]
    # DİKKAT: model.py'deki eğitim sırası: trip_distance, trip_duration, trip_hours, is_tolls
    numeric_data = np.array([[trip_distance, trip_duration, trip_hours, is_tolls]])

    # 2. Gün ismini encode et
    # Encoder bir DataFrame bekler veya 2D array
    day_df = pd.DataFrame({'day_name': [day_name]})
    day_encoded = encoder.transform(day_df[['day_name']])

    # 3. Verileri birleştir
    final_input = np.hstack([numeric_data, day_encoded])

    # 4. Tahmin yap
    prediction = model.predict(final_input)
    
    print(f"\n--- 🚕 TAKSİ TAHMİN ---")
    print(f"Mesafe: {trip_distance} km")
    print(f"Süre: {trip_duration} dk")
    print(f"Saat: {trip_hours}:00")
    print(f"Tolls: {'Var' if is_tolls else 'Yok'}")
    print(f"Gün: {day_name}")
    print(f"💰 Tahmini Ücret: {prediction[0]:.2f} $")
    print(f"-----------------------\n")
    return prediction[0]

if __name__ == '__main__':
    try:
        model, encoder = load_models()
        
        # Manuel Test Değerleri
        print("Manuel test yapılıyor...")
        make_custom_prediction(
            model=model, 
            encoder=encoder, 
            trip_distance=2.5, 
            trip_duration=15, 
            trip_hours=14, 
            is_tolls=0, 
            day_name='Monday'
        )
        
        # Başka bir örnek
        make_custom_prediction(
            model=model, 
            encoder=encoder, 
            trip_distance=10.5, 
            trip_duration=45, 
            trip_hours=20, 
            is_tolls=1, 
            day_name='Friday'
        )

    except Exception as e:
        print(f"Hata oluştu: {e}")
