"""Single-writer lock and durable request journal, without automatic replay.

This is a crash detector, not a sandbox or a multi-file transaction. External
effects cannot be rolled back by restoring a JSON file. Recovery is explicit.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + secrets.token_hex(8) + '.tmp')
    try:
        with temporary.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def now():
    return datetime.now(timezone.utc).isoformat()


def safe_root(project):
    project = Path(project).resolve()
    metadata = project / '.nasaq'
    # Includes junctions: resolve() follows them on Windows.
    if metadata.resolve() != metadata:
        raise ValueError('metadata_link_not_allowed')
    if metadata.exists():
        for name in ('writer.lock', 'requests.json', 'runtime.json', 'project.json'):
            item = metadata / name
            if item.resolve() != item:
                raise ValueError('metadata_link_not_allowed')
    return metadata


@contextmanager
def writer(project):
    metadata = safe_root(project)
    metadata.mkdir(parents=True, exist_ok=True)
    lock = metadata / 'writer.lock'
    token = secrets.token_hex(16)
    try:
        with lock.open('x', encoding='utf-8') as stream:
            json.dump({'pid': os.getpid(), 'token': token, 'created': now()}, stream)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise ValueError('writer_busy_or_recovery_required') from exc
    try:
        yield metadata
    finally:
        if lock.exists() and read(lock).get('token') == token:
            lock.unlink()


def clear_dead_writer(project):
    """Only called by explicit recovery; never steal a live writer's lock."""
    metadata = safe_root(project)
    lock = metadata / 'writer.lock'
    if not lock.exists():
        return False
    pid = read(lock).get('pid')
    if type(pid) is not int or pid <= 0:
        raise ValueError('invalid_writer_lock')
    # os.kill(pid, 0) is unsafe on Windows (may terminate). OpenProcess only
    # queries state; an inaccessible process is conservatively treated as live.
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if handle:
            code = wintypes.DWORD()
            try:
                live = not kernel.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value == 259
            finally:
                kernel.CloseHandle(handle)
        else:
            live = ctypes.get_last_error() != 87  # ERROR_INVALID_PARAMETER
    else:
        try:
            os.kill(pid, 0)
            live = True
        except ProcessLookupError:
            live = False
        except PermissionError:
            live = True
    if live:
        raise ValueError('writer_still_alive')
    lock.unlink()
    return True
