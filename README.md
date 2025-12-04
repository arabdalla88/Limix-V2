# Limix Backend 🐟

## Setup
```bash
pip install -r requirements.txt
```

## Run
```bash
# API only
python run.py api

# Everything (simulator + listener + API)
python run.py all
```

## API Endpoints
- `GET /api/dashboard` - ⭐ Main endpoint (use this in Flutter)
- `GET /api/sensor/latest` - Latest reading
- `GET /api/sensor/history?limit=20` - History for charts
- `GET /api/recommendation/latest` - Fish recommendation

## Flutter Integration
```dart
final response = await http.get(Uri.parse('YOUR-API-URL/api/dashboard'));
final data = jsonDecode(response.body)['data'];
print(data['current']['ph']);  // Current pH
print(data['recommendation']['fish_name']);  // Recommended fish
```
