from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

# ✅ Direct API Key (no Render issue now)
API_KEY = "3488ae6ddd7f4473e02f9066887a952b"

# Debug route
@app.route("/check")
def check():
    return f"API_KEY = {API_KEY}"

# Fetch weather
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        return None

    return {
        "city": city,
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"]
    }

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
    error = None

    if request.method == "POST":
        city = request.form.get("city")

        if city:
            weather = get_weather(city)
            if weather:
                risk = predict_risk(weather["temp"], weather["humidity"])
            else:
                error = "City not found or API error"

    return render_template("index.html", weather=weather, risk=risk, error=error)

# Render port config
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)