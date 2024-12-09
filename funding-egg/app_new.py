from flask import Flask, request, jsonify, render_template, Response
from flask_sqlalchemy import SQLAlchemy
import os
import atexit
import gzip
from apscheduler.schedulers.background import BackgroundScheduler
from cleanup_service import CleanupService
from functools import lru_cache
import time

# App Configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales_new.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Performance Optimizations
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 20
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 40
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800  # Recycle connections after 30 minutes

# Enable response compression
app.config['COMPRESS_ALGORITHM'] = 'gzip'
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

# Cache configuration
CACHE_TIMEOUT = 300  # 5 minutes

db = SQLAlchemy(app)

class SalesRecord(db.Model):
    """Model for storing sales records in the database."""
    id = db.Column(db.Integer, primary_key=True)
    salesperson = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def to_dict(self):
        """Convert the record to a dictionary for JSON serialization."""
        return {
            'id': self.id,
            'salesperson': self.salesperson,
            'amount': self.amount
        }

# Database initialization
with app.app_context():
    db.create_all()

# Schedule automatic cleanup every 10 minutes
scheduler = BackgroundScheduler()
cleanup_service = CleanupService()
scheduler.add_job(func=cleanup_service.run_cleanup, trigger="interval", minutes=10)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# Response compression middleware
def gzip_response(response):
    if not response.direct_passthrough and len(response.get_data()) > app.config['COMPRESS_MIN_SIZE']:
        content = gzip.compress(response.get_data(), 
                              compresslevel=app.config['COMPRESS_LEVEL'])
        response.set_data(content)
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = len(content)
    return response

app.after_request(gzip_response)

# Cache decorator for expensive operations
def timed_lru_cache(seconds: int, maxsize: int = 128):
    def wrapper_decorator(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = seconds
        func.expiration = time.time() + seconds

        def wrapped_func(*args, **kwargs):
            if time.time() > func.expiration:
                func.cache_clear()
                func.expiration = time.time() + func.lifetime
            return func(*args, **kwargs)

        return wrapped_func
    return wrapper_decorator

# Routes
@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index_new.html')

@app.route('/api/sales', methods=['GET'])
def get_sales():
    """Retrieve all sales records."""
    try:
        sales = SalesRecord.query.all()
        return jsonify([sale.to_dict() for sale in sales])
    except Exception as e:
        return jsonify({'error': 'Failed to fetch sales records'}), 500

@app.route('/api/sales', methods=['POST'])
def add_sale():
    """Add a new sales record."""
    try:
        data = request.get_json()
        
        # Validate input data
        if not data or 'salesperson' not in data or 'amount' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        # Create and save new record
        new_sale = SalesRecord(
            salesperson=str(data['salesperson']).strip(),
            amount=float(data['amount'])
        )
        db.session.add(new_sale)
        db.session.commit()
        
        return jsonify(new_sale.to_dict()), 201
        
    except ValueError:
        db.session.rollback()
        return jsonify({'error': 'Invalid amount value'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add sale'}), 400
    
@app.route('/api/sales/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    """Delete a sales record by ID."""
    try:
        sale = SalesRecord.query.get(sale_id)
        if not sale:
            return jsonify({'error': 'Sale not found'}), 404
        db.session.delete(sale)
        db.session.commit()
        return jsonify({'message': 'Sale deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete sale'}), 400

@app.route('/broker_dashboard')
def broker_dashboard():
    """Serve the broker dashboard page."""
    return render_template('broker_dashboard.html')

@app.route('/funding_egg')
def funding_egg():
    """Serve the funding egg page."""
    return render_template('funding_egg.html')

# Deleting old backup files
backup_files = [
    'app_new_backup.py',
    'app_new_backup_v2.py',
    'app_new_backup_v3.py',
    'app_new_backup_v4.py',
    'app_new_backup_v5.py',
    'app_new_backup_v6.py'
]
for file in backup_files:
    try:
        os.remove(file)
    except Exception as e:
        print(f'Error deleting {file}: {e}')

if __name__ == '__main__':
    app.run(debug=True)
