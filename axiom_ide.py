#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from axiomc import AxiomCompileError, compile_source  # noqa: E402

KEYWORDS = {
    'l.', 'g.', 'c.', 'f.', 'fend.', 'cls.', 'clsend.', 'i.', 'ef.', 'e.', 'end',
    'bring', 'look', 'as', 'do', 'r.', 'ign'
}

BUILTINS = {'log', 'warn', 'error'}

THEMES = {
    'dark': {
        'bg': '#1e1e1e', 'fg': '#d4d4d4', 'insert': '#d4d4d4', 'select': '#264f78',
        'keyword': '#569cd6', 'string': '#ce9178', 'comment': '#6a9955',
        'builtin': '#4ec9b0', 'status_bg': '#252526', 'status_fg': '#d4d4d4'
    },
    'light': {
        'bg': '#ffffff', 'fg': '#202020', 'insert': '#202020', 'select': '#cce8ff',
        'keyword': '#0000cc', 'string': '#a31515', 'comment': '#008000',
        'builtin': '#267f99', 'status_bg': '#f3f3f3', 'status_fg': '#202020'
    },
}


class AxiomIDE(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Axiom IDE')
        self.geometry('1100x720')
        self.current_file: pathlib.Path | None = None
        self.theme_name = 'dark'

        self._build_ui()
        self.apply_theme()
        self.load_sample()

    def _build_ui(self) -> None:
        toolbar = tk.Frame(self)
        toolbar.pack(fill='x')

        btn = lambda text, cmd: tk.Button(toolbar, text=text, command=cmd, padx=8, pady=4)
        btn('New', self.new_file).pack(side='left', padx=2, pady=4)
        btn('Open', self.open_file).pack(side='left', padx=2, pady=4)
        btn('Save', self.save_file).pack(side='left', padx=2, pady=4)
        btn('Compile', self.compile_current).pack(side='left', padx=2, pady=4)
        btn('Run', self.run_current).pack(side='left', padx=2, pady=4)
        btn('Toggle Theme', self.toggle_theme).pack(side='left', padx=8, pady=4)

        self.editor = tk.Text(self, wrap='none', undo=True, font=('Consolas', 12))
        self.editor.pack(fill='both', expand=True)
        self.editor.bind('<KeyRelease>', lambda e: self.highlight())

        self.status = tk.Label(self, anchor='w', padx=8)
        self.status.pack(fill='x')

        self.output = tk.Text(self, height=10, wrap='word', font=('Consolas', 10))
        self.output.pack(fill='x')

        self.editor.tag_configure('keyword')
        self.editor.tag_configure('string')
        self.editor.tag_configure('comment')
        self.editor.tag_configure('builtin')

    def apply_theme(self) -> None:
        theme = THEMES[self.theme_name]
        self.configure(bg=theme['status_bg'])
        self.editor.configure(bg=theme['bg'], fg=theme['fg'], insertbackground=theme['insert'], selectbackground=theme['select'])
        self.output.configure(bg=theme['bg'], fg=theme['fg'], insertbackground=theme['insert'])
        self.status.configure(bg=theme['status_bg'], fg=theme['status_fg'])
        self.editor.tag_configure('keyword', foreground=theme['keyword'])
        self.editor.tag_configure('string', foreground=theme['string'])
        self.editor.tag_configure('comment', foreground=theme['comment'])
        self.editor.tag_configure('builtin', foreground=theme['builtin'])
        self.highlight()

    def toggle_theme(self) -> None:
        self.theme_name = 'light' if self.theme_name == 'dark' else 'dark'
        self.apply_theme()

    def set_status(self, text: str) -> None:
        self.status.config(text=text)

    def write_output(self, text: str, clear: bool = True) -> None:
        if clear:
            self.output.delete('1.0', 'end')
        self.output.insert('end', text)
        self.output.see('end')

    def new_file(self) -> None:
        self.current_file = None
        self.editor.delete('1.0', 'end')
        self.set_status('New file')
        self.highlight()

    def open_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[('Axiom files', '*.axiom'), ('All files', '*.*')])
        if not path:
            return
        self.current_file = pathlib.Path(path)
        self.editor.delete('1.0', 'end')
        self.editor.insert('1.0', self.current_file.read_text(encoding='utf-8'))
        self.set_status(f'Opened {self.current_file.name}')
        self.highlight()

    def save_file(self) -> pathlib.Path | None:
        if self.current_file is None:
            path = filedialog.asksaveasfilename(defaultextension='.axiom', filetypes=[('Axiom files', '*.axiom')])
            if not path:
                return None
            self.current_file = pathlib.Path(path)
        self.current_file.write_text(self.editor.get('1.0', 'end-1c'), encoding='utf-8')
        self.set_status(f'Saved {self.current_file.name}')
        return self.current_file

    def compile_current(self) -> None:
        code = self.editor.get('1.0', 'end-1c')
        try:
            py_code = compile_source(code)
        except AxiomCompileError as exc:
            self.write_output(f'Compile error: {exc}\n')
            self.set_status('Compile failed')
            return
        self.write_output(py_code)
        self.set_status('Compile successful')

    def run_current(self) -> None:
        code = self.editor.get('1.0', 'end-1c')
        try:
            py_code = compile_source(code)
        except AxiomCompileError as exc:
            self.write_output(f'Compile error: {exc}\n')
            self.set_status('Run failed: compile error')
            return

        with tempfile.TemporaryDirectory() as temp_dir:
            temp = pathlib.Path(temp_dir)
            source_path = temp / 'main.axiom'
            py_path = temp / 'main.py'
            source_path.write_text(code, encoding='utf-8')
            py_path.write_text(py_code, encoding='utf-8')
            env = dict(**__import__('os').environ)
            existing = env.get('PYTHONPATH', '')
            env['PYTHONPATH'] = str(ROOT) + ((__import__('os').pathsep + existing) if existing else '')
            result = subprocess.run(
                [sys.executable, str(py_path)],
                capture_output=True,
                text=True,
                env=env,
                cwd=str(ROOT),
            )
        text = ''
        if result.stdout:
            text += result.stdout
        if result.stderr:
            text += result.stderr
        if not text:
            text = '[program finished with no output]\n'
        self.write_output(text)
        self.set_status(f'Run finished ({result.returncode})')

    def load_sample(self) -> None:
        sample = ROOT / 'examples' / 'demo.axiom'
        if sample.exists():
            self.current_file = sample
            self.editor.insert('1.0', sample.read_text(encoding='utf-8'))
            self.set_status(f'Loaded sample {sample.name}')
            self.highlight()

    def highlight(self) -> None:
        content = self.editor.get('1.0', 'end-1c')
        for tag in ('keyword', 'string', 'comment', 'builtin'):
            self.editor.tag_remove(tag, '1.0', 'end')

        lines = content.splitlines()
        for row, line in enumerate(lines, start=1):
            # comment
            if '#' in line:
                idx = line.find('#')
                self.editor.tag_add('comment', f'{row}.{idx}', f'{row}.{len(line)}')
                code_part = line[:idx]
            else:
                code_part = line

            # strings
            for match in __import__('re').finditer(r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'', code_part):
                self.editor.tag_add('string', f'{row}.{match.start()}', f'{row}.{match.end()}')

            for token in sorted(KEYWORDS | BUILTINS, key=len, reverse=True):
                start = 0
                while True:
                    idx = code_part.find(token, start)
                    if idx == -1:
                        break
                    end = idx + len(token)
                    prev_ok = idx == 0 or not (code_part[idx - 1].isalnum() or code_part[idx - 1] == '_')
                    next_ok = end >= len(code_part) or not (code_part[end:end+1].isalnum() or code_part[end:end+1] == '_')
                    if prev_ok and next_ok:
                        tag = 'builtin' if token in BUILTINS else 'keyword'
                        self.editor.tag_add(tag, f'{row}.{idx}', f'{row}.{end}')
                    start = end


def main() -> None:
    app = AxiomIDE()
    app.mainloop()


if __name__ == '__main__':
    main()
