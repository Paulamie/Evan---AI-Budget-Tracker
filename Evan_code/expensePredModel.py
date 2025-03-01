#this is the expense prediction model for the patterns page under the records.html template.

import pandas as pd
import numpy as np
import mysql.connector
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def train_spending_model_tf():
    # 1. Fetch data from your MySQL database
    conn = mysql.connector.connect(
        host='localhost',
        user='myuser',
        password='mypass',
        database='mydb'
    )
    df_expenses = pd.read_sql("SELECT username, expense_amount, created_at FROM expenses", conn)
    df_income = pd.read_sql("SELECT username, income_amount, created_at FROM income", conn)
    conn.close()

    # 2. Preprocess: aggregate monthly data for each user
    df_expenses['created_at'] = pd.to_datetime(df_expenses['created_at'])
    df_expenses['year_month'] = df_expenses['created_at'].dt.to_period('M')
    monthly_expenses = df_expenses.groupby(['username','year_month'])['expense_amount'].sum().reset_index()
    monthly_expenses.rename(columns={'expense_amount': 'monthly_expenses'}, inplace=True)

    df_income['created_at'] = pd.to_datetime(df_income['created_at'])
    df_income['year_month'] = df_income['created_at'].dt.to_period('M')
    monthly_income = df_income.groupby(['username','year_month'])['income_amount'].sum().reset_index()
    monthly_income.rename(columns={'income_amount': 'monthly_income'}, inplace=True)

    # Merge into one DataFrame
    df = pd.merge(monthly_expenses, monthly_income, on=['username','year_month'], how='outer').fillna(0)

    # 3. Sort by username and time, then shift monthly_expenses to get future_expenses
    df = df.sort_values(by=['username','year_month'])
    # Shift next month's expenses as the target
    df['future_expenses'] = df.groupby('username')['monthly_expenses'].shift(-1)

    # Drop rows without a future_expenses
    df = df.dropna(subset=['future_expenses'])
    
    # 4. Create feature matrix (X) and target (y)
    # Example: use current monthly_expenses, monthly_income to predict next month’s expenses
    X = df[['monthly_expenses', 'monthly_income']].values
    y = df['future_expenses'].values

    # Convert your year_month to numeric if you want to incorporate time trend, or skip for simplicity
    # e.g. df['time_idx'] = (df['year_month'] - df['year_month'].min()).apply(lambda p: p.n)
    # X = np.column_stack([X, df['time_idx'].values])

    # 5. Define a simple Keras model
    model = keras.Sequential([
        layers.Dense(16, activation='relu', input_shape=(2,)),  # or 3 if you add time_idx
        layers.Dense(8, activation='relu'),
        layers.Dense(1)  # single output: future_expenses
    ])

    model.compile(
        optimizer='adam',
        loss='mse',       # MSE for regression
        metrics=['mae']   # track mean absolute error
    )

    # 6. Train the model
    history = model.fit(
        X, y,
        epochs=20,
        batch_size=16,
        validation_split=0.2,
        verbose=1
    )

    # 7. Save the trained model
    model.save('spending_model_tf')
    print("TensorFlow model trained and saved to 'spending_model_tf' folder.")

if __name__ == "__main__":
    train_spending_model_tf()