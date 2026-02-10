import streamlit as st
import requests

# ---------------------------------------------------------
# 1. Sayfa Ayarları (Tabelayı Asıyoruz)
# ---------------------------------------------------------
st.set_page_config(
    page_title="NYC Taksi Tahmin",
    page_icon="🚕",
    layout="centered"
)

# Başlık ve Açıklama
st.title("🚖 NYC Taksi Ücret Tahmin Sistemi")
st.markdown("---")
st.info("Bu uygulama, geliştirdiğimiz **XGBoost Modeli** ve **FastAPI** servisi ile entegre çalışır.")

# ---------------------------------------------------------
# 2. Kullanıcıdan Veri Alma (Menü Seçimi)
# ---------------------------------------------------------
# Daha şık dursun diye ekranı iki sütuna bölelim
col1, col2 = st.columns(2)

with col1:
    mesafe = st.number_input("📏 Mesafe (Km)", min_value=0.1, max_value=100.0, value=2.0, step=0.5)
    sure = st.number_input("⏱️ Süre (Dakika)", min_value=1.0, max_value=300.0, value=10.0, step=1.0)
    
with col2:
    gunler = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    secilen_gun = st.selectbox("📅 Gün Seçimi", gunler)
    
    saat = st.slider("🕒 Saat Kaç?", 0, 23, 14)

# Köprü sorusu (Tek başına aşağıda dursun)
kopru_durumu = st.radio("Köprü/Tünel Ücreti Var mı?", ["Yok", "Var"])
# API bizden 0 veya 1 bekliyor, dönüşüm yapalım:
is_tolls = 1 if kopru_durumu == "Var" else 0

st.markdown("---")

# ---------------------------------------------------------
# 3. Buton ve API İletişimi (Siparişi Gönderme)
# ---------------------------------------------------------
if st.button("💸 Tahmini Ücreti Hesapla", type="primary"):
    
    # Kullanıcıya "Hesaplanıyor..." mesajı göster
    with st.spinner('Yapay Zeka Fiyatı Hesaplıyor...'):
        
        # A. Veriyi Paketle (API'nin beklediği format)
        veri_paketi = {
            "trip_distance": mesafe,
            "trip_duration": sure,
            "trip_hours": saat,
            "day_name": secilen_gun,
            "is_tolls": is_tolls
        }
        
        # B. API'ye Gönder (Garsona Seslen)
        try:
            # API adresi (Localhost)
            api_url = "http://127.0.0.1:8000/predict"
            
            # POST isteği atıyoruz
            cevap = requests.post(api_url, json=veri_paketi)
            
            # C. Sonucu İşle
            if cevap.status_code == 200:
                sonuc = cevap.json() # Gelen JSON: {"tahmin": 12.50, ...}
                fiyat = sonuc["tahmin"]
                
                # Ekrana Büyükçe Yazdır
                st.success(f"💰 Tahmini Tutar: ${fiyat}")
                
                # Detay (Opsiyonel)
                st.caption(f"Sunucudan Gelen Mesaj: {sonuc.get('mesaj', '')}")
            else:
                st.error(f"Hata Oluştu! Sunucu Kodu: {cevap.status_code}")
                st.write(cevap.text)
                
        except requests.exceptions.ConnectionError:
            st.error("🚨 HATA: API'ye bağlanılamadı!")
            st.warning("İpucu: 'api.py' dosyasını çalıştırdığından emin misin? (uvicorn app.api:app --reload)")
        except Exception as e:
            st.error(f"Beklenmeyen bir hata oluştu: {e}")

st.markdown("---")
st.markdown("© 2026 - NYC Data Science Project by Ertugrul Ozdemir | Powered by **FastAPI & Streamlit**")
