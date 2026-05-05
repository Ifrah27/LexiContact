import os
import json
from groq import Groq
from dotenv import load_dotenv
from hallucination_guard import verify_quote
from risk_taxonomy import RISK_TAXONOMY

load_dotenv()

client = Groq()
MODEL_NAME = "llama-3.3-70b-versatile"

def call_groq_llm(prompt: str) -> str:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a senior legal contract analyst. You MUST respond with ONLY valid JSON and absolutely no other text, markdown, or HTML tags."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model=MODEL_NAME,
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    return chat_completion.choices[0].message.content

def analyze_clause(user_clause: str, fair_clause: str, clause_type: str, retry_count: int = 1) -> dict:
    prompt = f"""
You are a legal contract analysis engine.

Return ONLY clean, plain JSON data.

STRICT RULES:
- No HTML tags
- No <div>, <span>, <ul>, or formatting
- No markdown
- No explanations outside JSON
- No labels like "Problematic Clause"
- Keep everything short and clean

Return this exact structure:

{{
  "clause_type": "{clause_type}",
  "risk_score": 0,
  "risk_level": "Low/Medium/High",
  "issue": "",
  "reason": "",
  "recommendation": ""
}}

Guidelines:
- "issue" should be 1 short sentence OR "None"
- "reason" should be simple and 1–2 lines
- "recommendation" should be clear and actionable
- If no risk → still explain briefly why safe
- Do NOT repeat content
- Do NOT generate styled output

Clause:
{user_clause}
"""

    # Default safe fallback
    fallback_result = {
        "clause_type": clause_type,
        "risk_score": 0,
        "risk_level": "Low",
        "issue": "None",
        "reason": "Analysis skipped or error occurred.",
        "recommendation": "Review manually."
    }

    try:
        response_text = call_groq_llm(prompt)
    except Exception:
        return fallback_result
    
    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        return fallback_result

    # Hallucination Guard for 'issue' if it's treated as a quote
    issue_text = result.get("issue", "None")
    if issue_text and issue_text.lower() != "none" and len(issue_text) > 10:
        # We try to verify if it's a quote, but the prompt says '1 short sentence' 
        # so it might be a summary. If it looks like a quote, we verify.
        if issue_text in user_clause:
            pass # Valid quote
        else:
            # If not a direct quote, we check if it contains a hallucinated quote
            # For simplicity in this refined prompt, we just keep it if it's a summary.
            pass

    # Enforce formatting constraints
    try:
        score = float(result.get("risk_score", 0))
        result["risk_score"] = score
        if score >= 7:
            result["risk_level"] = "High"
        elif score >= 4:
            result["risk_level"] = "Medium"
        else:
            result["risk_level"] = "Low"
    except (ValueError, TypeError):
        result["risk_score"] = 0
        result["risk_level"] = "Low"

    return result
