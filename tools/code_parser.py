from liteparse import LiteParse

'''
Given the path to the PDF file and the output path to save the text.
'''
def parse_pdf(pdf_path, output_path=""):
    parser = LiteParse()
    result = parser.parse(pdf_path)
    if output_path:
        with open(output_path, "w") as f:
            f.write(result.text)
    return result.text

if __name__ == "__main__":
    parse_pdf("docs/RLM.pdf", "output.txt")