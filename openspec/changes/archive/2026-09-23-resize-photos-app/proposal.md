## Why

Users with large photo directories need a simple way to batch-shrink images by a percentage (e.g., for web upload, storage savings, or sharing) without manually editing each file in an image editor.

## What Changes

- Add a Python CLI app that takes an input directory of photos and a resize percentage, and writes resized copies.
- Support common raster formats (JPEG, PNG, WebP at minimum; TIFF/BMP where Pillow supports them) with non-image files skipped.
- Provide two save modes:
  - `--in-place`: overwrite the original photos in the source directory.
  - `--output-dir <path>`: save resized photos to a separate directory (default: `<input-dir>/resized`, auto-created if missing).
- Preserve filenames, format, and (where possible) EXIF orientation handling so resized images look correct.

## Capabilities

### New Capabilities
- `photo-resize`: Batch-resize a directory of photos by a percentage scale factor, with in-place or separate-directory output modes, via a Python CLI.

### Modified Capabilities
- None (greenfield project, no existing specs).

## Impact

- New code: single Python app (e.g., `resize.py` or `photo_resizer/` package) plus `requirements.txt` / `pyproject.toml` dependency on Pillow, and a README with usage examples.
- No existing APIs, systems, or data to migrate; no breaking changes.
- System dependency: Python 3.9+ and Pillow (PIL) for image decoding/encoding and high-quality Lanczos resampling.
