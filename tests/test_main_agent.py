import os
from crewai import Task, Crew

os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_MODEL_NAME"] = "gemma4:e2b"

# To run test cases: python -m pytest tests/test_main_agent.py -v -s
# To run specified test cases: python -m pytest tests/test_main_agent.py::{test_case_name} -v -s


def test_repl_tool_returns_function_results():
    from tools.agent_tools import repl_tool

    result = repl_tool._run("ls()")

    assert isinstance(result, str)
    assert result != "Executed successfully"


def test_repl_tool_persists_state_between_calls():
    from tools.agent_tools import repl_tool

    repl_tool._run("saved_value = 42")
    result = repl_tool._run("saved_value")

    assert result.strip() == "42"

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


def test_zero_shot_self_routing():
    from rlm.main_agent import main_agent

    task = Task(
        description="According to the findings in select-then-solve, why isn't zero-shot self-routing a universally effective strategy for all LLMs?",
        agent=main_agent,
        expected_output="Explanation of why zero-shot self-routing isn't effective for all LLMs",
    )
    crew = Crew(agents=[main_agent], tasks=[task], verbose=True)
    result = crew.kickoff()

    # Expected answer is something like: "The paper demonstrates that zero-shot self-routing relies heavily on the baseline capability of the model. It was only effective for the most capable model tested (GPT-5, achieving 67.1%), but failed for weaker models, indicating it is not a viable strategy across the board."
    print(f"Result: {result}")


def test_main_agent_calls_subagent():
    """
    Test that main agent spawns a subagent when given a query requiring parallel search.
    The log should show [TOOL] spawn_subagent called with: '...'
    """
    from rlm.main_agent import main_agent

    task = Task(
        description="Search for the term 'REPL' across all documentation files. Find all mentions and return the results.",
        agent=main_agent,
        expected_output="List of all REPL mentions with file locations",
    )
    crew = Crew(agents=[main_agent], tasks=[task], verbose=True)
    
    # Run the agent
    crew.kickoff()

    # If the test fails, Pytest will automatically print everything captured here!
    # assert "[TOOL] spawn_subagent called" in ascii_output, (
    #     f"Expected spawn_subagent to be called. Output (first 1000): {ascii_output[:1000]}..."
    # )


"""
1. Factoid / Direct Retrieval
Tests if the LLM can locate specific entities and acronyms without relying on prior knowledge.

Query: What is the name of the unified evaluation framework introduced in the paper to test inference-time reasoning strategies?

Answer: PARADIGM.

2. Multi-Hop / Aggregation
Tests if the system can accurately pull together distinct data points from the text.

Query: Which four large language models were evaluated using the framework, and what was the exact improvement in average accuracy achieved by the learned router compared to the Direct prompting baseline?

Answer: The models evaluated were GPT-5, Gemini-3-Flash, Qwen3-Max, and Qwen3-30B. The router improved average accuracy from 47.6% (Direct) to 53.1%.

3. Reasoning / Implicit Context
Tests the LLM's ability to synthesize a conclusion explicitly stated in the findings.

Query: According to the findings, why isn't zero-shot self-routing a universally effective strategy for all LLMs?

Answer: The paper demonstrates that zero-shot self-routing relies heavily on the baseline capability of the model. It was only effective for the most capable model tested (GPT-5, achieving 67.1%), but failed for weaker models, indicating it is not a viable strategy across the board.

4. Quote / Exact Extraction
Forces the LLM to locate and extract a precise string, proving it is looking at the source text.

Query: What is the exact sentence the authors use to summarize their argument about how reasoning paradigm selection should be handled?

Answer: "Our results argue that reasoning paradigm selection should be a per-task decision made by a learned router, not a fixed architectural choice."

5. Distractor / Negative Constraint
Tests if the LLM hallucinated an answer that sounds plausible but isn't actually in the text.

Query: According to the text, what specific reinforcement learning algorithm was used to train the PARADIGM router?

Answer: The text mentions that recent work has explored reinforcement learning for inference-time reasoning, but it does not specify the exact reinforcement learning algorithm used to train the PARADIGM router itself.
"""
