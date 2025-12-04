import random
import time
from datetime import datetime
from config.firebase_config import FirebaseConfig
from services.classifier import FishClassifier

class LimixBackend:
    def __init__(self):
        self.classifier = FishClassifier()
        self.sensor_ref = FirebaseConfig.get_reference('sensor_data')
        self.recommendations_ref = FirebaseConfig.get_reference('ai_recommendations')
        self.alerts_ref = FirebaseConfig.get_reference('alerts')
        print("✅ Backend initialized")
    
    def generate_data(self):
        base = random.choice([
            {'ph': 7.5, 'temp': 28, 'turbidity': 4.2},
            {'ph': 7.2, 'temp': 26, 'turbidity': 3.8},
            {'ph': 8.0, 'temp': 30, 'turbidity': 5.5},
        ])
        
        return {
            'ph': round(base['ph'] + random.uniform(-0.3, 0.3), 2),
            'temperature': round(base['temp'] + random.uniform(-1, 1), 2),
            'turbidity': round(base['turbidity'] + random.uniform(-0.5, 0.5), 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def start_simulator(self, interval=5):
        print("📡 Simulator started")
        num = 0
        try:
            while True:
                num += 1
                data = self.generate_data()
                self.sensor_ref.push(data)
                print(f"📤 #{num}: pH={data['ph']}, T={data['temperature']}°C")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("⚠️ Stopped")
    
    def on_new_data(self, event):
        if not event.data:
            return
        
        data = event.data
        print(f"🔔 New: pH={data.get('ph')}, T={data.get('temperature')}°C")
        
        result = self.classifier.classify(
            data.get('ph'),
            data.get('temperature'),
            data.get('turbidity')
        )
        
        if 'error' not in result:
            print(f"🐟 Recommended: {result['fish_name']}")
            self.recommendations_ref.push({
                'fish_type': result['fish_type'],
                'fish_name': result['fish_name'],
                'confidence': result['confidence'],
                'timestamp': result['timestamp']
            })
    
    def start_listener(self):
        print("👂 Listener started")
        self.sensor_ref.listen(self.on_new_data)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("⚠️ Stopped")
