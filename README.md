# 🚖 NYC Taxi Fare Prediction Projesi

Bu proje, New York City taksi verilerini kullanarak tahmini taksi ücretlerini hesaplayan uçtan uca bir makine öğrenmesi ve web uygulamasıdır. Google Cloud Platform (GCP) teknolojilerini ve modern Python kütüphanelerini kullanarak geliştirilmiştir.

## 🚀 Proje Mimarisi

Proje veri akışı şu şekildedir:

1.  **Veri Kaynağı:** Google BigQuery Public Datasets (NYC Taxi Trips).
2.  **ETL (Extract, Transform, Load):** Veriler BigQuery'den çekilir, temizlenir ve işlenir.
3.  **Veritabanı:** İşlenen veriler Google Cloud üzerindeki **PostgreSQL** tabanlı veritabanına kaydedilir.
4.  **Model Eğitimi:** Veriler PostgreSQL'den okunur ve **XGBoost** algoritması ile eğitilir.
5.  **API:** Eğitilen model **FastAPI** ile dış dünyaya açılır.
6.  **Arayüz:** Kullanıcılar **Streamlit** ile geliştirilmiş web arayüzü üzerinden tahmin alır.

---

## 📂 Proje Yapısı

```
nyc_taxi_project/
├── app/
│   ├── api.py           # FastAPI uygulaması (Modeli servis eder)
│   └── frontend.py      # Streamlit arayüzü (Kullanıcı etkileşimi)
├── models/              # Eğitilmiş model (.pkl) dosyaları
├── src/
│   ├── from_bigquery_to_cloud.py  # BigQuery -> PostgreSQL ETL süreci
│   └── model.py                   # Model eğitimi ve kaydetme
├── .env                 # Ortam değişkenleri (Veritabanı şifreleri vb.)
├── .gitignore           # Git tarafından yok sayılacak dosyalar
├── requirements.txt     # Python kütüphaneleri
└── README.md            # Proje dokümantasyonu
```

---

## 🛠️ Kurulum

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### 1. Projeyi Klonlayın
```bash
git clone https://github.com/ertozdemir/end-to-end-taxi-ml-gcp.git
cd end-to-end-taxi-ml-gcp
```

### 2. Sanal Ortam Oluşturun
```bash
python -m venv venv
# Windows için:
venv\Scripts\activate
# Mac/Linux için:
source venv/bin/activate
```

### 3. Kütüphaneleri Yükleyin
```bash
pip install -r requirements.txt
```

### 4. .env Dosyasını Ayarlayın
Proje ana dizininde `.env` adında bir dosya oluşturun ve veritabanı bilgilerinizi girin:

```env
DB_HOST=kendi_google_cloud_ip_adresiniz
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=sifreniz
DB_PORT=5432
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account.json
```
*(Not: BigQuery erişimi için Google Cloud Service Account JSON dosyasına ihtiyacınız olabilir.)*

---

## ▶️ Çalıştırma Adımları

### Adım 1: Veri Çekme ve Veritabanına Yazma (ETL)
BigQuery'den veriyi çekip Cloud SQL (PostgreSQL) veritabanına yazar.
```bash
python src/from_bigquery_to_cloud.py
```

### Adım 2: Modeli Eğitme
Veritabanındaki veriyi okur, modeli eğitir ve `models/` klasörüne kaydeder.
```bash
python src/model.py
```

### Adım 3: API'yi Başlatma (Backend)
Modeli bir REST API olarak sunar.
```bash
uvicorn app.api:app --reload
```
*API şu adreste çalışacaktır: `http://127.0.0.1:8000`*

### Adım 4: Arayüzü Başlatma (Frontend)
Kullanıcı arayüzünü açar.
```bash
streamlit run app/frontend.py
```
*Arayüz şu adreste açılacaktır: `http://localhost:8501`*



---

## 📝 Lisans
Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.
