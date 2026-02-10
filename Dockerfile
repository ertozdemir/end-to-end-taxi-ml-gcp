# 1. Python 3.10 yüklü sanal bir bilgisayar (imaj) indir
FROM python:3.10-slim

# 2. Çalışma klasörünü oluştur
WORKDIR /app

# 3. Gereksinim dosyasını kopyala ve kütüphaneleri yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Tüm proje dosyalarını içeri kopyala
COPY . .

# 5. Portu dışarıya aç (Cloud Run genelde 8080 kullanır)
EXPOSE 8080

# 6. Konteyner başladığında çalışacak komut
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8080"]