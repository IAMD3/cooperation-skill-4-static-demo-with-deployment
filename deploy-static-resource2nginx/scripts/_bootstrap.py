"""Self-bootstrap: create a local venv with paramiko + scp on first run.

Every entry script (deploy.py, verify_nginx.py, setup_nginx.py) calls
ensure_venv() before importing any third-party module. The first call
creates ``<skill-dir>/.venv`` and installs the two SSH libs; subsequent
calls re-exec under the venv interpreter immediately.

Uses only the standard library so it works on a bare Python 3.8+ install.
"""

import os
import subprocess
import sys
import venv

_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_VENV_DIR = os.path.join(_SKILL_DIR, ".venv")
if os.name == "nt":
    _VENV_PY = os.path.join(_VENV_DIR, "Scripts", "python.exe")
else:
    _VENV_PY = os.path.join(_VENV_DIR, "bin", "python")
_STAMP = os.path.join(_VENV_DIR, ".deps-installed")
_REQUIREMENTS = ["paramiko", "scp"]


def _already_in_venv():
    # sys.prefix points to the venv root when running under that venv. We can't
    # compare sys.executable to _VENV_PY because venv's python is a symlink to
    # the system python on many platforms (e.g. macOS framework builds).
    try:
        return os.path.samefile(sys.prefix, _VENV_DIR)
    except OSError:
        return False


def _create_venv():
    print(f"[bootstrap] creating local venv at {_VENV_DIR} (one-time setup) ...", flush=True)
    venv.EnvBuilder(with_pip=True, clear=False).create(_VENV_DIR)


def _install_requirements():
    print(f"[bootstrap] installing {', '.join(_REQUIREMENTS)} into venv ...", flush=True)
    subprocess.check_call(
        [_VENV_PY, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", *_REQUIREMENTS]
    )
    with open(_STAMP, "w") as f:
        f.write("ok\n")


def ensure_venv():
    """Ensure we are running under .venv with paramiko+scp installed."""
    if _already_in_venv() and os.path.exists(_STAMP):
        return
    if not os.path.exists(_VENV_PY):
        _create_venv()
    if not os.path.exists(_STAMP):
        _install_requirements()
    if not _already_in_venv():
        os.execv(_VENV_PY, [_VENV_PY, *sys.argv])


if __name__ == "__main__":
    ensure_venv()
    print("[bootstrap] venv is ready.")
