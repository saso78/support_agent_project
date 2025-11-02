# Streamlit Cloud Deployment Guide

## Deployment Options

You have **two options** for deploying to Streamlit Cloud:

### Option 1: Call QA Tool Only (Recommended for Demo)

**Entry Point:** `app_call_qa.py`

**Deploy Steps:**
1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click "New app"
3. Connect your GitHub repository
4. Set configuration:
   - **Main file path:** `app_call_qa.py`
   - **Python version:** 3.11 or 3.12
5. Add secrets in Streamlit Cloud:
   - `OPENROUTER_API_KEY` (required for evaluation)
   - `USE_MOCK_APIS=true` (optional, for mock mode)
   - Other API keys only if `USE_MOCK_APIS=false`

**Command to run locally:**
```bash
streamlit run app_call_qa.py
```

---

### Option 2: Combined App (Support Agent + Call QA)

**Entry Point:** `app_main.py`

**Deploy Steps:**
1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click "New app"
3. Connect your GitHub repository
4. Set configuration:
   - **Main file path:** `app_main.py`
   - **Python version:** 3.11 or 3.12
5. Add secrets (same as Option 1)

**Command to run locally:**
```bash
streamlit run app_main.py
```

---

## Streamlit Cloud Secrets

Add these in Streamlit Cloud dashboard → App settings → Secrets:

### Required (for Call QA evaluation):
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Optional (for mock mode, no costs):
```
USE_MOCK_APIS=true
```

### Optional (only if USE_MOCK_APIS=false):
```
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1234567890
ELEVENLABS_API_KEY=xxx
DEEPGRAM_API_KEY=xxx
```

---

## Local Testing

Test the entry points locally before deploying:

```bash
# Test Call QA Tool only
python -m streamlit run app_call_qa.py

# Test combined app
python -m streamlit run app_main.py

# Or test individual components
python -m streamlit run streamlit_pages/call_qa_dashboard.py
python -m streamlit run web/app.py
```

---

## File Structure

```
support_agent_project/
├── app_call_qa.py          # ← Entry point for Call QA Tool only
├── app_main.py             # ← Entry point for combined app
├── web/
│   └── app.py             # ← Support Agent app
├── streamlit_pages/
│   └── call_qa_dashboard.py  # ← Call QA dashboard
└── .streamlit/
    └── config.toml        # ← Streamlit configuration
```

---

## Recommended Setup

For **Streamlit Cloud deployment**, use:

**Main file:** `app_call_qa.py`

This provides:
- ✅ Clean, focused Call QA Tool
- ✅ Easy to share with stakeholders
- ✅ Separate from Support Agent app
- ✅ Perfect for demos

---

## Troubleshooting

**Issue:** App won't start on Streamlit Cloud
- ✅ Make sure `app_call_qa.py` exists in root directory
- ✅ Check that all imports are correct
- ✅ Verify secrets are added correctly

**Issue:** Database errors
- ✅ SQLite will create `data/call_logs/call_qa.db` automatically
- ✅ Make sure `data/` directory structure exists

**Issue:** Import errors
- ✅ Ensure all dependencies are in `requirements.txt`
- ✅ Check that project root is in Python path

---

## Quick Deploy Checklist

- [ ] Push code to GitHub (feature/call-qa-tool branch)
- [ ] Create Streamlit Cloud account
- [ ] New app → Connect repository
- [ ] Set main file: `app_call_qa.py`
- [ ] Add `OPENROUTER_API_KEY` secret
- [ ] Add `USE_MOCK_APIS=true` secret (optional)
- [ ] Deploy!

Once deployed, your Call QA Tool will be available at:
`https://your-app-name.streamlit.app`

