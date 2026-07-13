import ply.yacc as yacc

from lexer import lexer, tokens


precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS'),
)


def p_program_file_multi(p):
    r"""
    program_file : program_file program_unit
    """
    p[1]['units'].append(p[2])
    p[0] = p[1]


def p_program_file_single(p):
    r"""
    program_file : program_unit
    """
    p[0] = {'node': 'program_file', 'units': [p[1]], 'lineno': p.lineno(1),
    }


def p_program_unit_main(p):
    r"""
    program_unit : main_program
    """
    p[0] = p[1]


def p_program_unit_function(p):
    r"""
    program_unit : function_def
    """
    p[0] = p[1]


def p_program_unit_subroutine(p):
    r"""
    program_unit : subroutine_def
    """
    p[0] = p[1]


def p_main_program(p):
    r"""
    main_program : PROGRAM ID declarations statements END
    """
    p[0] = {
        'node': 'main_program',
        'name': p[2],
        'declarations': p[3],
        'statements': p[4],
        'lineno': p.lineno(1),
    }


def p_function_def(p):
    r"""
    function_def : type FUNCTION ID LPAREN param_list_opt RPAREN declarations statements END
    """
    p[0] = {
        'node': 'function_def',
        'return_type': p[1],
        'name': p[3],
        'params': p[5],
        'declarations': p[7],
        'statements': p[8],
        'lineno': p.lineno(1),
    }


def p_subroutine_def_with_params(p):
    r"""
    subroutine_def : SUBROUTINE ID LPAREN param_list_opt RPAREN declarations statements END
    """
    p[0] = {
        'node': 'subroutine_def',
        'name': p[2],
        'params': p[4],
        'declarations': p[6],
        'statements': p[7],
        'lineno': p.lineno(1),
    }


def p_subroutine_def_no_params(p):
    r"""
    subroutine_def : SUBROUTINE ID declarations statements END
    """
    p[0] = {
        'node': 'subroutine_def',
        'name': p[2],
        'params': [],
        'declarations': p[3],
        'statements': p[4],
        'lineno': p.lineno(1),
    }


def p_param_list_opt_list(p):
    r"""
    param_list_opt : param_list
    """
    p[0] = p[1]


def p_param_list_opt_empty(p):
    r"""
    param_list_opt : empty
    """
    p[0] = []


def p_param_list_many(p):
    r"""
    param_list : param_list COMMA ID
    """
    p[0] = [*p[1], p[3]]


def p_param_list_one(p):
    r"""
    param_list : ID
    """
    p[0] = [p[1]]


def p_declarations_many(p):
    r"""
    declarations : declarations declaration
    """
    p[0] = [*p[1], p[2]]


def p_declarations_empty(p):
    r"""
    declarations : empty
    """
    p[0] = []


def p_declaration(p):
    r"""
    declaration : type id_decl_list
    """
    p[0] = {'node': 'declaration', 'type': p[1], 'ids': p[2], 'lineno': p.lineno(1),
    }


def p_type_integer(p):
    r"""
    type : INTEGER
    """
    p[0] = {'base': 'INTEGER', 'lineno': p.lineno(1),
    }


def p_type_real(p):
    r"""
    type : REAL
    """
    p[0] = {'base': 'REAL', 'lineno': p.lineno(1),
    }


def p_type_logical(p):
    r"""
    type : LOGICAL
    """
    p[0] = {'base': 'LOGICAL', 'lineno': p.lineno(1),
    }


def p_type_character(p):
    r"""
    type : CHARACTER
    """
    p[0] = {'base': 'CHARACTER', 'lineno': p.lineno(1),
    }


def p_type_character_size_paren(p):
    r"""
    type : CHARACTER LPAREN INT_CONST RPAREN
    """
    p[0] = {'base': 'CHARACTER', 'size': p[3], 'lineno': p.lineno(1),
    }


def p_type_character_size_star(p):
    r"""
    type : CHARACTER TIMES INT_CONST
    """
    p[0] = {'base': 'CHARACTER', 'size': p[3], 'lineno': p.lineno(1),
    }


def p_id_decl_list_many(p):
    r"""
    id_decl_list : id_decl_list COMMA id_decl
    """
    p[0] = [*p[1], p[3]]


def p_id_decl_list_one(p):
    r"""
    id_decl_list : id_decl
    """
    p[0] = [p[1]]


def p_id_decl(p):
    r"""
    id_decl : ID
            | ID LPAREN INT_CONST RPAREN
            | ID LPAREN ID RPAREN
    """
    if len(p) == 2:
        p[0] = {'node': 'id_decl', 'id': p[1], 'lineno': p.lineno(1),
    }
    else:
        p[0] = {'node': 'array_decl', 'id': p[1], 'size': p[3], 'lineno': p.lineno(1),
    }


def p_statements_many(p):
    r"""
    statements : statements labeled_stmt
    """
    p[0] = [*p[1], p[2]]


def p_statements_empty(p):
    r"""
    statements : empty
    """
    p[0] = []


def p_labeled_stmt_with_label(p):
    r"""
    labeled_stmt : INT_CONST statement
    """
    p[0] = {'node': 'labeled_stmt', 'label': p[1], 'statement': p[2], 'lineno': p.lineno(1),
    }


def p_labeled_stmt_plain(p):
    r"""
    labeled_stmt : statement
    """
    p[0] = p[1]


def p_statement_assign(p):
    r"""
    statement : assign_stmt
    """
    p[0] = p[1]


def p_statement_if(p):
    r"""
    statement : if_stmt
    """
    p[0] = p[1]


def p_statement_do(p):
    r"""
    statement : do_stmt
    """
    p[0] = p[1]


def p_statement_goto(p):
    r"""
    statement : goto_stmt
    """
    p[0] = p[1]


def p_statement_continue(p):
    r"""
    statement : continue_stmt
    """
    p[0] = p[1]


def p_statement_print(p):
    r"""
    statement : print_stmt
    """
    p[0] = p[1]


def p_statement_read(p):
    r"""
    statement : read_stmt
    """
    p[0] = p[1]


def p_statement_call(p):
    r"""
    statement : call_stmt
    """
    p[0] = p[1]


def p_statement_return(p):
    r"""
    statement : return_stmt
    """
    p[0] = p[1]


def p_assign_stmt_simple(p):
    r"""
    assign_stmt : ID EQUALS expr
    """
    p[0] = {
        'node': 'assign_stmt',
        'target': {'node': 'id', 'name': p[1], 'lineno': p.lineno(1),
    },
        'value': p[3],
    }


def p_assign_stmt_array(p):
    r"""
    assign_stmt : ID LPAREN expr RPAREN EQUALS expr
    """
    p[0] = {
        'node': 'assign_stmt',
        'target': {'node': 'array_access', 'name': p[1], 'index': p[3], 'lineno': p.lineno(1),
    },
        'value': p[6],
    }


def p_if_stmt_no_else(p):
    r"""
    if_stmt : IF LPAREN expr RPAREN THEN statements ENDIF
    """
    p[0] = {'node': 'if_stmt', 'condition': p[3], 'then': p[6], 'else': [], 'lineno': p.lineno(1),
    }


def p_if_stmt_with_else(p):
    r"""
    if_stmt : IF LPAREN expr RPAREN THEN statements ELSE statements ENDIF
    """
    p[0] = {'node': 'if_stmt', 'condition': p[3], 'then': p[6], 'else': p[8], 'lineno': p.lineno(1),
    }


def p_if_stmt_logical(p):
    r"""
    if_stmt : IF LPAREN expr RPAREN statement
    """
    p[0] = {'node': 'if_stmt', 'condition': p[3], 'then': [p[5]], 'else': [], 'lineno': p.lineno(1),
    }


def p_do_stmt_no_step(p):
    r"""
    do_stmt : DO INT_CONST ID EQUALS expr COMMA expr do_body do_end
    """
    if p[2] != p[9]:
        raise ParseError(f"DO label mismatch: expected {p[2]}, got {p[9]}")
    p[0] = {
        'node': 'do_stmt',
        'label': p[2],
        'var': p[3],
        'start': p[5],
        'end': p[7],
        'step': None,
        'body': p[8],
        'end_label': p[9],
        'lineno': p.lineno(1),
    }


def p_do_stmt_with_step(p):
    r"""
    do_stmt : DO INT_CONST ID EQUALS expr COMMA expr COMMA expr do_body do_end
    """
    if p[2] != p[11]:
        raise ParseError(f"DO label mismatch: expected {p[2]}, got {p[11]}")
    p[0] = {
        'node': 'do_stmt',
        'label': p[2],
        'var': p[3],
        'start': p[5],
        'end': p[7],
        'step': p[9],
        'body': p[10],
        'end_label': p[11],
        'lineno': p.lineno(1),
    }


def p_do_body_many(p):
    r"""
    do_body : do_body statement
    """
    p[0] = [*p[1], p[2]]


def p_do_body_empty(p):
    r"""
    do_body : empty
    """
    p[0] = []


def p_do_end(p):
    r"""
    do_end : INT_CONST CONTINUE
    """
    p[0] = p[1]


def p_goto_stmt(p):
    r"""
    goto_stmt : GOTO INT_CONST
    """
    p[0] = {'node': 'goto_stmt', 'label': p[2], 'lineno': p.lineno(1),
    }


def p_continue_stmt(p):
    r"""
    continue_stmt : CONTINUE
    """
    p[0] = {'node': 'continue_stmt', 'lineno': p.lineno(1),
    }


def p_print_stmt(p):
    r"""
    print_stmt : PRINT TIMES COMMA expr_list
    """
    p[0] = {'node': 'print_stmt', 'values': p[4], 'lineno': p.lineno(1),
    }


def p_read_stmt(p):
    r"""
    read_stmt : READ TIMES COMMA read_list
    """
    p[0] = {'node': 'read_stmt', 'items': p[4], 'lineno': p.lineno(1),
    }


def p_read_list_many(p):
    r"""
    read_list : read_list COMMA read_item
    """
    p[0] = [*p[1], p[3]]


def p_read_list_one(p):
    r"""
    read_list : read_item
    """
    p[0] = [p[1]]


def p_read_item_id(p):
    r"""
    read_item : ID
    """
    p[0] = {'node': 'id', 'name': p[1], 'lineno': p.lineno(1),
    }


def p_read_item_array(p):
    r"""
    read_item : ID LPAREN expr RPAREN
    """
    p[0] = {'node': 'array_access', 'name': p[1], 'index': p[3], 'lineno': p.lineno(1),
    }


def p_call_stmt_no_args(p):
    r"""
    call_stmt : CALL ID
    """
    p[0] = {'node': 'call_stmt', 'name': p[2], 'args': [], 'lineno': p.lineno(1),
    }


def p_call_stmt_with_args(p):
    r"""
    call_stmt : CALL ID LPAREN expr_list RPAREN
    """
    p[0] = {'node': 'call_stmt', 'name': p[2], 'args': p[4], 'lineno': p.lineno(1),
    }


def p_return_stmt(p):
    r"""
    return_stmt : RETURN
    """
    p[0] = {'node': 'return_stmt', 'lineno': p.lineno(1),
    }


def p_expr_list_many(p):
    r"""
    expr_list : expr_list COMMA expr
    """
    p[0] = [*p[1], p[3]]


def p_expr_list_one(p):
    r"""
    expr_list : expr
    """
    p[0] = [p[1]]


def p_expr_or(p):
    r"""
    expr : expr OR expr
    """
    p[0] = {'node': 'binop', 'op': 'OR', 'left': p[1], 'right': p[3], 'lineno': p.lineno(1),
    }


def p_expr_and(p):
    r"""
    expr : expr AND expr
    """
    p[0] = {'node': 'binop', 'op': 'AND', 'left': p[1], 'right': p[3], 'lineno': p.lineno(1),
    }


def p_expr_not(p):
    r"""
    expr : NOT expr
    """
    p[0] = {'node': 'unop', 'op': 'NOT', 'value': p[2], 'lineno': p.lineno(1),
    }


def p_expr_eq(p):
    r"""
    expr : expr EQ expr
    """
    p[0] = {'node': 'binop', 'op': 'EQ', 'left': p[1], 'right': p[3], 'lineno': p.lineno(1),
    }


def p_expr_ne(p):
    r"""
    expr : expr NE expr
    """
    p[0] = {'node': 'binop', 'op': 'NE', 'left': p[1], 'right': p[3], 'lineno': p.lineno(1),
    }


def p_expr_lt(p):
    r"""
    expr : expr LT expr
    """
    p[0] = {'node': 'binop', 'op': 'LT', 'left': p[1], 'right': p[3], 'lineno': p.lineno(1),
    }


def p_expr_le(p):
    r"""
    expr : expr LE expr
    """
    p[0] = {'node': 'binop', 'op': 'LE', 'left': p[1], 'right': p[3], 'lineno': p.lineno(1),
    }


def p_expr_gt(p):
    r"""
    expr : expr GT expr
    """
    p[0] = {'node': 'binop', 'op': 'GT', 'left': p[1], 'right': p[3], 'lineno': p.lineno(1),
    }


def p_expr_ge(p):
    r"""
    expr : expr GE expr
    """
    p[0] = {'node': 'binop', 'op': 'GE', 'left': p[1], 'right': p[3], 'lineno': p.lineno(1),
    }


def p_expr_plus(p):
    r"""
    expr : expr PLUS expr
    """
    p[0] = {'node': 'binop', 'op': 'PLUS', 'left': p[1], 'right': p[3], 'lineno': p.lineno(1),
    }


def p_expr_minus(p):
    r"""
    expr : expr MINUS expr
    """
    p[0] = {'node': 'binop', 'op': 'MINUS', 'left': p[1], 'right': p[3], 'lineno': p.lineno(1),
    }


def p_expr_times(p):
    r"""
    expr : expr TIMES expr
    """
    p[0] = {'node': 'binop', 'op': 'TIMES', 'left': p[1], 'right': p[3], 'lineno': p.lineno(1),
    }


def p_expr_divide(p):
    r"""
    expr : expr DIVIDE expr
    """
    p[0] = {'node': 'binop', 'op': 'DIVIDE', 'left': p[1], 'right': p[3], 'lineno': p.lineno(1),
    }


def p_expr_uminus(p):
    r"""
    expr : MINUS expr %prec UMINUS
    """
    p[0] = {'node': 'unop', 'op': 'UMINUS', 'value': p[2], 'lineno': p.lineno(1),
    }


def p_expr_group(p):
    r"""
    expr : LPAREN expr RPAREN
    """
    p[0] = p[2]


def p_expr_call(p):
    r"""
    expr : ID LPAREN expr_list RPAREN
    """
    p[0] = {'node': 'call_expr', 'name': p[1], 'args': p[3], 'lineno': p.lineno(1),
    }


def p_expr_id(p):
    r"""
    expr : ID
    """
    p[0] = {'node': 'id', 'name': p[1], 'lineno': p.lineno(1),
    }


def p_expr_int_const(p):
    r"""
    expr : INT_CONST
    """
    p[0] = {'node': 'int', 'value': p[1], 'lineno': p.lineno(1),
    }


def p_expr_real_const(p):
    r"""
    expr : REAL_CONST
    """
    p[0] = {'node': 'real', 'value': p[1], 'lineno': p.lineno(1),
    }


def p_expr_string(p):
    r"""
    expr : STRING
    """
    p[0] = {'node': 'string', 'value': p[1], 'lineno': p.lineno(1),
    }


def p_expr_true(p):
    r"""
    expr : TRUE
    """
    p[0] = {'node': 'bool', 'value': True, 'lineno': p.lineno(1),
    }


def p_expr_false(p):
    r"""
    expr : FALSE
    """
    p[0] = {'node': 'bool', 'value': False, 'lineno': p.lineno(1),
    }


def p_empty(p):
    r"""
    empty :
    """
    p[0] = None


class ParseError(Exception):
    pass


def p_error(t):
    raise ParseError(f"Unexpected token: {t.type if t else '$'}")


parser = yacc.yacc(start='program_file', write_tables=False)


def parse(text):
    try:
        return parser.parse(text, lexer=lexer)
    except ParseError:
        raise
