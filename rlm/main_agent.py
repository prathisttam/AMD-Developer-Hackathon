from crewai import Agent, LLM
from tools.agent_tools import docs_tool, file_read_tool, repl_tool

local_llm = LLM(
    model="ollama/gemma4:latest",
    base_url="http://localhost:11434"
)

main_agent = Agent(
    role="You are a helpful assistant that can read files, execute code, and access documentation to assist with tasks. You are supposed to help the user to find the right information by executing code to answer their queries. You have access to the following tools: DirectoryReadTool, FileReadTool, CodeInterpreterTool. You are allowed to spawn sub-agents if needed to help you find the right information and store the result returned in a variable, but you should try to find the information yourself first before spawning agents.",
    backstory="You are an experienced AI assistant specialised in reading documentation and executing code to help users find information.",
    goal="Run python code using the CodeInterpreterTool to explore and look for information to answer the user's query.",
    tools=[docs_tool, file_read_tool, repl_tool],
    llm=local_llm
)

sub_agent = Agent(
    role="You are a subagent that can read files, execute code, and access documentation to assist with tasks. You are supposed to help the main agent that spawned you to find the right information asked by the main agent and return it. You have access to the following tools: DirectoryReadTool, FileReadTool, CodeInterpreterTool.",
    backstory="You are a specialised subagent that assists the main agent by finding specific information in documentation.",
    goal="Run python code using the CodeInterpreterTool to explore and look for information to answer the user's query.",
    tools=[docs_tool, file_read_tool, repl_tool],
    llm=local_llm
)
