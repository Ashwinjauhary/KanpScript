from errors import BaklolError

# --- AST Nodes ---
class AST:
    pass

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f"({self.left} {self.op.value} {self.right})"

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value
    def __repr__(self):
        return str(self.value)

class String(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value
    def __repr__(self):
        return f'"{self.value}"'

class Boolean(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value
    def __repr__(self):
        return str(self.value)

class VarAccess(AST):
    def __init__(self, token):
        self.var_name = token.value
    def __repr__(self):
        return f"Var({self.var_name})"

class VarAssign(AST):
    def __init__(self, left, right):
        self.left = left # VarAccess
        self.right = right # Expression
    def __repr__(self):
        return f"Assign({self.left.var_name} = {self.right})"

class VarDecl(AST):
    def __init__(self, var_name, expression):
        self.var_name = var_name
        self.expression = expression
    def __repr__(self):
        return f"Decl({self.var_name} = {self.expression})"

class Print(AST):
    def __init__(self, expression):
        self.expression = expression
    def __repr__(self):
        return f"Print({self.expression})"

class IfBlock(AST):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body
    def __repr__(self):
        return f"If({self.condition}) {{ ... }}"

class WhileBlock(AST):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
        return f"While({self.condition}) {{ ... }}"

class BhaukaalBlock(AST):
    def __init__(self, body):
        self.body = body
    def __repr__(self):
        return "BhaukaalBlock"

class NoOp(AST):
    pass

class FunctionDecl(AST):
    def __init__(self, name, params, body, is_expert=False):
        self.name = name
        self.params = params
        self.body = body
        self.is_expert = is_expert
    def __repr__(self):
        return f"Func({self.name}, {self.params})"

class FunctionCall(AST):
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def __repr__(self):
        return f"Call({self.name}, {self.args})"

class Return(AST):
    def __init__(self, expression):
        self.expression = expression
    def __repr__(self):
        return f"Return({self.expression})"

# --- Parser ---
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_idx = 0
        self.current_token = self.tokens[self.token_idx]

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.token_idx += 1
            if self.token_idx < len(self.tokens):
                self.current_token = self.tokens[self.token_idx]
        else:
            raise BaklolError(f"Umeed thi '{token_type}' ki, par mila '{self.current_token.type}'", self.current_token.line)

    def factor(self):
        token = self.current_token
        if token.type == 'PLUS':
            self.eat('PLUS')
            return self.factor()
        elif token.type == 'MINUS':
            self.eat('MINUS')
            return BinOp(Num(0), token, self.factor()) # Unary minus
        elif token.type in ('INTEGER', 'FLOAT'):
            self.eat(token.type)
            return Num(token)
        elif token.type == 'STRING':
            self.eat('STRING')
            return String(token)
        elif token.type == 'BOOLEAN':
            self.eat('BOOLEAN')
            return Boolean(token)
        elif token.type == 'IDENTIFIER':
            self.eat('IDENTIFIER')
            # Check for function call
            if self.current_token.type == 'LPAREN':
                self.eat('LPAREN')
                args = []
                if self.current_token.type != 'RPAREN':
                    args.append(self.expr())
                    while self.current_token.type == 'COMMA':
                        self.eat('COMMA')
                        args.append(self.expr())
                self.eat('RPAREN')
                return FunctionCall(token.value, args)
            return VarAccess(token)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return node
        else:
            raise BaklolError("Expression expect kar rahe the, ye kya aa gaya?", token.line)

    def term(self):
        node = self.factor()
        while self.current_token.type in ('MUL', 'DIV'):
            token = self.current_token
            if token.type == 'MUL':
                self.eat('MUL')
            elif token.type == 'DIV':
                self.eat('DIV')
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in ('PLUS', 'MINUS', 'EQ', 'GT', 'LT', 'GTE', 'LTE', 'NEQ'):
            token = self.current_token
            self.eat(token.type)
            node = BinOp(left=node, op=token, right=self.term())
        return node

    def statement(self):
        if self.current_token.type == 'VAR_DECL':
            self.eat('VAR_DECL')
            var_name = self.current_token.value
            self.eat('IDENTIFIER')
            self.eat('ASSIGN')
            expr = self.expr()
            return VarDecl(var_name, expr)
        elif self.current_token.type == 'IDENTIFIER':
            # Assignment: x = 5 (OR Function Call as a statement?)
            # If function call, we parse it as expr, but need to handle result discard if just statement.
            # However, my factor() handles function call. Here we check for assignment.
            # If we don't see ASSIGN, distinct case?
            # Basic parsing: 
            #   x = 5
            #   func() 
            # My factor() consumes IDENTIFIER. So I need to peek or refactor.
            # Current `factor` logic: consume IDENTIFIER, then check LPAREN.
            
            # Let's peek.
            # Actually, `statement` logic was:
            # eat ID, eat ASSIGN.
            # If next is LPAREN, it acts as a call statement.
            # So I should delegate to expression statement if no ASSIGN.
            
            # Quick fix: Handle assignment specifically. 
            # If I consume IDENTIFIER here, I lose it for Call logic if it's a Call.
            # So, check lookahead if possible or try parse as call.
            
            # Cleanest way:
            # Parse IDENTIFIER. 
            # If next is ASSIGN -> Assignment.
            # If next is LPAREN -> FunctionCall (Expression Statement).
            
            var_token = self.current_token
            self.eat('IDENTIFIER')
            
            if self.current_token.type == 'ASSIGN':
                self.eat('ASSIGN')
                expr = self.expr()
                return VarAssign(VarAccess(var_token), expr)
            elif self.current_token.type == 'LPAREN':
                # Function Call
                self.eat('LPAREN')
                args = []
                if self.current_token.type != 'RPAREN':
                    args.append(self.expr())
                    while self.current_token.type == 'COMMA':
                        self.eat('COMMA')
                        args.append(self.expr())
                self.eat('RPAREN')
                return FunctionCall(var_token.value, args)
            else:
                 raise BaklolError(f"Na to assignment hai na function call, kya chahte ho '{var_token.value}' se?", var_token.line)

        elif self.current_token.type == 'PRINT':
            self.eat('PRINT')
            expr = self.expr()
            return Print(expr)
        elif self.current_token.type == 'IF':
            self.eat('IF')
            condition = self.expr()
            self.eat('LBRACE')
            body = self.block()
            self.eat('RBRACE')
            else_body = None
            if self.current_token.type == 'ELSE':
                self.eat('ELSE')
                self.eat('LBRACE')
                else_body = self.block()
                self.eat('RBRACE')
            return IfBlock(condition, body, else_body)
        elif self.current_token.type == 'WHILE':
            self.eat('WHILE')
            condition = self.expr()
            self.eat('LBRACE')
            body = self.block()
            self.eat('RBRACE')
            return WhileBlock(condition, body)
        elif self.current_token.type == 'ADVANCED_BLOCK':
            self.eat('ADVANCED_BLOCK')
            self.eat('LBRACE')
            body = self.block()
            self.eat('RBRACE')
            return BhaukaalBlock(body)
        elif self.current_token.type == 'THROW_ERROR':
            self.eat('THROW_ERROR')
            msg_token = self.current_token
            self.eat('STRING')
            return Throw(msg_token)
        elif self.current_token.type == 'RETURN':
            self.eat('RETURN')
            expr = self.expr()
            return Return(expr)
        elif self.current_token.type == 'FUNCTION':
            self.eat('FUNCTION')
            func_name = self.current_token.value
            self.eat('IDENTIFIER')
            self.eat('LPAREN')
            params = []
            if self.current_token.type == 'IDENTIFIER':
                params.append(self.current_token.value)
                self.eat('IDENTIFIER')
                while self.current_token.type == 'COMMA':
                    self.eat('COMMA')
                    params.append(self.current_token.value)
                    self.eat('IDENTIFIER')
            self.eat('RPAREN')
            self.eat('LBRACE')
            body = self.block()
            self.eat('RBRACE')
            return FunctionDecl(func_name, params, body, is_expert=False)
        elif self.current_token.type == 'EXPERT_FUNC':
            self.eat('EXPERT_FUNC')
            # Check if optional 'kaam' is present
            if self.current_token.type == 'FUNCTION':
                self.eat('FUNCTION')
            
            func_name = self.current_token.value
            self.eat('IDENTIFIER')
            self.eat('LPAREN')
            params = []
            if self.current_token.type == 'IDENTIFIER':
                params.append(self.current_token.value)
                self.eat('IDENTIFIER')
                while self.current_token.type == 'COMMA':
                    self.eat('COMMA')
                    params.append(self.current_token.value)
                    self.eat('IDENTIFIER')
            self.eat('RPAREN')
            self.eat('LBRACE')
            body = self.block()
            self.eat('RBRACE')
            return FunctionDecl(func_name, params, body, is_expert=True)
        
        elif self.current_token.type == 'LBRACE':
             # Nested block
            self.eat('LBRACE')
            stmts = self.block()
            self.eat('RBRACE')
            return stmts
        else:
             # Empty statement or error
             return NoOp()

    def block(self):
        valid_stops = ('RBRACE', 'EOF')
        statements = []
        while self.current_token.type not in valid_stops:
            stmt = self.statement()
            if not isinstance(stmt, NoOp):
                statements.append(stmt)
        return statements

    def parse(self):
        return self.block()

class Throw(AST):
    def __init__(self, message_token):
        self.message = message_token.value
        self.line = message_token.line
    def __repr__(self):
        return f"Throw('{self.message}')"
