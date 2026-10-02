## Context

Greenfield project in an empty repo (`/Users/emile.bassil/ai/unsw/resize-image`). No existing code, specs, or architecture. Stakeholder wants a minimal Python CLI that batch-resizes a directory of photos by a percentage, with two save modes: overwrite in place, or write to a separate directory defaulting to `<input>/resized`.

Constraints: must run locally with standard Python + Pillow, no cloud services, no GUI. Must be safe by default (no silent data loss).

## Goals / Non-Goals

**Goals:**
- Single-command batch resize: `python resize.py <input-dir> --scale 50 [--in-place | --output-dir <path>]`.
- Correct scaling math: `new_w = max(1, round(orig_w * scale/100))`, same for height, aspect ratio preserved.
- Safe defaults: default output is `<input>/resized` (auto-created); in-place mode requires explicit `--in-place` flag plus confirmation handling.
- Clear per-file success/skip/failure summary and non-zero exit on fatal errors.

**Non-Goals:**
- No recursive subdirectory traversal in v1 (top-level directory only, or opt-in flag later).
- No GUI, no image editing beyond resize (no crop, rotate, watermark, quality slider in v1 beyond format-preserving save).
- No parallel/distributed processing; simple sequential loop is sufficient.
- No cloud storage or database integration.

## Decisions

**1. Pillow (PIL) for imaging — over OpenCV / ImageMagick CLI.**
- Rationale: Pillow is the de-facto Python imaging lib, pure-pip install, supports JPEG/PNG/WebP/TIFF/BMP, provides `ImageOps.exif_transpose` and high-quality `Image.LANCZOS` resampling.
- Alternative considered: OpenCV — heavier native dep, overkill; Wand/ImageMagick — requires system binary.

**2. argparse CLI with `input_dir` (positional), `--scale` (required), `--in-place` vs `--output-dir` (mutually exclusive) — over config file or interactive prompts.**
- Rationale: scriptable, testable, matches user request for "two options". `--scale` as float percentage (e.g., `50` = 50%). Validate `0 < scale <= 100`? Actually allow >100 for upscale but cap sensibly (e.g., 1–500) — decide: allow 1–500, reject ≤0.
- If neither `--in-place` nor `--output-dir` given → default to `<input_dir>/resized`.
- If `--output-dir` is a relative name, resolve relative to CWD; if omitted, create `<input_dir>/resized` with `mkdir(parents=True, exist_ok=True)`.

**3. Preserve filename + format; skip non-images — over converting everything to JPEG.**
- Rationale: least surprise; `input.jpg` → `output.jpg` same format. Detect images by trying `Image.open` + extension allowlist (`.jpg .jpeg .png .webp .tiff .tif .bmp`). Non-image files logged as skipped, not fatal.
- EXIF: apply `ImageOps.exif_transpose` before resize so phone photos orient correctly.

**4. Overwrite safety in `--in-place` mode.**
- Write to temp file then atomic `os.replace` to avoid corrupting originals on crash mid-write. Log warning that originals are overwritten. Never write `resized` output back into scan set (exclude output dir if it lives inside input dir to avoid re-processing).

**5. Single-file script (`resize.py`) + `requirements.txt` — over packaged module.**
- Rationale: v1 simplicity; single file is easy to run and review. Promote to package only if features grow.

## Risks / Trade-offs

- [Risk] In-place overwrite destroys originals → Mitigation: require explicit `--in-place` flag, print warning, use temp-file + atomic replace, recommend backup in README; default mode is non-destructive `resized/`.
- [Risk] Large images exhaust memory → Mitigation: sequential processing, close handles per file (`with Image.open`), document limitation; no full-directory preload.
- [Risk] Format-specific save failures (e.g., RGBA → JPEG) → Mitigation: convert mode as needed (`RGBA` → `RGB` for JPEG), catch per-file exceptions, continue batch, report failures in summary.
- [Risk] Rounding to 0px on tiny images with small scale → Mitigation: clamp dimensions to minimum 1px.
- [Trade-off] Sequential loop is slower than multiprocessing → Accept for v1; batch sizes for personal photo dirs (hundreds of files) are fine.
