"""Batch-resize a directory of photos by a percentage scale factor."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp"}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resize all photos in a directory by a percentage.",
        epilog=(
            "examples:\n"
            "  python resize.py ./photos --scale 50\n"
            "  python resize.py ./photos --scale 50 --output-dir ./small\n"
            "  python resize.py ./photos --scale 50 --in-place\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input_dir", help="Directory containing photos to resize")
    parser.add_argument(
        "--scale",
        type=float,
        required=True,
        help="Resize scale as a percentage (e.g., 50 = half size). Must be > 0.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the original photos instead of writing to a directory.",
    )
    group.add_argument(
        "--output-dir",
        default=None,
        help="Directory to write resized photos to. Defaults to <input_dir>/resized.",
    )
    args = parser.parse_args(argv)

    if args.scale <= 0:
        parser.error("scale must be > 0 (e.g., --scale 50 for half size)")

    input_path = Path(args.input_dir)
    if not input_path.is_dir():
        parser.error(f"input directory not found: {args.input_dir}")

    return args


def compute_size(width: int, height: int, scale: float) -> tuple[int, int]:
    new_w = max(1, round(width * scale / 100))
    new_h = max(1, round(height * scale / 100))
    return new_w, new_h


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def iter_input_files(input_dir: Path, output_dir: Path | None) -> list[Path]:
    files: list[Path] = []
    output_resolved = output_dir.resolve() if output_dir else None
    for entry in sorted(input_dir.iterdir()):
        if entry.is_dir():
            # Exclude the output dir when nested inside the input dir
            # (e.g., the default <input>/resized) so we never re-process outputs.
            if output_resolved and (
                entry.resolve() == output_resolved or is_within(entry.resolve(), output_resolved)
            ):
                continue
            continue
        files.append(entry)
    return files


def resize_image(src: Path, dest: Path, scale: float, in_place: bool) -> None:
    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img)
        orig_format = img.format
        new_size = compute_size(img.width, img.height, scale)
        resized = img.resize(new_size, Image.LANCZOS)

        # JPEG (and BMP) have no alpha channel; flatten if needed.
        save_kwargs: dict = {}
        target_format = (orig_format or src.suffix.lstrip(".").upper()).upper()
        if target_format in ("JPG", "JPEG") and resized.mode in ("RGBA", "LA", "PA"):
            background = Image.new("RGB", resized.size, (255, 255, 255))
            background.paste(resized, mask=resized.split()[-1])
            resized = background
        elif target_format in ("JPG", "JPEG", "BMP") and resized.mode not in ("RGB", "L"):
            resized = resized.convert("RGB")

        if in_place:
            # Atomic overwrite: write temp file in same dir, then replace.
            suffix = src.suffix or ".tmp"
            fd, tmp_name = tempfile.mkstemp(suffix=suffix, dir=str(src.parent))
            os.close(fd)
            try:
                resized.save(tmp_name, format=orig_format or undefined_format(src))
                os.replace(tmp_name, dest)
            finally:
                if os.path.exists(tmp_name):
                    os.remove(tmp_name)
        else:
            resized.save(dest, format=orig_format or undefined_format(src))


def undefined_format(src: Path) -> str | None:
    ext = src.suffix.lower()
    mapping = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".png": "PNG",
        ".webp": "WEBP",
        ".tiff": "TIFF",
        ".tif": "TIFF",
        ".bmp": "BMP",
    }
    return mapping.get(ext)


def process_batch(input_dir: Path, scale: float, in_place: bool, output_dir: Path | None) -> int:
    if not in_place:
        assert output_dir is not None
        output_dir.mkdir(parents=True, exist_ok=True)

    files = iter_input_files(input_dir, None if in_place else output_dir)
    processed = skipped = failed = 0

    for src in files:
        if src.suffix.lower() not in SUPPORTED_EXTENSIONS:
            print(f"SKIP  {src.name} (unsupported file type)")
            skipped += 1
            continue
        dest = src if in_place else output_dir / src.name
        try:
            resize_image(src, dest, scale, in_place)
            print(f"OK    {src.name} -> {dest}")
            processed += 1
        except Exception as exc:  # per-file failure must not abort the batch
            print(f"FAIL  {src.name}: {exc}", file=sys.stderr)
            failed += 1

    location = "in place (originals overwritten)" if in_place else str(output_dir)
    print(f"\nDone: {processed} resized, {skipped} skipped, {failed} failed. Output: {location}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_dir = Path(args.input_dir).resolve()

    if args.in_place:
        print("WARNING: --in-place will overwrite your original photos. Consider a backup first.")
        return process_batch(input_dir, args.scale, True, None)

    output_dir = Path(args.output_dir).resolve() if args.output_dir else input_dir / "resized"
    return process_batch(input_dir, args.scale, False, output_dir)


if __name__ == "__main__":
    raise SystemExit(main())
