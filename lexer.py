import json
import re
import os
from errors import BaklolError

class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, Line:{self.line})"

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.current_char = self.source_code[0] if self.source_code else None
        
        # Load keywords
        base_path = os.path.dirname(os.path.abspath(__file__))
        keywords_path = os.path.join(base_path, "keywords.json")
        with open(keywords_path, "r") as f:
            data = json.load(f)
            self.keywords = data["keywords"]
            self.booleans = data["boolean"]

    def advance(self):
        self.position += 1
        if self.position >= len(self.source_code):
            self.current_char = None
        else:
            self.current_char = self.source_code[self.position]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            if self.current_char == '\n':
                self.line += 1
            self.advance()

    def make_identifier(self):
        result = ""
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        if result in self.keywords:
            return Token(self.keywords[result], result, self.line)
        elif result in self.booleans:
            return Token("BOOLEAN", True if result == "sahi" else False, self.line)
        return Token("IDENTIFIER", result, self.line)

    def make_number(self):
        result = ""
        dot_count = 0
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
            result += self.current_char
            self.advance()

        if dot_count == 0:
            return Token("INTEGER", int(result), self.line)
        else:
            return Token("FLOAT", float(result), self.line)

    def make_string(self):
        result = ""
        self.advance() # Skip opening quote
        while self.current_char is not None and self.current_char != '"':
            result += self.current_char
            self.advance()
        
        if self.current_char == '"':
            self.advance() # Skip closing quote
            return Token("STRING", result, self.line)
        else:
            raise BaklolError("String band karna bhool gaye kya?", self.line)

    def tokenize(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.make_identifier())
                continue
            
            if self.current_char.isdigit():
                tokens.append(self.make_number())
                continue

            if self.current_char == '"':
                tokens.append(self.make_string())
                continue

            if self.current_char == '+':
                tokens.append(Token("PLUS", "+", self.line))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token("MINUS", "-", self.line))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token("MUL", "*", self.line))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token("DIV", "/", self.line))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token("LPAREN", "(", self.line))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token("RPAREN", ")", self.line))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token("LBRACE", "{", self.line))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token("RBRACE", "}", self.line))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token("COMMA", ",", self.line))
                self.advance()
            elif self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token("EQ", "==", self.line))
                    self.advance()
                else:
                    tokens.append(Token("ASSIGN", "=", self.line))
            elif self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token("GTE", ">=", self.line))
                    self.advance()
                else:
                    tokens.append(Token("GT", ">", self.line))
            elif self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token("LTE", "<=", self.line))
                    self.advance()
                else:
                    tokens.append(Token("LT", "<", self.line))
            elif self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    tokens.append(Token("NEQ", "!=", self.line))
                    self.advance()
                else:
                    raise BaklolError("Ye '!' kya hai be? '!=' likhna chah rahe ho kya?", self.line)
            else:
                self.advance() 
                # Keeping it simple, skipping unknown chars or could throw error
                # raise BaklolError(f"Ye '{self.current_char}' kya bawaseer hai?", self.line)

        tokens.append(Token("EOF", None, self.line))
        return tokens
