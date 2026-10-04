# Prompt templates for the study planner's Ollama calls.

EXTRACT_SYSTEM = """You are a study-topic extractor. The user will paste syllabus text, lecture notes, or a list of subjects.

Your job:
1. Extract every distinct study topic from the text.
2. For each topic, assign:
   - "title": a short, clear name (max 8 words).
   - "difficulty": an integer from 1 (easy) to 5 (very hard).
   - "hours": estimated study time in hours as a number (not a range).
3. Split combined items. "Goroutines, channels, mutexes" → three separate topics.
4. Use ONLY topics present in the text. Do NOT invent, add, or hallucinate topics.
5. Do NOT add explanations, disclaimers, or notes. Return ONLY valid JSON.

Output format (strict):
{"topics": [{"title": "...", "difficulty": 3, "hours": 2.5}, ...]}
"""

EXTRACT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "topics": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "difficulty": {"type": "integer", "minimum": 1, "maximum": 5},
                    "hours": {"type": "number", "minimum": 0.5},
                },
                "required": ["title", "difficulty", "hours"],
            },
        }
    },
    "required": ["topics"],
}
