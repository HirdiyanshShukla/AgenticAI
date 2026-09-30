import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# -----------------------------------
# 1. ACTUAL TOOL
# -----------------------------------

def calculate(expression: str):

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


# -----------------------------------
# 2. TOOL DECLARATION
# -----------------------------------

calculate_tool = {
    "name": "calculate",
    "description": "Calculate a mathematical expression.",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A mathematical expression such as 25 * 4"
            }
        },
        "required": ["expression"]
    }
}


# -----------------------------------
# 3. FIRST CALL TO GEMINI
# -----------------------------------

response = client.models.generate_content(
    model="gemini-3-flash-preview",

    contents="What is 125 * 48?",

    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                function_declarations=[
                    calculate_tool
                ]
            )
        ]
    )
)


# -----------------------------------
# 4. CHECK WHETHER GEMINI REQUESTED
#    A TOOL
# -----------------------------------

if response.function_calls:

    function_call = response.function_calls[0]

    print("Gemini requested:")
    print("Tool:", function_call.name)
    print("Arguments:", function_call.args)
    print("Full function call:", function_call)


    # -----------------------------------
    # 5. EXECUTE THE TOOL
    # -----------------------------------

    if function_call.name == "calculate":

        result = calculate(
            function_call.args["expression"]
        )

        print("\nTool result:")
        print(result)


    # -----------------------------------
    # 6. SEND TOOL RESULT BACK TO GEMINI
    # -----------------------------------

    final_response = client.models.generate_content(
        model="gemini-3-flash-preview",

        contents=[
            "What is 125 * 48?",

            response.candidates[0].content,

            types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        name=function_call.name,
                        response=result
                    )
                ]
            )
        ],

        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    function_declarations=[
                        calculate_tool
                    ]
                )
            ]
        )
    )


    print("\nFinal answer:")
    print(final_response.text)


else:

    print("\nGemini answered directly:")
    print(response.text)