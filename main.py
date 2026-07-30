import sys
from voice_enhance import enhance

path = (sys.argv[1] if len(sys.argv) > 1
        else input("Nhap duong dan file audio: ")).strip().strip('"')

if not path:
    print("Khong co file.")
    sys.exit(1)

try:
    result = enhance(path)
    print(f"Xong! File da luu tai: {result}")
except Exception as e:
    print(f"Loi: {e}")
    sys.exit(1)
