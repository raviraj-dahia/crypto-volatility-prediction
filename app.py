from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import pandas as pd

# Load model and features
model = joblib.load("final_model.pkl")
features = joblib.load("model_features.pkl")

# Load dataset for history
history_df = pd.read_csv("notebook/dataset.csv")

app = Flask(__name__)
CORS(app)

# 🔹 Feature Engineering Function
def create_features(df):
    df = df.copy()

    # Moving averages
    df['ma_7'] = df['close'].rolling(7).mean()
    df['ma_30'] = df['close'].rolling(30).mean()

    # Liquidity
    df['liquidity_ratio'] = df['volume'] / df['marketCap']

    # Bollinger Bands
    rolling_mean = df['close'].rolling(20).mean()
    rolling_std = df['close'].rolling(20).std()
    df['bb_upper'] = rolling_mean + (2 * rolling_std)
    df['bb_lower'] = rolling_mean - (2 * rolling_std)

    # ATR
    df['atr_14'] = (df['high'] - df['low']).rolling(14).mean()

    return df


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/predict', methods=['POST'])
def predict():
    global history_df

    try:
        data = request.json

        # Convert input to DataFrame
        new_row = pd.DataFrame([data])

        # Append to history
        history_df = pd.concat([history_df, new_row], ignore_index=True)

        # Generate features
        history_df = create_features(history_df)

        # Take latest row
        df = history_df.tail(1)

        # Handle NaN (important for rolling features)
        df = df.fillna(method='bfill').fillna(method='ffill')

        # Select required features
        df = df[features]

        # Predict
        prediction = model.predict(df)

        return jsonify({
            'predicted_volatility': float(prediction[0])
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        })


if __name__ == '__main__':
    app.run(debug=True)