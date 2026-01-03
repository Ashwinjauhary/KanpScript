import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from errors import KanpError

def run_script(filename):
    try:
        with open(filename, 'r') as f:
            code = f.read()
        
        # 1. Lexer
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        # 2. Parser
        parser = Parser(tokens)
        ast = parser.parse()
        
        # 3. Interpreter
        interpreter = Interpreter()
        interpreter.visit(ast)
        
        print("\n✅ Execution Complete: Sab chaukas chal raha hai")

    except KanpError as e:
        print(e)
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' nahi mili bhai.")
    except Exception as e:
        print(f"❌ BaklolError: Interpreter hi fat gaya.\n{str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python kanp.py <filename.kanp>")
    else:
        run_script(sys.argv[1])
