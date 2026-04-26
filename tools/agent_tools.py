import os
import ast
import io
import traceback
from contextlib import redirect_stdout
from crewai import Agent

DOCS_OUTPUT_DIR = "./docs_output"

sub_agent = None
judge_agent = None


def get_sub_agent():
    global sub_agent
    if sub_agent is None:
        from rlm.agents import sub_agent as agent

        sub_agent = agent
    return sub_agent


def get_judge_agent() -> Agent:
    global judge_agent
    if judge_agent is None:
        from rlm.agents import judge_agent as agent

        judge_agent = agent
    return judge_agent


def read(filename: str, max_chars: int = 10000) -> str:
    """Read a file from docs_output folder. Returns up to max_chars (default 10000)."""
    print(f"[TOOL] read called with: '{filename}', max_chars={max_chars}")
    path = os.path.join(DOCS_OUTPUT_DIR, filename)
    if not os.path.exists(path):
        print("[TOOL] read result: File not found")
        return f"File not found: {filename}"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        print(
            f"[TOOL] read result: {len(content)} chars total, returning up to {max_chars}"
        )
        if len(content) > max_chars:
            return (
                content[:max_chars]
                + f"\n\n... [truncated {len(content) - max_chars} chars. Use read_range() to read specific sections]"
            )
        return content


def read_range(filename: str, start: int, end: int) -> str:
    """Read specific line range from a file. start and end are line numbers (1-indexed)."""
    print(f"[TOOL] read_range called with: '{filename}', lines {start}-{end}")
    path = os.path.join(DOCS_OUTPUT_DIR, filename)
    if not os.path.exists(path):
        print("[TOOL] read_range result: File not found")
        return f"File not found: {filename}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            if start < 1:
                start = 1
            if end > len(lines):
                end = len(lines)
            if start > end:
                return f"Invalid range: start ({start}) > end ({end})"
            result = "".join(lines[start - 1 : end])
            print(
                f"[TOOL] read_range result: {len(result)} chars ({end - start + 1} lines)"
            )
            return result
    except Exception as e:
        print(f"[TOOL] read_range error: {e}")
        return f"Error reading file: {e}"


def ls() -> str:
    """List all files in docs_output folder."""
    print("[TOOL] ls called")
    if not os.path.exists(DOCS_OUTPUT_DIR):
        print("[TOOL] ls result: docs_output folder does not exist")
        return "docs_output folder does not exist"
    files = os.listdir(DOCS_OUTPUT_DIR)
    result = "\n".join(files) if files else "No files found"
    print(f"[TOOL] ls result: {result}")
    return result


def search(query: str) -> str:
    """Search files in docs_output by name containing query."""
    print(f"[TOOL] search called with: '{query}'")
    if not os.path.exists(DOCS_OUTPUT_DIR):
        print("[TOOL] search result: docs_output folder does not exist")
        return "docs_output folder does not exist"
    files = [f for f in os.listdir(DOCS_OUTPUT_DIR) if query.lower() in f.lower()]
    result = "\n".join(files) if files else f"No files found matching: {query}"
    print(f"[TOOL] search result: {len(files)} matches")
    return result


def grep(filename: str, pattern: str, context_lines: int = 3) -> str:
    """Search contents of a specific file for pattern. Returns matching lines with context (default 3 lines before/after)."""
    print(
        f"[TOOL] grep called with: '{filename}', '{pattern}', context_lines={context_lines}"
    )
    if not os.path.exists(DOCS_OUTPUT_DIR):
        print("[TOOL] grep result: docs_output folder does not exist")
        return "docs_output folder does not exist"
    path = os.path.join(DOCS_OUTPUT_DIR, filename)
    if not os.path.exists(path):
        print("[TOOL] grep result: File not found")
        raise FileNotFoundError(f"File not found: {filename}")
    results = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if pattern.lower() in line.lower():
                    start = max(0, i - context_lines)
                    end = min(len(lines), i + context_lines + 1)
                    context = "".join(lines[start:end])
                    results.append(f"=== {filename}:{i + 1} ===\n{context}")
    except Exception:
        pass
    result = "\n---\n".join(results) if results else f"No matches found for: {pattern}"
    print(f"[TOOL] grep result: {len(results)} matches")
    return result


def spawn_subagent(query: str) -> str:
    """Spawn a subagent to answer a query. The subagent will explore the docs_output folder and return the result."""
    print(f"[TOOL] spawn_subagent called with following query: '{query}'")
    try:
        agent = get_sub_agent()
        result = agent.kickoff(messages=[{"role": "user", "content": query}])
        print(f"[TOOL] spawn_subagent result: {len(str(result))} chars")
        return str(result)
    except Exception as e:
        traceback.print_exc()
        print(f"[TOOL] spawn_subagent error: {type(e).__name__}: {e}")
        raise ValueError(f"Error spawning subagent: {type(e).__name__}: {e}")


def judge_response(query: str, response: str) -> bool:
    """Use the model to check if the response adequately answers the query. Returns True if it does, False otherwise."""
    print(
        f"[TOOL] judge_response called with query: '{query}' and response length: {len(response)}"
    )
    try:
        agent = get_judge_agent()
        result = agent.kickoff(
            messages=[
                {
                    "role": "user",
                    "content": f"""
                    Given the {response} for this query: {query}\n

                    Give a score between 0.0 to 1.0 for the response's relevance to the query. 
                    Make sure to also provide a reasoning for your score
                    """,
                }
            ],
        )
        print(f"[TOOL] judge_response result: {result}")
        return str(result).strip().lower() == "yes"
    except Exception as e:
        traceback.print_exc()
        print(f"[TOOL] judge_response error: {type(e).__name__}: {e}")
        raise ValueError(f"Error judging response: {type(e).__name__}: {e}")


def create_repl_tool():
    from crewai.tools import BaseTool

    class DocsOutputREPLTool(BaseTool):
        name: str = "repl_tool"
        description: str = (
            "Execute Python code to read files in docs_output folder. "
            "Write Python code that calls these functions DIRECTLY (not as methods):\n"
            "- read('filename', max_chars=10000) - read file content (truncated to max_chars)\n"
            "- read_range('filename', start_line, end_line) - read specific line range\n"
            "- ls() - list all files\n"
            "- search('query') - search files by name\n"
            "- grep('filename', 'pattern', context_lines=3) - search file contents with context\n"
            "- spawn_subagent('your query in natural language') - break down your task into smaller subtasks and delegate to subagents in natural language\n"
            "VALID examples (write these in your code):\n"
            "  grep('harrypotter.md', 'three centaurs Forbidden Forest', context_lines=10)\n"
            "  read_range('harrypotter.md', 100, 150)\n"
            "  ls()\n"
            "  read('chapter1.md')\n"
            "INVALID (DO NOT use):\n"
            "  repl_tool.grep('pattern') - NOT a method call\n"
            "  docs_tool.read('file') - no such object\n"
            "IMPORTANT: The return value of this tool is added to the agent context. "
            "To make results available to the agent, either print them or put the value you want as the final expression.\n"
            "Examples:\n"
            "  files = ls()\n"
            "  files\n"
            "  print(grep('paper.md', 'RLM'))"
        )
        _session_globals: dict | None = None

        def _get_session_globals(self) -> dict:
            if self._session_globals is None:
                allowed_builtins = {
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                    "set": set,
                    "print": print,
                    "range": range,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                    "sorted": sorted,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "sum": sum,
                    "any": any,
                    "all": all,
                    "True": True,
                    "False": False,
                    "None": None,
                }
                self._session_globals = {
                    "__builtins__": allowed_builtins,
                    "read": read,
                    "read_range": read_range,
                    "ls": ls,
                    "search": search,
                    "grep": grep,
                    "spawn_subagent": spawn_subagent,
                }
            return self._session_globals

        def _run(self, code: str) -> str:
            try:
                print(f"[REPL] Executing code:\n{code}\n---")
                safe_globals = self._get_session_globals()
                stdout = io.StringIO()
                last_value = None

                parsed = ast.parse(code, mode="exec")
                body = parsed.body
                final_expr = None

                if body and isinstance(body[-1], ast.Expr):
                    final_expr = ast.Expression(body[-1].value)
                    body = body[:-1]

                with redirect_stdout(stdout):
                    if body:
                        exec(
                            compile(
                                ast.Module(body=body, type_ignores=[]),
                                "<repl_tool>",
                                "exec",
                            ),
                            safe_globals,
                        )
                    if final_expr is not None:
                        last_value = eval(
                            compile(final_expr, "<repl_tool>", "eval"),
                            safe_globals,
                        )

                output_parts = []
                printed = stdout.getvalue().strip()
                if printed:
                    output_parts.append(printed)
                if last_value is not None:
                    output_parts.append(str(last_value))

                return (
                    "\n".join(output_parts) if output_parts else "Executed successfully"
                )
            except Exception as e:
                traceback.print_exc()
                return f"Error: {type(e).__name__}: {e}"

    return DocsOutputREPLTool()


repl_tool = create_repl_tool()
