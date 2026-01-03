import http.server
import socketserver
import json
import sys
import io
import os

# Add parent dir to path to import interpreter modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from errors import KanpError

PORT = int(os.environ.get("PORT", 8000))

class KanpHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Mapping URLs to file paths in 'web' folder
        if self.path == '/':
            self.path = '/web/index.html'
        elif self.path == '/docs':
            self.path = '/web/docs.html'
        elif self.path == '/learn':
            self.path = '/web/learn.html'
        elif self.path == '/examples':
            self.path = '/web/examples.html'
        elif self.path == '/playground':
            self.path = '/web/playground.html'
        elif self.path.startswith('/css/'):
            # Allow serving css from web/css
            self.path = '/web' + self.path
        
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/run':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            code = data.get('code', '')

            # Capture stdout
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout

            response = {}
            try:
                # Run the interpreter logic
                lexer = Lexer(code)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
                interpreter = Interpreter()
                interpreter.visit(ast)
                
                print("\n✅ Execution Complete: Sab chaukas chal raha hai")
                response['success'] = True
            except KanpError as e:
                print(str(e))
                response['success'] = False
            except Exception as e:
                print(f"❌ BaklolError: System fat gaya.\n{str(e)}")
                response['success'] = False
            finally:
                sys.stdout = old_stdout

            response['output'] = new_stdout.getvalue()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

print(f"Serving KanpScript Website at http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), KanpHandler) as httpd:
    httpd.serve_forever()
