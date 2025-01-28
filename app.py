import requests
from flask import Flask, render_template, request
from datetime import datetime


app = Flask(__name__)


def adjust_city_name(city_name):
    # Türkçe karakterleri değiştir
    replacements = {
        'ı': 'i', 'İ': 'I', 'ğ': 'g', 'Ğ': 'G', 'ü': 'u', 'Ü': 'U',
        'ş': 's', 'Ş': 'S', 'ö': 'o', 'Ö': 'O', 'ç': 'c', 'Ç': 'C'
    }
    
    # Şehir ismindeki Türkçe karakterleri dönüştür
    for char, replacement in replacements.items():
        city_name = city_name.replace(char, replacement)
    
    return city_name


def get_cities():
    response = requests.get("https://turkiyeapi.dev/api/v1/provinces")
    if response.status_code == 200:
        data = response.json()
        return [province['name'] for province in data['data']]
    return []

@app.route('/', methods=['GET', 'POST'])
def index():
    cities = get_cities()
    
    # Formdan şehir adını al
    selected_city = request.form.get('city', 'istanbul')  # Varsayılan olarak 'istanbul'
    
    # Türkçe karakterleri düzenle
    adjusted_city = adjust_city_name(selected_city)
    
    api_key = "942562e68acf4420b15120736252701"
    url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={adjusted_city}&days=7'

    # API'den veri al
    response = requests.get(url)
    data = response.json()

    # Şu anki hava durumu
    current_weather = {
        "temp_c": data['current']['temp_c'],
        "condition": data['current']['condition']['text'],
        "icon": data['current']['condition']['icon'],
        "day": datetime.strptime(data['forecast']['forecastday'][0]['date'], "%Y-%m-%d").strftime("%A"),
        "date": datetime.strptime(data['forecast']['forecastday'][0]['date'], "%Y-%m-%d").strftime("%d,%m,%Y")
    }

    # 7 günlük hava tahmini
    forecast_weather = []
    for day in data['forecast']['forecastday']:
        day_weather = {
            "date": day['date'],
            "day": datetime.strptime(day['date'], "%Y-%m-%d").strftime("%A"),
            "formatted_date": datetime.strptime(day['date'], "%Y-%m-%d").strftime("%d,%m,%Y"),
            "mintemp_c": day['day']['mintemp_c'],
            "maxtemp_c": day['day']['maxtemp_c'],
            "avgtemp_c": day['day']['avgtemp_c'],
            "daily_chance_of_rain": day['day']['daily_chance_of_rain'],
            "daily_chance_of_snow": day['day']['daily_chance_of_snow'],
            "uv": day['day']['uv']
        }
        forecast_weather.append(day_weather)

    return render_template(
        'index.html', 
        cities=cities, 
        selected_city=selected_city, 
        adjusted_city=adjusted_city, 
        current=current_weather, 
        forecast=forecast_weather
    )

@app.route('/day/<date>/<city>')
def day_detail(date, city):
    api_key = "942562e68acf4420b15120736252701"
    url = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&days=7'
    response = requests.get(url)
    data = response.json()

    # Günün verisini alıyoruz
    day_weather = next((day for day in data['forecast']['forecastday'] if day['date'] == date), None)

    return render_template('day-detail.html', day=day_weather, city=city)

    
if __name__ == '__main__':
    app.run(debug=True)
