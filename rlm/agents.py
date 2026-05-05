from crewai import Agent, LLM
from tools.agent_tools import repl_tool

main_llm = LLM(model="ollama/gemma4:latest", base_url="http://localhost:11434")

sub_llm = LLM(model="ollama/gemma4:latest", base_url="http://localhost:11434")

judge_llm = LLM(model="ollama/gemma4:latest", base_url="http://localhost:11434")

main_agent = Agent(
    role="You are a helpful assistant that can read files, execute code, and access documentation to assist with tasks. You have access to the following tools: repl_tool. CRITICAL: Run ls() to list files, then use grep() to search for relevant keywords BEFORE reading entire files. Only read specific line ranges using read_range() after finding matches. Never read entire files - they are too large. IMPORTANT: For ANY search that is too complex, you can break it down into smaller subtasks and delegate to subagents using spawn_subagent() in natural language.",
    backstory="You are an experienced AI assistant specialised in reading documentation and executing code that will help you get focused sets of documents and store it in your variables in your REPL to help users find information. You always search first, then read only relevant sections. For any complex or multi-file search, delegate to a subagent.",
    goal="Find the answer to the user's query by using grep to search for relevant keywords, then read only the specific line ranges that contain the answer. Be targeted and efficient. For searches across multiple files, ALWAYS use spawn_subagent() to delegate the work.",
    tools=[repl_tool],
    llm=main_llm,
)

sub_agent = Agent(
    role="You are a subagent that can read files, execute code, and access documentation to assist with tasks. You have access to the following tools: repl_tool. CRITICAL: Run ls() to list files, then use grep() to search for relevant keywords and return ONLY the matching lines with context. Never read entire files - use grep first to find relevant sections, then read only specific line ranges with read_range(). Your job is to find the answer and return it clearly.",
    backstory="You are a specialised subagent that assists the main agent by finding specific information in documentation. You are focused and targeted - always search before reading. Complete the search task and return the results to the main agent.",
    goal="Use grep() to search for the relevant keywords from the query, then use read_range() to read only the relevant sections. Return the specific answer found, not the entire file. Be thorough and return all matching results.",
    tools=[repl_tool],
    llm=sub_llm,
)

judge_agent = Agent(
    role="You are a rigorous judge agent that evaluates answers by verifying them against source documentation. You have access to the following tools: repl_tool. You MUST use these tools to fact-check claims before rating an answer. Never rate an answer based on your internal knowledge alone.",
    backstory="You are an experienced, skeptical judge agent. Before giving any rating, you independently verify claims by searching the docs_output folder (ls, grep, read_range). You are tough but fair: an unsupported answer always gets a low score, even if it sounds correct.",
    goal="Evaluate the answer provided by the main agent. Use repl_tool to verify every key claim against the documentation. Assess correctness, completeness, and evidence. Provide a clear rating (0.0-1.0) and constructive feedback.",
    llm=judge_llm,
    tools=[repl_tool],
)
