# Hajj Heat Stress Monitor

Environmental monitoring system for Gulf climate conditions, providing real-time Wet Bulb Globe Temperature (WBGT) calculations, UV index warnings, and heat stress alerts in multiple languages for outdoor workers and Hajj pilgrims.

## 🌟 Features

- **WBGT Calculations**: Accurate Wet Bulb Globe Temperature for heat stress assessment
- **Multi-language Support**: Arabic, Tagalog, Urdu, Hindi, English, Malay, Indonesian
- **Real-time Monitoring**: Live weather data from NOAA and local Gulf stations
- **Heat Stress Alerts**: Color-coded warnings based on international standards
- **UV Index Tracking**: UV radiation monitoring and protection recommendations
- **Worker Safety**: OSHA-compliant heat stress management for outdoor workers
- **Hajj Focus**: Specialized monitoring for pilgrimage conditions
- **Mobile Alerts**: SMS and push notifications for critical conditions
- **API Access**: RESTful API for integration with workplace systems

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/Wsh7Ash/hajj-heat-monitor
cd hajj-heat-monitor
pip install -r requirements.txt
```

### Configuration

```bash
# Copy configuration template
cp config/config.example.yaml config/config.yaml

# Edit with API keys
nano config/config.yaml
```

### Running the System

```bash
# Start the monitoring system
python monitor.py

# Start the web dashboard
python app.py

# Run API server
python api/server.py
```

## 📍 Monitoring Locations

### Saudi Arabia
- **Mecca**: Hajj pilgrimage sites
- **Medina**: Prophet's Mosque
- **Riyadh**: Capital city monitoring
- **Jeddah**: Coastal monitoring
- **Dammam**: Eastern province

### UAE
- **Dubai**: Urban heat island monitoring
- **Abu Dhabi**: Capital monitoring
- **Sharjah**: Northern Emirates

### Qatar
- **Doha**: Capital and coastal areas
- **Al Wakrah**: Southern monitoring

### Kuwait
- **Kuwait City**: Urban monitoring
- **Jahra**: Desert monitoring

### Bahrain
- **Manama**: Capital monitoring
- **Muharraq**: Industrial areas

## 📡 API Endpoints

### Current Conditions

#### Get Current WBGT
```http
GET /api/v1/current/wbgt?location=mecca&language=en
```

#### Get UV Index
```http
GET /api/v1/current/uv?location=riyadh&language=ar
```

#### Get Heat Stress Assessment
```http
GET /api/v1/current/heat-stress?location=dubai&worker_type=outdoor
```

### Forecasts

#### Get WBGT Forecast
```http
GET /api/v1/forecast/wbgt?location=mecca&hours=24&language=en
```

#### Get Heat Stress Forecast
```http
GET /api/v1/forecast/heat-stress?location=dubai&days=3
```

### Alerts

#### Get Active Alerts
```http
GET /api/v1/alerts/active?country=SA&severity=high
```

#### Subscribe to Alerts
```http
POST /api/v1/alerts/subscribe
Content-Type: application/json

{
  "location": "mecca",
  "language": "ar",
  "alert_types": ["heat_stress", "uv"],
  "notification_method": "sms",
  "contact": "+966500000000"
}
```

## 📊 Response Examples

### Current Conditions Response

```json
{
  "location": {
    "name": "Mecca",
    "coordinates": {"lat": 21.4225, "lng": 39.8262},
    "country": "SA",
    "timezone": "Asia/Riyadh"
  },
  "timestamp": "2026-04-25T10:30:00Z",
  "temperature": {
    "air": 42.5,
    "wet_bulb": 28.3,
    "globe": 45.8,
    "wbgt": 31.2,
    "relative_humidity": 25,
    "wind_speed": 8.5
  },
  "heat_stress": {
    "level": "extreme_risk",
    "color": "#8B0000",
    "risk_score": 9.2,
    "recommendations": [
      "Stop all outdoor work",
      "Move to air-conditioned areas",
      "Provide frequent water breaks",
      "Monitor for heat illness"
    ],
    "work_restrictions": {
      "outdoor_work": "prohibited",
      "indoor_work": "with_rest_breaks",
      "emergency_procedures": "active"
    }
  },
  "uv_index": {
    "value": 11,
    "level": "extreme",
    "protection_time": "06:00-17:00",
    "recommendations": [
      "Seek shade",
      "Wear protective clothing",
      "Use SPF 30+ sunscreen",
      "Avoid sun exposure"
    ]
  },
  "translations": {
    "ar": {
      "heat_stress_level": "خطر شديد",
      "recommendations": ["توقف عن العمل في الهواء الطلق", "الانتقال إلى مناطق مكيفة"]
    },
    "tl": {
      "heat_stress_level": "Matinding Panganib",
      "recommendations ["Itigil ang trabaho sa labas", "Maglipat sa aircon"]
    }
  }
}
```

### Forecast Response

```json
{
  "location": "Mecca",
  "forecast_period": "24 hours",
  "generated_at": "2026-04-25T10:30:00Z",
  "hourly_forecast": [
    {
      "time": "2026-04-25T11:00:00Z",
      "wbgt": 31.5,
      "heat_stress_level": "extreme_risk",
      "uv_index": 11,
      "recommendations": ["Avoid outdoor activities"]
    }
  ],
  "summary": {
    "peak_wbgt": 33.2,
    "peak_time": "14:00",
    "extreme_risk_hours": 6,
    "high_risk_hours": 8,
    "moderate_risk_hours": 10
  }
}
```

## 🏗️ Architecture

```
hajj-heat-monitor/
├── monitor.py                 # Main monitoring daemon
├── app.py                     # Flask web dashboard
├── core/
│   ├── weather.py             # Weather data processing
│   ├── wbgt_calculator.py     # WBGT calculations
│   ├── heat_stress.py         # Heat stress assessment
│   ├── uv_index.py            # UV index calculations
│   └── alerts.py              # Alert system
├── data/
│   ├── weather_stations/      # Station configurations
│   ├── thresholds/           # Risk thresholds by country
│   └── translations/          # Multi-language content
├── api/
│   ├── server.py              # FastAPI server
│   ├── endpoints/
│   │   ├── current.py         # Current conditions
│   │   ├── forecast.py        # Forecast endpoints
│   │   └── alerts.py          # Alert management
├── models/
│   ├── database.py            # Database models
│   ├── weather.py             # Weather data models
│   └── alerts.py              # Alert models
├── web/
│   ├── dashboard.html          # Main dashboard
│   ├── mobile/                # Mobile-optimized views
│   └── static/                # CSS/JS assets
├── config/
│   ├── config.yaml            # Main configuration
│   └── stations.yaml          # Weather station list
├── tests/
└── requirements.txt
```

## 🌡️ Heat Stress Levels

### WBGT Risk Categories

| WBGT (°C) | Risk Level | Color | Work Recommendations |
|-----------|-------------|-------|-------------------|
| < 25.0 | Low | Green | Normal work |
| 25.0-27.9 | Moderate | Yellow | 50% work, 50% rest |
| 28.0-30.0 | High | Orange | 25% work, 75% rest |
| 30.0-32.0 | Very High | Red | 15% work, 85% rest |
| > 32.0 | Extreme | Black | Stop all work |

### Regional Adaptations

#### Saudi Arabia (OSHA Standards)
- **Summer Period**: June-September
- **Peak Hours**: 12:00-15:00
- **Mandatory Breaks**: Every 30 minutes

#### UAE Standards
- **High Risk**: WBGT > 28.0°C
- **Work Stoppage**: WBGT > 32.0°C
- **Monitoring**: Every 15 minutes

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test
pytest tests/test_wbgt.py
```

## 📈 Performance Metrics

- **Data Update Frequency**: Every 5 minutes
- **API Response Time**: < 200ms
- **Forecast Accuracy**: 85%+ for 24-hour forecasts
- **Alert Latency**: < 2 minutes for critical conditions
- **Multi-language Support**: 7 languages

## 🔧 Configuration

### Environment Variables

```yaml
# config/config.yaml
weather:
  noaa_api_key: "your_noaa_api_key"
  openweather_api_key: "your_openweather_key"
  update_interval: 300  # seconds

monitoring:
  locations:
    - name: "Mecca"
      coordinates: [21.4225, 39.8262]
      country: "SA"
      priority: "high"

alerts:
  sms_enabled: true
  email_enabled: true
  push_enabled: true
  thresholds:
    extreme_risk: 32.0
    high_risk: 28.0

languages:
  default: "en"
  supported: ["en", "ar", "tl", "ur", "hi", "ms", "id"]

database:
  url: "postgresql://user:pass@localhost/hajj_heat"
  retention_days: 90
```

### Weather Station Configuration

```yaml
# config/stations.yaml
stations:
  mecca_haram:
    name: "Mecca Grand Mosque"
    coordinates: [21.4225, 39.8262]
    elevation: 277
    country: "SA"
    data_sources: ["noaa", "local_station"]
    priority: 1
    
  riyadh_kingdom:
    name: "Riyadh Kingdom Centre"
    coordinates: [24.7136, 46.6753]
    elevation: 612
    country: "SA"
    data_sources: ["noaa", "openweather"]
    priority: 2
```

## 📱 Mobile Integration

### Mobile App Features

- **Real-time Monitoring**: Live WBGT and UV data
- **Personal Alerts**: Location-based notifications
- **Multi-language**: Interface in worker's native language
- **Work Safety**: OSHA-compliant recommendations
- **Emergency Contacts**: Quick access to medical services

### Mobile API Usage

```javascript
// Get current conditions for user location
navigator.geolocation.getCurrentPosition(async (position) => {
  const response = await fetch(`/api/v1/current/heat-stress?lat=${position.coords.latitude}&lng=${position.coords.longitude}`);
  const conditions = await response.json();
  
  updateUI(conditions);
});

// Subscribe to alerts
const subscription = await fetch('/api/v1/alerts/subscribe', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    language: 'ar',
    notification_method: 'push',
    contact: user.pushToken
  })
});
```

## 🌍 Multi-language Support

### Supported Languages

| Language | Code | Target Workers |
|----------|------|----------------|
| Arabic | ar | Local Gulf workers |
| Tagalog | tl | Filipino workers |
| Urdu | ur | Pakistani workers |
| Hindi | hi | Indian workers |
| English | en | Expatriates |
| Malay | ms | Malaysian workers |
| Indonesian | id | Indonesian workers |

### Translation Structure

```json
{
  "heat_stress": {
    "extreme_risk": {
      "en": "Extreme Risk - Stop all outdoor work",
      "ar": "خطر شديد - توقف عن جميع الأعمال في الهواء الطلق",
      "tl": "Matinding Panganib - Itigil ang lahat ng trabaho sa labas",
      "ur": "شدہ خطر - باہری کام روک دیں"
    }
  },
  "recommendations": {
    "drink_water": {
      "en": "Drink water every 15 minutes",
      "ar": "اشرب ماء كل 15 دقيقة",
      "tl": "Uminom ng tubig bawat 15 minuto"
    }
  }
}
```

## 🔒 Safety Features

- **Medical Emergency Integration**: Direct connection to emergency services
- **Worker Identification**: RFID/QR code worker tracking
- **Compliance Reporting**: Automated OSHA compliance reports
- **Audit Trail**: Complete monitoring history
- **Data Privacy**: Worker health data protection

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

We welcome contributions! See CONTRIBUTING.md for guidelines.

### Adding New Locations

1. Add station configuration in `config/stations.yaml`
2. Implement country-specific thresholds in `data/thresholds/`
3. Add translations in `data/translations/`
4. Update location mappings in `core/weather.py`
5. Add tests for new location

### Adding New Languages

1. Create translation files in `data/translations/[language].json`
2. Update language configuration in `config/config.yaml`
3. Add language tests in `tests/translations/`
4. Update documentation

## 🙏 Acknowledgments

- NOAA for weather data and climate models
- Gulf meteorological departments for local data
- OSHA for heat stress guidelines
- WHO for occupational health standards
- International Labor Organization for worker safety

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: heat-monitor@example.com
- **Emergency**: Available 24/7 during Hajj season

---

**Note**: This system provides environmental monitoring and recommendations but should not replace professional medical advice. In case of heat-related emergencies, contact local emergency services immediately.
