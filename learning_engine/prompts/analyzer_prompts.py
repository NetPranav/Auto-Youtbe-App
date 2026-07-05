PERFORMANCE_ANALYSIS_PROMPT = """
You are an expert YouTube Strategist.
Analyze the following video performance metrics and return a structured JSON evaluation.

Metrics:
Views: {views}
CTR: {ctr}%
Avg Duration: {duration}s

Rules:
1. Return a score from 0 to 100 based on the metrics (high CTR and duration = good).
2. Return a short conclusion on what worked or didn't work.

Return ONLY a valid JSON object matching this schema:
{
    "overall_score": 85,
    "conclusion": "String"
}
"""

RETENTION_ANALYSIS_PROMPT = """
You are an expert YouTube Strategist.
Analyze the following retention graph (Timestamp -> Retention %) and return a structured JSON evaluation.

Retention Graph:
{graph}

Rules:
1. Identify if there is a massive drop in the first 5 seconds. If so, flag 'bad_hook'.
2. Provide a single concrete recommendation for the Content Engine (e.g. "Use faster pacing in the first 5 seconds").

Return ONLY a valid JSON object matching this schema:
{
    "hook_quality": "good" | "bad",
    "recommendation": "String"
}
"""
