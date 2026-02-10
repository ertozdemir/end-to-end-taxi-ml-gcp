import pandas as pd 
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib   
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# Current file is in src/, so we go up one level to get project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')

def load_data(db_user,db_password,db_host,db_port,db_name):
    connection_string = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    try:
        # Motoru oluştur
        engine = create_engine(connection_string)
        
        # Veriyi Çek (SQL Sorgusu ile daha garantidir)
        query = f"SELECT * FROM taxi_table"
        df = pd.read_sql(query, engine)
        
        print(f"✅ Başarılı! Toplam {len(df)} satır veri çekildi.")
        return df
        
    except Exception as e:
        print(f"❌ Veri çekme hatası: {e}")
        return None


def predict_model(df):
    #train-test split
    X = df.drop('total_amount', axis=1)
    y = df['total_amount']
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=42)

    # one hot encode categorical features
    
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    
    train_days = encoder.fit_transform(X_train[['day_name']])
    test_days = encoder.transform(X_test[['day_name']])
    
    # Sayısal Kolonları Ayır (Mesafe, Süre, Saat, is_tolls)
    X_train_numeric = X_train.drop('day_name', axis=1).values
    X_test_numeric = X_test.drop('day_name', axis=1).values
    
    # BİRLEŞTİRME (Sayısal Veriler + Encode Edilmiş Günler)
    X_train_final = np.hstack([X_train_numeric, train_days])
    X_test_final = np.hstack([X_test_numeric, test_days])

    xgb_model = XGBRegressor(random_state=42)
    xgb_model.fit(X_train_final, y_train)

    y_pred = xgb_model.predict(X_test_final)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    y_train_pred = xgb_model.predict(X_train_final)
    r2_train = r2_score(y_train, y_train_pred)
    print(f'Train R2: {r2_train:.4f} | Test R2: {r2:.4f}')
    print(f'MAE: {mae:.2f}')
    print(f'MSE: {mse:.2f}')


    # feature importance
    feature_names = list(X_train.drop('day_name', axis=1).columns) + list(encoder.get_feature_names_out(['day_name']))
    importances = xgb_model.feature_importances_

    feat_imp = pd.Series(importances, index=feature_names).sort_values(ascending=False)
    print(feat_imp) 

    print('model saving...')
    # Use BASE_DIR which points to project root, then join with 'models'
    models_dir = os.path.join(BASE_DIR, 'models')
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        
    joblib.dump(xgb_model , os.path.join(models_dir, 'xgb_model.pkl'))
    joblib.dump(encoder , os.path.join(models_dir, 'encoder.pkl'))
    print(f'model saved to {models_dir}')



if __name__ == '__main__':
    df = load_data(DB_USER,DB_PASSWORD,DB_HOST,DB_PORT,DB_NAME)
    if df is not None:
        predict_model(df)
