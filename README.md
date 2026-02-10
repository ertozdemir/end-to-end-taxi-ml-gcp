# 🚖 NYC Taxi Fare Prediction Projesi

Bu proje, New York City taksi verilerini kullanarak tahmini taksi ücretlerini hesaplayan uçtan uca bir makine öğrenmesi ve web uygulamasıdır. Google Cloud Platform (GCP) teknolojilerini ve modern Python kütüphanelerini kullanarak geliştirilmiştir.

## 🚀 Proje Mimarisi

Proje veri akışı şu şekildedir:

1.  **Veri Kaynağı:** Google BigQuery Public Datasets (NYC Taxi Trips).
2.  **ETL (Extract, Transform, Load):** Veriler BigQuery'den çekilir, temizlenir ve işlenir.
3.  **Veritabanı:** İşlenen veriler Google Cloud üzerindeki **PostgreSQL** tabanlı veritabanına kaydedilir.
4.  **Model Eğitimi:** Veriler PostgreSQL'den okunur ve **XGBoost** algoritması ile eğitilir.
5.  **API Geliştirme:** Eğitilen model **FastAPI** ile dış dünyaya açılır.
6.  **Konteynerizasyon:** API uygulaması **Docker** ile imaj haline getirilir.
7.  **Dağıtım (Deployment):** Docker imajı **Google Cloud Run** üzerinde serverless olarak canlıya alınır.
8.  **Arayüz:** Kullanıcılar **Streamlit** ile geliştirilmiş web arayüzü üzerinden canlı servise bağlanır.

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
DB_NAME=user
DB_USER=user
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

## 🐳 Docker ile Paketleme (API)

Arka uç (Backend) API uygulamasını Docker konteyneri olarak paketlemek için:

### 1. Docker İmajını Oluşturma
Terminali proje ana dizininde açın ve imajı oluşturun:
```bash
docker build -t nyc-taxi-api .
```

### 2. Konteyneri Yerel Çalıştırma
Oluşturulan imajı test etmek için:
```bash
docker run -d -p 8080:8080 --name nyc-taxi-container nyc-taxi-api
```
*API şu adreste çalışacaktır: `http://localhost:8080`*

---

## ☁️ Google Cloud Run ile Canlıya Alma

API servisini Google Cloud Platform (GCP) üzerinde serverless olarak yayınlamak için aşağıdaki adımları izleyin.

### Ön Hazırlık
1.  **Google Cloud Projesi:** Bir proje oluşturun ve faturalandırmayı (billing) etkinleştirin.
2.  **SDK Kurulumu:** `gcloud` CLI aracını yükleyin ve terminalde `gcloud init` komutuyla giriş yapın.
3.  **API'leri Açın:** Cloud Run ve Container Registry (veya Artifact Registry) API'lerini konsoldan etkinleştirin.

### 1. Proje Ayarı ve Yetkilendirme
```bash
# Proje ID'nizi aktif edin (köşeli parantezleri silip ID'nizi yazın)
gcloud config set project [PROJE_ID]

# Docker'ın Google Cloud registry'sine erişmesi için yetki verin
gcloud auth configure-docker
```

### 2. İmajı Etiketleme ve Gönderme (Push)
İmajı Google Container Registry'e (GCR) yüklemek için önce etiketleyin, sonra gönderin.

```bash
# Etiketleme
docker tag nyc-taxi-api gcr.io/[PROJE_ID]/nyc-taxi-api

# Gönderme (Push)
docker push gcr.io/[PROJE_ID]/nyc-taxi-api
```

### 3. Cloud Run Üzerinde Yayınlama (Deploy)
Yüklediğiniz imajı canlıya alın:

```bash
gcloud run deploy nyc-taxi-api-service \
  --image gcr.io/[PROJE_ID]/nyc-taxi-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

*İşlem başarılı olduğunda terminalde size bir **Service URL** verilecektir. Bu URL, API'nizin canlı adresidir.*

---

## 📝 Lisans
Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.
