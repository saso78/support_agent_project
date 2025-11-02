# Call QA Tool - Quick Demo Guide

## 🚀 Quick Start for Demo

### Step 1: Set up demo data (one time)
```powershell
python demo_call_qa_setup.py
```

This creates 3 sample calls with different quality levels:
- Excellent call (high scores)
- Average call (medium scores)  
- Poor call (low scores)

### Step 2: Launch the dashboard
```powershell
python -m streamlit run streamlit_pages/call_qa_dashboard.py
```

### Step 3: Open in browser
- The dashboard will automatically open at: **http://localhost:8501**
- Or manually navigate to that URL

---

## 📊 What You'll See

### Call History Tab (Default)
- Table of all calls with scores
- Filter by status, date, phone number
- Click "View Call Details" to see full transcript

### Make Test Call Tab
- Create new test calls
- Select scenario (cancel_subscription)
- Use mock mode (no real API calls)

### Agent Performance Tab
- View agent statistics
- Performance rankings

### Analytics Tab
- Score trends over time
- Charts showing performance metrics

---

## 🎯 Demo Workflow

1. **View existing calls:**
   - Go to "Call History"
   - See the 3 sample calls with different scores
   - Click any call ID to see detailed evaluation

2. **Create a new call:**
   - Go to "Make Test Call"
   - Enter agent name and phone
   - Select scenario: `cancel_subscription`
   - Keep "Use Mock APIs" checked
   - Click "Make Test Call"

3. **Check scores:**
   - Each call has 5 metrics:
     - **Greeting** (0-10)
     - **Hold Time** (0-10)
     - **Resolution** (0-10)
     - **Tone/Empathy** (0-10)
     - **Script Compliance** (0-10)
   - Plus an overall **Total Score**

---

## 🔧 Alternative: Command Line Demo

If you prefer command line:
```powershell
python scripts/quick_demo.py
```

This creates one call and shows results in terminal.

---

## 📝 Notes

- **Mock Mode**: All calls use mock APIs (no real Twilio/Deepgram calls)
- **Database**: Data is saved in `data/call_logs/call_qa.db`
- **API Keys**: Only OpenRouter API key needed for evaluation (LLM scoring)
- **Cost**: $0.00 in mock mode (no real API calls)

---

## 🛠️ Troubleshooting

**Dashboard won't start?**
- Make sure you're in the project root directory
- Use: `python -m streamlit run streamlit_pages/call_qa_dashboard.py`

**No data showing?**
- Run `python demo_call_qa_setup.py` first to create sample data

**Port 8501 already in use?**
- Stop any existing Streamlit instance
- Or use: `python -m streamlit run streamlit_pages/call_qa_dashboard.py --server.port 8502`

---

## ✅ Success Criteria

You should see:
- ✅ Dashboard loads at http://localhost:8501
- ✅ 3+ calls in Call History
- ✅ Each call has scores displayed
- ✅ Can view detailed transcript for each call
- ✅ Can create new test calls

Enjoy your demo! 🎉

