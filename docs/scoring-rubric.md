# Call QA Scoring Rubric

This document describes the detailed scoring criteria used by the Call QA Tool to evaluate call center agent performance.

## Overview

Each call is evaluated on 5 key metrics, each scored from 0-10. The scores are then weighted and averaged to produce an overall score (0-10).

## Scoring Metrics

### 1. Greeting Quality (0-10)

**Weight:** 1.0 (Standard)

**Scoring Criteria:**

- **10 points:** Professional greeting with ALL of the following:
  - Company name mentioned
  - Agent name provided
  - Professional greeting word ("Hello", "Hi", "Good morning", etc.)
  
  *Example: "Hello, thank you for calling ABC Company. This is Sarah. How can I help you today?"*

- **7-9 points:** Good greeting with one element missing
  - Company name OR agent name missing
  
  *Example: "Hello, thank you for calling. This is Sarah. How may I assist you?"*

- **4-6 points:** Generic greeting
  - Basic greeting word only, no company/agent identification
  
  *Example: "Hello, how can I help you?"*

- **0-3 points:** Poor or missing greeting
  - No greeting, unprofessional language, or inappropriate response
  
  *Example: "Yeah?" or "What do you want?"*

---

### 2. Hold Time Management (0-10)

**Weight:** 0.5 (Lower priority, but still important)

**Scoring Criteria:**

- **10 points:** No hold or <30 seconds with explanation
  - Agent explains why they're putting customer on hold
  - Minimal wait time
  
  *Example: "One moment please, let me check that for you." [15 seconds] "Thank you for holding..."*

- **7-9 points:** 30-60 seconds with explanation
  - Reasonable hold time with proper communication
  
  *Example: "Please hold while I check your account." [45 seconds] "I'm still working on that..."*

- **4-6 points:** 60-120 seconds or no explanation
  - Long hold without regular updates
  - Agent doesn't explain why customer is waiting
  
  *Example: "Hold on." [90 second silence]*

- **0-3 points:** >120 seconds or customer hang-up
  - Excessive hold time
  - Agent doesn't return to call
  - Customer hangs up due to frustration

---

### 3. Problem Resolution (0-10)

**Weight:** 2.0 (HIGHEST PRIORITY)

**Scoring Criteria:**

- **10 points:** Issue fully resolved with confirmation
  - Problem completely solved
  - Confirmation number or reference provided
  - Clear explanation of what was done
  
  *Example: "I've processed your cancellation. Your confirmation number is CAN-12345. Your subscription will end on [date]."*

- **7-9 points:** Resolved but missing confirmation
  - Issue resolved but no reference number provided
  - Customer left without clear confirmation
  
  *Example: "Okay, I've canceled it for you."*

- **4-6 points:** Partial resolution, requires callback
  - Issue partially addressed
  - Agent needs to call back or escalate
  - Problem not fully solved
  
  *Example: "I'll need to escalate this. Someone will call you back within 24 hours."*

- **0-3 points:** Not resolved or incorrect information
  - Problem not addressed
  - Agent provided incorrect information
  - Customer's needs not met
  
  *Example: "I can't help with that. You'll need to call back later."*

---

### 4. Tone/Empathy (0-10)

**Weight:** 1.5 (Important for customer satisfaction)

**Scoring Criteria:**

- **10 points:** Consistently positive, empathetic language
  - Warm, friendly tone throughout
  - Shows understanding of customer's situation
  - Uses positive language ("happy to help", "I understand", "I appreciate")
  
  *Example: "I'm so sorry to hear you're experiencing this issue. I completely understand your frustration. I'm here to help resolve this for you right away."*

- **7-9 points:** Professional but neutral
  - Polite and courteous
  - No negative language
  - Lacks emotional connection
  
  *Example: "I can help you with that. Let me check your account."*

- **4-6 points:** Occasionally short or impatient
  - Some positive language
  - Occasional impatience or abruptness
  - Mixed tone
  
  *Example: "What's your account number? I need that to proceed."*

- **0-3 points:** Rude, dismissive, or hostile
  - Negative language
  - Dismissive attitude
  - Unprofessional tone
  
  *Example: "I'm busy. What do you want?"*

**Note:** This metric uses AI sentiment analysis via OpenRouter LLM to evaluate the tone of agent's speech throughout the call.

---

### 5. Script Compliance (0-10)

**Weight:** 1.0 (Standard)

**Scoring Criteria:**

Script compliance is measured against scenario-specific requirements. For example, in a "cancel subscription" scenario:

**Required Elements:**
- Greeting with company name and agent name
- Retention attempt (ask why customer is canceling)
- Clear process explanation
- Confirmation number provided

**Scoring:**

- **10 points:** All required script elements present
  - Every expected behavior is demonstrated
  
- **5 points:** 50% of required elements present
  - Half of script requirements met
  
- **0 points:** No script elements detected
  - Agent doesn't follow any required procedures

**Customization:**

Script requirements are defined in scenario JSON files (`data/call_scenarios/*.json`) under the `expected_agent_behavior` field. You can customize requirements per scenario.

---

## Weighted Score Calculation

The overall score is calculated using weighted averages:

```
Total Score = (Greeting × 1.0 + Hold Time × 0.5 + Resolution × 2.0 + Tone × 1.5 + Compliance × 1.0) / 6.0
```

**Example:**
- Greeting: 10.0 × 1.0 = 10.0
- Hold Time: 8.0 × 0.5 = 4.0
- Resolution: 9.0 × 2.0 = 18.0
- Tone: 8.5 × 1.5 = 12.75
- Compliance: 9.0 × 1.0 = 9.0
- **Total: (10.0 + 4.0 + 18.0 + 12.75 + 9.0) / 6.0 = 8.96/10**

---

## Customizing Weights

You can customize scoring weights per scenario in the scenario JSON file:

```json
{
  "scoring_weights": {
    "greeting": 1.0,
    "hold_time": 0.5,
    "resolution": 2.0,
    "tone": 1.5,
    "compliance": 1.0
  }
}
```

**Weight Guidelines:**
- **Resolution** should typically have the highest weight (2.0) as it's most important
- **Tone** is important for satisfaction (1.5)
- **Greeting** and **Compliance** are standard (1.0)
- **Hold Time** can be lower (0.5) if not critical to your business

---

## Score Interpretation

- **9.0 - 10.0:** 🌟 Excellent - Exceeds expectations
- **7.0 - 8.9:** ✅ Good - Meets standards
- **5.0 - 6.9:** ⚠️ Needs Improvement - Below expectations
- **0.0 - 4.9:** ❌ Poor - Requires immediate attention

---

## Recommendations

Based on scores, the system automatically generates improvement recommendations:

- **Low Greeting Score:** "Improve greeting: Include company name and agent name in initial greeting"
- **Low Hold Time Score:** "Reduce hold times: Keep holds under 60 seconds and always explain why"
- **Low Resolution Score:** "Ensure complete resolution: Confirm issue is resolved and provide reference number"
- **Low Tone Score:** "Improve tone: Use more empathetic language and positive phrasing"
- **Low Compliance Score:** "Follow script requirements: Ensure all required script elements are included"

---

## Examples

### Excellent Call (Score: 9.2/10)

**Transcript:**
- Agent: "Hello, thank you for calling ABC Company. This is Sarah. How can I help you today?"
- Customer: "I'd like to cancel my subscription."
- Agent: "I'm sorry to hear that. May I ask what led to this decision?"
- Customer: "Not using it anymore."
- Agent: "I understand. I've processed your cancellation. Your confirmation number is CAN-12345. Is there anything else I can help with?"
- Customer: "No, thanks."
- Agent: "You're welcome. Have a great day!"

**Scores:**
- Greeting: 10/10 ✅
- Hold Time: 10/10 ✅
- Resolution: 10/10 ✅
- Tone: 9/10 ✅
- Compliance: 9/10 ✅

---

### Poor Call (Score: 2.8/10)

**Transcript:**
- Customer: "I want to cancel."
- Agent: "What?" [long pause]
- Customer: "Cancel subscription."
- Agent: "I can't do that right now. Call back later."
- [Call ends]

**Scores:**
- Greeting: 2/10 ❌
- Hold Time: 1/10 ❌
- Resolution: 0/10 ❌
- Tone: 3/10 ❌
- Compliance: 1/10 ❌

---

## Best Practices

1. **Always greet professionally** - Include company and agent name
2. **Explain holds** - Tell customers why they're waiting
3. **Confirm resolution** - Provide reference numbers
4. **Stay positive** - Use empathetic, professional language
5. **Follow scripts** - Ensure all required elements are covered

---

For more information, see:
- [Architecture Documentation](call-qa-architecture.md)
- [Demo Guide](../README_CALL_QA_DEMO.md)

