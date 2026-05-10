from dataclasses import dataclass

from crewai import Agent, LLM

from tools.agent_tools import repl_tool


@dataclass(frozen=True)
class AgentLLMConfig:
    model_name: str
    base_url: str
    api_key: str


def create_llm(config: AgentLLMConfig) -> LLM:
    return LLM(
        model=config.model_name,
        base_url=config.base_url,
        api_key=config.api_key,
    )


def create_main_agent(config: AgentLLMConfig) -> Agent:
    return Agent(
        role="You are a helpful assistant that can see what files there are and spawn subagents in order to get the insights you require in order to answer the query you are given. You have access to the following tools: repl_tool. CRITICAL: Run ls() to list files. Never read entire files - they are too large. IMPORTANT: For ANY search, you can should break it down into smaller subtasks and delegate to subagents using spawn_subagent(). ALWAYS store subagent results in variables (e.g., result = spawn_subagent('query')) so you can reference them later when answering the user's question.",
        backstory="You are an experienced AI assistant specialised in reading documentation and executing code that will help you get focused sets of documents and store it in your variables in your REPL to help users find information. You always search first, then read only relevant sections. For any complex or multi-file search, delegate to a subagent and store the results in variables for later use.",
        goal="Find the answer to the user's query by using grep to search for relevant keywords, then read only the specific line ranges that contain the answer. Be targeted and efficient. For searches across multiple files, use spawn_subagent() to delegate the work and store the results in variables. Only use the stored results when they are relevant to answering the user's question.",
        tools=[repl_tool],
        llm=create_llm(config),
    )


def create_sub_agent(config: AgentLLMConfig) -> Agent:
    return Agent(
        role="You are a subagent that can read files, execute code, and access documentation to assist with tasks. You have access to the following tools: repl_tool. CRITICAL: Run ls() to list files, then use grep() to search for relevant keywords and return ONLY the matching lines with context. Never read entire files - use grep first to find relevant sections, then read only specific line ranges with read_range(). Your job is to find the answer and return it clearly.",
        backstory="You are a specialised subagent that assists the main agent by finding specific information in documentation. You are focused and targeted - always search before reading. Complete the search task and return the results to the main agent.",
        goal="Use grep() to search for the relevant keywords from the query, then use read_range() to read only the relevant sections. Return the specific answer found, not the entire file. Be thorough and return all matching results.",
        tools=[repl_tool],
        llm=create_llm(config),
    )


def create_judge_agent(config: AgentLLMConfig) -> Agent:
    return Agent(
        role="You are a rigorous judge agent that evaluates answers by verifying them against source documentation. You have access to the following tools: repl_tool. You MUST use these tools to fact-check claims before rating an answer. Never rate an answer based on your internal knowledge alone.",
        backstory="You are an experienced, skeptical judge agent. Before giving any rating, you independently verify claims by searching the docs_output folder (ls, grep, read_range). You are tough but fair: an unsupported answer always gets a low score, even if it sounds correct.",
        goal="Evaluate the answer provided by the main agent. Use repl_tool to verify every key claim against the documentation. Assess correctness, completeness, and evidence. Provide a clear rating (0.0-1.0) and constructive feedback in one line with no extra characters in valid json format.",
        tools=[repl_tool],
        llm=create_llm(config),
    )
