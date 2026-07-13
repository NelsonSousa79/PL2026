import sys
import json
from parser import parse, ParseError
from semantic import SemanticAnalyzer, SemanticError
from codegen import CodeGenerator

import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/main.py <file.f90>")
        return
    filename = sys.argv[1]
    try:
        with open(filename, 'r') as f:
            code = f.read()
        try:
            ast = parse(code)
            
            # Semantic Analysis
            analyzer = SemanticAnalyzer()
            try:
                analyzer.analyze(ast)
                
               
                cg = CodeGenerator(analyzer.st)
                instructions = cg.generate(ast)
                
               
                base_name = os.path.splitext(filename)[0]
                out_filename = base_name + '.vm'
                
                with open(out_filename, 'w') as out_f:
                    for instr in instructions:
                        out_f.write(instr + '\n')
                        
                print(f"Codigo gerado com sucesso: {out_filename}")
                
            except SemanticError as e:
                print(f"Semantic Error: {e}")
                sys.exit(1)

        except ParseError as e:
            print(f"Syntax Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File {filename} não foi encontrado.")
        sys.exit(1)

if __name__ == '__main__':
    main()
