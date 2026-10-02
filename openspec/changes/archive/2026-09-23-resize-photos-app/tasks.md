## 1. Project Setup

- [x] 1.1 Create `resize.py` scaffold with argparse CLI (`input_dir`, `--scale`, `--in-place`, `--output-dir` mutually exclusive) and `--help` examples
- [x] 1.2 Add `requirements.txt` with Pillow dependency and verify `pip install -r requirements.txt` works

## 2. Core Resize Implementation

- [x] 2.1 Implement image discovery (extension allowlist + `Image.open` check, top-level only, exclude output dir when nested)
- [x] 2.2 Implement resize logic (`max(1, round(dim * scale/100))`, `LANCZOS`, `ImageOps.exif_transpose`, mode conversion for JPEG save)
- [x] 2.3 Implement output handling: default `<input>/resized` creation, explicit `--output-dir` creation, and `--in-place` atomic overwrite via temp file + `os.replace`
- [x] 2.4 Implement per-file error handling (skip non-images, catch corrupt/save failures, continue batch) plus final summary counts and exit codes

## 3. Verification & Docs

- [x] 3.1 Manually verify all spec scenarios: 50% resize dims, 1px clamp, default `resized/` output, explicit output dir, in-place overwrite, mixed dir skip, mutual-exclusion error, invalid scale/dir errors
- [x] 3.2 Add README with install, usage examples (default, explicit dir, in-place), and backup warning for in-place mode
