#!/usr/bin/env python3
"""Beyond the Map's Edge — solve builder.

ONE COMMAND:   python3 run.py
That starts the tool and opens it in your browser. Everything else is optional:

  python3 run.py import FILE.json       load your research database through mapping.json
  python3 run.py fetch-data MT WY ID    download USGS place names for those states, then verify the inventory
  python3 run.py verify                 re-check built-in features against downloaded GNIS
  python3 run.py monitor                check the forums / Mysterious Writings / treasure.quest for new statements
  python3 run.py rescore                re-score every saved solve
  python3 run.py --port 8765            use a different port

Technology (why): plain Python 3 (already on your machine), SQLite (one file, no
server, works offline), a single web page for the interface. The only optional
dependency is the official 'anthropic' package for the AI features; this script
installs it into a private folder (.venv) the first time it has internet. If it
cannot, the tool still runs — only the AI buttons are greyed out.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.join(HERE, ".venv")


def venv_python():
    return os.path.join(VENV, "Scripts" if os.name == "nt" else "bin", "python.exe" if os.name == "nt" else "python")


def ensure_anthropic():
    """Make the AI package available without asking the user to install anything."""
    if os.environ.get("SOLVEBUILDER_NO_INSTALL"):
        return
    try:
        import anthropic  # noqa: F401
        return
    except Exception:
        pass
    if sys.prefix != VENV and os.path.exists(venv_python()):
        os.execv(venv_python(), [venv_python(), __file__] + sys.argv[1:])
    if sys.prefix != VENV:
        print("First run: creating a private Python environment and installing the 'anthropic' package (needs internet, ~20 seconds)…")
        try:
            import venv
            venv.create(VENV, with_pip=True)
            subprocess.check_call([venv_python(), "-m", "pip", "install", "-q", "anthropic"])
            os.execv(venv_python(), [venv_python(), __file__] + sys.argv[1:])
        except Exception as e:
            print(f"  Could not install it ({e}). Continuing without AI features; run again with internet to enable them.")
            os.environ["SOLVEBUILDER_NO_INSTALL"] = "1"


def main():
    ensure_anthropic()
    sys.path.insert(0, HERE)
    from app import server
    args = sys.argv[1:]
    if args and args[0] == "import":
        server.cli_import(args[1])
    elif args and args[0] == "fetch-data":
        server.cli_fetch(args[1:] or ["MT", "WY", "ID", "UT"])
    elif args and args[0] == "verify":
        server.cli_verify()
    elif args and args[0] == "monitor":
        server.cli_monitor()
    elif args and args[0] == "rescore":
        server.cli_rescore()
    else:
        port = 8765
        if "--port" in args:
            port = int(args[args.index("--port") + 1])
        server.serve(port, open_browser="--no-browser" not in args)


if __name__ == "__main__":
    main()
