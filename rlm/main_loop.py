from pydantic import BaseModel
from agents import main_agent, judge_agent


class JudgeResult(BaseModel):
    rating: float
    reasoning: str


class MainLoop:
    def main_loop(self, query: str) -> str:
        prompt = query
        best_response = ""
        best_score = 0.0

        for _ in range(5):
            response = main_agent.kickoff(messages=prompt)

            judgement = judge_agent.kickoff(
                messages=f"""
                For the query: {query}
                This is the response: {response}
                Give your judgement for this response.
                """,
                response_format=JudgeResult,
            )

            rating = judgement.pydantic.rating  # type: ignore
            reasoning = judgement.pydantic.reasoning  # type: ignore

            if rating > best_score:
                best_score = rating
                best_response = str(response)

            if rating > 0.7:
                return str(response)

            prompt = (
                f"Original query: {query}\n"
                f"Your previous response: {response}\n"
                f"Why it was rejected: {reasoning}\n"
                "Improve your answer based on the feedback above."
            )

        return best_response

