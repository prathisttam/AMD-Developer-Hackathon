from crewai import Agent
from tools.agent_tools import docs_tool, file_read_tool, repl_tool

main_agent = Agent(
    role="You are a helpful assistant that can read files, execute code, and access documentation to assist with tasks. You are supposed to help the user to find the right information and execute code to solve problems. You have access to the following tools: DirectoryReadTool, FileReadTool, CodeInterpreterTool.",
    goal="Assist the user with their tasks by using the available tools to read files, execute code, and access documentation.",
    tools=[
        docs_tool,
        file_read_tool,
        repl_tool
    ]
)