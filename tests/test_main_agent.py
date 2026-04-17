import os
from crewai import Task, Crew
from tools.agent_tools import docs_tool, file_read_tool, repl_tool

os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_MODEL_NAME"] = "gemma4:latest"

# To run test cases: python -m pytest tests/test_main_agent.py -v

def test_docs_tool_finds_rlm_md():
    result = docs_tool.run(query="recursive language models")
    assert "RLM.md" in result or len(result) > 0


def test_file_read_tool_can_read_rlm_md():
    result = file_read_tool.run("docs_output/RLM.md")
    assert "Recursive Language Models" in result or len(result) > 0


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


def test_harry_centaur_names():
    from rlm.main_agent import main_agent

    task = Task(
        description="What are the exact names of the three centaurs Harry encounters in the Forbidden Forest?",
        agent=main_agent,
        expected_output="Ronan, Bane, and Firenze",
    )
    crew = Crew(agents=[main_agent], tasks=[task], verbose=True)
    result = crew.kickoff()
    result_str = str(result).lower()
    print(f"Result: {result}")
    assert "ronan" in result_str and "bane" in result_str and "firenze" in result_str, (
        f"Expected 'Ronan, Bane, and Firenze', got: {result}"
    )


"""
1. Factoid / Direct Retrieval
Tests the LLM’s ability to find specific, explicitly stated entities (names, places, numbers).

Query: Where exactly does Harry sleep at the Dursleys' house before he is moved to Dudley's second bedroom?

Answer: In the cupboard under the stairs.

Query: What are the exact names of the three centaurs Harry encounters in the Forbidden Forest?

Answer: Ronan, Bane, and Firenze.

2. Multi-Hop / Aggregation
Tests the LLM’s ability to pull together information from different parts of the text or combine two related facts.

Query: Who arranged for Harry to receive the Nimbus 2000 broomstick, and what specific position was he chosen to play on the Gryffindor Quidditch team?

Answer: Professor McGonagall arranged for the broomstick, and he plays the position of Seeker.

Query: Which three professors helped create the obstacles guarding the Sorcerer's Stone, and what was the specific obstacle created by Professor Sprout?

Answer: Professors Sprout, Flitwick, McGonagall, Quirrell, and Snape (any three of these, plus Dumbledore). Professor Sprout provided the Devil's Snare plant.

3. Reasoning / Implicit Context
Tests the LLM’s ability to understand cause and effect, or to infer why an event happened based on retrieved context.

Query: Why did Harry and Ron accidentally lock the mountain troll inside the girls' bathroom?

Answer: They were trying to lock the troll away to trap it, but they didn't realize until it was too late that Hermione was inside that specific bathroom.

Query: How does Harry ultimately manage to get the Sorcerer's Stone out of the Mirror of Erised?

Answer: Because he only wanted to find the stone, not use it. The mirror's magic was designed by Dumbledore to only yield the stone to someone who wanted to find it but not use it for selfish gain.

4. Quote / Exact Extraction
Tests the LLM’s ability to pull an exact string of text rather than paraphrasing.

Query: What is the exact inscription written around the top of the Mirror of Erised?

Answer: "Erised stra ehru oyt ube cafru oyt on wohsi"

5. Distractor / Negative Constraint
Tests if the LLM hallucinates outside knowledge or relies strictly on the provided text.

Query: According to the text, what spell does Hermione use to fix Harry's glasses on the Hogwarts Express?

Answer: Hermione does not fix Harry's glasses on the Hogwarts Express in the text of the book. (Note: She fixes them in Diagon Alley in the movie adaptation, making this a great test to see if the LLM relies on its training data instead of your specific PDF document).
"""
