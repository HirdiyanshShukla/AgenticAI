
import os
import json

from datetime import datetime

import requests
from bs4 import BeautifulSoup

from dotenv import load_dotenv
from ddgs import DDGS
from google import genai
from google.genai import types


# ==========================================
# SETUP
# ==========================================

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ==========================================
# 1. CALCULATOR TOOL
# ==========================================

def calculator(expression: str):

    try:

        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        return {
            "result": result
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ==========================================
# 2. CURRENT TIME TOOL
# ==========================================

def get_current_time():

    now = datetime.now()

    return {
        "current_time": now.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }


# ==========================================
# 3. WEB SEARCH TOOL
# ==========================================

def search_web(query: str):

    try:

        results = DDGS().text(
            query,
            max_results=5
        )

        trimmed_results = []

        for result in results:

            trimmed_results.append({
                "title": result.get("title"),
                "url": result.get("href"),
                "snippet": result.get("body")
            })

        return {
            "results": trimmed_results
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ==========================================
# 4. FETCH PAGE TOOL
# ==========================================

def fetch_page(url: str):

    try:

        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove elements that usually contain
        # unnecessary content.
        for element in soup(
            ["script", "style", "nav", "footer"]
        ):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        # Limit the amount of content sent
        # back to Gemini.
        MAX_CHARS = 12000

        text = text[:MAX_CHARS]

        return {
            "url": url,
            "content": text
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ==========================================
# TOOL DECLARATIONS
# ==========================================

calculator_tool = {

    "name": "calculator",

    "description": """
Calculate a mathematical expression.

Use this when a mathematical calculation
is required.
""",

    "parameters": {

        "type": "object",

        "properties": {

            "expression": {

                "type": "string",

                "description":
                    "Mathematical expression such as 125 * 48"

            }

        },

        "required": [
            "expression"
        ]
    }
}


current_time_tool = {

    "name": "get_current_time",

    "description": """
Get the current local date and time.

Use this when the user asks what time or
date it currently is.
""",

    "parameters": {

        "type": "object",

        "properties": {}
    }
}


search_web_tool = {

    "name": "search_web",

    "description": """
Search the web only when external or up-to-date
information is necessary to answer the user's
question accurately.

Do NOT use this tool for questions that can be
answered reliably using your existing knowledge.

Use it especially for:

- current or real-time information
- recent events or developments
- information that may have changed recently
- requests requiring specific external sources

Prefer answering directly when the question is
general, conceptual, or stable.
""",

    "parameters": {

        "type": "object",

        "properties": {

            "query": {

                "type": "string",

                "description":
                    "The search query"

            }

        },

        "required": [
            "query"
        ]
    }
}


fetch_page_tool = {

    "name": "fetch_page",

    "description": """
Fetch and extract readable text from a webpage.

Use this when a search result URL needs to be
examined in more detail.

The tool returns the webpage's readable text.
""",

    "parameters": {

        "type": "object",

        "properties": {

            "url": {

                "type": "string",

                "description":
                    "The URL of the webpage to fetch"

            }

        },

        "required": [
            "url"
        ]
    }
}


# ==========================================
# TOOL REGISTRY
# ==========================================

tools = {

    "calculator": calculator,

    "get_current_time": get_current_time,

    "search_web": search_web,

    "fetch_page": fetch_page
}


tool_declarations = [

    calculator_tool,

    current_time_tool,

    search_web_tool,

    fetch_page_tool

]


# ==========================================
# AGENT LOOP
# ==========================================

def run_agent(user_question):

    contents = [

        types.Content(

            role="user",

            parts=[

                types.Part.from_text(

                    text=user_question

                )

            ]
        )

    ]

    MAX_ITERATIONS = 5

    for iteration in range(MAX_ITERATIONS):

        print(
            f"\n========== ITERATION {iteration + 1} =========="
        )

        # ----------------------------------
        # ASK GEMINI WHAT TO DO
        # ----------------------------------

        response = client.models.generate_content(

            model="gemini-3-flash-preview",

            contents=contents,

            config=types.GenerateContentConfig(

                tools=[

                    types.Tool(

                        function_declarations=
                            tool_declarations

                    )

                ],

                automatic_function_calling={
                    "disable": True
                }
            )
        )

        # ----------------------------------
        # NO TOOL → FINAL ANSWER
        # ----------------------------------

        if not response.function_calls:

            return response.text

        # ----------------------------------
        # GEMINI REQUESTED A TOOL
        # ----------------------------------

        contents.append(
            response.candidates[0].content
        )

        for function_call in response.function_calls:

            tool_name = function_call.name

            arguments = function_call.args

            print("\n-----------------------------")

            print("TOOL CALL")

            print("-----------------------------")

            print("Tool:", tool_name)

            print("Arguments:", arguments)

            # ----------------------------------
            # FIND TOOL
            # ----------------------------------

            tool = tools.get(tool_name)

            if tool is None:

                result = {

                    "error":
                        f"Unknown tool: {tool_name}"

                }

            else:

                try:

                    # Execute the actual Python function

                    result = tool(**arguments)

                except Exception as e:

                    result = {

                        "error": str(e)

                    }

            # ----------------------------------
            # PRINT TOOL RESULT
            # ----------------------------------

            print("\nTOOL RESULT:")

            print(

                json.dumps(

                    result,

                    indent=2,

                    ensure_ascii=False

                )

            )

            # ----------------------------------
            # SEND RESULT BACK TO GEMINI
            # ----------------------------------

            contents.append(

                types.Content(

                    role="user",

                    parts=[

                        types.Part.from_function_response(

                            name=tool_name,

                            response=result

                        )

                    ]

                )

            )

        # ----------------------------------
        # LOOP BACK TO GEMINI
        # ----------------------------------

    # ----------------------------------
    # MAX ITERATIONS REACHED
    # ----------------------------------

    return (
        "I couldn't complete the task "
        "within the allowed number of steps."
    )


# ==========================================
# PROGRAM
# ==========================================

if __name__ == "__main__":

    while True:

        question = input(
            "\nResearch question: "
        )

        if question.lower() == "exit":

            break

        answer = run_agent(question)

        print(
            "\n=============================="
        )

        print("FINAL ANSWER")

        print(
            "=============================="
        )

        print(answer)
