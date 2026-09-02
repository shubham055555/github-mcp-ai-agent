import asyncio
import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set in .env"
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

gemini = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# PATHS
# ============================================================

PROJECT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PYTHON_PATH = os.path.join(
    PROJECT_DIR,
    ".venv",
    "Scripts",
    "python.exe"
)

SERVER_PATH = os.path.join(
    PROJECT_DIR,
    "server.py"
)


# ============================================================
# MCP SERVER PARAMETERS
# ============================================================

server_params = StdioServerParameters(
    command=PYTHON_PATH,
    args=[SERVER_PATH],
    env={
        **os.environ,
    },
)


# ============================================================
# CONVERT MCP TO GEMINI TOOLS
# ============================================================

def convert_mcp_tools(mcp_tools):

    declarations = []

    for tool in mcp_tools:

        declarations.append(
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description or "",
                parameters_json_schema=tool.input_schema,
            )
        )

    return declarations


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are an intelligent GitHub assistant.

You are connected to the authenticated GitHub account:

Owner / Username:
shubham055555

IMPORTANT CONTEXT:

- QueryMind is a repository owned by shubham055555.
- If the user mentions QueryMind without an owner,
  use owner = shubham055555.
- If the user mentions another repository without
  specifying an owner, assume it belongs to
  shubham055555 unless explicitly stated otherwise.

TOOL RULES:

1. Use MCP tools whenever GitHub information is required.

2. Never invent GitHub information.

3. Select the most appropriate tool automatically.

4. Use multiple tools when the task requires multiple steps.

5. If the result of one tool is needed to decide what to do
   next, call the next appropriate tool.

6. Do not ask unnecessary clarification questions when
   information can be inferred from the context.

7. If a tool returns an empty list, clearly explain that
   no matching results were found.

8. After completing all required tool calls, provide a
   concise natural-language answer.

9. Do not expose internal tool-calling details unless useful.
"""


# ============================================================
# EXECUTE MCP TOOL
# ============================================================

async def execute_mcp_tool(
    mcp_client,
    tool_name,
    arguments,
):

    print("\n" + "=" * 60)
    print("MCP TOOL CALL")
    print("=" * 60)

    print(f"Tool: {tool_name}")
    print(f"Arguments: {arguments}")

    try:

        result = await mcp_client.call_tool(
            tool_name,
            arguments,
        )

        if result.structured_content:

            tool_output = (
                result.structured_content
            )

        else:

            tool_output = [
                str(item)
                for item in result.content
            ]

        print("\nMCP RESULT:")

        print(
            json.dumps(
                tool_output,
                indent=2,
                default=str,
            )
        )

        return tool_output

    except Exception as error:

        error_output = {
            "error": str(error)
        }

        print("\nMCP ERROR:")
        print(error_output)

        return error_output


# ============================================================
# AI AGENT LOOP
# ============================================================

async def run_agent(
    mcp_client,
    question,
    mcp_tools,
):

    # --------------------------------------------------------
    # Convert MCP tools
    # --------------------------------------------------------

    declarations = convert_mcp_tools(
        mcp_tools
    )

    gemini_tools = types.Tool(
        function_declarations=declarations
    )

    # --------------------------------------------------------
    # Initial conversation
    # --------------------------------------------------------

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(
                    text=question
                )
            ],
        )
    ]

    # --------------------------------------------------------
    # AGENT LOOP
    # --------------------------------------------------------

    max_steps = 10

    for step in range(1, max_steps + 1):

        print("\n" + "=" * 60)
        print(f"AGENT STEP {step}")
        print("=" * 60)

        # ----------------------------------------------------
        # Ask Gemini
        # ----------------------------------------------------

        response = gemini.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[gemini_tools],
            ),
        )

        # ----------------------------------------------------
        # Find function calls
        # ----------------------------------------------------

        function_calls = []

        for part in response.candidates[0].content.parts:

            if part.function_call:

                function_calls.append(
                    part.function_call
                )

        # ----------------------------------------------------
        # No tool call
        # ----------------------------------------------------

        if not function_calls:

            return response.text

        # ----------------------------------------------------
        # Add Gemini response to conversation
        # ----------------------------------------------------

        contents.append(
            response.candidates[0].content
        )

        tool_response_parts = []

        # ----------------------------------------------------
        # Execute requested tools
        # ----------------------------------------------------

        for function_call in function_calls:

            tool_name = function_call.name

            arguments = dict(
                function_call.args
            )

            tool_output = await execute_mcp_tool(
                mcp_client,
                tool_name,
                arguments,
            )

            # ------------------------------------------------
            # Send result back to Gemini
            # ------------------------------------------------

            tool_response_parts.append(
                types.Part.from_function_response(
                    name=tool_name,
                    response={
                        "result": tool_output
                    },
                )
            )

        # ----------------------------------------------------
        # Add MCP results to conversation
        # ----------------------------------------------------

        contents.append(
            types.Content(
                role="user",
                parts=tool_response_parts,
            )
        )

    # --------------------------------------------------------
    # Safety limit
    # --------------------------------------------------------

    return (
        "I could not complete the request within "
        "the maximum number of agent steps."
    )


# ============================================================
# MAIN
# ============================================================

async def main():

    print("=" * 60)
    print("GITHUB MULTI-STEP AI + MCP AGENT")
    print("=" * 60)

    # --------------------------------------------------------
    # Connect to MCP server
    # --------------------------------------------------------

    async with Client(
        stdio_client(server_params)
    ) as mcp_client:

        print(
            "\nConnected to GitHub MCP Server"
        )

        # ----------------------------------------------------
        # Discover tools
        # ----------------------------------------------------

        tools_result = await mcp_client.list_tools()

        print("\nMCP tools discovered:")

        for tool in tools_result.tools:

            print(
                f"- {tool.name}"
            )

        # ----------------------------------------------------
        # User question
        # ----------------------------------------------------

        question = input(
            "\nAsk something about your GitHub: "
        )

        # ----------------------------------------------------
        # Run agent
        # ----------------------------------------------------

        answer = await run_agent(
            mcp_client,
            question,
            tools_result.tools,
        )

        # ----------------------------------------------------
        # Final answer
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("FINAL AI ANSWER")
        print("=" * 60)

        print(answer)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())