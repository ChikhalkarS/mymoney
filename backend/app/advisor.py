"""
Financial advisor module.

1. Tries to call a local Ollama instance for AI-powered advice.
2. Falls back to a rule-based 50/30/20 analyser if Ollama is unreachable.
"""

from __future__ import annotations

import os

import httpx

# In Docker Compose, OLLAMA_URL points to the ollama service.
# Default falls back to localhost for local development.
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
OLLAMA_TIMEOUT = 30  # seconds – slightly longer to account for Docker cold-start

# 50/30/20 budget guidelines (as a fraction of total spending)
BUDGET_GUIDELINES: dict[str, float] = {
    "Housing": 0.30,
    "Groceries": 0.10,
    "Transportation": 0.10,
    "Healthcare": 0.05,
    "Utilities": 0.05,
    "Dining": 0.05,
    "Entertainment": 0.05,
    "Shopping": 0.05,
    "Subscriptions": 0.03,
    "Education": 0.05,
    "Savings": 0.20,
}


def _rule_based_advice(category_totals: dict[str, float]) -> str:
    """Generate advice using the 50/30/20 rule when Ollama is unavailable."""
    total_spending = sum(
        v for k, v in category_totals.items() if k not in ("Income", "Savings")
    )
    if total_spending == 0:
        return "No spending data available to analyse."

    lines: list[str] = [
        "💡 **Rule-Based Financial Advice (50/30/20 Framework)**\n",
        f"Total Tracked Spending: **${total_spending:,.2f}**\n",
        "---",
    ]

    flagged = False
    for category, limit_pct in BUDGET_GUIDELINES.items():
        spent = category_totals.get(category, 0.0)
        pct = spent / total_spending if total_spending else 0
        limit_amount = limit_pct * total_spending

        if spent > limit_amount * 1.10:  # 10% tolerance
            lines.append(
                f"⚠️  **{category}**: You spent **${spent:,.2f}** "
                f"({pct:.1%} of budget), which exceeds the recommended "
                f"{limit_pct:.0%} guideline (${limit_amount:,.2f})."
            )
            flagged = True

    if not flagged:
        lines.append("✅ All spending categories are within recommended guidelines. Great job!")

    savings = category_totals.get("Savings", 0.0)
    savings_pct = savings / total_spending if total_spending else 0
    if savings_pct < 0.20:
        lines.append(
            f"\n💰 **Savings Alert**: You are saving **{savings_pct:.1%}** of your "
            "spending. The 50/30/20 rule recommends saving at least **20%**."
        )

    return "\n".join(lines)


def get_advice(category_totals: dict[str, float]) -> str:
    """
    Return financial advice.
    Attempts Ollama first; falls back to rule-based logic on failure.
    """
    prompt = _build_prompt(category_totals)

    try:
        response = httpx.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception:
        # Ollama unreachable or returned an error – use rule-based fallback
        return _rule_based_advice(category_totals)


def _build_prompt(category_totals: dict[str, float]) -> str:
    breakdown = "\n".join(
        f"  - {cat}: ${amt:,.2f}" for cat, amt in sorted(category_totals.items())
    )
    return (
        "You are a professional personal finance advisor. "
        "A user has shared their monthly spending breakdown:\n\n"
        f"{breakdown}\n\n"
        "Identify any bad spending habits, compare against the 50/30/20 rule, "
        "and give 3-5 actionable tips to improve their finances. "
        "Be concise, friendly, and practical."
    )
