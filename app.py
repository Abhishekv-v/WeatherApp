from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)

app.secret_key = os.getenv('api_key')
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        new_city = request.form.get('city')
        if new_city:
            existing_city = City.query.filter_by(name=new_city).first()

            if existing_city:
                flash('City already exists!', 'warning')
            else:
                url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=' + os.getenv('api_key')
                r = requests.get(url.format(new_city)).json()

                if r.get('cod') == 200:
                    new_city_obj = City(name=new_city)
                    db.session.add(new_city_obj)
                    db.session.commit()
                    flash(f'City {new_city} added successfully!', 'success')
                else:
                    flash('City not found!', 'danger')

    cities = City.query.all()
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=' + os.getenv('api_key')

    weather_data = []

    for city in cities:
        r = requests.get(url.format(city.name)).json()
        weather = {
            'id': city.id,
            'city': city.name,
            'temperature': r['main']['temp'] ,
            'description': r['weather'][0]['description'] ,
            'icon': r['weather'][0]['icon'] ,
        }
        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)

@app.route('/delete/<int:city_id>', methods=['POST'])

def delete_city(city_id):
    city = City.query.get_or_404(city_id)
    db.session.delete(city)
    db.session.commit()
    flash(f'City {city.name} deleted successfully!', 'success')
    return redirect(url_for('index'))