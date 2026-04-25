from flask import Flask, render_template, jsonify, request
from core.weather import WeatherService
from core.wbgt_calculator import WBGTCalculator
from core.heat_stress import HeatStressAssessor
from core.uv_index import UVIndexCalculator
from core.alerts import AlertManager

app = Flask(__name__)

# Initialize services
weather_service = WeatherService()
wbgt_calculator = WBGTCalculator()
heat_stress_assessor = HeatStressAssessor()
uv_calculator = UVIndexCalculator()
alert_manager = AlertManager()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/v1/current/wbgt')
def current_wbgt():
    """Get current WBGT for a location"""
    location = request.args.get('location', 'mecca')
    language = request.args.get('language', 'en')
    
    # Get weather data
    weather = weather_service.get_current_weather(location)
    
    # Calculate WBGT
    wbgt = wbgt_calculator.calculate_wbgt(
        weather['temperature'],
        weather['humidity'],
        weather['wind_speed'],
        weather['solar_radiation']
    )
    
    # Assess heat stress
    heat_stress = heat_stress_assessor.assess(wbgt, location)
    
    # Get UV index
    uv_index = uv_calculator.calculate_uv_index(
        weather['uv_index'],
        weather['cloud_cover']
    )
    
    return jsonify({
        'location': weather['location'],
        'timestamp': weather['timestamp'],
        'temperature': {
            'air': weather['temperature'],
            'wet_bulb': wbgt['wet_bulb'],
            'globe': wbgt['globe'],
            'wbgt': wbgt['wbgt'],
            'relative_humidity': weather['humidity'],
            'wind_speed': weather['wind_speed']
        },
        'heat_stress': heat_stress,
        'uv_index': uv_index,
        'language': language
    })

@app.route('/api/v1/current/uv')
def current_uv():
    """Get current UV index for a location"""
    location = request.args.get('location', 'riyadh')
    language = request.args.get('language', 'ar')
    
    weather = weather_service.get_current_weather(location)
    uv_index = uv_calculator.calculate_uv_index(
        weather['uv_index'],
        weather['cloud_cover']
    )
    
    return jsonify({
        'location': weather['location'],
        'timestamp': weather['timestamp'],
        'uv_index': uv_index,
        'language': language
    })

@app.route('/api/v1/current/heat-stress')
def current_heat_stress():
    """Get current heat stress assessment"""
    location = request.args.get('location', 'dubai')
    worker_type = request.args.get('worker_type', 'outdoor')
    
    weather = weather_service.get_current_weather(location)
    wbgt = wbgt_calculator.calculate_wbgt(
        weather['temperature'],
        weather['humidity'],
        weather['wind_speed'],
        weather['solar_radiation']
    )
    
    heat_stress = heat_stress_assessor.assess(wbgt, location, worker_type)
    
    return jsonify({
        'location': weather['location'],
        'timestamp': weather['timestamp'],
        'heat_stress': heat_stress,
        'worker_type': worker_type
    })

@app.route('/api/v1/forecast/wbgt')
def forecast_wbgt():
    """Get WBGT forecast"""
    location = request.args.get('location', 'mecca')
    hours = int(request.args.get('hours', 24))
    language = request.args.get('language', 'en')
    
    forecast = weather_service.get_forecast(location, hours)
    
    hourly_forecast = []
    for hour_data in forecast:
        wbgt = wbgt_calculator.calculate_wbgt(
            hour_data['temperature'],
            hour_data['humidity'],
            hour_data['wind_speed'],
            hour_data['solar_radiation']
        )
        heat_stress = heat_stress_assessor.assess(wbgt['wbgt'], location)
        
        hourly_forecast.append({
            'time': hour_data['time'],
            'wbgt': wbgt['wbgt'],
            'heat_stress_level': heat_stress['level'],
            'uv_index': hour_data['uv_index'],
            'recommendations': heat_stress['recommendations']
        })
    
    # Calculate summary
    wbgt_values = [h['wbgt'] for h in hourly_forecast]
    extreme_hours = len([h for h in hourly_forecast if h['heat_stress_level'] == 'extreme_risk'])
    high_hours = len([h for h in hourly_forecast if h['heat_stress_level'] == 'high_risk'])
    moderate_hours = len([h for h in hourly_forecast if h['heat_stress_level'] == 'moderate_risk'])
    
    return jsonify({
        'location': location,
        'forecast_period': f"{hours} hours",
        'generated_at': forecast[0]['timestamp'] if forecast else None,
        'hourly_forecast': hourly_forecast,
        'summary': {
            'peak_wbgt': max(wbgt_values) if wbgt_values else 0,
            'extreme_risk_hours': extreme_hours,
            'high_risk_hours': high_hours,
            'moderate_risk_hours': moderate_hours
        },
        'language': language
    })

@app.route('/api/v1/alerts/active')
def active_alerts():
    """Get active alerts"""
    country = request.args.get('country', 'SA')
    severity = request.args.get('severity', 'high')
    
    alerts = alert_manager.get_active_alerts(country, severity)
    
    return jsonify({
        'country': country,
        'severity': severity,
        'alerts': alerts,
        'count': len(alerts)
    })

@app.route('/api/v1/alerts/subscribe', methods=['POST'])
def subscribe_alerts():
    """Subscribe to alerts"""
    data = request.json
    
    subscription = alert_manager.subscribe(
        location=data.get('location'),
        language=data.get('language', 'en'),
        alert_types=data.get('alert_types', ['heat_stress', 'uv']),
        notification_method=data.get('notification_method', 'sms'),
        contact=data.get('contact')
    )
    
    return jsonify({
        'status': 'subscribed',
        'subscription_id': subscription['id'],
        'subscription': subscription
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
