## ADDED Requirements

### Requirement: CLI accepts input directory and scale percentage
The system SHALL provide a Python CLI that accepts an input photo directory (positional) and a required resize scale percentage.

#### Scenario: Valid invocation with scale
- **WHEN** user runs `python resize.py /path/to/photos --scale 50`
- **THEN** the system validates the directory exists and scale is a positive number, then processes the batch.

#### Scenario: Missing or invalid inputs rejected
- **WHEN** user provides a non-existent directory or a scale <= 0 (or non-numeric)
- **THEN** the system exits with a non-zero code and prints a clear error message (e.g., "input directory not found", "scale must be > 0").

#### Scenario: Help text available
- **WHEN** user runs `python resize.py --help`
- **THEN** the system displays usage, arguments (`input_dir`, `--scale`, `--in-place`, `--output-dir`), and examples.

### Requirement: Photos are resized by percentage preserving aspect ratio
The system SHALL scale each supported image so `new_width = max(1, round(orig_width * scale / 100))` and likewise for height, preserving aspect ratio with high-quality resampling.

#### Scenario: 50% resize halves dimensions
- **WHEN** a 2000x1000 JPEG is processed with `--scale 50`
- **THEN** the output image is 1000x500 pixels.

#### Scenario: Tiny scale clamps to minimum 1px
- **WHEN** scaling would compute a 0px dimension
- **THEN** the system clamps that dimension to 1px rather than failing.

#### Scenario: EXIF orientation honored
- **WHEN** a phone photo with EXIF orientation is processed
- **THEN** the resized output appears with the same visual orientation as the source.

### Requirement: In-place overwrite mode
The system SHALL support `--in-place` mode that overwrites the original photos with their resized versions.

#### Scenario: In-place overwrite
- **WHEN** user runs `python resize.py /photos --scale 50 --in-place`
- **THEN** each supported image in `/photos` is replaced by its resized version with the same filename and format, and no `resized/` directory is created.

#### Scenario: In-place and output-dir are mutually exclusive
- **WHEN** user passes both `--in-place` and `--output-dir`
- **THEN** the system rejects the invocation with a clear error and non-zero exit code.

### Requirement: Directory output mode with default resized folder
The system SHALL support writing resized photos to a separate directory; when `--output-dir` is omitted and `--in-place` is not set, the system SHALL default to `<input-dir>/resized`, creating it if needed.

#### Scenario: Default output directory
- **WHEN** user runs `python resize.py /photos --scale 50` with no output flags
- **THEN** resized images are written to `/photos/resized/` with original filenames, and originals in `/photos` are unchanged.

#### Scenario: Explicit output directory
- **WHEN** user runs `python resize.py /photos --scale 50 --output-dir /tmp/out`
- **THEN** resized images are written to `/tmp/out/` (created if missing) with original filenames.

#### Scenario: Output dir inside input dir is not re-processed
- **WHEN** the output directory is inside the input directory (e.g., default `resized/`)
- **THEN** the system excludes already-generated outputs from the scan set.

### Requirement: Format handling and non-image skipping
The system SHALL process common raster formats (JPEG, PNG, WebP, TIFF, BMP via Pillow), preserve each file's format and filename, and skip non-image files without failing the batch.

#### Scenario: Mixed directory with non-images
- **WHEN** the input directory contains `a.jpg`, `b.png`, and `notes.txt`
- **THEN** `a.jpg` and `b.png` are resized and `notes.txt` is reported as skipped while the batch succeeds.

#### Scenario: Unsupported/corrupt image reported but batch continues
- **WHEN** one file fails to decode or save (corrupt, unsupported mode)
- **THEN** the system logs the failure, continues with remaining files, and reports the failure count in the final summary.

### Requirement: Batch summary and exit behavior
The system SHALL print a per-run summary (processed, skipped, failed counts) and exit non-zero only on fatal errors (bad args, missing input dir) — per-file failures SHALL NOT abort the batch.

#### Scenario: Successful batch summary
- **WHEN** a batch completes with 10 resized, 2 skipped, 1 failed
- **THEN** stdout/stderr shows those counts and the output locations.
