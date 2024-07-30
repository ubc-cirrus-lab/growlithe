from typing import Tuple
from tree_sitter import Language, Parser, Tree, Node
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript

PY_LANGUAGE = Language(tspython.language())
JS_LANGUAGE = Language(tsjavascript.language())


class ASTParser:
    def __init__(self, language) -> None:
        if language == "python":
            self.language: Language = PY_LANGUAGE
        elif language == "javascript":
            self.language: Language = JS_LANGUAGE
        self.parser: Parser = Parser(self.language)
        self.instrumentations: Tuple[Tuple[str, int], ...] = ()

    def get_parser(self) -> Parser:
        return self.parser

    def parse(self, code: bytes) -> Tree:
        self.code = code.decode("utf8")
        self.tree: Tree = self.parser.parse(code)
        return self.tree

    # Get the indentation level of a given line
    def get_indentation_level(self, line_number):
        lines = self.code.split("\n")
        line = lines[line_number - 1]
        indentation = len(line) - len(line.lstrip())
        return indentation

    def add_instrumentation(self, instrumentation: str, line_number: int):
        self.instrumentations += ((instrumentation, line_number),)

    # Add a print statement before a given line number
    def add_statement(self, statement: str, line_number: int) -> str:
        indentation_level = self.get_indentation_level(line_number)
        indentation = " " * indentation_level
        new_code_lines = (
            self.code.split("\n")[: line_number - 1]
            + [indentation + statement]
            + self.code.split("\n")[line_number - 1 :]
        )
        return "\n".join(new_code_lines)

    def get_updated_code(self) -> str:
        updated_code = self.code
        for instrumentation in self.instrumentations:
            updated_code = self.add_statement(instrumentation[0], instrumentation[1])

        # Check if updated code is a valid tree with the parser
        try:
            self.parser.parse(updated_code.encode("utf8"))
            return updated_code
        except Exception as e:
            print(f"Invalid code: {e}")
            return self.code
