import asyncio
import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")


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
# MCP SERVER CONFIGURATION
# ============================================================

server_params = StdioServerParameters(
    command=PYTHON_PATH,
    args=[SERVER_PATH],
    env={
        **os.environ,
    },
)


# ============================================================
# CONVERT MCP TOOL → GEMINI FUNCTION DECLARATION
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
# MAIN
# ============================================================

async def main():

    print("=" * 60)
    print("GITHUB AI + MCP AGENT")
    print("=" * 60)

    # --------------------------------------------------------
    # Connect to MCP Server
    # --------------------------------------------------------

    async with Client(
        stdio_client(server_params)
    ) as mcp_client:

        print("\nConnected to GitHub MCP Server")

        # ----------------------------------------------------
        # Discover MCP tools
        # ----------------------------------------------------

        tools_result = await mcp_client.list_tools()

        print("\nMCP tools discovered:")

        for tool in tools_result.tools:
            print(f"- {tool.name}")

        # ----------------------------------------------------
        # Convert tools for Gemini
        # ----------------------------------------------------

        declarations = convert_mcp_tools(
            tools_result.tools
        )

        gemini_tools = types.Tool(
            function_declarations=declarations
        )

        # ----------------------------------------------------
        # User question
        # ----------------------------------------------------

        question = input(
            "\nAsk something about your GitHub: "
        )

        # ----------------------------------------------------
        # Conversation contents
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Gemini request
        # ----------------------------------------------------

        response = gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a GitHub assistant. "
                    "Use the available GitHub MCP tools "
                    "when GitHub data is required. "
                    "Never invent GitHub information."
                ),
                tools=[gemini_tools],
            ),
        )

        # ----------------------------------------------------
        # Process Gemini response
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

            print("\n" + "=" * 60)
            print("AI ANSWER")
            print("=" * 60)

            print(response.text)

            return

        # ----------------------------------------------------
        # Execute MCP tools
        # ----------------------------------------------------

        tool_response_parts = []

        for function_call in function_calls:

            tool_name = function_call.name

            arguments = dict(
                function_call.args
            )

            print("\n" + "=" * 60)
            print("AI SELECTED MCP TOOL")
            print("=" * 60)

            print(f"Tool: {tool_name}")
            print(f"Arguments: {arguments}")

            # ----------------------------------------------
            # Call MCP tool
            # ----------------------------------------------

            result = await mcp_client.call_tool(
                tool_name,
                arguments,
            )

            # ----------------------------------------------
            # Extract result
            # ----------------------------------------------

            if result.structured_content:

                tool_output = (
                    result.structured_content
                )

            else:

                tool_output = str(
                    result.content
                )

            print("\nMCP RESULT:")
            print(tool_output)

            # ----------------------------------------------
            # Send result back to Gemini
            # ----------------------------------------------

            tool_response_parts.append(
                types.Part.from_function_response(
                    name=tool_name,
                    response={
                        "result": tool_output
                    },
                )
            )

        # ----------------------------------------------------
        # Add tool result to conversation
        # ----------------------------------------------------

        contents.append(
            response.candidates[0].content
        )

        contents.append(
            types.Content(
                role="user",
                parts=tool_response_parts,
            )
        )

        # ----------------------------------------------------
        # Final Gemini response
        # ----------------------------------------------------

        final_response = gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Answer the user's GitHub question "
                    "using the MCP tool results. "
                    "Do not invent information."
                ),
                tools=[gemini_tools],
            ),
        )

        # ----------------------------------------------------
        # Final answer
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("FINAL AI ANSWER")
        print("=" * 60)

        print(final_response.text)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())