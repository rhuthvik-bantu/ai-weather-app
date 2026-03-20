from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
from sklearn.linear_model import LogisticRegression
import numpy as np

app = Flask(__name__)

# Replace with your OpenWeatherMap API key
API_KEY = "848e871df384d555b82ca61ef5e03baf"

# ----- ML Models for AI Prediction -----
# Temperature risk (0=safe, 1=risk)
X_temp = np.array([[30], [32], [35], [40]])
y_temp = np.array([0, 0, 1, 1])
temp_model = LogisticRegression()
temp_model.fit(X_temp, y_temp)

# Humidity risk (0=safe, 1=high risk)
X_hum = np.array([[40], [50], [60], [70], [80]])
y_hum = np.array([0,0,1,1,1])
hum_model = LogisticRegression()
hum_model.fit(X_hum, y_hum)

# Rain probability (0=no, 1=likely)
X_rain = np.array([[0], [1], [2], [3]])
y_rain = np.array([0, 0, 1, 1])
rain_model = LogisticRegression()
rain_model.fit(X_rain, y_rain)

# ----- Functions -----
def get_weather_by_city(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()
    if response.get("cod") != 200:
        return None
    return {
        "city": city,
        "temp": response["main"]["temp"],
        "weather": response["weather"][0]["description"],
        "humidity": response["main"]["humidity"],
        "lat": response["coord"]["lat"],
        "lon": response["coord"]["lon"]
    }

def get_weather_by_coords(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()
    if response.get("cod") != 200:
        return None
    return {
        "city": response["name"],
        "temp": response["main"]["temp"],
        "weather": response["weather"][0]["description"],
        "humidity": response["main"]["humidity"],
        "lat": lat,
        "lon": lon
    }

def predict_risk_ai(weather_data):
    temp = weather_data["temp"]
    hum = weather_data["humidity"]
    rain_flag = 1 if "rain" in weather_data["weather"].lower() else 0

    # ML predictions
    temp_risk = temp_model.predict([[temp]])[0]
    hum_risk = hum_model.predict([[hum]])[0]
    rain_risk = rain_model.predict([[rain_flag]])[0]

    # Combine risk messages
    messages = []
    messages.append("⚠️ High Temp Risk" if temp_risk else "✅ Temp Safe")
    messages.append("⚠️ High Humidity Risk" if hum_risk else "✅ Humidity Safe")
    messages.append("⚠️ Rain Likely" if rain_risk else "✅ No Rain")
    return " | ".join(messages)

# ----- Routes -----
@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    risk = None

    if request.method == "POST":
        city = request.form.get("city")
        if city:
            weather_data = get_weather_by_city(city)
            if weather_data:
                risk = predict_risk_ai(weather_data)

    return render_template("index.html", weather=weather_data, risk=risk)

@app.route("/location")
def location():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    global location_weather
    location_weather = get_weather_by_coords(lat, lon)
    return jsonify({"status": "ok"})

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)