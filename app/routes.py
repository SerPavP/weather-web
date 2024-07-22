from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
from datetime import datetime, timedelta
from app.models import db, City, SearchHistory
from app.translations import weather_descriptions

# Инициализация приложения Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'

# Инициализация базы данных
db.init_app(app)

API_KEY = 'ad572a8533544b8aed08413794668da5'
API_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        current_temp = data['main']['temp']
        weather_description = data['weather'][0]['description']
        icon = data['weather'][0]['icon']
        timezone_offset = data['timezone']

        # Перевод описания погоды на русский язык
        weather_description = weather_descriptions.get(weather_description, weather_description)

        # Получаем текущее время с учетом смещения часового пояса
        current_time_utc = datetime.utcnow()
        current_time = current_time_utc + timedelta(seconds=timezone_offset)
        current_time_str = current_time.strftime('%H:%M')

        # Сохраняем историю поиска
        search_history = SearchHistory(
            city_name=city,
            temperature=current_temp,
            weather_description=weather_description,
            icon=icon,
            timestamp=current_time
        )
        db.session.add(search_history)
        db.session.commit()

        return {
            'city_name': city,
            'current_temp': current_temp,
            'timezone': current_time_str,
            'weather_description': weather_description,
            'icon': icon
        }
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None

    if request.method == 'POST':
        city_name = request.form.get('city')
        weather_data = get_weather(city_name)
        if weather_data:
            flash('City found!', 'success')
        else:
            flash('City not found or invalid input!', 'error')

    search_history = SearchHistory.query.order_by(SearchHistory.timestamp.desc()).limit(10).all()

    return render_template('index.html', weather=weather_data, search_history=search_history)

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q')
    if query:
        cities = City.query.filter(City.name.ilike(f"{query}%")).limit(5).all()
        city_names = [city.name for city in cities]
        return jsonify(matching_results=city_names)
    return jsonify(matching_results=[])

@app.route('/delete/<int:id>', methods=['POST'])
def delete_city(id):
    search_entry = SearchHistory.query.get(id)
    if search_entry:
        db.session.delete(search_entry)
        db.session.commit()
        flash('City deleted!', 'success')
    else:
        flash('City not found!', 'error')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
