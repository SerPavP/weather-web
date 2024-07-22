from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    weather_description = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    icon = db.Column(db.String(50), nullable=False)
