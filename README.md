# Adobe Podcast Enhance — GitHub Actions Workflow

Tự động hóa việc nâng cấp chất lượng âm thanh (enhance speech) qua **Adobe Podcast** bằng GitHub Actions. Workflow kích hoạt khi một issue comment bắt đầu bằng `/enhance` và chứa URL trỏ đến file âm thanh.

---

## Cấu trúc thư mục

```
.
├── .github/
│   └── workflows/
│       └── enhance_from_issue.yml   # Workflow YAML
├── scripts/
│   ├── enhance.py                   # Script chính
│   ├── login_helper.py              # Script tạo auth.json
│   └── requirements.txt             # Python dependencies
└── README.md
```

---

## Thiết lập (Setup)

### Bước 1: Clone repository và copy file

```bash
# Tạo thư mục cấu trúc
mkdir -p .github/workflows scripts

# Copy các file vào đúng vị trí
cp enhance_from_issue.yml .github/workflows/
cp enhance.py scripts/
cp login_helper.py scripts/
cp requirements.txt scripts/
```

### Bước 2: Tạo auth.json (một lần duy nhất)

`auth.json` chứa session cookies và local storage của Adobe Podcast, cho phép Playwright đăng nhập tự động trên CI.

```bash
# Cài Playwright trên máy local
pip install playwright
playwright install chromium

# Chạy script login helper
python scripts/login_helper.py
```

Script sẽ mở trình duyệt headed. Bạn đăng nhập vào Adobe Podcast, sau đó nhấn ENTER. File `auth.json` sẽ được lưu trong thư mục hiện tại.

> **Quan trọng**: Không commit `auth.json` lên repository.

### Bước 3: Lưu auth.json thành GitHub Secret

1. Mở repository trên GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Nhấn **New repository secret**
3. Tên secret: `AUTH_JSON`
4. Giá trị: toàn bộ nội dung JSON của file `auth.json`
5. Nhấn **Add secret**

### Bước 4: Push workflow

```bash
git add .github/workflows/enhance_from_issue.yml
git add scripts/enhance.py scripts/login_helper.py scripts/requirements.txt
git add README.md
git commit -m "Add Adobe Podcast enhance workflow"
git push
```

> **Nhớ thêm** `.gitignore`: thêm dòng `auth.json` để tránh commit nhầm.

---

## Cách sử dụng

### Trong issue comment

Comment bất kỳ issue nào với từ khóa `/enhance` kèm URL file âm thanh:

```
/enhance
https://example.com/recording.mp3
https://example.com/podcast.wav
```

Workflow sẽ:
1. Nhận diện comment có `/enhance`
2. Tải tất cả URL âm thanh từ comment
3. Upload từng file lên Adobe Podcast qua Playwright
4. Chờ xử lý (tối đa 5 phút/file)
5. Tải file đã enhance về
6. Upload kết quả thành artifact
7. Comment kết quả lên issue

### Kết quả

Workflow sẽ comment lại trên issue với bảng tổng kết:

| Metric | Count |
|--------|-------|
| Total files | 2 |
| Enhanced | 2 |
| Failed | 0 |

Kèm link tải artifact chứa các file `enhanced_<original_name>`.

---

## Định dạng file được hỗ trợ

| Extension | Loại |
|-----------|------|
| `.mp3` | Audio |
| `.wav` | Audio |
| `.m4a` | Audio |
| `.flac` | Audio |
| `.ogg` / `.oga` | Audio |
| `.aac` | Audio |
| `.mp4` | Video |
| `.m4v` | Video |
| `.mov` | Video |
| `.3gp` / `.3gpp` | Video |
| `.webm` | Video |

---

## Biến môi trường & Secrets

| Tên | Loại | Mô tả |
|-----|------|-------|
| `AUTH_JSON` | Repository Secret | Nội dung JSON của file auth.json (Playwright storage state) |

---

## Refresh auth.json

Session Adobe có thể hết hạn sau một thời gian. Khi workflow bắt đầu fail với lỗi xác thực, hãy:

1. Chạy lại `python scripts/login_helper.py` trên máy local
2. Đăng nhập lại Adobe Podcast
3. Copy nội dung `auth.json` mới
4. Cập nhật secret `AUTH_JSON` trên GitHub

---

## Cấu hình tùy chỉnh

### Thay đổi thời gian timeout

Trong `scripts/enhance.py`, sửa hằng số:

```python
MAX_WAIT_SECONDS = 300  # Tăng/giảm thời gian chờ tối đa (giây)
```

### Thêm định dạng file

Sửa set `SUPPORTED_EXTENSIONS` trong `scripts/enhance.py`:

```python
SUPPORTED_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".oga", ".aac",
    ".mp4", ".m4v", ".mov", ".3gp", ".webm", ".3gpp",
    ".aif", ".aiff",  # Thêm định dạng mới
}
```

---

## Troubleshooting

| Vấn đề | Nguyên nhân | Giải pháp |
|--------|-------------|-----------|
| `auth.json is NOT valid JSON` | Secret bị paste sai định dạng | Đảm bảo paste toàn bộ JSON, không thêm whitespace thừa |
| `Download button did not appear` | Adobe xử lý quá chậm hoặc quota hết | Tăng `MAX_WAIT_SECONDS` hoặc kiểm tra tài khoản Adobe |
| `No audio files found` | URL không trỏ đến file hợp lệ | Kiểm tra URL có đuôi file hoặc có thể truy cập công khai |
| `✗ Failed or empty download` | URL không public hoặc cần auth | Đảm bảo URL trỏ đến file công khai, không cần đăng nhập |
| Workflow không chạy | Comment không bắt đầu bằng `/enhance` | Đảm bảo `/enhance` là từ đầu tiên trong comment |

---

## License

MIT
