from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from config.firebase_config import FirebaseConfig
import os

app = Flask(__name__)
CORS(app)

FirebaseConfig.initialize(
    credential_path='serviceAccountKey.json',
    database_url=os.getenv('FIREBASE_DATABASE_URL', 'https://limix-fishfarm-v2-default-rtdb.firebaseio.com/')
)

sensor_ref = FirebaseConfig.get_reference('sensor_data')
recommendations_ref = FirebaseConfig.get_reference('ai_recommendations')
alerts_ref = FirebaseConfig.get_reference('alerts')

@app.route('/')
def home():
    return jsonify({
        'message': '🐟 Limix API',
        'version': '1.0',
        'endpoints': {
            '/api/sensor/latest': 'Latest reading',
            '/api/sensor/history': 'History for charts',
            '/api/recommendation/latest': 'Fish recommendation',
            '/api/dashboard': '⭐ All data (use this)',
            '/api/alerts': 'Alerts'
        }
    })

@app.route('/api/sensor/latest')
def get_latest():
    try:
        data = sensor_ref.order_by_key().limit_to_last(1).get()
        if not data:
            return jsonify({'success': False}), 404
        
        latest = list(data.values())[0]
        return jsonify({
            'success': True,
            'data': {
                'ph': latest.get('ph'),
                'temperature': latest.get('temperature'),
                'turbidity': latest.get('turbidity'),
                'timestamp': latest.get('timestamp')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sensor/history')
def get_history():
    try:
        limit = request.args.get('limit', 20, type=int)
        limit = min(limit, 100)
        
        data = sensor_ref.order_by_key().limit_to_last(limit).get()
        if not data:
            return jsonify({'success': False}), 404
        
        history = []
        for key, val in data.items():
            history.append({
                'id': key,
                'ph': val.get('ph'),
                'temperature': val.get('temperature'),
                'turbidity': val.get('turbidity'),
                'timestamp': val.get('timestamp')
            })
        
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({'success': True, 'count': len(history), 'data': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recommendation/latest')
def get_recommendation():
    try:
        data = recommendations_ref.order_by_key().limit_to_last(1).get()
        if not data:
            return jsonify({'success': False}), 404
        
        rec = list(data.values())[0]
        return jsonify({
            'success': True,
            'data': {
                'fish_name': rec.get('fish_name'),
                'confidence': rec.get('confidence'),
                'timestamp': rec.get('timestamp')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard')
def dashboard():
    """⭐ Main endpoint for Flutter app"""
    try:
        # Latest
        latest_data = sensor_ref.order_by_key().limit_to_last(1).get()
        latest = list(latest_data.values())[0] if latest_data else {}
        
        # History
        history_data = sensor_ref.order_by_key().limit_to_last(20).get()
        history = []
        if history_data:
            for k, v in history_data.items():
                history.append({
                    'ph': v.get('ph'),
                    'temperature': v.get('temperature'),
                    'turbidity': v.get('turbidity'),
                    'timestamp': v.get('timestamp')
                })
        
        # Averages
        if history:
            avg_ph = round(sum(h['ph'] for h in history) / len(history), 2)
            avg_temp = round(sum(h['temperature'] for h in history) / len(history), 2)
            avg_turb = round(sum(h['turbidity'] for h in history) / len(history), 2)
        else:
            avg_ph = avg_temp = avg_turb = 0
        
        # Recommendation
        rec_data = recommendations_ref.order_by_key().limit_to_last(1).get()
        recommendation = list(rec_data.values())[0] if rec_data else None
        
        return jsonify({
            'success': True,
            'data': {
                'current': {
                    'ph': latest.get('ph', 0),
                    'temperature': latest.get('temperature', 0),
                    'turbidity': latest.get('turbidity', 0),
                    'timestamp': latest.get('timestamp')
                },
                'averages': {
                    'ph': avg_ph,
                    'temperature': avg_temp,
                    'turbidity': avg_turb
                },
                'history': history,
                'recommendation': {
                    'fish_name': recommendation.get('fish_name') if recommendation else 'N/A',
                    'confidence': recommendation.get('confidence') if recommendation else 0
                } if recommendation else None
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
