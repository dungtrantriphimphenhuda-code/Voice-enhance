# Voice Enhance Pipeline

[Audio Gốc] → [1. AI Denoise & Dereverberation] → [2. AI Speech Restoration] → [3. DSP Studio] → [Audio Output Studio]

Pipeline xử lý giọng nói chất lượng phòng thu dành cho YouTuber, Podcasters — hoàn toàn mã nguồn mở.

## Pipeline

| Step | Engine | Chức năng |
|------|--------|-----------|
| **1. Denoise** | DeepFilterNet / Resemble Enhance | Lọc nhiễu môi trường, khử vang, giữ nguyên dải mid |
| **2. Restore** | VoiceFixer | Khôi phục dải tần cao bị mất, sửa méo tiếng |
| **3. DSP** | Pedalboard (Spotify) | HPF, DeEsser, Compressor, Limiter — chuẩn phòng thu |
| **4. Normalize** | pyloudnorm (EBU R128) | Chuẩn hóa âm lượng -16 LUFS / -14 LUFS |

## Quick Start

```bash
pip install -r requirements.txt
python -m voice_enhance.cli input.wav -o enhanced.wav
```

## Tùy chỉnh

```bash
# Chỉ denoise + normalize, bỏ qua restore và DSP
python -m voice_enhance.cli input.wav --no-restore --no-dsp

# Dùng Resemble Enhance thay DeepFilterNet
python -m voice_enhance.cli input.wav --denoise-engine resemble

# Chuẩn hóa podcast (-16 LUFS mặc định)
python -m voice_enhance.cli input.wav --target-lufs -16

# Giữ file trung gian để debug
python -m voice_enhance.cli input.wav --keep-intermediate
```

## Yêu cầu

- Python 3.10+
- PyTorch (cho VoiceFixer / Resemble Enhance)
- FFmpeg (cho đọc multi-format)

## License

MIT
