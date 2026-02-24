from flask import Flask, request, jsonify
import joblib
import pandas as pd

model = joblib.load("final_model.pkl")
features = joblib.load('model_features.pkl')

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    pd_data = pd.DataFrame([data])
    pd_data = pd_data[features]
    
    prediction = model.predict(pd_data)
    return jsonify({
        'predicted_volatility': float(prediction[0])
    })
    
if __name__ == '__main__':
    app.run(debug=True)    