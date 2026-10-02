# Photo Resizer

Batch-resize every photo in a directory by a percentage — e.g. shrink a 4000px-wide
camera dump to 50% for web upload — while keeping filenames, formats, and aspect ratio.

- **Safe by default:** writes resized copies to `<input-dir>/resized/`, originals untouched.
- **Optional in-place mode:** `--in-place` overwrites the originals (back up first!).
- **Skips non-images** (`notes.txt`, etc.) and keeps going if one file is corrupt.

## Requirements

- Python 3.9+
- Pillow (installed via `requirements.txt`)

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python resize.py <input_dir> --scale <percent> [--in-place | --output-dir <path>]
```

| Argument       | Required | Description |
|----------------|----------|-------------|
| `input_dir`    | Yes      | Directory of photos (top-level files only, no recursion). |
| `--scale`      | Yes      | Resize percentage, must be `> 0`. `50` = half width/height. Values over 100 upscale. |
| `--in-place`   | No       | Overwrite originals. Cannot be combined with `--output-dir`. |
| `--output-dir` | No       | Where to write resized copies. Defaults to `<input_dir>/resized` (auto-created). |

New dimensions are `max(1, round(orig * scale / 100))` per side, so aspect ratio is
preserved and tiny images never collapse to 0px. EXIF orientation is honored, so
phone photos come out the right way up.

Supported formats: JPEG (`.jpg`, `.jpeg`), PNG, WebP, TIFF (`.tiff`, `.tif`), BMP.
Anything else is reported as `SKIP` and does not stop the batch.

## Common examples

```bash
# 1. Halve a folder of photos, keep originals (writes to ./photos/resized/)
python resize.py ./photos --scale 50

# 2. Shrink to 25% for email / web upload into a separate folder
python resize.py ./photos --scale 25 --output-dir ./photos-small

# 3. Make thumbnails at 10%
python resize.py ./photos --scale 10 --output-dir ./thumbs

# 4. Slightly reduce large images to save disk space (80% of original)
python resize.py ./photos --scale 80

# 5. Upscale small images 2x (e.g. for printing)
python resize.py ./icons --scale 200 --output-dir ./icons-2x

# 6. Overwrite originals in place — BACK UP FIRST, this cannot be undone
cp -r ./photos ./photos-backup
python resize.py ./photos --scale 50 --in-place

# 7. Show full help
python resize.py --help
```

## What the output looks like

```text
OK    a.jpg -> /path/to/photos/resized/a.jpg
OK    b.png -> /path/to/photos/resized/b.png
SKIP  notes.txt (unsupported file type)

Done: 2 resized, 1 skipped, 1 failed. Output: /path/to/photos/resized
```

- `OK` — file resized successfully.
- `SKIP` — not a supported image, ignored.
- `FAIL` — corrupt/unsupported file (printed to stderr); the rest of the batch still completes.
- Exit code is `0` on success, non-zero for fatal errors (missing directory, bad `--scale`,
  or passing `--in-place` together with `--output-dir`).

## Tips & troubleshooting

- **"input directory not found"** — check the path exists and is a directory.
- **"scale must be > 0"** — `--scale` needs a positive number (`50`, not `50%` or `-10`).
- **Only top-level files are processed** — subdirectories are ignored in v1.
- **Output folder inside the input is excluded** from scanning, so re-running the
  command won't re-resize its own output.
- **JPEG transparency:** RGBA images saved as JPEG get flattened onto white, since
  JPEG has no alpha channel.
