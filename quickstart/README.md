# Quickstart — Defending Against Prompt Injection

**Time required:** ~10 minutes  
**Skill used:** `defending-against-prompt-injection`  
**Runtime:** Claude (claude.ai or API) — the pattern works with any LLM that accepts a system prompt

---

## What you're doing

You will load an AI security skill as agent context, provide a sample prompt-injection payload as input, and receive a structured analysis and hardening recommendation. This is the core pattern for every skill in this library: skill as procedure, your artefact as input, agent as executor.

This skill maps to **AICM domain AIS** (Application & Interface Security), control **AIS-08**, owned by the Application Provider. Executing and documenting it supports a YES response to AIS-08 in your AI-CAIQ self-assessment.

---

## Step 1 — Read the skill

Open `skills/defending-against-prompt-injection/SKILL.md`.

Skim **When to Use** to confirm this skill fits your scenario, then read **Procedure** to understand what the agent will execute.

---

## Step 2 — Set up the agent

**On claude.ai:**

1. Open a new conversation.
2. Paste the full contents of `SKILL.md` as your first message, preceded by:

   ```
   You are an AI application security engineer. Use the following skill as your operating procedure:
   ```

3. Send the message. The agent acknowledges the skill.

**Via the Anthropic API:**

```python
import anthropic

with open("skills/defending-against-prompt-injection/SKILL.md") as f:
    skill = f.read()

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=2048,
    messages=[
        {
            "role": "user",
            "content": (
                "You are an AI application security engineer. "
                "Use the following skill as your operating procedure:\n\n"
                + skill
            ),
        }
    ],
)
print(response.content[0].text)
# Then send the sample input as the next user message (Step 3)
```

---

## Step 3 — Provide the sample input

Send the contents of `sample-input/prompt_injection_payload.txt` as the next message:

```
Analyse this potential prompt injection payload and assess the risk to our RAG application:

<paste sample-input/prompt_injection_payload.txt here>
```

---

## Step 4 — Review the output

The agent should return a structured analysis. Compare it against the **Quality Checks** section of the skill to verify completeness.

Expected output structure:

```
PROMPT INJECTION ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━
Payload classification: <Direct / Indirect / Jailbreak attempt>
Attack vector: <System-prompt override / Data exfiltration / Tool misuse>
Risk level: <Critical / High / Medium / Low>

Technical analysis:
  - <Injection technique identified>
  - <Bypass attempt details>
  - <Target: system prompt / context window / tool calls>

Recommended mitigations:
  1. <Input validation / sanitisation step>
  2. <Prompt engineering defence>
  3. <Output filtering control>

AI-CAIQ evidence: Execution of this analysis and implementation of the
recommended controls supports a YES response to AIS-08.
```

---

## Step 5 — Document as AI-CAIQ evidence

If you implement the recommended controls and document the outcome, that documentation supports a **YES** response to AICM control **AIS-08** in your AI-CAIQ self-assessment. Save the agent's output alongside your implementation notes as your evidence artefact.

---

## Next steps

- Browse `index.json` to find skills matching your next AI security task.
- Load a different skill following the same 5-step pattern.
- For the full methodology, AICM coverage assessments, and STAR for AI Level 1 preparation: **[aisecurityskills.com](https://www.aisecurityskills.com)**
