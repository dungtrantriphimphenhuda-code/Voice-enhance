import sys, subprocess, pathlib

subprocess.run([sys.executable, str(pathlib.Path(__file__).parent.parent / "main.py"), *sys.argv[1:]])
