#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import re
import runpy
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import List

INDENT = 4


class AxiomCompileError(Exception):
    pass


@dataclass
class Block:
    kind: str
    indent: int


VAR_RE = re.compile(r'^(l\.|g\.|c\.)\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$')
FUNC_RE = re.compile(r'^f\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\((.*)\)\s*$')
CLASS_RE = re.compile(r'^cls\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*;\s*$')
IF_RE = re.compile(r'^i\.\s+(.+?)\s+do\s*$')
ELIF_RE = re.compile(r'^ef\.\s+(.+?)\s+do\s*$')
ELSE_RE = re.compile(r'^e\.\s*(.*?)\s*do\s*$')
BRING_RE = re.compile(r'^bring\s+([A-Za-z0-9_\.]+)(?:\s+as\s+([A-Za-z_][A-Za-z0-9_]*))?\s*$')
LOOK_RE = re.compile(r'^look\s+([A-Za-z0-9_\.]+)\s+bring\s+(.+)$')
DECORATOR_RE = re.compile(r'^\$([A-Za-z_][A-Za-z0-9_]*)\s*$')


def normalize_indent(line: str) -> tuple[int, str]:
    expanded = line.replace('\t', ' ' * INDENT)
    stripped = expanded.lstrip(' ')
    spaces = len(expanded) - len(stripped)
    if spaces % INDENT != 0:
        raise AxiomCompileError(
            f"invalid indentation: use tabs or multiples of {INDENT} spaces only"
        )
    return spaces // INDENT, stripped.rstrip()


def translate_expr(expr: str) -> str:
    expr = re.sub(r'\btrue\b', 'True', expr)
    expr = re.sub(r'\bfalse\b', 'False', expr)
    expr = re.sub(r'\bnone\b', 'None', expr)
    return expr


def compile_source(source: str, source_name: str = '<string>') -> str:
    py_lines: List[str] = [
        'import builtins as __axiom_builtins',
        '',
        'def log(*args):',
        '    __axiom_builtins.print(*args)',
        '',
        'def warn(*args):',
        '    __axiom_builtins.print("[warn]", *args)',
        '',
        'def error(*args):',
        '    __axiom_builtins.print("[error]", *args)',
        '',
    ]

    blocks: List[Block] = []
    pending_decorators: List[str] = []
    lines = source.splitlines()

    for lineno, raw in enumerate(lines, start=1):
        if not raw.strip():
            py_lines.append('')
            continue

        indent, content = normalize_indent(raw)

        if content.startswith('#'):
            py_lines.append(' ' * (indent * INDENT) + content)
            continue

        if content in {'fend.', 'clsend.', 'end'}:
            if not blocks:
                raise AxiomCompileError(f'Line {lineno}: unexpected {content}')
            top = blocks.pop()
            if content == 'fend.' and top.kind != 'function':
                raise AxiomCompileError(f'Line {lineno}: fend. closes a function only')
            if content == 'clsend.' and top.kind != 'class':
                raise AxiomCompileError(f'Line {lineno}: clsend. closes a class only')
            if content == 'end' and top.kind not in {'if', 'elif', 'else'}:
                raise AxiomCompileError(f'Line {lineno}: end closes a condition block only')
            # If closing if/elif/else chain, pop any earlier chain blocks at same indent
            if content == 'end':
                while blocks and blocks[-1].kind in {'ifchain'} and blocks[-1].indent == top.indent:
                    blocks.pop()
            continue

        # ef./e. need to close previous branch first, but keep chain marker alive
        if ELIF_RE.match(content) or ELSE_RE.match(content):
            if not blocks:
                raise AxiomCompileError(f'Line {lineno}: {content.split()[0]} without matching i.')
            if blocks[-1].kind not in {'if', 'elif'}:
                raise AxiomCompileError(f'Line {lineno}: {content.split()[0]} without matching active branch')
            branch = blocks.pop()
            if branch.indent != indent:
                raise AxiomCompileError(f'Line {lineno}: {content.split()[0]} must align with i.')
            if not blocks or blocks[-1].kind != 'ifchain' or blocks[-1].indent != indent:
                raise AxiomCompileError(f'Line {lineno}: broken condition chain')

        # Non-branch lines must be nested one level deeper than active executable block
        expected_min_indent = 0
        if blocks:
            active = blocks[-1]
            if active.kind in {'ifchain'}:
                # actual active branch is one below ifchain, already handled above
                pass
            else:
                expected_min_indent = active.indent + 1
        if content not in {'fend.', 'clsend.', 'end'} and not (ELIF_RE.match(content) or ELSE_RE.match(content)):
            if blocks and blocks[-1].kind not in {'ifchain'}:
                parent = blocks[-1]
                allowed_same = ((parent.kind == 'class' and CLASS_RE.match(content) is None and FUNC_RE.match(content) is not None)
                                or False)
                if indent < expected_min_indent and not (
                    (parent.kind == 'class' and indent == parent.indent + 1 and FUNC_RE.match(content))
                ):
                    raise AxiomCompileError(
                        f'Line {lineno}: expected indent level {expected_min_indent}, got {indent}. '
                        'Indent one level only inside blocks and use fend./clsend./end to close.'
                    )

        out_indent = ' ' * (indent * INDENT)

        m = DECORATOR_RE.match(content)
        if m:
            pending_decorators.append(m.group(1))
            continue

        m = BRING_RE.match(content)
        if m:
            module, alias = m.groups()
            if alias:
                py_lines.append(f'{out_indent}import {module} as {alias}')
            else:
                py_lines.append(f'{out_indent}import {module}')
            continue

        m = LOOK_RE.match(content)
        if m:
            module, items = m.groups()
            items = items.strip()
            if items == 'a.':
                py_lines.append(f'{out_indent}from {module} import *')
            else:
                py_lines.append(f'{out_indent}from {module} import {items}')
            continue

        m = CLASS_RE.match(content)
        if m:
            if pending_decorators:
                for deco in pending_decorators:
                    py_lines.append(f'{out_indent}@{deco}')
                pending_decorators.clear()
            py_lines.append(f'{out_indent}class {m.group(1)}:')
            blocks.append(Block('class', indent))
            continue

        m = FUNC_RE.match(content)
        if m:
            if pending_decorators:
                for deco in pending_decorators:
                    py_lines.append(f'{out_indent}@{deco}')
                pending_decorators.clear()
            name, args = m.groups()
            if name == 'init':
                name = '__init__'
            py_lines.append(f'{out_indent}def {name}({args}):')
            blocks.append(Block('function', indent))
            continue

        m = IF_RE.match(content)
        if m:
            condition = translate_expr(m.group(1))
            py_lines.append(f'{out_indent}if {condition}:')
            blocks.append(Block('ifchain', indent))
            blocks.append(Block('if', indent))
            continue

        m = ELIF_RE.match(content)
        if m:
            condition = translate_expr(m.group(1))
            py_lines.append(f'{out_indent}elif {condition}:')
            blocks.append(Block('elif', indent))
            continue

        m = ELSE_RE.match(content)
        if m:
            py_lines.append(f'{out_indent}else:')
            blocks.append(Block('else', indent))
            continue

        m = VAR_RE.match(content)
        if m:
            scope, name, expr = m.groups()
            if scope == 'g.' and any(b.kind == 'function' for b in blocks):
                py_lines.append(f'{out_indent}global {name}')
            py_lines.append(f'{out_indent}{name} = {translate_expr(expr)}')
            continue

        if content == 'ign':
            py_lines.append(f'{out_indent}pass')
            continue

        if content.startswith('r. '):
            py_lines.append(f'{out_indent}return {translate_expr(content[3:].strip())}')
            continue

        py_lines.append(f'{out_indent}{translate_expr(content)}')

    if pending_decorators:
        raise AxiomCompileError('Dangling decorator at end of file')
    if blocks:
        openers = ', '.join(b.kind for b in blocks)
        raise AxiomCompileError(f'Unclosed blocks: {openers}')
    return '\n'.join(py_lines) + '\n'


def compile_file(input_path: pathlib.Path, output_path: pathlib.Path | None = None) -> pathlib.Path:
    source = input_path.read_text(encoding='utf-8')
    compiled = compile_source(source, str(input_path))
    if output_path is None:
        output_path = input_path.with_suffix('.py')
    output_path.write_text(compiled, encoding='utf-8')
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description='Compile Axiom source to Python.')
    parser.add_argument('input', type=pathlib.Path, help='Input .axiom file')
    parser.add_argument('-o', '--output', type=pathlib.Path, help='Output .py file')
    parser.add_argument('--run', action='store_true', help='Run after compiling')
    args = parser.parse_args()

    try:
        output = compile_file(args.input, args.output)
    except AxiomCompileError as exc:
        print(f'Compile error: {exc}', file=sys.stderr)
        return 1

    print(f'Compiled -> {output}')

    if args.run:
        env = dict(**__import__('os').environ)
        root = pathlib.Path(__file__).resolve().parent
        existing = env.get('PYTHONPATH', '')
        env['PYTHONPATH'] = str(root) + ((__import__('os').pathsep + existing) if existing else '')
        result = subprocess.run([sys.executable, str(output)], env=env)
        return result.returncode
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
