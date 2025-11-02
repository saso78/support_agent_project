# Git Workflow Guide - Call QA Tool

## Standard Git Flow

```
master (production)
  ↑
develop (development/integration)
  ↑
feature/call-qa-tool (your feature)
```

## Recommended Process

### Step 1: Push Feature Branch to Remote

```bash
# Push your feature branch to GitHub
git push origin feature/call-qa-tool
```

### Step 2: Create Pull Request to `develop`

1. Go to GitHub → Pull Requests
2. Click "New Pull Request"
3. **Base:** `develop`
4. **Compare:** `feature/call-qa-tool`
5. Add description:
   ```
   # Call Center QA Tool - Feature Implementation
   
   ## Summary
   Adds automated call testing and evaluation system.
   
   ## Features Added
   - Twilio integration for outbound calls
   - Deepgram transcription with speaker diarization
   - Five-metric scoring system (greeting, hold time, resolution, tone, compliance)
   - SQLite database for call logs and analytics
   - Streamlit dashboard for QA reporting
   - Mock mode for cost-free development
   
   ## Testing
   - ✅ 49 tests passing, 4 skipped (optional dependencies)
   - ✅ All core functionality tested
   - ✅ Mock mode working correctly
   
   ## Breaking Changes
   - None - this is a new feature, no existing functionality affected
   
   ## Deployment Notes
   - Entry point: `app_call_qa.py`
   - Requires: OPENROUTER_API_KEY
   - Optional: Twilio/ElevenLabs/Deepgram (if USE_MOCK_APIS=false)
   ```

6. Request review if working with a team
7. Merge to `develop` when approved

### Step 3: Merge `develop` → `master` (Later)

After testing in `develop`:
```bash
git checkout master
git pull origin master
git merge develop
git push origin master
```

## Why This Approach?

✅ **Safe:** Develop branch is for integration/testing  
✅ **Reversible:** Can revert merge before going to master  
✅ **Collaborative:** Team can review before production  
✅ **Standard Practice:** Follows Git Flow methodology  

## Current Status

You have **4 commits** ready to merge:
- `dc05bb6` - Core functionality implementation
- `71301d6` - Linter fixes
- `8a50da4` - SQLAlchemy error fixes
- `110ad79` - Streamlit deployment entry points

All commits are on `feature/call-qa-tool` branch, ready for PR to `develop`.

