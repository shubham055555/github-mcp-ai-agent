\# GitHub MCP AI Agent



An AI-powered GitHub assistant built using the Model Context Protocol (MCP), GitHub REST API, Python, and Google Gemini.



The project allows an AI agent to interact with GitHub repositories and issues through MCP tools instead of directly coupling the AI model with the GitHub API.



\## Features



\* GitHub API authentication using Personal Access Token

\* MCP-based GitHub server

\* Gemini-powered AI agent

\* Four GitHub MCP tools

\* Repository and issue search

\* Open, closed, and all issue filtering

\* Individual GitHub issue retrieval

\* Multi-step AI tool execution

\* Deterministic local evaluation

\* 20/20 MCP evaluation tests passed



\## Architecture



```text

&#x20;                   User Query

&#x20;                       |

&#x20;                       v

&#x20;               +----------------+

&#x20;               |  Gemini Agent  |

&#x20;               |  ai\_client.py  |

&#x20;               +-------+--------+

&#x20;                       |

&#x20;                       v

&#x20;               +----------------+

&#x20;               |   MCP Client   |

&#x20;               |   client.py    |

&#x20;               +-------+--------+

&#x20;                       |

&#x20;                 STDIO Transport

&#x20;                       |

&#x20;                       v

&#x20;               +----------------+

&#x20;               |   MCP Server   |

&#x20;               |   server.py    |

&#x20;               +-------+--------+

&#x20;                       |

&#x20;                       v

&#x20;               +----------------+

&#x20;               | GitHub REST API|

&#x20;               +----------------+

```



\## MCP Tools



The MCP server currently provides four tools.



\### 1. list\_repositories



Lists repositories belonging to the authenticated GitHub user.



\### 2. list\_issues



Lists issues from a specified GitHub repository.



Supported states:



```text

open

closed

all

```



\### 3. get\_issue



Retrieves details about a specific GitHub issue using its issue number.



\### 4. search\_issues



Searches repository issues using a search query.



Example queries:



```text

bug

authentication

API

security

database

login

```



\## Project Structure



```text

github-mcp-server/

|

+-- .env

+-- .gitignore

+-- README.md

+-- requirements.txt

|

+-- github\_client.py

+-- server.py

+-- client.py

+-- ai\_client.py

+-- evaluation.py

|

+-- evaluation\_results/

&#x20;   +-- local\_evaluation\_YYYYMMDD\_HHMMSS.json

```



\## File Description



| File               | Purpose                        |

| ------------------ | ------------------------------ |

| `github\_client.py` | GitHub REST API client         |

| `server.py`        | MCP server and GitHub tools    |

| `client.py`        | MCP client                     |

| `ai\_client.py`     | Gemini AI agent                |

| `evaluation.py`    | Local deterministic evaluation |

| `.env`             | API credentials                |

| `requirements.txt` | Python dependencies            |



\## Requirements



\* Python 3.11 or higher

\* GitHub account

\* GitHub Personal Access Token

\* Google Gemini API key

\* MCP Python SDK



\## Installation



Clone the repository:



```bash

git clone <YOUR\_GITHUB\_REPOSITORY\_URL>

cd github-mcp-server

```



Create a virtual environment:



```bash

python -m venv .venv

```



Activate the virtual environment on Windows:



```cmd

.venv\\Scripts\\activate

```



Install dependencies:



```bash

pip install -r requirements.txt

```



\## Environment Variables



Create a `.env` file in the project root:



```env

GITHUB\_TOKEN=your\_github\_token

GEMINI\_API\_KEY=your\_gemini\_api\_key

```



Do not commit the `.env` file to GitHub.



The `.gitignore` file excludes sensitive and generated files such as:



```text

.env

.venv/

\_\_pycache\_\_/

evaluation\_results/

```



\## Running the MCP Server



Check the server syntax:



```cmd

python -m py\_compile server.py

```



Run the MCP server:



```cmd

python server.py

```



The server communicates through STDIO and can be connected to using an MCP client or MCP Inspector.



\## Running the MCP Client



Run:



```cmd

python client.py

```



The MCP client connects to the local MCP server using STDIO transport.



\## Running the AI Agent



Run:



```cmd

python ai\_client.py

```



Example query:



```text

Show me all open issues in QueryMind

```



The AI agent identifies the appropriate MCP tool and executes it through the MCP client and MCP server.



Example tool selection:



```text

User Query

&#x20;   |

&#x20;   v

Gemini

&#x20;   |

&#x20;   v

list\_issues

&#x20;   |

&#x20;   v

MCP Client

&#x20;   |

&#x20;   v

MCP Server

&#x20;   |

&#x20;   v

GitHub API

```



\## Evaluation



The project includes a deterministic local evaluation system.



Run:



```cmd

python -m py\_compile evaluation.py

python evaluation.py

```



The evaluation checks:



\* MCP tool availability

\* Tool execution

\* Expected arguments

\* Repository operations

\* Issue listing

\* Issue searching

\* Individual issue retrieval

\* Multi-step scenarios



\## Evaluation Results



The current evaluation contains 20 test cases.



```text

Total Tests              : 20

Completed Tests          : 20

Passed Tests             : 20

Failed Tests             : 0

Execution Errors         : 0



Tool Accuracy            : 100.00%

Argument Accuracy        : 100.00%

Tool Execution Success   : 100.00%

```



All 20 tests passed successfully.



Evaluation results are saved automatically in:



```text

evaluation\_results/

```



\## Example Workflow



A user asks:



```text

Show me the open issues in QueryMind.

```



The system follows this workflow:



```text

User

&#x20;|

&#x20;v

Gemini AI Agent

&#x20;|

&#x20;v

MCP Tool Selection

&#x20;|

&#x20;v

MCP Client

&#x20;|

&#x20;v

MCP Server

&#x20;|

&#x20;v

GitHub REST API

&#x20;|

&#x20;v

GitHub Data

&#x20;|

&#x20;v

MCP Client

&#x20;|

&#x20;v

Gemini AI Agent

&#x20;|

&#x20;v

Final Response

```



\## Why MCP?



Model Context Protocol provides a standardized interface between AI applications and external tools and data sources.



In this project, GitHub functionality is exposed as MCP tools. This allows the AI agent to interact with GitHub through a structured tool interface rather than directly implementing every GitHub operation inside the AI application.



This architecture also makes the GitHub tools reusable by different MCP-compatible clients.



\## Project Goals



This project demonstrates:



1\. Building an MCP server

2\. Creating MCP tools

3\. Creating an MCP client

4\. Integrating an AI model with MCP

5\. Connecting external APIs through MCP tools

6\. Implementing multi-step agent workflows

7\. Testing MCP tools independently

8\. Building a deterministic evaluation pipeline



\## Future Improvements



Possible future improvements include:



\* Create GitHub issues through MCP

\* Update GitHub issues

\* Close GitHub issues

\* Create pull requests

\* Search repositories

\* Analyze repository activity

\* Add GitHub Actions CI/CD

\* Add more comprehensive agent evaluation

\* Add persistent conversation memory

\* Add a web interface

\* Support multiple GitHub accounts

\* Add structured logging and monitoring



\## Current Status



```text

GitHub API Integration       Completed

MCP Server                   Completed

MCP Client                   Completed

Gemini AI Agent              Completed

MCP Inspector Testing        Completed

Multi-step Tool Calling      Completed

Local Evaluation             Completed

20/20 Tests Passed           Completed

Documentation               Completed

```



\## License



This project is intended for learning, experimentation, and open-source development.



