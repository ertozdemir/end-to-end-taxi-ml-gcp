from google.cloud import bigquery
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

PROJECT_ID = "datapipeline-486114"

def fetch_and_save():

    client = bigquery.Client(project=PROJECT_ID, location="US")

    query = """
        (SELECT 
            pickup_datetime, 
            dropoff_datetime,
            trip_distance, 
            fare_amount, 
            tip_amount,
            tolls_amount,
            mta_tax + imp_surcharge AS surcharges_and_taxes,
            total_amount
        FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022` 
        WHERE fare_amount BETWEEN 2.5 AND 20 
        AND trip_distance BETWEEN 0.5 AND 6
        AND passenger_count > 0
        AND rate_code LIKE '%1%'
        AND payment_type LIKE '%1%'
        LIMIT 20000)
        UNION ALL
        (SELECT 
            pickup_datetime, 
            dropoff_datetime,
            trip_distance, 
            fare_amount, 
            tip_amount,
            tolls_amount,
            mta_tax + imp_surcharge AS surcharges_and_taxes,
            total_amount
        FROM `bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2022` 
        WHERE fare_amount > 20 
        AND trip_distance > 6 
        AND passenger_count > 0
        AND rate_code LIKE '%1%'
        AND payment_type LIKE '%1%'
        LIMIT 20000)
    """
    print('Veriler çekiliyor...')
    df = client.query(query).to_dataframe()
    print('Veriler çekildi.')
    
    return df

def process_data(df):
    
    #tarih kolonlarını datetime formatına çeviriyoruz.
    df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
    df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])

    # toplam yolculuk süresi hesabı
    df['trip_duration'] = ((df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds() / 60).round(3)

    # Yolculuk saati ve günü 
    df['trip_hours'] = df['pickup_datetime'].dt.hour
    df['day_name'] = df['pickup_datetime'].dt.day_name()

    # is_tolls kolonu
    df['is_tolls'] = (df['tolls_amount'] > 0).astype(int)

    # Gürültü kolonları drop etme
    df.drop(['pickup_datetime', 'dropoff_datetime','fare_amount','tip_amount','surcharges_and_taxes','tolls_amount'],
            axis=1, inplace=True)
             
    
    # duration outlier tespiti
    outlier_dur = list(df[df['trip_duration'] > 110].index)
    minus_dur = list(df[df['trip_duration'] < 0].index)
    df.drop(outlier_dur,axis=0, inplace=True)
    df.drop(minus_dur, axis=0, inplace=True)

    # distance outliers tespiti
    distance_outliers =list(df[df['trip_distance']>34].index)
    df.drop(index=distance_outliers, axis=0, inplace=True)

    print('data preprocessing is success.')
    print('data augmentation is starting...')
    # Kısa mesafe için manuel data augmentation
    short_distance = pd.DataFrame({
        'trip_distance': np.random.uniform(0.5, 3.0, 2500),  # 0.5 ile 3 km arası
        'trip_duration': np.random.uniform(3, 15, 2500),          # 3 ile 15 dk arası
        'trip_hours': np.random.randint(0, 24, 2500),        # Rastgele saatler
        'is_tolls': 0,                                       # Köprü yok
        'day_name': np.random.choice(['Monday', 'Tuesday', 'Wednesday',
                   'Thursday', 'Friday', 'Saturday', 'Sunday'], 2500) # Rastgele günler
    })

    short_distance['total_amount'] = 3.0 + (short_distance['trip_distance'] * 1.5) + (short_distance['trip_duration'] * 0.5)

    # İki dataseti birleştiriyoruz
    df = pd.concat([df, short_distance], ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    df['trip_distance'] = df['trip_distance'].astype(float)
    df['total_amount'] = df['total_amount'].astype(float)
    df['trip_distance'] = df['trip_distance'].round(2)
    df['trip_duration'] = df['trip_duration'].round(2)
    df['total_amount'] = df['total_amount'].round(2)

    print('data augmentation is success.')

    return df
    ### GRAFIK EKLENECEK

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')


def to_database(df,db_host,db_name,db_user,db_password,db_port):

    print(f"🔌 Cloud SQL ({db_host}) veritabanına bağlanılıyor...")
    
    # Bağlantı Stringi
    connection_string = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        engine = create_engine(connection_string)
        
        print(f"🚀 Veriler 'taxi_table' tablosuna yazılıyor... (Lütfen bekleyin)")
        
        # if_exists='replace' -> Tablo varsa siler, sıfırdan kurar.
        df.to_sql('taxi_table', engine, index=False, if_exists='replace')
        
        print("✅ BAŞARILI! Veritabanı güncellendi.")
        
    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")


if __name__ == '__main__':
    df = fetch_and_save()
    final_df = process_data(df)
    to_database(final_df,DB_HOST,DB_NAME,DB_USER,DB_PASSWORD,DB_PORT)
