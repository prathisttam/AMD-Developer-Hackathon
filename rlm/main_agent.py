from crewai import Agent
from tools.agent_tools import docs_tool, file_read_tool, repl_tool

main_agent = Agent(
    role="You are a helpful assistant that can read files, execute code, and access documentation to assist with tasks. You are supposed to help the user to find the right information by executing code to answer their queries. You have access to the following tools: DirectoryReadTool, FileReadTool, CodeInterpreterTool.",
    goal="Run python code using the CodeInterpreterTool to explore and look for information to answer the user's query.",
    tools=[
        docs_tool,
        file_read_tool,
        repl_tool
    ]
)

sub_agent = Agent(
    role="You are a subagent that can read files, execute code, and access documentation to assist with tasks. You are supposed to help the main agent that spawned you to find the right information asked by the main agent and return it. You have access to the following tools: DirectoryReadTool, FileReadTool, CodeInterpreterTool.",
    goal="Run python code using the CodeInterpreterTool to explore and look for information to answer the user's query.",
    tools=[
        docs_tool,
        file_read_tool,
        repl_tool
    ]
)