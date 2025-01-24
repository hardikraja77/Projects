# app.py

from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Function to find WOEID by city name
def get_woeid(city):
    url = f"https://www.metaweather.com/api/location/search/?query={city}"
    response = requests.get(url)
    data = response.json()
    
    if data:
        return data[0]['woeid']
    else:
        return None

# Function to get weather data by WOEID
def get_weather_by_woeid(woeid):
    url = f"https://www.metaweather.com/api/location/{woeid}/"
    response = requests.get(url)
    data = response.json()
    
    if data:
        return data
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_weather', methods=['POST'])
def get_weather():
    city = request.json['city']
    woeid = get_woeid(city)
    
    if woeid:
        weather_data = get_weather_by_woeid(woeid)
        if weather_data:
            consolidated_weather = weather_data['consolidated_weather'][0]  # Get today's weather
            result = {
                'city': city,
                'temperature': consolidated_weather['the_temp'],
                'weather_state': consolidated_weather['weather_state_name'],
                'latitude': weather_data['latt_long'].split(',')[0],
                'longitude': weather_data['latt_long'].split(',')[1]
            }
            return jsonify(result)
    return jsonify({'error': 'City not found!'}), 404

if __name__ == '__main__':
    app.run(debug=True)
