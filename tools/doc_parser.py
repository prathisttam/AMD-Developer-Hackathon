from liteparse import LiteParse
from pathlib import Path

'''
Given the path to the PDF file and the output path to save the text.
'''
def parse_pdf(pdf_path, output_path=""):
    parser = LiteParse()
    result = parser.parse(pdf_path)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.text)
    return result.text

if __name__ == "__main__":
    folder_path = Path("docs")
    for file in folder_path.glob("*.pdf"):
        output_path = Path("docs_output") / f"{file.stem}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        parse_pdf(file, output_path)
        print(f"Parsed {file.name} to {output_path}")