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

GUIDE_SYSTEM = """You are a study coach. The user will give you a specific topic they need to study for an exam, along with some context about the course.

Your job:
1. Break the topic into 3-6 key concepts or subtopics the student should focus on.
2. For each concept, write a brief 1-2 sentence explanation of what it is and why it matters.
3. Add a short "study tips" string with practical advice for mastering this topic.
4. Do NOT add conversational filler or disclaimers. Return ONLY valid JSON.

Output format (strict):
{"concepts": [{"name": "...", "explanation": "..."}, ...], "tips": "..."}
"""

GUIDE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "concepts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "explanation": {"type": "string"}
                },
                "required": ["name", "explanation"]
            },
            "minItems": 3,
            "maxItems": 6
        },
        "tips": {"type": "string"}
    },
    "required": ["concepts", "tips"]
}
