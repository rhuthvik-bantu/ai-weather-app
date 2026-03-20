from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

# API Key from Render Environment
API_KEY = os.environ.get("848e871df384d555b82ca61ef5e03baf")

if not API_KEY:
    raise ValueError("API_KEY not found. Please set it in Render environment variables.")

# Get weather data
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        return None

    weather = {
        "city": city,
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"]
    }

    return weather

# Simple AI logic
def predict_risk(temp, humidity):
    if temp > 35:
        return "🔥 High Temperature Alert!"
    elif humidity > 80:
        return "🌧️ High Humidity Alert!"
    else:
        return "✅ Normal Weather"

# Main route
@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    risk = None

    if request.method == "POST":
        city = request.form.get("city")
        if city:
            weather = get_weather(city)
            if weather:
                risk = predict_risk(weather["temp"], weather["humidity"])

    return render_template("index.html", weather=weather, risk=risk)

# IMPORTANT for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)