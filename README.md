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

-> added multiple tools (time, calculator and websearch) and the model chose if or not to use them, also added a max iteration limit so the agent doesn't loop infinitely

manual tool-calling loop + tool registry + 3 tools + error handling + max-iteration limit + understanding of automatic function calling

we can also add **timeout** for cases like the tools we are using (here duckduckgo for web search) get stuck.

we should also add trace logging-
**Trace Logging**
Trace logging records the execution path of the agent for each task.

A trace can contain:
- User question
- Iteration number
- Tool selected by the model
- Tool arguments
- Tool result
- Final answer

Example flow:

User Question
→ Gemini
→ search_web(query)
→ search result
→ Gemini
→ Final Answer

Trace logging is useful for debugging agent behavior, analyzing
unnecessary tool calls, and evaluating agent performance.

For this learning project, persistent trace-file logging is not
implemented; the tool calls and results are currently printed to
the terminal.


=============================================================================================================
=============================================================================================================
=============================================================================================================
=============================================================================================================

############### WEEK 4 #############################


-> adding fetch_page() tool to go from this:-
    search_web(query)
        ↓
    title + URL + snippet
        ↓
    Gemini


    to this:-

    search_web(query)
        ↓
    Gemini selects useful URL
        ↓
    fetch_page(url)
        ↓
    page content
        ↓
    Gemini
        ↓
    answer

==========================================================

cleaning the page before sending it to gemini:-

**Context Engineering**

Context engineering is the practice of controlling what information is given to an LLM, how it is structured, and how much of it is included in the model's context.

Earlier, when we used `search_web`, the tool returned search results containing information such as the title, URL, and snippet:

```text
search_web()
    ↓
Search results
    ↓
title + URL + snippet
    ↓
Gemini
```

When we added `fetch_page`, the agent could follow a URL and retrieve the webpage itself. However, a webpage contains much more than the information we actually need:

```text
fetch_page(url)
    ↓
Raw HTML
    ↓
Remove script/style/nav/footer
    ↓
Extract webpage text
    ↓
Limit to 12,000 characters
    ↓
Gemini
```

This is already a basic form of context engineering. Instead of sending the entire raw HTML—including JavaScript, CSS, navigation elements, and other unnecessary data—we clean the page and limit the amount of information sent to the model.

However, this can still be improved. Even after basic cleaning, the remaining text may contain advertisements, sidebars, unrelated sections, repeated content, or information that is irrelevant to the user's question. A better approach is to progressively filter the information so that only the most useful content reaches the LLM:

```text
Webpage
   ↓
Extract text
   ↓
Remove unnecessary content
   ↓
Identify relevant sections
   ↓
Keep only useful information
   ↓
Gemini
```

This is better because the model receives **less noise and more relevant information**, which can reduce token usage and improve the quality of its response. Context engineering is therefore not simply "cleaning webpages"; it is about designing the flow of information between the user, agent, tools, and LLM so that the model receives the right information at the right time.


-> python execution tool and tool failures on hold