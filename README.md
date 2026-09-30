#####################WEEK 3#####################

-> created functions for agent tools like def calculate() and then created tool declarations so ai can understand how does this tool works and what parameters are needed :

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

giving it to the ai :
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                function_declarations=[
                    calculate_tool
                ]
            )
        ]
    )
  

-> then check whether the gemini requested tool and if yes execute and pass the result back to it
            types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        name=function_call.name,
                        response=result
                    )
                ]
            )



============================================================================================================



