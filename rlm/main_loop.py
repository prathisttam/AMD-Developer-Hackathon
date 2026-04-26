from pydantic import BaseModel
from agents import main_agent, judge_agent


class JudgeResult(BaseModel):
    rating: float
    reasoning: str


class MainLoop:
    def __init__(self) -> None:
        self.best_response = ""
        self.best_score = 0.0

    def main_loop(self, query: str, iteration: int) -> str:
        if iteration == 5:
            return self.best_response

        response = main_agent.kickoff(messages=query)

        judgement = judge_agent.kickoff(
            messages=f"""
            For the query: {query}\n
            This is the response: {response}\n
            Give your judgement for this response.
            """,
            response_format=JudgeResult,
        )
        return (
            str(response)
            if judgement.pydantic.rating > 0.7  # type: ignore
            else self.main_loop(query, iteration + 1)
        )
