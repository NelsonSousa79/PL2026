class SemanticError(Exception):
    pass

class SymbolTable:
    def __init__(self):
        self.stack = [{}]
        self.var_count = 0  
        self.stack[0]['MOD'] = {
            'kind': 'function',
            'type': 'INTEGER',
            'params': ['INTEGER', 'INTEGER'],
            'lineno': 0
        }

    def push_scope(self):
        self.stack.append({})

    def pop_scope(self):
        if len(self.stack) > 1:
            self.stack.pop()

    def declare_var(self, name, type_info, lineno, is_array=False, size=1):
        current_scope = self.stack[-1]
        if name in current_scope:
            prev_lineno = current_scope[name]['lineno']
            raise SemanticError(f"line {lineno}: Duplicate declaration {name} (previously declared at line {prev_lineno})")
        
        current_scope[name] = {
            'kind': 'var',
            'type': type_info,
            'initialized': False,
            'is_array': is_array,
            'lineno': lineno,
            'index': self.var_count
        }
        self.var_count += size

    def declare_fun(self, name, type_info, params, kind, lineno):
        global_scope = self.stack[0]
        if name in global_scope:
            prev_lineno = global_scope[name]['lineno']
            raise SemanticError(f"line {lineno}: Duplicate declaration {name} (previously declared at line {prev_lineno})")
        global_scope[name] = {
            'kind': kind, 
            'type': type_info,
            'params': params, 
            'lineno': lineno
        }

    def lookup(self, name, lineno):
        for scope in reversed(self.stack):
            if name in scope:
                return scope[name]
        raise SemanticError(f"line {lineno}: Undeclared identifier {name}")

    def initialize(self, name, lineno):
        symbol = self.lookup(name, lineno)
        if symbol['kind'] == 'var':
            symbol['initialized'] = True

    def check_initialized(self, name, lineno):
        symbol = self.lookup(name, lineno)
        if symbol['kind'] == 'var' and not symbol['initialized']:
            raise SemanticError(f"line {lineno}: Uninitialized variable {name}")


class SemanticAnalyzer:
    def __init__(self):
        self.st = SymbolTable()
        self.labels = set()
        self.type_map = {
            'INTEGER': 'int',
            'LOGICAL': 'bool',
            'REAL': 'float',
            'CHARACTER': 'string'
        }

    def _collect_labels(self, statements):
        labels = set()
        for stmt in statements:
            if stmt is None:
                continue
            nt = stmt.get('node')
            if nt == 'labeled_stmt':
                labels.add(stmt['label'])
                inner = stmt.get('statement')
                if inner:
                    labels |= self._collect_labels([inner])
            elif nt == 'if_stmt':
                labels |= self._collect_labels(stmt.get('then', []))
                labels |= self._collect_labels(stmt.get('else', []))
            elif nt == 'do_stmt':
                if 'end_label' in stmt:
                    labels.add(stmt['end_label'])
                labels |= self._collect_labels(stmt.get('body', []))
        return labels

    def analyze(self, ast):
        if ast['node'] != 'program_file':
            return

        for unit in ast['units']:
            unit_lineno = unit.get('lineno', 0)
            if unit['node'] == 'function_def':
                param_types = self._extract_param_types(unit)
                self.st.declare_fun(unit['name'], unit['return_type']['base'], param_types, 'function', unit_lineno)
            elif unit['node'] == 'subroutine_def':
                param_types = self._extract_param_types(unit)
                self.st.declare_fun(unit['name'], None, param_types, 'subroutine', unit_lineno)

        for unit in ast['units']:
            if unit['node'] == 'main_program':
                self._analyze_main(unit)
            elif unit['node'] in ['function_def', 'subroutine_def']:
                self._analyze_subprogram(unit)

    def _extract_param_types(self, node):
        param_names = node['params']
        types_map = {}
        for decl in node['declarations']:
            tpe = decl['type']['base']
            for id_node in decl['ids']:
                if id_node['id'] in param_names:
                    types_map[id_node['id']] = tpe
        
        result = []
        for name in param_names:
            if name not in types_map:
                raise SemanticError(f"line {node.get('lineno', 0)}: Parameter {name} not declared in subprogram {node['name']}")
            result.append(types_map[name])
        return result

    def _analyze_main(self, node):
        self.st.push_scope()
        self.labels = self._collect_labels(node['statements'])
        self._declare_block_vars(node['declarations'])
        for stmt in node['statements']:
            self._visit_stmt(stmt)
        self.st.pop_scope()

    def _analyze_subprogram(self, node):
        self.st.push_scope()
        self.labels = self._collect_labels(node['statements'])

        self._declare_block_vars(node['declarations'])
        
        current_scope = self.st.stack[-1]
        param_indices = []
        for name in node['params']:
            self.st.initialize(name, node['lineno'])
            param_indices.append(current_scope[name]['index'])
            
        global_fun = self.st.stack[0][node['name']]
        global_fun['param_indices'] = param_indices

        if node['node'] == 'function_def':
            if node['name'] not in current_scope:
                self.st.declare_var(node['name'], node['return_type']['base'], node['lineno'])
            node['sym_index'] = current_scope[node['name']]['index']

        for stmt in node['statements']:
            self._visit_stmt(stmt)
            
        self.st.pop_scope()

    def _declare_block_vars(self, declarations):
        for decl in declarations:
            tpe = decl['type']['base']
            for id_node in decl['ids']:
                name = id_node['id']
                is_array = (id_node['node'] == 'array_decl')
                size = id_node.get('size', 1) if is_array else 1
                self.st.declare_var(name, tpe, id_node['lineno'], is_array=is_array, size=size)

    def _visit_stmt(self, stmt):
        if stmt is None:
            return

        node_type = stmt['node']
        lineno = stmt.get('lineno', 0)

        if node_type == 'assign_stmt':
            target = stmt['target']
            val_type = self._visit_expr(stmt['value'])
            
            if target['node'] == 'id':
                name = target['name']
                sym = self.st.lookup(name, target['lineno'])
                target['sym_index'] = sym.get('index')  
                if sym['kind'] != 'var':
                    raise SemanticError(f"line {target['lineno']}: Cannot assign to {sym['kind']} {name}")
                if sym['type'] != val_type:
                    raise SemanticError(f"line {target['lineno']}: Type error expected {self.type_map.get(sym['type'], sym['type'])}, got {self.type_map.get(val_type, val_type)}")
                self.st.initialize(name, target['lineno'])
            
            elif target['node'] == 'array_access':
                name = target['name']
                sym = self.st.lookup(name, target['lineno'])
                target['sym_index'] = sym.get('index')  
                idx_type = self._visit_expr(target['index'])
                if idx_type != 'INTEGER':
                    raise SemanticError(f"line {target['lineno']}: Type error expected int for array index, got {self.type_map.get(idx_type, idx_type)}")
                if sym['type'] != val_type:
                    raise SemanticError(f"line {target['lineno']}: Type error expected {self.type_map.get(sym['type'], sym['type'])}, got {self.type_map.get(val_type, val_type)}")
                self.st.initialize(name, target['lineno'])

        elif node_type == 'if_stmt':
            cond_type = self._visit_expr(stmt['condition'])
            if cond_type != 'LOGICAL':
                raise SemanticError(f"line {lineno}: Type error expected bool for condition, got {self.type_map.get(cond_type, cond_type)}")
            for s in stmt['then']:
                self._visit_stmt(s)
            for s in stmt['else']:
                self._visit_stmt(s)

        elif node_type == 'do_stmt':
            var_name = stmt['var']
            sym = self.st.lookup(var_name, lineno)
            stmt['sym_index'] = sym.get('index')  
            if sym['type'] != 'INTEGER':
                raise SemanticError(f"line {lineno}: Type error expected int for loop variable, got {self.type_map.get(sym['type'], sym['type'])}")
            
            self.st.initialize(var_name, lineno)
            
            start_t = self._visit_expr(stmt['start'])
            end_t = self._visit_expr(stmt['end'])
            if start_t != 'INTEGER' or end_t != 'INTEGER':
                raise SemanticError(f"line {lineno}: Type error expected int for loop range")
            
            if stmt['step']:
                step_t = self._visit_expr(stmt['step'])
                if step_t != 'INTEGER':
                    raise SemanticError(f"line {lineno}: Type error expected int for loop step")
            
            for s in stmt['body']:
                self._visit_stmt(s)

        elif node_type == 'read_stmt':
            for item in stmt['items']:
                if item['node'] == 'id':
                    sym = self.st.lookup(item['name'], item['lineno'])
                    item['sym_index'] = sym.get('index')  
                    self.st.initialize(item['name'], item['lineno'])
                elif item['node'] == 'array_access':
                    sym = self.st.lookup(item['name'], item['lineno'])
                    item['sym_index'] = sym.get('index')  
                    self.st.initialize(item['name'], item['lineno'])
                    self._visit_expr(item['index'])

        elif node_type == 'print_stmt':
            for val in stmt['values']:
                self._visit_expr(val)

        elif node_type == 'labeled_stmt':
            self._visit_stmt(stmt['statement'])

        elif node_type == 'call_stmt':
            name = stmt['name']
            sym = self.st.lookup(name, lineno)
            if sym['kind'] != 'subroutine':
                raise SemanticError(f"line {lineno}: {name} is not a subroutine")
            
            args = stmt['args']
            if len(args) != len(sym['params']):
                raise SemanticError(f"line {lineno}: Subroutine {name} expected {len(sym['params'])} arguments, got {len(args)}")
            
            for i, arg in enumerate(args):
                arg_type = self._visit_expr(arg, check_init=False)
                expected_type = sym['params'][i]
                if arg_type != expected_type:
                    raise SemanticError(f"line {lineno}: Subroutine {name} argument {i+1} expected {self.type_map.get(expected_type)}, got {self.type_map.get(arg_type)}")
                if arg['node'] == 'id':
                    self.st.initialize(arg['name'], lineno)

        elif node_type == 'goto_stmt':
            if stmt['label'] not in self.labels:
                raise SemanticError(f"line {lineno}: GOTO to undefined label {stmt['label']}")

        elif node_type == 'return_stmt':
            pass

    def _visit_expr(self, expr, check_init=True):
        if expr is None:
            return None

        node_type = expr['node']
        lineno = expr.get('lineno', 0)

        if node_type == 'int':
            return 'INTEGER'
        elif node_type == 'real':
            return 'REAL'
        elif node_type == 'bool':
            return 'LOGICAL'
        elif node_type == 'string':
            return 'CHARACTER'

        elif node_type == 'id':
            name = expr['name']
            sym = self.st.lookup(name, lineno)
            expr['sym_index'] = sym.get('index')  
            if sym['kind'] != 'var':
                 raise SemanticError(f"line {lineno}: {name} is not a variable")
            if check_init:
                self.st.check_initialized(name, lineno)
            return sym['type']

        elif node_type == 'array_access':
            name = expr['name']
            sym = self.st.lookup(name, lineno)
            expr['sym_index'] = sym.get('index')  
            if sym['kind'] != 'var':
                 raise SemanticError(f"line {lineno}: {name} is not a variable")
            if check_init:
                self.st.check_initialized(name, lineno)
            idx_type = self._visit_expr(expr['index'])
            if idx_type != 'INTEGER':
                raise SemanticError(f"line {lineno}: Type error expected int for array index, got {self.type_map.get(idx_type, idx_type)}")
            return sym['type']

        elif node_type == 'binop':
            op = expr['op']
            left_t = self._visit_expr(expr['left'])
            right_t = self._visit_expr(expr['right'])
            
            if op in ['PLUS', 'MINUS', 'TIMES', 'DIVIDE']:
                if left_t not in ['INTEGER', 'REAL'] or right_t not in ['INTEGER', 'REAL']:
                    raise SemanticError(f"line {lineno}: Type error numeric operation expected numeric types, got {self.type_map.get(left_t, left_t)} and {self.type_map.get(right_t, right_t)}")
                return 'REAL' if (left_t == 'REAL' or right_t == 'REAL') else 'INTEGER'
            
            elif op in ['EQ', 'NE', 'LT', 'LE', 'GT', 'GE']:
                if left_t != right_t:
                    raise SemanticError(f"line {lineno}: Type error comparison expected same types, got {self.type_map.get(left_t, left_t)} and {self.type_map.get(right_t, right_t)}")
                return 'LOGICAL'
            
            elif op in ['AND', 'OR']:
                if left_t != 'LOGICAL' or right_t != 'LOGICAL':
                    raise SemanticError(f"line {lineno}: Type error logical operation expected bool types, got {self.type_map.get(left_t, left_t)} and {self.type_map.get(right_t, right_t)}")
                return 'LOGICAL'

        elif node_type == 'unop':
            op = expr['op']
            val_t = self._visit_expr(expr['value'])
            if op == 'UMINUS':
                if val_t not in ['INTEGER', 'REAL']:
                    raise SemanticError(f"line {lineno}: Type error unary minus expected numeric type, got {self.type_map.get(val_t, val_t)}")
                return val_t
            elif op == 'NOT':
                if val_t != 'LOGICAL':
                    raise SemanticError(f"line {lineno}: Type error logical NOT expected bool type, got {self.type_map.get(val_t, val_t)}")
                return 'LOGICAL'

        elif node_type == 'call_expr':
            name = expr['name']
            sym = self.st.lookup(name, lineno)
            
            if sym['kind'] == 'var' and not sym.get('is_array'):
                global_sym = self.st.stack[0].get(name)
                if global_sym and global_sym['kind'] == 'function':
                    sym = global_sym
            
            if sym['kind'] == 'var' and sym.get('is_array'):
                expr['node'] = 'array_access'
                expr['name'] = name
                expr['sym_index'] = sym.get('index') 
                args = expr['args']
                expr['index'] = args[0]
                for arg in args:
                    arg_t = self._visit_expr(arg)
                    if arg_t != 'INTEGER':
                        raise SemanticError(f"line {lineno}: Type error expected int for array index, got {self.type_map.get(arg_t, arg_t)}")
                self.st.check_initialized(name, lineno)
                return sym['type']
            
            elif sym['kind'] == 'function':
                expr['param_indices'] = sym.get('param_indices', [])
                args = expr['args']
                if len(args) != len(sym['params']):
                    raise SemanticError(f"line {lineno}: Function {name} expected {len(sym['params'])} arguments, got {len(args)}")
                
                for i, arg in enumerate(args):
                    arg_type = self._visit_expr(arg)
                    expected_type = sym['params'][i]
                    if arg_type != expected_type:
                        raise SemanticError(f"line {lineno}: Function {name} argument {i+1} expected {self.type_map.get(expected_type)}, got {self.type_map.get(arg_type)}")
                
                return sym['type']
            else:
                raise SemanticError(f"line {lineno}: {name} is not a function or array")

        return None
