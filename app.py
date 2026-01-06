from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

# Try to import CORS, but don't fail if not available
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    print("⚠️  flask-cors not installed - CORS disabled")

import pickle
import numpy as np
import pandas as pd
import json
from datetime import datetime

# Import Gemini AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai not installed - Chatbot will use fallback")

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS if available
if CORS_AVAILABLE:
    from flask_cors import CORS
    CORS(app)
    print("✓ CORS enabled")

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_AVAILABLE and GEMINI_API_KEY and GEMINI_API_KEY != 'your_gemini_api_key_here':
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    # List of models to try in order
        model_names = [
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro-latest', 
            'gemini-pro'
        ]
    
        gemini_model = None
        for model_name in model_names:
            try:
                gemini_model = genai.GenerativeModel(model_name)
                print(f"✓ Gemini AI configured with model: {model_name}")
                GEMINI_READY = True
                break
            except:
                continue
    
        if gemini_model is None:
            print("⚠️ Could not initialize Gemini model")
            GEMINI_READY = False
    except Exception as e:
        print(f"⚠️  Gemini configuration failed: {e}")
        GEMINI_READY = False
else:
    print("⚠️  Gemini API key not found - using fallback chatbot")
    GEMINI_READY = False

# Load ML model with error handling
model = None
try:
    with open('randomforest_energy_model.pkl', 'rb') as f:
        loaded_data = pickle.load(f)
    
    if hasattr(loaded_data, 'predict'):
        model = loaded_data
        print("✓ ML Model loaded successfully!")
    else:
        print(f"⚠️  model.pkl contains {type(loaded_data)}, not a trained model")
        print("   Using fallback prediction formula")
except FileNotFoundError:
    print("⚠️  model.pkl not found - using fallback prediction formula")
except Exception as e:
    print(f"⚠️  Error loading model: {e}")
    print("   Using fallback prediction formula")

def create_features(input_data):
    """
    Create features matching the Random Forest training data
    
    REQUIRED FEATURES (21 features in exact order):
    1. Temperature
    2. Humidity
    3. Occupancy
    4. HVACUsage
    5. LightingUsage
    6. Thermal_Energy_Load
    7. Occupancy_Energy_Load
    8. Environmental_Stress_Level
    9. High_Temp_Regime
    10. High_Occupancy_Regime
    11. HVAC_On_Peak
    12. Temp_Bucket
    13. Recent_Consumption_Level
    14. Load_Consistency
    15. Daily_Usage_Sin
    16. Daily_Usage_Cos
    17. Load_Change_1H
    18. HVAC_Stress
    19. Lighting_Demand_Intensity
    20. Is_Peak_Hour
    21. Short_Term_Trend
    """
    
    # Parse timestamp
    timestamp = datetime.strptime(input_data['timestamp'], '%Y-%m-%dT%H:%M')
    hour = timestamp.hour
    
    # Base features
    temperature = input_data['Temperature']
    humidity = input_data['Humidity']
    occupancy = input_data['Occupancy']
    hvac_usage = 1 if input_data['HVACUsage'] == 'On' else 0
    lighting_usage = 1 if input_data['LightingUsage'] == 'On' else 0
    
    # Engineered features
    # 6. Thermal_Energy_Load - Energy needed for temperature control
    thermal_energy_load = temperature * hvac_usage * 1.5
    
    # 7. Occupancy_Energy_Load - Energy from people
    occupancy_energy_load = occupancy * 3.0
    
    # 8. Environmental_Stress_Level - Combined environmental stress
    environmental_stress_level = (temperature * humidity) / 100.0
    
    # 9. High_Temp_Regime - Binary indicator for high temperature
    high_temp_regime = 1 if temperature > 25 else 0
    
    # 10. High_Occupancy_Regime - Binary indicator for high occupancy
    high_occupancy_regime = 1 if occupancy >= 5 else 0
    
    # 11. HVAC_On_Peak - HVAC during peak hours
    is_peak_hour = 1 if 18 <= hour <= 22 else 0
    hvac_on_peak = hvac_usage * is_peak_hour
    
    # 12. Temp_Bucket - Temperature category (0: low, 1: medium, 2: high)
    if temperature < 20:
        temp_bucket = 0
    elif temperature < 25:
        temp_bucket = 1
    else:
        temp_bucket = 2
    
    # 13. Recent_Consumption_Level - Estimated recent consumption
    recent_consumption_level = 50 + (temperature - 20) * 1.5 + occupancy * 3
    
    # 14. Load_Consistency - Measure of consistent load
    load_consistency = 0.8  # Default consistency score
    
    # 15 & 16. Daily_Usage_Sin & Daily_Usage_Cos - Cyclical time encoding
    daily_usage_sin = np.sin(2 * np.pi * hour / 24)
    daily_usage_cos = np.cos(2 * np.pi * hour / 24)
    
    # 17. Load_Change_1H - Rate of load change
    load_change_1h = 0.0  # Default to no change
    
    # 18. HVAC_Stress - Stress on HVAC system
    hvac_stress = hvac_usage * (abs(temperature - 22) / 10.0)
    
    # 19. Lighting_Demand_Intensity - Lighting demand
    lighting_demand_intensity = lighting_usage * occupancy * 0.5
    
    # 20. Is_Peak_Hour - Already calculated above
    # is_peak_hour = 1 if 18 <= hour <= 22 else 0
    
    # 21. Short_Term_Trend - Trend indicator
    short_term_trend = 0.0  # Neutral trend
    
    # Create DataFrame with exact feature order
    features = pd.DataFrame([{
        'Temperature': temperature,
        'Humidity': humidity,
        'Occupancy': occupancy,
        'HVACUsage': hvac_usage,
        'LightingUsage': lighting_usage,
        'Thermal_Energy_Load': thermal_energy_load,
        'Occupancy_Energy_Load': occupancy_energy_load,
        'Environmental_Stress_Level': environmental_stress_level,
        'High_Temp_Regime': high_temp_regime,
        'High_Occupancy_Regime': high_occupancy_regime,
        'HVAC_On_Peak': hvac_on_peak,
        'Temp_Bucket': temp_bucket,
        'Recent_Consumption_Level': recent_consumption_level,
        'Load_Consistency': load_consistency,
        'Daily_Usage_Sin': daily_usage_sin,
        'Daily_Usage_Cos': daily_usage_cos,
        'Load_Change_1H': load_change_1h,
        'HVAC_Stress': hvac_stress,
        'Lighting_Demand_Intensity': lighting_demand_intensity,
        'Is_Peak_Hour': is_peak_hour,
        'Short_Term_Trend': short_term_trend
    }])
    
    return features

def fallback_prediction(data):
    """Simple formula-based prediction when model is unavailable"""
    base = 50.0
    temp_factor = (data['Temperature'] - 20) * 1.5
    occupancy_factor = data['Occupancy'] * 3
    sqft_factor = data['SquareFootage'] / 50
    hvac_factor = 20 if data['HVACUsage'] == 'On' else 0
    lighting_factor = 10 if data['LightingUsage'] == 'On' else 0
    renewable_offset = data['RenewableEnergy'] * -0.5
    holiday_factor = -5 if data['Holiday'] == 'Yes' else 0
    
    prediction = base + temp_factor + occupancy_factor + sqft_factor + hvac_factor + lighting_factor + renewable_offset + holiday_factor
    prediction = max(30, min(150, prediction))
    return float(prediction)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        print(f"Received prediction request: {data}")
        
        features_df = create_features(data)
        
        prediction = None
        
        if model is not None:
            try:
                prediction = float(model.predict(features_df)[0])
                print(f"✓ Model prediction: {prediction}")
            except Exception as e:
                print(f"Model prediction failed: {e}")
                prediction = None
        
        if prediction is None:
            prediction = fallback_prediction(data)
            print(f"Fallback prediction: {prediction}")
        
        is_high_usage = prediction > 80
        efficiency_score = max(0, min(100, 100 - (prediction - 50)))
        
        recommendations = []
        if data['Temperature'] > 25 and data['HVACUsage'] == 'On':
            recommendations.append("Consider raising thermostat by 2°C to reduce consumption")
        if data['Occupancy'] > 6 and data['LightingUsage'] == 'On':
            recommendations.append("Use natural lighting when possible")
        if prediction > 85:
            recommendations.append("Peak usage detected - consider load balancing")
        if data['RenewableEnergy'] < 5:
            recommendations.append("Increase renewable energy usage to reduce costs")
        
        response = {
            'success': True,
            'prediction': round(prediction, 2),
            'usage_level': 'High' if is_high_usage else 'Normal',
            'efficiency_score': round(efficiency_score, 1),
            'recommendations': recommendations,
            'peak_hour': int(features_df['Is_Peak_Hour'].iloc[0]) == 1,
            'comfort_index': round(float(features_df['Environmental_Stress_Level'].iloc[0]), 2)
        }
        
        print(f"Response: {response}")
        return jsonify(response)
    
    except Exception as e:
        print(f"ERROR in prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        }), 400

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        print(f"Chatbot received: {message}")
        
        if GEMINI_READY:
            # Use Gemini AI for intelligent responses
            try:
                # Create a context-aware prompt for energy domain
                system_context = """You are a friendly and helpful Smart Energy Assistant. 
Your role is to help users understand and optimize their energy consumption.

Key information:
- You can help predict energy consumption
- You provide tips for reducing energy usage
- You explain energy-related concepts
- You're knowledgeable about HVAC, lighting, renewable energy, and household appliances

Keep responses:
- Concise (2-3 sentences max)
- Friendly and conversational
- Focused on energy topics
- Helpful and actionable

If someone asks for predictions, tell them you can help collect their data step by step, or they can use the Prediction tab."""

                full_prompt = f"{system_context}\n\nUser: {message}\nAssistant:"
                
                response = gemini_model.generate_content(full_prompt)
                ai_response = response.text
                
                print(f"Gemini response: {ai_response}")
                
                return jsonify({
                    'response': ai_response,
                    'powered_by': 'gemini'
                })
                
            except Exception as e:
                print(f"Gemini error: {e}")
                # Fall back to simple responses if Gemini fails
                return fallback_chatbot_response(message)
        else:
            # Use fallback responses when Gemini not available
            return fallback_chatbot_response(message)
    
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        return jsonify({
            'response': f"Sorry, I encountered an error: {str(e)}"
        }), 400

def fallback_chatbot_response(message):
    """Simple rule-based chatbot when Gemini unavailable"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        response = "Hello! I'm your Smart Energy Assistant. I can help you predict energy consumption and provide optimization tips. How can I assist you today?"
    
    elif any(word in message_lower for word in ['predict', 'prediction', 'calculate', 'energy']):
        response = "I can help you predict energy consumption! You can either use the Prediction tab for quick results, or I can guide you through the data collection step by step. Would you like me to collect your data?"
    
    elif any(word in message_lower for word in ['how', 'what', 'explain']):
        response = "I analyze energy consumption based on factors like temperature, humidity, occupancy, HVAC usage, and more. I use machine learning to provide accurate predictions and personalized recommendations!"
    
    elif any(word in message_lower for word in ['reduce', 'save', 'optimize', 'tips']):
        response = "Here are quick energy-saving tips: 1) Raise thermostat by 2°C in summer, 2) Use natural lighting when possible, 3) Turn off devices when not in use, 4) Consider renewable energy sources. Want personalized recommendations? Use the Prediction tab!"
    
    elif any(word in message_lower for word in ['thank', 'thanks']):
        response = "You're welcome! Feel free to ask if you need anything else about energy optimization!"
    
    else:
        response = "I'm here to help with energy predictions and optimization! Try asking me about: predicting energy consumption, energy-saving tips, or how the system works. You can also use the Prediction tab for detailed analysis!"
    
    return jsonify({
        'response': response,
        'powered_by': 'fallback'
    })

@app.route('/api/submit-review', methods=['POST'])
def submit_review():
    try:
        data = request.json
        reviews_file = 'reviews.json'
        
        if os.path.exists(reviews_file):
            with open(reviews_file, 'r') as f:
                reviews = json.load(f)
        else:
            reviews = []
        
        review_entry = {
            'name': data.get('name', 'Anonymous'),
            'rating': data.get('rating', 5),
            'comment': data.get('comment', ''),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        reviews.append(review_entry)
        
        with open(reviews_file, 'w') as f:
            json.dump(reviews, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your review!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/get-reviews', methods=['GET'])
def get_reviews():
    try:
        reviews_file = 'reviews.json'
        if os.path.exists(reviews_file):
            with open(reviews_file, 'r') as f:
                reviews = json.load(f)
            return jsonify({
                'success': True,
                'reviews': reviews
            })
        else:
            return jsonify({
                'success': True,
                'reviews': []
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/charts-data', methods=['GET'])
def get_charts_data():
    """Provide sample data for dashboard charts"""
    return jsonify({
        'energy_trend': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'data': [75, 82, 78, 85, 88, 72, 70]
        },
        'device_breakdown': {
            'labels': ['HVAC', 'Lighting', 'Appliances', 'Others'],
            'data': [45, 20, 25, 10]
        },
        'temperature_correlation': {
            'temperature': [20, 22, 24, 26, 28, 30],
            'energy': [65, 70, 75, 82, 88, 95]
        },
        'occupancy_impact': {
            'occupancy': [1, 2, 3, 4, 5, 6, 7, 8],
            'energy': [60, 65, 68, 72, 76, 80, 84, 88]
        }
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Smart Energy Analysis Server")
    print("="*60)
    print(f"✓ Flask app initialized")
    print(f"✓ CORS: {'Enabled' if CORS_AVAILABLE else 'Disabled'}")
    print(f"✓ ML Model: {'Loaded' if model else 'Using fallback predictions'}")
    print(f"✓ Gemini AI: {'Ready' if GEMINI_READY else 'Using fallback chatbot'}")
    print(f"✓ Server starting on http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)