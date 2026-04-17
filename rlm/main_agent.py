from crewai import Agent, LLM
from tools.agent_tools import docs_tool, file_read_tool, repl_tool

main_llm = LLM(model="ollama/gemma4:latest", base_url="http://localhost:11434")

sub_llm = LLM(model="ollama/gemma4:latest", base_url="http://localhost:11434")

main_agent = Agent(
    role="You are a helpful assistant that can read files, execute code, and access documentation to assist with tasks. You have access to the following tools: repl_tool. CRITICAL: You MUST use grep() to search for relevant keywords BEFORE reading entire files. Only read specific line ranges using read_range() after finding matches. Never read entire files - they are too large. Use spawn_subagent() to parallelize searches.",
    backstory="You are an experienced AI assistant specialised in reading documentation and executing code that will help you get focused sets of documents and store it in your variables in your REPL to help users find information. You always search first, then read only relevant sections.",
    goal="Find the answer to the user's query by using grep to search for relevant keywords, then read only the specific line ranges that contain the answer. Be targeted and efficient.",
    tools=[repl_tool],
    llm=main_llm,
)

sub_agent = Agent(
    role="You are a subagent that can read files, execute code, and access documentation to assist with tasks. You have access to the following tools: repl_tool. CRITICAL: Use grep() to search for relevant keywords and return ONLY the matching lines with context. Never read entire files - use grep first to find relevant sections, then read only specific line ranges with read_range().",
    backstory="You are a specialised subagent that assists the main agent by finding specific information in documentation. You are focused and targeted - always search before reading.",
    goal="Use grep() to search for the relevant keywords from the query, then use read_range() to read only the relevant sections. Return the specific answer found, not the entire file.",
    tools=[repl_tool],
    llm=sub_llm,
)
