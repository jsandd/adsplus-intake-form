#!/usr/bin/env python3
"""Beyond the Map's Edge — constraint-filter map (local).

ONE COMMAND:   python3 run.py
Starts the tool and opens it in your browser (http://localhost:8790).

Optional:
  python3 run.py fetch-dem MT WY        download 30 m elevation tiles for whole states ahead of time
  python3 run.py fetch-tran MT WY       download USGS roads / trails / railroads for those states
  python3 run.py fetch-gnis MT WY       download USGS place names (cemeteries, caves, mines)
  python3 run.py load-padus PATH.gpkg   load the PAD-US GeoPackage you downloaded (land owner, access)
  python3 run.py --port 8790            use a different port

First run creates a private Python environment (.venv) and installs five
packages (numpy, shapely, pyproj, pyogrio, rasterio). That needs internet once.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.join(HERE, ".venv")
PKGS = ["numpy", "shapely", "pyproj", "pyogrio", "rasterio"]


def venv_python():
    return os.path.join(VENV, "Scripts" if os.name == "nt" else "bin", "python.exe" if os.name == "nt" else "python")


def ensure_deps():
    try:
        import numpy, shapely, pyproj, pyogrio, rasterio  # noqa: F401
        return
    except Exception:
        pass
    if sys.prefix != VENV and os.path.exists(venv_python()):
        os.execv(venv_python(), [venv_python(), __file__] + sys.argv[1:])
    if sys.prefix != VENV:
        print("First run: creating a private Python environment and installing the map libraries (needs internet, 1–3 minutes)…")
        import venv
        venv.create(VENV, with_pip=True)
        subprocess.check_call([venv_python(), "-m", "pip", "install", "-q"] + PKGS)
        os.execv(venv_python(), [venv_python(), __file__] + sys.argv[1:])
    print("The map libraries could not be imported. Try: python3 -m pip install " + " ".join(PKGS))
    sys.exit(1)


def main():
    ensure_deps()
    sys.path.insert(0, HERE)
    from app import server, config, dem, vectors, padus
    args = sys.argv[1:]
    if args and args[0] == "fetch-dem":
        for st in args[1:]:
            dem.fetch_state(st.upper(), log=print)
        return
    if args and args[0] == "fetch-tran":
        for st in args[1:]:
            vectors.ingest_tran(st.upper(), log=print)
        return
    if args and args[0] == "fetch-gnis":
        for st in args[1:]:
            vectors.ingest_gnis(st.upper(), log=print)
        return
    if args and args[0] == "load-padus":
        padus.ingest(args[1], log=print)
        return
    port = int(args[args.index("--port") + 1]) if "--port" in args else config.PORT
    server.serve(port, open_browser="--no-browser" not in args)


if __name__ == "__main__":
    main()
