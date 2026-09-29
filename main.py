import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

response = client.models.generate_content(
    model="gemini-3-flash-preview",

    config=types.GenerateContentConfig(
        system_instruction="""
You are a rigorous research assistant.

For each question:

1. Identify the main question.
2. Break the question into sub-questions when useful.
3. Separate information into:
   - FACT: information you have strong confidence is established.
   - INFERENCE: a conclusion derived from available information.
   - UNCERTAINTY: information you cannot confidently establish.
4. Do not fabricate facts, sources, statistics, or citations.
5. If the question contains a false assumption, point it out.
6. Keep the answer concise and organized.
""",

        response_mime_type="application/json",

        response_schema={
            "type": "object",
            "properties": {
                "main_question": {
                    "type": "string"
                },
                "sub_questions": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "facts": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "inferences": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "uncertainties": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": [
                "main_question",
                "sub_questions",
                "facts",
                "inferences",
                "uncertainties"
            ]
        }
    ),

    contents="How does RAG reduce hallucinations in LLM applications?"
)

data = json.loads(response.text)

print("\nMAIN QUESTION:")
print(data["main_question"])

print("\nSUB QUESTIONS:")
for question in data["sub_questions"]:
    print("-", question)

print("\nFACTS:")
for fact in data["facts"]:
    print("-", fact)

print("\nINFERENCES:")
for inference in data["inferences"]:
    print("-", inference)

print("\nUNCERTAINTIES:")
for uncertainty in data["uncertainties"]:
    print("-", uncertainty)