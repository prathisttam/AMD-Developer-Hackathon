import os
from crewai import Task, Crew
from tools.agent_tools import docs_tool, file_read_tool, repl_tool

os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_MODEL_NAME"] = "gemma4:latest"


def test_docs_tool_finds_rlm_md():
    result = docs_tool.run("recursive language models")
    assert "RLM.md" in result or len(result) > 0


def test_file_read_tool_can_read_rlm_md():
    result = file_read_tool.run("docs_output/RLM.md")
    assert "Recursive Language Models" in result or len(result) > 0


def test_main_agent_has_all_tools():
    from rlm.main_agent import main_agent

    tool_names = [t.name for t in main_agent.tools]
    assert "DirectoryReadTool" in tool_names or "docs_tool" in tool_names
    assert "FileReadTool" in tool_names or "file_read_tool" in tool_names
    assert "CodeInterpreterTool" in tool_names or "repl_tool" in tool_names


def test_main_agent_can_query_docs():
    from rlm.main_agent import main_agent

    task = Task(
        description="What is the paper about? Find information about RLMs in the docs.",
        agent=main_agent,
        expected_output="Information about Recursive Language Models",
    )
    crew = Crew(agents=[main_agent], tasks=[task], verbose=True)
    result = crew.kickoff()
    assert result is not None and len(str(result)) > 0
