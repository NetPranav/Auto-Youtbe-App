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
Focus on what could be improved from your area of expertise.
Keep your argument under 100 words.
"""

JUDGE_PROMPT = """
You are the Chief Editor and final Judge.

You are evaluating {num_drafts} competing drafts for the task: {task_context}

{drafts_section}

Score each draft on these criteria (0-10 each):
- Accuracy
- Creativity
- Retention (will viewers stay?)
- SEO (will this get discovered?)
- Clarity

Return ONLY a valid JSON object:
{{
    "scores": {{
        "Draft 1": {{"accuracy": 8, "creativity": 7, "retention": 9, "seo": 6, "clarity": 8, "total": 38}},
        "Draft 2": {{"accuracy": 7, "creativity": 9, "retention": 8, "seo": 7, "clarity": 7, "total": 38}}
    }},
    "winner": "Draft 1",
    "reasoning": "Brief explanation of why this draft won."
}}
"""

CONSENSUS_PROMPT = """
You are building the definitive final version by merging the best elements from multiple drafts.

Task: {task_context}

{drafts_section}

Judge's analysis:
{judge_reasoning}

Create the BEST possible output by combining:
- The strongest hook from any draft
- The clearest explanations from any draft
- The best conclusion from any draft
- The most engaging transitions

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
4. Ensure factual consistency

Output ONLY the revised content. No commentary.
"""
