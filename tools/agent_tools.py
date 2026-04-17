import os
import traceback
from crewai_tools import DirectoryReadTool, FileReadTool

DOCS_OUTPUT_DIR = "./docs_output"

def read(filename: str) -> str:
    """Read a file from docs_output folder."""
    path = os.path.join(DOCS_OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return f"File not found: {filename}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def ls() -> str:
    """List all files in docs_output folder."""
    if not os.path.exists(DOCS_OUTPUT_DIR):
        return "docs_output folder does not exist"
    files = os.listdir(DOCS_OUTPUT_DIR)
    return "\n".join(files) if files else "No files found"


def search(query: str) -> str:
    """Search files in docs_output by name containing query."""
    if not os.path.exists(DOCS_OUTPUT_DIR):
        return "docs_output folder does not exist"
    files = [f for f in os.listdir(DOCS_OUTPUT_DIR) if query.lower() in f.lower()]
    return "\n".join(files) if files else f"No files found matching: {query}"


def grep(pattern: str) -> str:
    """Search contents of all files in docs_output for pattern."""
    if not os.path.exists(DOCS_OUTPUT_DIR):
        return "docs_output folder does not exist"
    results = []
    for filename in os.listdir(DOCS_OUTPUT_DIR):
        path = os.path.join(DOCS_OUTPUT_DIR, filename)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if pattern.lower() in content.lower():
                        results.append(f"{filename}: found '{pattern}'")
            except Exception:
                pass
    return "\n".join(results) if results else f"No matches found for: {pattern}"


def create_repl_tool():
    from crewai.tools import BaseTool

    class DocsOutputREPLTool(BaseTool):
        name: str = "repl_tool"
        description: str = (
            "Execute Python code to read files in docs_output folder. "
            "Available functions: read('filename'), ls(), search('query'), grep('pattern'). "
            "Example: read('architecture.md') or ls()"
        )

        def _run(self, code: str) -> str:
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
            safe_globals = {
                "__builtins__": allowed_builtins,
                "read": read,
                "ls": ls,
                "search": search,
                "grep": grep,
            }

            try:
                result = eval(code, safe_globals)
                if result is None:
                    return "Executed successfully (no output)"
                return str(result)
            except Exception as e:
                traceback.print_exc()
                return f"Error: {type(e).__name__}: {e}"

    return DocsOutputREPLTool()


docs_tool = DirectoryReadTool(directory="./docs_output", file_types=[".md"])
file_read_tool = FileReadTool()
repl_tool = create_repl_tool()
