from crewai_tools import (
    Tool, 
    DirectoryReadTool, 
    FileReadTool, 
    CodeInterpreterTool
)

docs_tool = DirectoryReadTool(directory="./docs_output", file_types=[".md"])
file_read_tool = FileReadTool()
repl_tool = CodeInterpreterTool()  # This tool allows you to execute Python code in a REPL environment.