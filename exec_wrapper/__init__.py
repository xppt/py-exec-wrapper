import os
import shlex
import stat
import sys
import textwrap
from io import BytesIO
from pathlib import Path
from typing import Sequence
from zipfile import ZipFile


def write_exec_wrapper(
        dest_path: str,
        args: Sequence[str],
        *,
        python: str = sys.executable,
        chmod: bool = True,
) -> None:

    Path(dest_path).write_bytes(build_exec_wrapper(args, python=python))

    if chmod and os.name == 'posix':
        _add_exec_bit(dest_path)


def build_exec_wrapper(
        args: Sequence[str],
        *,
        python: str = sys.executable,
) -> bytes:

    if os.name == 'posix':
        script = build_exec_wrapper_posix(args)

        # probably we should support non-utf8 filesystem encoding
        wrapper_bytes = script.encode('utf-8')

    elif os.name == 'nt':
        wrapper_bytes = build_exec_wrapper_nt(args, python)

    else:
        raise NotImplementedError

    return wrapper_bytes


def build_exec_wrapper_posix(args: Sequence[str]) -> str:
    args_str = ' '.join(shlex.quote(arg) for arg in args)

    script = textwrap.dedent(f'''
        #!/usr/bin/env bash
        exec {args_str} "$@"
    ''').lstrip()

    return script


def build_exec_wrapper_nt(args: Sequence[str], python: str) -> bytes:
    script = textwrap.dedent(f'''
        import sys
        import subprocess
        sys.exit(subprocess.run({list(args)!r} + sys.argv[1:]).returncode)
    ''').lstrip()

    return build_nt_wrapper(build_nt_shebang(python), script)


def build_nt_shebang(executable: str) -> str:
    assert '"' not in executable
    return f'#!"{executable}"'


def build_nt_wrapper(shebang: str, script: str) -> bytes:
    stream = BytesIO()
    with ZipFile(stream, 'w') as zip_file:
        zip_file.writestr('__main__.py', script.encode('utf-8'))

    return _nt_launcher + shebang.rstrip().encode('utf-8') + b'\n' + stream.getvalue()


def executable_suffix() -> str:
    if os.name == 'nt':
        return '.exe'
    else:
        return ''


def _add_exec_bit(path: str) -> None:
    mode = os.stat(path).st_mode
    mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    os.chmod(path, mode)


# https://bitbucket.org/vinay.sajip/simple_launcher/src/master/
_nt_launcher = Path(__file__).parent.joinpath('_nt_launcher.exe').read_bytes()
