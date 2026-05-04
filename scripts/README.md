# Scripts

Operational scripts for local and remote AI4Agri runs.

Conventions:

- Every script should accept explicit paths such as `--data-dir`, `--out-dir`, or `--zip-path`.
- Long-running remote commands should write artifacts under `results/`.
- Important experiments should be logged in `results/runs.csv`.
- Smoke-test options should use `--limit` where applicable.

Current scripts:

- `validate_submission_zip.py`: configurable ZIP sanity checker for candidate submissions.
