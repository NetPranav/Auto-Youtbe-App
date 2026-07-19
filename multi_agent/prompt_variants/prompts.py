PEER_REVIEW_PROMPT = """
You are reviewing another AI agent's work.

The task was: {task_context}

Here is the draft you are reviewing:
---
{draft}
---

Provide structured feedback as a JSON object:
{{
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "score": 7,
    "suggested_improvement": "One specific actionable improvement."
}}

CRITICAL RULE: Evaluate strictly on factual accuracy, neutrality, and educational value. Reject any political bias, blame, or sensationalism.
Return ONLY the JSON object.
"""

DEBATE_PROMPT = """
You are debating another AI agent's output.

Your expertise: {expertise}

The draft being debated:
---
{draft}
---

Previous arguments in this debate:
{previous_arguments}

Based on your expertise, make ONE specific, well-reasoned argument about this draft.
Focus on factual accuracy, missing evidence, or potential bias.
CRITICAL RULE: You must enforce strict political neutrality. Do not tolerate speculation or blame.
Keep your argument under 100 words.
"""

JUDGE_PROMPT = """
You are the Chief Editor and final Judge.

You are evaluating {num_drafts} competing drafts for the task: {task_context}

{drafts_section}

Score each draft on these criteria (0-10 each):
- Accuracy (Are the claims supported by evidence?)
- Neutrality (Is it free from political bias and blame?)
- Retention (will viewers stay?)
- SEO (will this get discovered?)
- Clarity (Is it easy to understand?)

Return ONLY a valid JSON object:
{{
    "scores": {{
        "Draft 1": {{"accuracy": 8, "neutrality": 9, "retention": 9, "seo": 6, "clarity": 8, "total": 40}},
        "Draft 2": {{"accuracy": 7, "neutrality": 8, "retention": 8, "seo": 7, "clarity": 7, "total": 37}}
    }},
    "winner": "Draft 1",
    "reasoning": "Brief explanation of why this draft won based on evidence and neutrality."
}}
"""

CONSENSUS_PROMPT = """
You are building the definitive final version by merging the best elements from multiple drafts.

Task: {task_context}

{drafts_section}

Judge's analysis:
{judge_reasoning}

Create the BEST possible output by combining:
- The strongest, most factual hook from any draft
- The clearest explanations of the root causes
- The most balanced, neutral conclusion
- The most engaging transitions

CRITICAL RULE: The final output must be 100% politically neutral, evidence-based, and educational. Remove any sensationalism or bias.
Output ONLY the final merged content. No commentary.
"""

REVISION_PROMPT = """
You are performing a final editorial polish on this content.

Content:
---
{content}
---

Improve:
1. Flow and readability
2. Remove any repetition
3. Strengthen engagement
4. Ensure absolute political neutrality and factual consistency

CRITICAL RULE: Do not add any new claims. Ensure the tone is objective, respectful, and fact-first.
Output ONLY the revised content. No commentary.
"""
