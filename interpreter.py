from parser import *
from errors import BaklolError, BhaukaalError

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class Interpreter:
    def __init__(self):
        self.global_env = {}
        self.functions = {} # Store function declarations

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')

    def visit_list(self, nodes):
        # Visit a list of statements
        result = None
        for node in nodes:
            result = self.visit(node)
        return result

    def visit_Num(self, node):
        return node.value

    def visit_String(self, node):
        return node.value
    
    def visit_Boolean(self, node):
        return node.value

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if node.op.type == 'PLUS':
            return left + right
        elif node.op.type == 'MINUS':
            return left - right
        elif node.op.type == 'MUL':
            return left * right
        elif node.op.type == 'DIV':
            return left / right
        elif node.op.type == 'EQ':
            return left == right
        elif node.op.type == 'NEQ':
            return left != right
        elif node.op.type == 'GT':
            return left > right
        elif node.op.type == 'LT':
            return left < right
        elif node.op.type == 'GTE':
            return left >= right
        elif node.op.type == 'LTE':
            return left <= right
            
    def visit_VarDecl(self, node):
        val = self.visit(node.expression)
        self.global_env[node.var_name] = val
    
    def visit_VarAccess(self, node):
        var_name = node.var_name
        if var_name in self.global_env:
            return self.global_env[var_name]
        else:
            raise BaklolError(f"Variable '{var_name}' dhoond rahe ho? Pehle declare to karo!", 0)

    def visit_VarAssign(self, node):
        var_name = node.left.var_name
        if var_name in self.global_env:
            val = self.visit(node.right)
            self.global_env[var_name] = val
        else:
             raise BaklolError(f"Variable '{var_name}' declare nahi kiya hai be.", 0)

    def visit_Print(self, node):
        val = self.visit(node.expression)
        print(val)
    
    def visit_IfBlock(self, node):
        if self.visit(node.condition):
            self.visit(node.body)
        elif node.else_body:
            self.visit(node.else_body)

    def visit_WhileBlock(self, node):
        while self.visit(node.condition):
            self.visit(node.body)

    def visit_BhaukaalBlock(self, node):
        try:
            self.visit(node.body)
        except Exception as e:
            raise BhaukaalError(f"Bhaukaal machane me galti ho gayi: {str(e)}", 0)

    def visit_Throw(self, node):
        raise BaklolError(node.message, node.line)
        
    def visit_FunctionDecl(self, node):
        self.functions[node.name] = node
        
    def visit_FunctionCall(self, node):
        if node.name not in self.functions:
            raise BaklolError(f"Function '{node.name}' kaun banayega? Hum?", 0)
        
        func_def = self.functions[node.name]
        if len(node.args) != len(func_def.params):
            raise BaklolError(f"Function '{node.name}' maang raha hai {len(func_def.params)} arguments, tum diye {len(node.args)}.", 0)
            
        # Create local scope
        # For simplicity, we will save global_env, update it with params, then restore it.
        # This gives us dynamic scoping or simple recursion support if we are careful.
        # Ideally we should have a chain of environments.
        
        # Simple implementation: Copy global env to NEW env? 
        # No, that's expensive and separate.
        # Better: Backup global state of specific overridden vars?
        # Or Just use a new dict for local vars and fallback to global. 
        # But visit_VarAccess currently only checks self.global_env.
        
        # Let's refactor visit_VarAccess to support scopes roughly.
        # Actually for this prototype, I'll temporarily patch global_env and restore it.
        # This effectively implements dynamic scoping.
        
        old_values = {}
        for param, arg in zip(func_def.params, node.args):
            arg_val = self.visit(arg)
            if param in self.global_env:
                old_values[param] = self.global_env[param]
            self.global_env[param] = arg_val
            
        try:
            self.visit(func_def.body)
        except ReturnValue as r:
            return r.value
        finally:
            # Restore
            for param in func_def.params:
                if param in old_values:
                    self.global_env[param] = old_values[param]
                else:
                    del self.global_env[param]

    def visit_Return(self, node):
        val = self.visit(node.expression)
        raise ReturnValue(val)
