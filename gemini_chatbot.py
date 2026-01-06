"""
Gemini AI Chatbot Integration for Smart Energy Platform

This module provides enhanced chatbot functionality using Google's Gemini API.
Replace the simple chatbot endpoint in app.py with this implementation.

Setup:
1. Install: pip install google-generativeai
2. Get API key from: https://makersuite.google.com/app/apikey
3. Set environment variable: GEMINI_API_KEY=your_api_key_here
"""

import google.generativeai as genai
import os
import json

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
genai.configure(api_key=GEMINI_API_KEY)

# Initialize model
model = genai.GenerativeModel('gemini-pro')

# System context for the chatbot
SYSTEM_CONTEXT = """You are an AI Energy Assistant for the Smart Energy Analysis platform. 
Your role is to help users predict their energy consumption by collecting necessary information.

**Your Capabilities:**
1. Greet users warmly and explain your purpose
2. Ask for energy prediction parameters one by one:
   - Temperature (in Celsius)
   - Humidity (percentage)
   - Square Footage (of the building)
   - Occupancy (number of people)
   - Renewable Energy generation (in kWh)
   - HVAC Usage (On/Off)
   - Lighting Usage (On/Off)
   - Holiday status (Yes/No)
   - Date and Time

3. Answer questions about:
   - How the platform works
   - What each parameter means
   - Energy saving tips
   - The machine learning model used
   - How to interpret results

**Important Guidelines:**
- Be friendly, helpful, and conversational
- If users ask off-topic questions, politely redirect them to energy-related topics
- When you have all parameters, confirm them and indicate you're ready to make a prediction
- Provide energy-saving tips when appropriate
- Keep responses concise but informative (2-4 sentences)

**Do NOT:**
- Discuss topics unrelated to energy, buildings, or sustainability
- Provide medical, legal, or financial advice
- Make up information about the platform's capabilities
- Process personal or sensitive information beyond what's needed for predictions

Current conversation context will be provided with each message."""

class GeminiChatbot:
    def __init__(self):
        self.conversation_history = {}
        self.user_data = {}
    
    def get_response(self, user_id, message):
        """
        Get chatbot response using Gemini API
        
        Args:
            user_id: Unique identifier for the user session
            message: User's message
            
        Returns:
            dict: Response containing bot message and any collected data
        """
        # Initialize user history if new
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
            self.user_data[user_id] = {}
        
        # Add user message to history
        self.conversation_history[user_id].append({
            'role': 'user',
            'content': message
        })
        
        # Build prompt with context
        conversation_context = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}" 
            for msg in self.conversation_history[user_id][-5:]  # Last 5 messages
        ])
        
        collected_data = self.user_data[user_id]
        data_status = f"\n\nCurrently collected data: {json.dumps(collected_data, indent=2)}" if collected_data else ""
        
        prompt = f"""{SYSTEM_CONTEXT}

Recent conversation:
{conversation_context}
{data_status}

Respond to the user's latest message. Be helpful and guide them through the prediction process."""

        try:
            # Generate response
            response = model.generate_content(prompt)
            bot_message = response.text
            
            # Add bot response to history
            self.conversation_history[user_id].append({
                'role': 'assistant',
                'content': bot_message
            })
            
            # Try to extract data from user message (simple keyword matching)
            self._extract_data_from_message(user_id, message)
            
            return {
                'response': bot_message,
                'collected_data': self.user_data[user_id],
                'data_complete': self._is_data_complete(user_id)
            }
            
        except Exception as e:
            return {
                'response': f"I apologize, but I encountered an error. Please try again. ({str(e)})",
                'collected_data': self.user_data[user_id],
                'data_complete': False
            }
    
    def _extract_data_from_message(self, user_id, message):
        """Extract prediction parameters from user message"""
        message_lower = message.lower()
        
        # Temperature
        if 'temperature' in message_lower or '°c' in message_lower or 'degrees' in message_lower:
            import re
            temp_match = re.search(r'(\d+\.?\d*)\s*(?:°c|degrees|celsius)?', message_lower)
            if temp_match:
                self.user_data[user_id]['Temperature'] = float(temp_match.group(1))
        
        # Humidity
        if 'humidity' in message_lower or '%' in message_lower:
            import re
            humidity_match = re.search(r'(\d+\.?\d*)\s*%?', message_lower)
            if humidity_match:
                self.user_data[user_id]['Humidity'] = float(humidity_match.group(1))
        
        # Square Footage
        if 'square' in message_lower or 'sq ft' in message_lower or 'sqft' in message_lower:
            import re
            sqft_match = re.search(r'(\d+)', message_lower)
            if sqft_match:
                self.user_data[user_id]['SquareFootage'] = int(sqft_match.group(1))
        
        # Occupancy
        if 'people' in message_lower or 'person' in message_lower or 'occupancy' in message_lower:
            import re
            occ_match = re.search(r'(\d+)\s*(?:people|person)?', message_lower)
            if occ_match:
                self.user_data[user_id]['Occupancy'] = int(occ_match.group(1))
        
        # HVAC
        if 'hvac' in message_lower or 'air conditioning' in message_lower or 'ac' in message_lower:
            if 'on' in message_lower:
                self.user_data[user_id]['HVACUsage'] = 'On'
            elif 'off' in message_lower:
                self.user_data[user_id]['HVACUsage'] = 'Off'
        
        # Lighting
        if 'light' in message_lower:
            if 'on' in message_lower:
                self.user_data[user_id]['LightingUsage'] = 'On'
            elif 'off' in message_lower:
                self.user_data[user_id]['LightingUsage'] = 'Off'
    
    def _is_data_complete(self, user_id):
        """Check if all required parameters are collected"""
        required_fields = [
            'Temperature', 'Humidity', 'SquareFootage', 'Occupancy',
            'RenewableEnergy', 'HVACUsage', 'LightingUsage', 'Holiday'
        ]
        return all(field in self.user_data[user_id] for field in required_fields)
    
    def clear_session(self, user_id):
        """Clear conversation history and data for a user"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
        if user_id in self.user_data:
            del self.user_data[user_id]


# Flask route implementation
"""
Add this to your app.py:

from gemini_chatbot import GeminiChatbot

chatbot = GeminiChatbot()

@app.route('/api/chatbot', methods=['POST'])
def chatbot_endpoint():
    data = request.json
    message = data.get('message', '')
    user_id = data.get('user_id', 'default_user')  # In production, use session ID
    
    result = chatbot.get_response(user_id, message)
    
    # If data is complete, make prediction
    if result['data_complete']:
        prediction_data = result['collected_data']
        prediction_data['timestamp'] = datetime.now().strftime('%Y-%m-%dT%H:%M')
        
        try:
            features_df = create_features(prediction_data)
            prediction = model.predict(features_df)[0]
            
            result['response'] += f"\n\n✨ Based on the information you provided, I predict your energy consumption will be approximately **{prediction:.2f} kWh**. Would you like me to explain this result or provide energy-saving recommendations?"
            result['prediction'] = prediction
        except Exception as e:
            result['response'] += f"\n\nI have all the information, but encountered an error making the prediction. Please check your inputs."
    
    return jsonify(result)
"""

# Example usage
if __name__ == '__main__':
    chatbot = GeminiChatbot()
    
    print("Smart Energy Chatbot Test")
    print("-" * 50)
    
    user_id = "test_user"
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break
        
        response = chatbot.get_response(user_id, user_input)
        print(f"Bot: {response['response']}")
        
        if response['collected_data']:
            print(f"\nCollected Data: {json.dumps(response['collected_data'], indent=2)}")
        
        if response['data_complete']:
            print("\n✅ All data collected! Ready for prediction.")
        
        print()
