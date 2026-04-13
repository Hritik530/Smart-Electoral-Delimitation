import pandas as pd
from sklearn.preprocessing import StandardScaler

def process_data(df):
    # Handle missing values
    df = df.fillna(df.mean(numeric_only=True))
    
    # Feature Engineering
    df['pop_density'] = df['population'] / (df['area'] + 1e-6)
    df['socio_score'] = (df['income'] * 0.6) + (df['education'] * 0.4)
    
    # Standardize for ML
    scaler = StandardScaler()
    df[['lat_std', 'lon_std']] = scaler.fit_transform(df[['latitude', 'longitude']])
    
    return df