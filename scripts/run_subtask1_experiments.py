#!/usr/bin/env python3
"""Run a sequence of Subtask 1 baseline experiments and rank the results."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Experiment:
    run_id: str
    model: str
    sampling: str
    feature_mode: str
    pixels_per_patch: int
    max_train_pixels: int
    random_state: int
    patch_limit: int = 0
    val_patch_limit: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, type=Path, help="RunPod AgriPotential data directory.")
    parser.add_argument("--out-dir", type=Path, default=Path("results/subtask1/experiments"))
    parser.add_argument("--suite", choices=["smoke", "quick", "overnight"], default="overnight")
    parser.add_argument("--label-name", default="viticulture", choices=["viticulture", "market", "field"])
    parser.add_argument("--train-split", default="train.csv")
    parser.add_argument("--val-split", default="val.csv")
    parser.add_argument("--infer-best", action="store_true", help="Run inference for the best validation run.")
    parser.add_argument("--validate-best", action="store_true", help="Validate the inferred best ZIP.")
    parser.add_argument("--force", action="store_true", help="Rerun experiments even if metrics already exist.")
    return parser.parse_args()


def experiment_suite(name: str) -> list[Experiment]:
    if name == "smoke":
        return [
            Experiment("smoke_hgb_cb_temporal", "hist_gradient_boosting", "class_balanced", "raw_temporal", 256, 5000, 42, 20, 5),
            Experiment("smoke_hgb_uniform_temporal", "hist_gradient_boosting", "uniform", "raw_temporal", 256, 5000, 43, 20, 5),
        ]
    if name == "quick":
        return [
            Experiment("hgb_cb_temporal_100k_s42", "hist_gradient_boosting", "class_balanced", "raw_temporal", 512, 100000, 42),
            Experiment("hgb_uniform_temporal_100k_s43", "hist_gradient_boosting", "uniform", "raw_temporal", 512, 100000, 43),
            Experiment("hgb_cb_raw_100k_s44", "hist_gradient_boosting", "class_balanced", "raw", 512, 100000, 44),
            Experiment("extra_cb_temporal_100k_s45", "extra_trees", "class_balanced", "raw_temporal", 512, 100000, 45),
        ]
    return [
        Experiment("hgb_cb_temporal_200k_s42", "hist_gradient_boosting", "class_balanced", "raw_temporal", 512, 200000, 42),
        Experiment("hgb_uniform_temporal_200k_s43", "hist_gradient_boosting", "uniform", "raw_temporal", 512, 200000, 43),
        Experiment("hgb_cb_raw_200k_s44", "hist_gradient_boosting", "class_balanced", "raw", 512, 200000, 44),
        Experiment("hgb_cb_temporal_400k_s45", "hist_gradient_boosting", "class_balanced", "raw_temporal", 768, 400000, 45),
        Experiment("extra_cb_temporal_150k_s46", "extra_trees", "class_balanced", "raw_temporal", 512, 150000, 46),
        Experiment("extra_uniform_temporal_150k_s47", "extra_trees", "uniform", "raw_temporal", 512, 150000, 47),
    ]


def run_command(command: list[str], log_path: Path) -> tuple[int, float]:
    started = time.monotonic()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w") as log:
        log.write("$ " + " ".join(command) + "\n\n")
        log.flush()
        process = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, text=True, check=False)
    return process.returncode, time.monotonic() - started


def read_metrics(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def score_key(result: dict) -> tuple[float, float, float]:
    metrics = result.get("metrics") or {}
    return (
        float(metrics.get("accuracy_pm1", -1.0)),
        float(metrics.get("exact_accuracy", -1.0)),
        -float(metrics.get("mean_absolute_error", 999.0)),
    )


def train_experiment(args: argparse.Namespace, root: Path, experiment: Experiment) -> dict:
    run_dir = root / experiment.run_id
    metrics_path = run_dir / "metrics.json"
    if metrics_path.exists() and not args.force:
        return {
            "run_id": experiment.run_id,
            "status": "skipped_existing",
            "run_dir": str(run_dir),
            "config": asdict(experiment),
            "metrics": read_metrics(metrics_path),
        }

    command = [
        sys.executable,
        "scripts/subtask1_baseline.py",
        "train",
        "--data-dir",
        str(args.data_dir),
        "--out-dir",
        str(run_dir),
        "--label-name",
        args.label_name,
        "--train-split",
        args.train_split,
        "--val-split",
        args.val_split,
        "--pixels-per-patch",
        str(experiment.pixels_per_patch),
        "--max-train-pixels",
        str(experiment.max_train_pixels),
        "--random-state",
        str(experiment.random_state),
        "--model",
        experiment.model,
        "--sampling",
        experiment.sampling,
        "--feature-mode",
        experiment.feature_mode,
    ]
    if experiment.patch_limit:
        command.extend(["--patch-limit", str(experiment.patch_limit)])
    if experiment.val_patch_limit:
        command.extend(["--val-patch-limit", str(experiment.val_patch_limit)])

    returncode, elapsed_seconds = run_command(command, run_dir / "train.log")
    status = "ok" if returncode == 0 and metrics_path.exists() else "failed"
    return {
        "run_id": experiment.run_id,
        "status": status,
        "returncode": returncode,
        "elapsed_seconds": round(elapsed_seconds, 3),
        "run_dir": str(run_dir),
        "config": asdict(experiment),
        "metrics": read_metrics(metrics_path),
    }


def write_summary(root: Path, results: list[dict]) -> None:
    ranked = sorted(results, key=score_key, reverse=True)
    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ranking_metric": ["accuracy_pm1", "exact_accuracy", "negative_mean_absolute_error"],
        "best_run": ranked[0] if ranked else None,
        "results": ranked,
    }
    (root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    fields = [
        "rank",
        "run_id",
        "status",
        "model",
        "sampling",
        "feature_mode",
        "pixels_per_patch",
        "max_train_pixels",
        "random_state",
        "accuracy_pm1",
        "exact_accuracy",
        "mean_absolute_error",
        "train_pixels",
        "val_pixels",
        "feature_count",
        "run_dir",
    ]
    with (root / "summary.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for rank, result in enumerate(ranked, start=1):
            config = result.get("config") or {}
            metrics = result.get("metrics") or {}
            writer.writerow(
                {
                    "rank": rank,
                    "run_id": result.get("run_id"),
                    "status": result.get("status"),
                    "model": config.get("model"),
                    "sampling": config.get("sampling"),
                    "feature_mode": config.get("feature_mode"),
                    "pixels_per_patch": config.get("pixels_per_patch"),
                    "max_train_pixels": config.get("max_train_pixels"),
                    "random_state": config.get("random_state"),
                    "accuracy_pm1": metrics.get("accuracy_pm1"),
                    "exact_accuracy": metrics.get("exact_accuracy"),
                    "mean_absolute_error": metrics.get("mean_absolute_error"),
                    "train_pixels": metrics.get("train_pixels"),
                    "val_pixels": metrics.get("val_pixels"),
                    "feature_count": metrics.get("feature_count"),
                    "run_dir": result.get("run_dir"),
                }
            )


def infer_and_validate_best(args: argparse.Namespace, root: Path, results: list[dict]) -> None:
    completed = [result for result in results if result.get("status") in {"ok", "skipped_existing"}]
    if not completed:
        print("No completed experiment available for inference.")
        return
    best = sorted(completed, key=score_key, reverse=True)[0]
    run_id = best["run_id"]
    run_dir = Path(best["run_dir"])
    zip_path = Path("results/subtask1/submissions") / f"{root.parent.name}_{root.name}_{run_id}.zip"
    infer_command = [
        sys.executable,
        "scripts/subtask1_baseline.py",
        "infer",
        "--data-dir",
        str(args.data_dir),
        "--model-path",
        str(run_dir / "model.pkl"),
        "--out",
        str(zip_path),
    ]
    returncode, elapsed_seconds = run_command(infer_command, root / f"{run_id}_infer.log")
    infer_result = {
        "run_id": run_id,
        "zip_path": str(zip_path),
        "returncode": returncode,
        "elapsed_seconds": round(elapsed_seconds, 3),
    }

    if args.validate_best and returncode == 0:
        validate_command = [
            sys.executable,
            "scripts/validate_submission_zip.py",
            "--zip-path",
            str(zip_path),
            "--subtask1-codabench",
            "--expected-ids-file",
            str(args.data_dir / "test.csv"),
            "--check-class-values",
        ]
        validate_returncode, validate_elapsed = run_command(validate_command, root / f"{run_id}_validate.log")
        infer_result["validate_returncode"] = validate_returncode
        infer_result["validate_elapsed_seconds"] = round(validate_elapsed, 3)

    (root / "best_inference.json").write_text(json.dumps(infer_result, indent=2) + "\n")


def main() -> None:
    args = parse_args()
    root = args.out_dir / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") / args.suite
    root.mkdir(parents=True, exist_ok=True)

    experiments = experiment_suite(args.suite)
    (root / "suite.json").write_text(json.dumps([asdict(item) for item in experiments], indent=2) + "\n")

    results = []
    for index, experiment in enumerate(experiments, start=1):
        print(f"[{index}/{len(experiments)}] {experiment.run_id}")
        result = train_experiment(args, root, experiment)
        results.append(result)
        write_summary(root, results)
        status = result.get("status")
        metrics = result.get("metrics") or {}
        print(
            f"  {status}: pm1={metrics.get('accuracy_pm1')} "
            f"exact={metrics.get('exact_accuracy')} mae={metrics.get('mean_absolute_error')}"
        )

    if args.infer_best:
        infer_and_validate_best(args, root, results)

    print(f"Wrote {root / 'summary.csv'}")
    print(f"Wrote {root / 'summary.json'}")


if __name__ == "__main__":
    main()
