# Voice Enhance

[Audio Gốc] → [Denoise] → [Restore] → [DSP] → [Normalize] → [Output Studio]

## Cach dung

```bash
pip install -r requirements.txt
python main.py
```

No se hoi duong dan file, xu ly, va tra ve file da enhance.

## GitHub Actions

Vao repo → Actions → "Enhance Audio" → Run workflow.

## API

```python
from voice_enhance import enhance
enhance("input.wav", "output.wav")
enhance("input.wav", "output.wav", denoise_engine="resemble", target_lufs=-14)
```

MIT
