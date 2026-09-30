import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types


# -----------------------------------
# Setup
# -----------------------------------

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# -----------------------------------
# 1. DECOMPOSE
# -----------------------------------

def decompose_question(question):

    response = client.models.generate_content(
        model="gemini-3-flash-preview",

        config=types.GenerateContentConfig(

            response_mime_type="application/json",

            response_schema={
                "type": "object",
                "properties": {
                    "sub_questions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "sub_questions"
                ]
            }
        ),

        contents=f"""
Break this research question into 3-5
specific sub-questions that together would
help answer the original question.

Research question:
{question}
"""
    )

    return json.loads(response.text)


# -----------------------------------
# 2. ANSWER
# -----------------------------------

def answer_question(question):

    response = client.models.generate_content(
        model="gemini-3-flash-preview",

        config=types.GenerateContentConfig(

            system_instruction="""
You are a research assistant.

Answer the question using established knowledge.

Clearly distinguish facts from inferences.

If something cannot be confidently established,
say so.

Do not invent sources or citations.
"""
        ),

        contents=question
    )

    return response.text


# -----------------------------------
# 3. SYNTHESIZE
# -----------------------------------

def synthesize(question, answers):

    research_data = json.dumps(
        answers,
        indent=2
    )

    response = client.models.generate_content(
        model="gemini-3-flash-preview",

        config=types.GenerateContentConfig(

            system_instruction="""
You are a research report writer.

Create a concise research report based ONLY
on the research answers provided.

Do not introduce unsupported claims.
""",

            response_mime_type="application/json",

            response_schema={
                "type": "object",
                "properties": {

                    "summary": {
                        "type": "string"
                    },

                    "key_findings": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },

                    "confidence": {
                        "type": "string"
                    },

                    "gaps": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },

                "required": [
                    "summary",
                    "key_findings",
                    "confidence",
                    "gaps"
                ]
            }
        ),

        contents=f"""
Original research question:

{question}

Research findings:

{research_data}
"""
    )

    return json.loads(response.text)


# -----------------------------------
# MAIN PIPELINE
# -----------------------------------

def research(question):

    # Step 1: Decompose
    print("\n=== DECOMPOSING QUESTION ===")

    decomposition = decompose_question(question)

    sub_questions = decomposition["sub_questions"]

    for i, sub_question in enumerate(sub_questions, start=1):
        print(f"{i}. {sub_question}")


    # Step 2: Answer each sub-question
    print("\n=== ANSWERING QUESTIONS ===")

    answers = []

    for i, sub_question in enumerate(sub_questions, start=1):

        print(f"\nQuestion {i}: {sub_question}")

        answer = answer_question(sub_question)

        print(f"Answer: {answer}")

        answers.append({
            "question": sub_question,
            "answer": answer
        })


    # Step 3: Synthesize
    print("\n=== SYNTHESIZING ===")

    report = synthesize(
        question,
        answers
    )


    # Step 4: Display final report
    print("\n================================")
    print("FINAL RESEARCH REPORT")
    print("================================")

    print("\nSUMMARY:")
    print(report["summary"])

    print("\nKEY FINDINGS:")

    for finding in report["key_findings"]:
        print("-", finding)

    print("\nCONFIDENCE:")
    print(report["confidence"])

    print("\nGAPS:")

    for gap in report["gaps"]:
        print("-", gap)

    return report


# -----------------------------------
# PROGRAM START
# -----------------------------------

if __name__ == "__main__":

    question = input(
        "\nEnter your research question: "
    )

    research(question)