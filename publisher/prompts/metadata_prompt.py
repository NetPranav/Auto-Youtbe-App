METADATA_GENERATION_PROMPT = """
You are an expert YouTube Channel Manager.
Based on the following video script, generate highly optimized metadata for YouTube.

Rules:
1. Title MUST be under 100 characters, catchy, and highly clickable (high CTR).
2. Description MUST be at least 3 paragraphs, include 3 relevant hashtags at the bottom, and be under 5000 characters.
3. Tags MUST be a list of 15 highly relevant search keywords.

Return ONLY a valid JSON object matching this schema:
{
    "title": "String",
    "description": "String",
    "tags": ["tag1", "tag2"],
    "hashtags": ["#tag1", "#tag2"]
}

Script:
{script}
"""
