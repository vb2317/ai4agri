# Scripts

Operational scripts for local and remote AI4Agri runs.

Conventions:

- Every script should accept explicit paths such as `--data-dir`, `--out-dir`, or `--zip-path`.
- Long-running remote commands should write artifacts under `results/`.
- Important experiments should be logged in `results/runs.csv`.
- Smoke-test options should use `--limit` where applicable.

Current scripts:

- `inspect_subtask1.py`: inspect AgriPotential CSV metadata and optionally smoke-read Sentinel-2/label windows with `--limit`, `--read-pixels`, and `--read-labels`.
- `inspect_subtask2.py`: inspect extracted DACIA5 file layout, labels, years, and optional TIFF array shapes.
- `validate_submission_zip.py`: configurable ZIP sanity checker for candidate submissions. Use `--subtask1-codabench` for confirmed AgriPotential rules: root-level `<patch_id>.png` masks, optional `report.pdf`, and class ids `0..4`.
