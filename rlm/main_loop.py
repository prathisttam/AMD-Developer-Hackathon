import re
import traceback
from pydantic import BaseModel
from rlm.agents import main_agent, judge_agent
from tools.agent_tools import repl_tool


class JudgeResult(BaseModel):
    rating: float
    reasoning: str


def _extract_rating(raw: str) -> float | None:
    """Try to extract a rating between 0.0 and 1.0 from raw text."""
    matches = re.findall(r"\b([0-1](?:\.\d+)?)\b", raw)
    for match in matches:
        val = float(match)
        if 0.0 <= val <= 1.0:
            return val
    return None


def _get_raw_output(output) -> str:
    """Safely extract raw string output from CrewAI LiteAgentOutput."""
    return getattr(output, "raw", str(output))


class MainLoop:
    async def main_loop(self, query: str) -> str:
        prompt = query
        best_response = ""
        best_score = 0.0

        for iteration in range(5):
            print(f"[MainLoop] Iteration {iteration + 1}/5")

            # Reset REPL session to prevent state leakage between iterations
            repl_tool._session_globals = None

            # 3. Try/except around main agent generation
            try:
                response_obj = main_agent.kickoff(messages=prompt)

            except Exception as e:
                traceback.print_exc()
                if best_response:
                    return best_response
                prompt = (
                    f"Original query: {query}\n"
                    f"Your previous attempt failed with error: {e}\n"
                    "Please try again."
                )
                continue

            response = _get_raw_output(response_obj)

            # 1. Grounded judge prompt: explicitly instructs judge to use repl_tool
            judge_prompt = (
                f"You are evaluating the following answer to a query.\n\n"
                f"Query: {query}\n\n"
                f"Answer: {response}\n\n"
                f"CRITICAL INSTRUCTIONS:\n"
                f"1. You MUST verify the answer against the source documentation using your repl_tool.\n"
                f"   - First run ls() to see available docs.\n"
                f"   - Use grep() to search for key claims made in the answer.\n"
                f"   - Use read_range() to verify specific sections.\n"
                f"2. Rate the answer on a scale of 0.0 to 1.0 based on:\n"
                f"   - Correctness (are facts accurate per the docs?)\n"
                f"   - Completeness (does it fully answer the query?)\n"
                f"   - Evidence (are claims supported by doc citations?)\n"
                f"3. Provide clear reasoning for your rating.\n"
                f'4. Return ONLY valid JSON matching this schema: {{"rating": float, "reasoning": string}}'
            )

            # 2. Try/except around judge evaluation + structured output fallback
            try:
                judgement = judge_agent.kickoff(
                    messages=judge_prompt,
                    response_format=JudgeResult,
                )
            except Exception as _:
                traceback.print_exc()
                if best_response:
                    return best_response
                prompt = (
                    f"Original query: {query}\n"
                    f"Your previous response: {response}\n"
                    f"The judge evaluation failed. Please improve your answer and ensure it is well-supported by the documentation."
                )
                continue

            # Structured output fallback: handle None pydantic output
            rating = None
            reasoning = None

            pydantic_result = getattr(judgement, "pydantic", None)
            if pydantic_result is not None:
                rating = getattr(pydantic_result, "rating", None)
                reasoning = getattr(pydantic_result, "reasoning", None)
            else:
                raw_judge = _get_raw_output(judgement)

                rating = _extract_rating(raw_judge)
                reasoning = raw_judge.strip() if raw_judge else "No reasoning provided."

            if rating is None or not isinstance(rating, (int, float)):
                if best_response:
                    return best_response
                prompt = (
                    f"Original query: {query}\n"
                    f"Your previous response: {response}\n"
                    f"The judge could not produce a valid rating. Please improve your answer and ensure claims are clearly supported by documentation."
                )
                continue

            rating = float(rating)

            if rating > best_score:
                best_score = rating
                best_response = response

            if rating > 0.7:
                return response

            prompt = (
                f"Original query: {query}\n"
                f"Your previous response: {response}\n"
                f"Why it was rejected: {reasoning}\n"
                "Improve your answer based on the feedback above. Use the repl_tool to verify your claims against the documentation."
            )

            print(
                "======================MAIN AGENT RESPONSE==========================="
            )
            print(f"MAIN AGENT's RESPONSE: {response}")
            print(
                "======================JUDGE AGENT RESPONSE==========================="
            )
            print(f"JUDGE AGENT's RATING: {rating}")
            print(f"JUDGE AGENT's REASONING: {reasoning}")
            print("==============================================================")

        return best_response
