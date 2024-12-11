import os
import sys
import socket
from flask import Flask, render_template, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Gauge
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from sqlalchemy.exc import OperationalError
import redis
import logging

app = Flask(__name__)
#Configuracion DB y redis cache

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgresql:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'redis'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 0
app.config['CACHE_REDIS_URL'] = 'redis://redis:6379/0'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

cache = Cache(app)

metrics = PrometheusMetrics(app)

app_up = Gauge('flask_app_up', 'Application health status: 1 = up, 0 = down')

db = SQLAlchemy(app)

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)

def check_db_connection():
    try:
        # Try to execute a simple query
        db.session.execute('SELECT 1')
        return True
    except OperationalError:
        return False

@app.route('/health')
def health():
    try:
        # Perform health checks here (e.g., DB, dependencies)
        app_up.set(1)  # App is up
        return "App is healthy!", 200
    except Exception as e:
        app_up.set(0)  # App is down
        return f"Health check failed: {str(e)}", 500
    
def check_redis_connection():
    """Check if the Redis is reachable."""
    try:
        # Create a Redis client and check the connection
        r = redis.Redis(host='redis', port=6379, db=0)
        return r.ping()  # Returns True if the server is reachable
    except redis.exceptions.ConnectionError:
        return False
    except Exception as e:
        logging.error(f"Redis connection failed: {e}")  # Log any other exception
        return False


@app.route('/get_ip', methods=['GET'])
def get_ip():
    try:
        # Get the container's IP address using socket
        ip_address = socket.gethostbyname(socket.gethostname())  # Gets the IP of the container
        return jsonify({'ip': ip_address})  # Return the IP in JSON format
    except Exception as e:
        # In case of any error, return an error message in JSON format
        return jsonify({'error': str(e)}), 500


@app.route('/')
def index():
    items = []
    item_count = 0

    db_connected = check_db_connection()  # Check database connection
    redis_connected = check_redis_connection()  # Check Redis connection
    

    if redis_connected:
        items = cache.get('items')  # Try fetching from cache
        
        if items is None:  # Cache miss
            if db_connected:
                items = Item.query.all()  # Fetch items if connected
                cache.set('items', items, timeout=60)  # Cache the result for 5 minutes
        item_count = len(items)
        return render_template('index.html', items=items, item_count=item_count, db_connected=db_connected, redis_connected=redis_connected)
    elif db_connected:
        items = Item.query.all()  # Fetch items if connected
        item_count = Item.query.count()
        return render_template('index.html', items=items, item_count=item_count, db_connected=db_connected, redis_connected=redis_connected)

    


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

