# Call Center QA Tool - Architecture Documentation

## Overview

The Call Center QA Tool is a new feature that extends the existing Support Agent SaaS with automated call center quality assurance capabilities. It makes outbound test calls to support agents, transcribes conversations, scores performance, and generates QA reports.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit Dashboard                        │
│                  (web/app.py + streamlit_pages/)                  │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Call QA Orchestration Layer                    │
│                    (agents/call_qa_agent.py)                     │
│  • Manages call workflow                                         │
│  • Coordinates voice, transcription, and evaluation              │
│  • Generates QA reports                                          │
└───────┬───────────────────┬───────────────────┬──────────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐  ┌─────────────────┐  ┌──────────────────┐
│ Voice Engine │  │ Transcription   │  │ Evaluation       │
│ (voice.py)   │  │ (transcription. │  │ (extends qa_     │
│              │  │      py)        │  │  evaluator.py)   │
│ • Twilio API │  │                 │  │                  │
│ • Call mgmt  │  │ • Deepgram API  │  │ • Scoring        │
│ • Recording  │  │ • Diarization    │  │ • Rubric logic   │
│ • TTS (11L)  │  │ • Timestamps    │  │ • Recommendations│
└──────┬───────┘  └────────┬────────┘  └────────┬─────────┘
       │                   │                    │
       └───────────────────┴────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   SQLite Database      │
              │   (core/database.py)   │
              │                        │
              │  • calls               │
              │  • transcripts         │
              │  • scores              │
              │  • agents              │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Existing Components  │
              │                        │
              │  • core/llm.py         │
              │  • core/config.py      │
              │  • core/memory.py      │
              └────────────────────────┘
```

## Component Integration

### 1. Extension of Existing Codebase

The Call QA Tool integrates seamlessly with existing components:

#### **core/config.py** (UPDATE)
- **New Settings:**
  - `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
  - `ELEVENLABS_API_KEY`, `DEEPGRAM_API_KEY`
  - `USE_MOCK_APIS` (for testing without costs)
  - Call timeout and duration limits

- **Pattern:** Uses existing `get_secret()` function for both env vars and Streamlit secrets

#### **agents/call_qa_agent.py** (NEW)
- **Inherits from:** `agents/base_agent.py`
- **Uses:** `core/llm.py` (OpenRouterLLM) for evaluation logic
- **Extends:** `agents/qa_evaluator.py` patterns for scoring
- **Integrates with:** `core/database.py` for storing results

#### **Streamlit Integration**
- **Location:** `streamlit_pages/call_qa_dashboard.py` (NEW)
- **Pattern:** Follows `web/app.py` structure
- **Uses:** Same session state initialization pattern
- **Access:** Can be added as a Streamlit page or standalone app

### 2. New Core Components

#### **core/models.py** (NEW)
SQLAlchemy ORM models for:
- `Call` - Call metadata (phone, duration, status, cost)
- `Transcript` - Speaker-segmented transcript with timestamps
- `Score` - Evaluation scores (greeting, hold_time, resolution, tone, compliance)
- `Agent` - Agent profile with performance metrics

#### **core/database.py** (NEW)
- Database initialization
- CRUD operations for all models
- Query helpers (get agent stats, filter calls, etc.)
- Uses SQLAlchemy (already in requirements.txt)

#### **core/voice.py** (NEW)
- Twilio integration for outbound calls
- ElevenLabs TTS for customer voice
- Call state management (dialing → in-progress → completed)
- Recording and storage
- Mock mode support

#### **core/transcription.py** (NEW)
- Deepgram real-time transcription
- Speaker diarization (agent vs. customer)
- Confidence scoring
- Timestamp tracking
- Mock mode support

### 3. Data Flow

```
1. USER INITIATES CALL (via CLI or Dashboard)
   │
   ├─► Select scenario (cancel_subscription.json)
   ├─► Provide agent phone number
   └─► Click "Make Test Call"
   
2. CALL ORCHESTRATION (call_qa_agent.py)
   │
   ├─► Load scenario from data/call_scenarios/
   ├─► Initialize voice engine (core/voice.py)
   └─► Initialize transcription (core/transcription.py)
   
3. CALL EXECUTION
   │
   ├─► voice.py: Dial Twilio outbound call
   ├─► voice.py: Generate customer voice via ElevenLabs TTS
   ├─► transcription.py: Start Deepgram real-time transcription
   ├─► Real-time: Both sides speak (agent + AI customer)
   └─► Call ends (agent hangs up or timeout)
   
4. POST-CALL PROCESSING
   │
   ├─► transcription.py: Process final transcript
   ├─► transcription.py: Segment by speaker (agent/customer)
   ├─► Save call record to database (calls table)
   └─► Save transcript segments (transcripts table)
   
5. EVALUATION (call_qa_agent.py)
   │
   ├─► Load transcript from database
   ├─► Score on 5 metrics (greeting, hold_time, resolution, tone, compliance)
   ├─► Use OpenRouterLLM for sentiment/tone analysis
   ├─► Generate recommendations
   └─► Save scores to database (scores table)
   
6. REPORTING (streamlit_pages/call_qa_dashboard.py)
   │
   ├─► Query database for call history
   ├─► Display scores, trends, rankings
   └─► Export to CSV/PDF
```

## Data Models

### Database Schema (SQLite)

```sql
-- Calls Table
CREATE TABLE calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT NOT NULL,
    duration INTEGER,  -- seconds
    status TEXT,      -- 'completed', 'failed', 'timeout'
    cost REAL,        -- estimated cost in USD
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    scenario_id TEXT, -- foreign key to scenario
    recording_path TEXT
);

-- Transcripts Table
CREATE TABLE transcripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id INTEGER NOT NULL,
    speaker TEXT,     -- 'agent' or 'customer'
    text TEXT,
    timestamp REAL,   -- seconds from call start
    confidence REAL,  -- 0.0-1.0
    FOREIGN KEY (call_id) REFERENCES calls(id)
);

-- Scores Table
CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    call_id INTEGER NOT NULL UNIQUE,
    greeting REAL,      -- 0-10
    hold_time REAL,     -- 0-10
    resolution REAL,    -- 0-10
    tone REAL,         -- 0-10
    compliance REAL,    -- 0-10
    total REAL,        -- weighted average
    recommendations TEXT,  -- JSON array of strings
    FOREIGN KEY (call_id) REFERENCES calls(id)
);

-- Agents Table
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone_number TEXT NOT NULL UNIQUE,
    average_score REAL,
    total_calls INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## API Integration Details

### Twilio Voice API
- **Endpoint:** Twilio Programmable Voice
- **Method:** Outbound calls via `Call.create()`
- **Features:** Call recording, status callbacks
- **Cost:** $0.013/minute
- **Mock:** Return fake call SID, simulate states

### ElevenLabs Text-to-Speech
- **Endpoint:** `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
- **Voice ID:** Default `21m00Tcm4TlvDq8ikWAM` (Rachel)
- **Cost:** $0.30 per 1,000 characters
- **Mock:** Generate dummy audio file or skip TTS

### Deepgram Speech-to-Text
- **Endpoint:** Deepgram Real-Time API (WebSocket)
- **Features:** Real-time transcription, speaker diarization
- **Cost:** $0.0043/minute
- **Mock:** Return pre-defined transcript JSON

### OpenRouter (Existing)
- **Usage:** Evaluation scoring, sentiment analysis
- **Already configured:** No changes needed
- **Reused for:** Tone analysis, recommendation generation

## Integration Points & Potential Conflicts

### ✅ No Conflicts Expected

1. **Config Management:**
   - New settings added to `core/config.py`
   - Uses existing `get_secret()` pattern
   - No breaking changes to existing config

2. **Agent Base Class:**
   - `call_qa_agent.py` inherits from `base_agent.py`
   - Doesn't override core methods that other agents use
   - Separate `process_message()` implementation

3. **Database:**
   - New SQLite database (`data/call_qa.db`)
   - Separate from existing ChromaDB (`data/rag_db/`)
   - No schema conflicts

4. **Dependencies:**
   - SQLAlchemy already in `requirements.txt` (v2.0.43)
   - New packages: `twilio`, `elevenlabs`, `deepgram-sdk`, `pydub`
   - No version conflicts expected

5. **File Structure:**
   - New directories: `data/call_scenarios/`, `data/call_logs/`
   - New files don't conflict with existing ones
   - Dashboard can be added as Streamlit page or separate app

### ⚠️ Considerations

1. **Streamlit Pages:**
   - Current app is `web/app.py` (single-file app)
   - Option A: Create `streamlit_pages/` directory for multi-page app
   - Option B: Add dashboard as separate route in `web/app.py`
   - **Recommendation:** Use `streamlit_pages/` for cleaner separation

2. **Environment Variables:**
   - New API keys needed in `.env` and Streamlit secrets
   - Document in `.env.example`
   - Use `USE_MOCK_APIS=true` for development

3. **Error Handling:**
   - Follow existing patterns (try/except with logging)
   - No print statements (use `logging` module)
   - Graceful degradation if APIs fail

4. **Cost Tracking:**
   - Track estimated costs per call
   - Store in database for reporting
   - Alert if exceeding budget

## Security & Compliance

### Data Privacy
- Phone numbers sanitized in logs (show only last 4 digits)
- Call recordings stored securely in `data/call_logs/`
- Database encrypted at rest (SQLite encryption if needed)

### API Key Security
- All keys in environment variables (never hardcoded)
- Use `get_secret()` for Streamlit Cloud compatibility
- Never log full API keys

### Call Recording Compliance
- Add consent message at start of call
- Store consent flag in database
- Comply with local call recording laws

## Testing Strategy

### Mock Mode (`USE_MOCK_APIS=true`)
- **Voice:** Simulate call states without real Twilio calls
- **TTS:** Skip ElevenLabs, use text-only mode or dummy audio
- **STT:** Return pre-defined transcript JSON
- **Cost:** $0.00 during development

### Test Coverage Goals
- Unit tests for each component (80%+ coverage)
- Integration tests for full call workflow
- Edge cases: failed calls, poor audio, low scores
- Database tests for all CRUD operations

## Deployment Considerations

### Development
- Use mock mode (`USE_MOCK_APIS=true`)
- Test locally with SQLite database
- Run tests before committing

### Staging
- Optional: Real API testing with small budget
- Monitor costs closely
- Test with actual phone calls

### Production
- Real API calls enabled
- Cost tracking and alerts
- Database backups
- Call recording retention policy

## Performance Considerations

### Call Duration
- Max call duration: 5 minutes (300 seconds)
- Timeout: 30 seconds if no answer
- Handle dropped calls gracefully

### Database Performance
- SQLite suitable for MVP (single-user/small team)
- Add indexes on frequently queried fields (call_id, timestamp)
- Consider PostgreSQL for production scale

### API Rate Limits
- Twilio: No hard limits on outbound calls
- ElevenLabs: Check rate limits in docs
- Deepgram: Pay-as-you-go, no limits
- OpenRouter: Already handled in existing code

## Next Steps

After architecture approval, proceed to:
1. **Phase 2:** Generate all code files
2. **Phase 3:** Create test suite
3. **Phase 4:** Documentation

## Questions & Decisions Needed

1. **Streamlit Pages Structure:**
   - Create `streamlit_pages/` directory?
   - Or integrate dashboard into existing `web/app.py`?

2. **Database Location:**
   - Confirm `data/call_qa.db` is acceptable
   - Or prefer different path?

3. **Call Recording:**
   - Store audio files in `data/call_logs/`?
   - Or use Twilio recording URLs only?

4. **Scenario Management:**
   - JSON files in `data/call_scenarios/` sufficient?
   - Or need database-backed scenarios?

---

**Architecture Status:** ✅ Ready for implementation  
**Last Updated:** Initial version  
**Reviewer Approval:** Pending

