# Quickstart — SOC Tier-1 Alert Triage

**Time required:** ~10 minutes  
**Skill used:** `triaging-security-alerts-in-splunk`  
**Runtime:** Claude (claude.ai or API) — the pattern works with any LLM that accepts a system prompt

---

## What you're doing

You will load a security skill as agent context, provide a sample alert as input, and get a structured triage report back. This is the core pattern for every skill in this library.

---

## Step 1 — Read the skill

Open `skills/triaging-security-alerts-in-splunk/SKILL.md`.

Skim the **When to Use** section to confirm this is the right skill for your task, then read the **Procedure** section to understand what the agent will do.

---

## Step 2 — Set up the agent

**On claude.ai:**

1. Open a new conversation.
2. Paste the *full contents* of `SKILL.md` into the message box, preceded by this line:

   ```
   You are a security operations analyst. Use the following skill as your operating procedure:
   ```

3. Send that message. The agent will acknowledge the skill.

**Via the Anthropic API:**

```python
import anthropic

with open('skills/triaging-security-alerts-in-splunk/SKILL.md') as f:
    skill = f.read()

client = anthropic.Anthropic()
messages = [
    {
        "role": "user",
        "content": f"You are a security operations analyst. Use the following skill as your operating procedure:\n\n{skill}"
    }
]
# Add the alert as the next user message (see Step 3)
```

---

## Step 3 — Provide the alert

Copy the contents of `sample-input/alert.json` and send it as the next message:

```
Triage this alert:

<paste alert.json contents here>
```

---

## Step 4 — Review the output

The agent should return a structured triage report. Compare it against the **Quality Checks** section of the skill to verify the output is complete.

Expected output structure:

```
TRIAGE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━
Alert:        <rule name>
Alert ID:     <id>
Time:         <timestamp>
Source:       <ip / hostname>
Destination:  <ip / hostname>
User:         <username if present>

Investigation:
  - <what telemetry was examined>
  - <correlation findings>
  - <threat intelligence matches or absence>

Disposition:  <TRUE POSITIVE / FALSE POSITIVE / BENIGN / UNDETERMINED>
Action:       <escalation step, suppression note, or closure rationale>
```

---

## Next steps

- Browse `index.json` to find skills matching your next task.
- Load a different skill following the same pattern.
- For the full library (750+ skills, framework crosswalks, maturity model): [aisecurityskills.com](https://www.aisecurityskills.com)
