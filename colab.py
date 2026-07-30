"""
Google Colab — 1 cell la chay.
Copy toan bo cell nay vao Colab va chay.
"""
import subprocess, sys, IPython.display

subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "git+https://github.com/dungtrantriphimphenhuda-code/Voice-enhance.git",
    "deepfilternet", "voicefixer", "pedalboard", "pyloudnorm"])

from voice_enhance import enhance
from google.colab import files

uploaded = files.upload()
for fname in uploaded:
    out = enhance(fname)
    IPython.display.Audio(out)
    files.download(out)
