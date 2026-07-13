class CodeGenerator:
    def __init__(self, symbol_table):
        self.st = symbol_table
        self.code = []
        self.label_counter = 0

    def new_label(self, prefix="L"):
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"

    def emit(self, instruction):
        self.code.append(instruction)

    def generate(self, ast):
        if ast['node'] != 'program_file':
            return []

        main_prog = None
        subprograms = []
        for unit in ast['units']:
            if unit['node'] == 'main_program':
                main_prog = unit
            else:
                subprograms.append(unit)

        if main_prog:
            self.emit("START")
            num_vars = self.st.var_count
            for _ in range(num_vars):
                self.emit("PUSHI 0")

            self._generate_statements(main_prog['statements'])
            
            self.emit("STOP")

        for subprog in subprograms:
            name = subprog['name'].replace('_', '')
            self.emit(f"{name}:")
            self._generate_statements(subprog['statements'])
            
            if subprog['node'] == 'function_def':
                idx = subprog.get('sym_index')
                if idx is not None:
                    self.emit(f"PUSHG {idx}")
                    
            self.emit("RETURN")

        return self.code

    def _generate_statements(self, statements):
        for stmt in statements:
            self._visit_stmt(stmt)

    def _visit_stmt(self, stmt):
        if stmt is None:
            return

        nt = stmt['node']

        if nt == 'assign_stmt':
            target = stmt['target']
            if target['node'] == 'id':
                self._visit_expr(stmt['value'])
                idx = target.get('sym_index')
                if idx is not None:
                    self.emit(f"STOREG {idx}")
            elif target['node'] == 'array_access':
                self.emit("PUSHGP")
                idx = target.get('sym_index')
                self.emit(f"PUSHI {idx}")
                self._visit_expr(target['index'])
                self.emit("ADD")
                self.emit("PUSHI 1")
                self.emit("SUB")
                self._visit_expr(stmt['value'])
                self.emit("STOREN")

        elif nt == 'print_stmt':
            for val in stmt['values']:
                if val['node'] == 'string':
                    self.emit(f"PUSHS \"{val['value']}\"")
                    self.emit("WRITES")
                else:
                    self._visit_expr(val)
                    self.emit("WRITEI")
            self.emit("PUSHS \"\\n\"")
            self.emit("WRITES")

        elif nt == 'read_stmt':
            for item in stmt['items']:
                if item['node'] == 'id':
                    self.emit("READ")
                    self.emit("ATOI")
                    idx = item.get('sym_index')
                    if idx is not None:
                        self.emit(f"STOREG {idx}")
                elif item['node'] == 'array_access':
                    self.emit("PUSHGP")
                    idx = item.get('sym_index')
                    self.emit(f"PUSHI {idx}")
                    self._visit_expr(item['index'])
                    self.emit("ADD")
                    self.emit("PUSHI 1")
                    self.emit("SUB")
                    self.emit("READ")
                    self.emit("ATOI")
                    self.emit("STOREN")

        elif nt == 'if_stmt':
            l_else = self.new_label("ELSE")
            l_fi = self.new_label("ENDIF")

            self._visit_expr(stmt['condition'])
            
            if not stmt['else']:
                self.emit(f"JZ {l_fi}")
                self._generate_statements(stmt['then'])
                self.emit(f"{l_fi}:")
            else:
                self.emit(f"JZ {l_else}")
                self._generate_statements(stmt['then'])
                self.emit(f"JUMP {l_fi}")
                self.emit(f"{l_else}:")
                self._generate_statements(stmt['else'])
                self.emit(f"{l_fi}:")

        elif nt == 'do_stmt':
            l_loop = self.new_label("LOOP")
            l_endloop = self.new_label("ENDLOOP")

            idx = stmt.get('sym_index')

            self._visit_expr(stmt['start'])
            if idx is not None:
                self.emit(f"STOREG {idx}")

            self.emit(f"{l_loop}:")

            if idx is not None:
                self.emit(f"PUSHG {idx}")
            self._visit_expr(stmt['end'])
            self.emit("INFEQ")
            self.emit(f"JZ {l_endloop}")

            self._generate_statements(stmt['body'])

            if idx is not None:
                self.emit(f"PUSHG {idx}")
            if stmt['step']:
                self._visit_expr(stmt['step'])
            else:
                self.emit("PUSHI 1")
            self.emit("ADD")
            if idx is not None:
                self.emit(f"STOREG {idx}")

            self.emit(f"JUMP {l_loop}")
            self.emit(f"{l_endloop}:")

        elif nt == 'call_stmt':
            sym = self.st.stack[0].get(stmt['name'])
            param_indices = sym.get('param_indices', []) if sym else []
            for arg, p_idx in zip(stmt['args'], param_indices):
                self._visit_expr(arg)
                self.emit(f"STOREG {p_idx}")
            name = stmt['name'].replace('_', '')
            self.emit(f"PUSHA {name}")
            self.emit("CALL")

        elif nt == 'goto_stmt':
            self.emit(f"JUMP LBL{stmt['label']}")
            
        elif nt == 'labeled_stmt':
            self.emit(f"LBL{stmt['label']}:")
            self._visit_stmt(stmt['statement'])

        elif nt == 'continue_stmt':
            pass

    def _visit_expr(self, expr):
        if expr is None:
            return

        nt = expr['node']

        if nt == 'int':
            self.emit(f"PUSHI {expr['value']}")
        elif nt == 'real':
            self.emit(f"PUSHF {expr['value']}")
        elif nt == 'bool':
            val = 1 if expr['value'] else 0
            self.emit(f"PUSHI {val}")
        elif nt == 'string':
            self.emit(f"PUSHS \"{expr['value']}\"")
            
        elif nt == 'id':
            idx = expr.get('sym_index')
            if idx is not None:
                self.emit(f"PUSHG {idx}")

        elif nt == 'array_access':
            self.emit("PUSHGP")
            idx = expr.get('sym_index')
            self.emit(f"PUSHI {idx}")
            self._visit_expr(expr['index'])
            self.emit("ADD")
            self.emit("PUSHI 1")
            self.emit("SUB")
            self.emit("LOADN")

        elif nt == 'binop':
            self._visit_expr(expr['left'])
            self._visit_expr(expr['right'])
            
            op = expr['op']
            if op == 'PLUS': self.emit("ADD")
            elif op == 'MINUS': self.emit("SUB")
            elif op == 'TIMES': self.emit("MUL")
            elif op == 'DIVIDE': self.emit("DIV")
            elif op == 'LT': self.emit("INF")
            elif op == 'GT': self.emit("SUP")
            elif op == 'EQ': self.emit("EQUAL")
            elif op == 'LE': self.emit("INFEQ")
            elif op == 'GE': self.emit("SUPEQ")
            elif op == 'NE': 
                self.emit("EQUAL")
                self.emit("NOT")
            elif op == 'AND': self.emit("AND") 
            elif op == 'OR': self.emit("OR")

        elif nt == 'unop':
            self._visit_expr(expr['value'])
            op = expr['op']
            if op == 'UMINUS':
                self.emit("PUSHI -1")
                self.emit("MUL")
            elif op == 'NOT':
                self.emit("NOT")

        elif nt == 'call_expr':
            if expr['name'] == 'MOD':
                self._visit_expr(expr['args'][0])
                self._visit_expr(expr['args'][1])
                self.emit("MOD")
                return

            sym = self.st.stack[0].get(expr['name'])
            param_indices = sym.get('param_indices', []) if sym else []
            for arg, p_idx in zip(expr['args'], param_indices):
                self._visit_expr(arg)
                self.emit(f"STOREG {p_idx}")
            name = expr['name'].replace('_', '')
            self.emit(f"PUSHA {name}")
            self.emit("CALL")

