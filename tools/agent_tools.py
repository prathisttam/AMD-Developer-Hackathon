from crewai_tools import DirectoryReadTool, FileReadTool

docs_tool = DirectoryReadTool(directory="./docs_output", file_types=[".md"])
file_read_tool = FileReadTool()
repl_tool = None
