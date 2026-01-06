# ⚡ Quick Start Guide - Smart Energy Platform

## 🎯 Get Started in 3 Minutes!

### Prerequisites
- Python 3.8+ installed
- Your trained `model.pkl` file

### Option 1: Automated Setup (Recommended)

**Windows:**
```cmd
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

That's it! Open your browser to `http://localhost:5000`

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

Access at: `http://localhost:5000`

---

## 🎨 What You Get

### ✨ **8 Amazing Tabs**

1. **🏠 Home** - Beautiful animated hero section
2. **📊 Prediction** - Enter data, get predictions instantly
3. **🤖 AI Chat** - Conversational AI assistant (Gemini ready)
4. **📈 Dashboard** - 4 interactive charts with analytics
5. **ℹ️ About** - Project info and tech stack
6. **📖 Guide** - Step-by-step user instructions
7. **🔌 API** - REST API documentation
8. **⭐ Reviews** - User feedback system

### 🎯 **Key Features**

✅ Modern, responsive UI with animations
✅ Dark theme with cyan/purple gradients
✅ Waving robot assistant in corner
✅ Real-time predictions with ML model
✅ Interactive Chart.js visualizations
✅ Form validation and error handling
✅ Review system with star ratings
✅ API endpoints for integration
✅ Mobile-friendly design

---

## 🚀 Using the Platform

### Make a Prediction

1. Click **Prediction** tab
2. Fill in the form:
   - Date/Time
   - Temperature (°C)
   - Humidity (%)
   - Square Footage
   - Occupancy (1-10)
   - Renewable Energy (kWh)
   - HVAC: On/Off
   - Lighting: On/Off
   - Holiday: Yes/No
3. Click **Predict**
4. Get instant results with recommendations!

### Use AI Chatbot

1. Click **AI Chat** tab
2. Type your message
3. Chat naturally - the bot will guide you
4. *Note:* Currently uses rule-based responses
5. **To enable Gemini AI:**
   - Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Edit `.env` file with your key
   - Follow instructions in `gemini_chatbot.py`

### View Analytics

1. Click **Dashboard** tab
2. See 4 interactive charts:
   - Energy trend over time
   - Device breakdown (pie chart)
   - Temperature vs Energy correlation
   - Occupancy impact analysis

---

## 🔧 Configuration

### Enable Gemini AI Chatbot

```bash
# 1. Install Gemini SDK
pip install google-generativeai

# 2. Get API key from:
https://makersuite.google.com/app/apikey

# 3. Set in .env file
GEMINI_API_KEY=your_api_key_here

# 4. Update app.py
# Replace chatbot endpoint with code from gemini_chatbot.py
```

### Customize Colors

Edit `templates/index.html` CSS variables:
```css
:root {
    --primary: #00f0ff;     /* Change main color */
    --secondary: #ff006e;   /* Change accent */
    --accent: #8338ec;      /* Change tertiary */
}
```

### Update Model

Replace `model.pkl` with your newly trained model. Ensure:
- Same feature names
- Same feature order
- Same preprocessing steps

---

## 📱 Testing Checklist

- [ ] Home page loads with animations
- [ ] All tabs switch correctly
- [ ] Prediction form accepts input
- [ ] Results display after submission
- [ ] Chatbot responds to messages
- [ ] Dashboard charts render
- [ ] Reviews can be submitted
- [ ] API documentation visible
- [ ] Robot assistant appears in corner
- [ ] Mobile view works properly

---

## 🐛 Common Issues

### Port Already in Use
```python
# In app.py, change:
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Model Not Found
- Ensure `model.pkl` is in the same directory as `app.py`
- Check file name matches exactly

### Charts Not Showing
- Wait a moment for them to load
- Check browser console for errors
- Verify Chart.js CDN is accessible

### Virtual Environment Issues
```bash
# Delete and recreate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🎯 Next Steps

### Enhance Your Platform

1. **Add Database**: Store predictions and user data
2. **User Authentication**: Add login/signup
3. **Real-time Updates**: WebSocket for live data
4. **Export Features**: Download predictions as CSV/PDF
5. **Email Notifications**: Alert on high usage
6. **Mobile App**: React Native version
7. **Advanced Analytics**: More ML insights

### Integrate Gemini AI

Follow the detailed guide in `gemini_chatbot.py` to enable:
- Natural language understanding
- Context-aware responses
- Automatic data extraction
- Intelligent recommendations

### Deploy to Production

See `DEPLOYMENT.md` for:
- Heroku deployment
- AWS EC2 setup
- Docker containerization
- Security best practices

---

## 📞 Need Help?

1. Check `README.md` for detailed docs
2. See `DEPLOYMENT.md` for deployment
3. Review `gemini_chatbot.py` for AI integration
4. Check Flask logs for errors

---

## 🎉 You're All Set!

Your Smart Energy Platform is ready to go!

**Access it at:** `http://localhost:5000`

**Enjoy predicting and optimizing energy! ⚡🌱**

---

## 📊 Project Structure

```
smart_energy_app/
│
├── app.py                    # Main Flask application
├── model.pkl                 # Your trained ML model
├── gemini_chatbot.py         # Enhanced AI chatbot
├── requirements.txt          # Python dependencies
├── reviews.json             # User reviews storage
│
├── templates/
│   └── index.html           # Frontend UI (all tabs)
│
├── README.md                # Full documentation
├── DEPLOYMENT.md            # Deployment guide
├── QUICKSTART.md           # This file
├── .env.example            # Environment config template
│
├── start.sh                # Linux/Mac startup script
└── start.bat               # Windows startup script
```

---

**Built with ❤️ for Smart Energy Management**

**Happy Energy Saving! ⚡💚**
