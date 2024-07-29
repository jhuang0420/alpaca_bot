import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


def train_randforest():
    data = pd.read_csv('data/TSLA_2014-01-01_2024-07-01.csv')
    data['t'] = pd.to_datetime(data['t'], format='%Y-%m-%dT%H:%M:%SZ')
    data['t'] = data['t'].astype('int64') // 10**9  # Convert to seconds
     
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)
    data_scaled = pd.DataFrame(scaled_data, columns=data.columns)
    x = data_scaled.drop(columns=['c'])
    y = data_scaled['c']
    
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)

    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Mean Absolute Error: {mae}")
    print(f"R-squared Score: {r2}")
    
train_randforest()