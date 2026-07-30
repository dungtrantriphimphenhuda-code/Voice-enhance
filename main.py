import sys
from voice_enhance import enhance

DEPS = [("deepfilternet", "1.Denoise"), ("voicefixer", "2.Restore"),
        ("pedalboard", "3.DSP"), ("pyloudnorm", "4.Normalize")]

print("--- Kiem tra thu vien ---")
for name, label in DEPS:
    try:
        __import__(name)
        print(f"  {label}: OK")
    except ImportError:
        print(f"  {label}: THIEU (pip install {name})")

path = (sys.argv[1] if len(sys.argv) > 1
        else input("\nNhap duong dan file audio: ")).strip().strip('"')

if not path:
    print("Khong co file.")
    sys.exit(1)

try:
    result = enhance(path)
    print(f"\nXong! File da luu tai: {result}")
except Exception as e:
    print(f"Loi: {e}")
    sys.exit(1)
