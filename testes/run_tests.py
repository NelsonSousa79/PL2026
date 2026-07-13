#!/usr/bin/env python3
"""Test runner do compilador Fortran -> VM.

Corre todos os .f90 em positivos/ (devem compilar) e em negativos/
(devem falhar com a mensagem em <nome>.expected).
"""
import os
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
COMPILER = os.path.join(ROOT, 'src', 'main.py')
PYTHON = sys.executable

GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def ok(msg):
    print(f"  {GREEN}OK{RESET} {msg}")

def fail(msg, detail=''):
    print(f"  {RED}FAIL{RESET} {msg}")
    if detail:
        for line in detail.splitlines():
            print(f"       {line}")

def run_compiler(f90):
    return subprocess.run(
        [PYTHON, COMPILER, f90],
        capture_output=True, text=True,
    )

def test_positivos():
    print("== Positivos ==")
    folder = os.path.join(HERE, 'positivos')
    files = sorted(f for f in os.listdir(folder) if f.endswith('.f90'))
    passed = 0
    for f in files:
        path = os.path.join(folder, f)
        vm_path = os.path.splitext(path)[0] + '.vm'
        if os.path.exists(vm_path):
            os.remove(vm_path)
        res = run_compiler(path)
        if res.returncode != 0:
            fail(f, res.stdout + res.stderr)
        elif not os.path.exists(vm_path):
            fail(f, 'compilou mas nao gerou .vm')
        else:
            ok(f)
            passed += 1
    return passed, len(files)

def test_negativos():
    print("== Negativos ==")
    folder = os.path.join(HERE, 'negativos')
    files = sorted(f for f in os.listdir(folder) if f.endswith('.f90'))
    passed = 0
    for f in files:
        path = os.path.join(folder, f)
        exp_path = os.path.splitext(path)[0] + '.expected'
        if not os.path.exists(exp_path):
            fail(f, f'falta {os.path.basename(exp_path)}')
            continue
        with open(exp_path) as ef:
            expected = ef.read().strip()
        res = run_compiler(path)
        output = res.stdout + res.stderr
        if res.returncode == 0:
            fail(f, 'compilou (era suposto falhar)')
        elif expected not in output:
            fail(f, f"esperava '{expected}', obteve:\n{output.strip()}")
        else:
            ok(f)
            passed += 1
    return passed, len(files)

def main():
    p_ok, p_tot = test_positivos()
    n_ok, n_tot = test_negativos()
    print()
    total_ok = p_ok + n_ok
    total = p_tot + n_tot
    print(f"Resultado: {total_ok}/{total} testes passaram")
    sys.exit(0 if total_ok == total else 1)

if __name__ == '__main__':
    main()
