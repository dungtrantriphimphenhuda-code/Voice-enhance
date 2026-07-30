from voice_enhance import enhance

path = input("Nhap duong dan file audio: ").strip().strip('"')
if not path:
    print("Khong co file.")
else:
    result = enhance(path)
    print(f"Xong! File da luu tai: {result}")
