#!/usr/bin/env python3
"""Create a source/report bundle for AI4Agri Subtask 2 submission review."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


DEFAULT_INCLUDE_PATHS = [
    "submissions/subtask2/README.md",
    "reports/subtask2_technical_report.md",
    "notebooks/subtask2_submission.ipynb",
    "notebooks/subtask2_submission.py",
    "notebooks/subtask2_testbed.ipynb",
    "notebooks/subtask2_testbed.py",
    "scripts/download_subtask2_zenodo.py",
    "scripts/extract_subtask2_zip.sh",
    "scripts/inspect_subtask2.py",
    "scripts/inspect_subtask2_labels.py",
    "scripts/subtask2_baseline.py",
    "scripts/summarize_subtask2_features.py",
    "results/subtask2/inspection/subtask2_inspection.json",
    "results/subtask2/inspection/subtask2_label_inspection.json",
    "results/subtask2/inspection/subtask2_feature_summary.json",
    "results/subtask2/inspection/subtask2_baseline_summary.json",
    "requirements.txt",
    "README.md",
    "ARCHITECTURE.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, default=Path("results/subtask2/submissions/subtask2_source_bundle.zip"))
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Additional file or directory to include, relative to --repo-root. May be repeated.",
    )
    return parser.parse_args()


def iter_files(root: Path, relative: Path):
    path = root / relative
    if not path.exists():
        return
    if path.is_file():
        yield path
        return
    for child in sorted(path.rglob("*")):
        if child.is_file():
            yield child


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    out_path = args.out if args.out.is_absolute() else repo_root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    include_paths = [Path(path) for path in DEFAULT_INCLUDE_PATHS]
    include_paths.extend(Path(path) for path in args.include)

    written: set[str] = set()
    missing: list[str] = []
    with ZipFile(out_path, "w", compression=ZIP_DEFLATED) as archive:
        for relative in include_paths:
            source = repo_root / relative
            if not source.exists():
                missing.append(str(relative))
                continue
            for file_path in iter_files(repo_root, relative):
                archive_name = file_path.relative_to(repo_root).as_posix()
                if archive_name in written:
                    continue
                archive.write(file_path, archive_name)
                written.add(archive_name)

    print(f"Wrote {out_path} with {len(written)} file(s).")
    if missing:
        print("Missing optional paths:")
        for path in missing:
            print(f"  {path}")


if __name__ == "__main__":
    main()
