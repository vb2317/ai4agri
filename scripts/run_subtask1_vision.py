#!/usr/bin/env python3
"""Train, review, and infer Subtask 1 vision segmentation models."""

from __future__ import annotations

import argparse
import json
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from tqdm import tqdm

from ai4agri.subtask1.data import AgriPotentialVisionDataset, collate_patches
from ai4agri.subtask1.metrics import (
    decode_logits,
    median_smooth,
    pm1_multihot_binary_cross_entropy,
    segmentation_metrics,
    soft_ordinal_cross_entropy,
)
from ai4agri.subtask1.models import build_model
from ai4agri.subtask1.png import grayscale_png


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    train = subparsers.add_parser("train", help="Train a vision model and export notebook-ready artifacts.")
    add_common_model_args(train)
    train.add_argument("--epochs", type=int, default=30)
    train.add_argument("--batch-size", type=int, default=8)
    train.add_argument("--lr", type=float, default=1e-3)
    train.add_argument("--weight-decay", type=float, default=1e-4)
    train.add_argument("--num-workers", type=int, default=2)
    train.add_argument("--patch-limit", type=int, default=0)
    train.add_argument("--val-patch-limit", type=int, default=0)
    train.add_argument("--visual-limit", type=int, default=20)
    train.add_argument("--loss", choices=["soft_ce", "ce", "pm1_bce"], default="soft_ce")
    train.add_argument("--class-weights", default="", help="Optional comma-separated CE weights for classes 0..4.")
    train.add_argument("--patience", type=int, default=8)
    train.add_argument("--write-test-visuals", action="store_true")
    train.add_argument("--test-visual-limit", type=int, default=20)
    train.add_argument("--cache-dir", type=Path, default=None, help="Optional feature cache directory for decoded patch tensors.")
    train.add_argument("--precache", action="store_true", help="Build the feature cache before training starts.")

    infer = subparsers.add_parser("infer", help="Infer masks from a saved checkpoint and write a CodaBench ZIP.")
    add_common_model_args(infer)
    infer.add_argument("--checkpoint", required=True, type=Path)
    infer.add_argument("--split", default="test", choices=["train", "val", "test"])
    infer.add_argument("--limit", type=int, default=0)
    infer.add_argument("--out", type=Path, default=None)
    infer.add_argument("--num-workers", type=int, default=2)
    infer.add_argument("--visual-limit", type=int, default=20)
    infer.add_argument(
        "--submission-label-offset",
        type=int,
        default=1,
        help="Value added to model classes before writing PNG masks. Use 1 for raw AgriPotential labels 1..5.",
    )
    infer.set_defaults(decode=None, median_size=None)

    smoke = subparsers.add_parser("self-test", help="Run a synthetic forward/metric smoke check without data files.")
    smoke.add_argument("--model", choices=["unet", "resnet_fpn", "tiny_vit"], default="unet")
    smoke.add_argument("--channels", type=int, default=40)

    return parser.parse_args()


def add_common_model_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--model", choices=["unet", "resnet_fpn", "tiny_vit"], default="unet")
    parser.add_argument("--temporal-mode", choices=["summary", "seasonal", "concat"], default="summary")
    parser.add_argument("--label-name", choices=["viticulture", "market", "field"], default="viticulture")
    parser.add_argument("--out-root", type=Path, default=Path("results/subtask1"))
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--decode", choices=["argmax", "expected", "neighbor_sum", "neighbor_sum_sigmoid"], default="argmax")
    parser.add_argument("--median-size", type=int, choices=[1, 3, 5], default=1)
    parser.add_argument("--base-channels", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)


def make_run_id(args: argparse.Namespace) -> str:
    if args.run_id:
        return args.run_id
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}_{args.model}_{args.temporal_mode}"


def run_paths(out_root: Path, run_id: str) -> dict[str, Path]:
    return {
        "run_dir": out_root / "vision_runs" / run_id,
        "visual_dir": out_root / "visuals" / run_id,
        "val_pred_dir": out_root / "val_preds",
        "submission_dir": out_root / "submissions",
    }


def make_loader(dataset: AgriPotentialVisionDataset, batch_size: int, workers: int, shuffle: bool) -> DataLoader:
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=workers,
        pin_memory=torch.cuda.is_available(),
        persistent_workers=workers > 0,
        prefetch_factor=4 if workers > 0 else None,
        collate_fn=collate_patches,
    )


def warm_feature_cache(dataset: AgriPotentialVisionDataset, batch_size: int, workers: int, name: str) -> None:
    if dataset.cache_dir is None:
        return
    loader = make_loader(dataset, batch_size, workers, shuffle=False)
    for _ in tqdm(loader, desc=f"cache:{name}", leave=False):
        pass


def parse_class_weights(value: str, device: str) -> torch.Tensor | None:
    if not value:
        return None
    weights = [float(item.strip()) for item in value.split(",") if item.strip()]
    if len(weights) != 5:
        raise ValueError("--class-weights must contain exactly 5 comma-separated values")
    return torch.tensor(weights, dtype=torch.float32, device=device)


def compute_loss(logits: torch.Tensor, target: torch.Tensor, loss_name: str, class_weights: torch.Tensor | None) -> torch.Tensor:
    if loss_name == "soft_ce":
        return soft_ordinal_cross_entropy(logits, target)
    if loss_name == "pm1_bce":
        return pm1_multihot_binary_cross_entropy(logits, target)
    return F.cross_entropy(logits, target.clamp(0, 4), weight=class_weights, ignore_index=255)


def train_one_epoch(model, loader, optimizer, device: str, loss_name: str) -> float:
    model.train()
    class_weights = getattr(model, "_class_weights", None)
    total_loss = 0.0
    batches = 0
    for batch in tqdm(loader, desc="train", leave=False):
        x = batch["x"].to(device, non_blocking=True)
        y = batch["y"].to(device, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        logits = model(x)
        loss = compute_loss(logits, y, loss_name, class_weights)
        loss.backward()
        optimizer.step()
        total_loss += float(loss.detach().cpu())
        batches += 1
    return total_loss / max(batches, 1)


@torch.no_grad()
def evaluate(model, loader, device: str, decode: str, median_size: int) -> tuple[dict[str, object], dict[str, np.ndarray]]:
    model.eval()
    true_blocks = []
    pred_blocks = []
    prob_blocks = []
    patch_ids = []
    for batch in tqdm(loader, desc="val", leave=False):
        x = batch["x"].to(device, non_blocking=True)
        logits = model(x)
        probs_tensor = torch.sigmoid(logits) if decode == "neighbor_sum_sigmoid" else torch.softmax(logits, dim=1)
        probs = probs_tensor.cpu().numpy().astype("float16")
        pred = decode_logits(logits, mode=decode).cpu().numpy().astype("uint8")
        if median_size > 1:
            pred = np.stack([median_smooth(item, median_size) for item in pred], axis=0)
        true_blocks.append(batch["y"].numpy().astype("uint8"))
        pred_blocks.append(pred)
        prob_blocks.append(probs)
        patch_ids.extend(batch["patch_id"])
    y_true = np.concatenate(true_blocks, axis=0)
    y_pred = np.concatenate(pred_blocks, axis=0)
    metrics = segmentation_metrics(y_true, y_pred)
    payload = {
        "patch_ids": np.array(patch_ids),
        "probs": np.concatenate(prob_blocks, axis=0),
        "y_true": y_true,
        "y_pred": y_pred,
    }
    return metrics, payload


def export_visuals(
    dataset: AgriPotentialVisionDataset,
    pred_payload: dict[str, np.ndarray] | None,
    visual_dir: Path,
    prefix: str,
    limit: int,
) -> None:
    from ai4agri.subtask1.visualize import save_sample_panel

    count = min(limit, len(dataset))
    for index in range(count):
        item = dataset[index]
        x = item["x"].numpy()
        y_true = item["y"].numpy() if "y" in item else None
        y_pred = None
        if pred_payload is not None:
            y_pred = pred_payload["y_pred"][index]
        save_sample_panel(
            visual_dir / f"{prefix}_{index:03d}_{item['patch_id']}.png",
            x,
            y_true=y_true,
            y_pred=y_pred,
            title=str(item["patch_id"]),
        )


def save_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def jsonable_args(args: argparse.Namespace) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in vars(args).items():
        payload[key] = str(value) if isinstance(value, Path) else value
    return payload


def train_command(args: argparse.Namespace) -> None:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    run_id = make_run_id(args)
    paths = run_paths(args.out_root, run_id)
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)

    train_ds = AgriPotentialVisionDataset(
        args.data_dir,
        "train",
        args.temporal_mode,
        label_name=args.label_name,
        patch_limit=args.patch_limit,
        augment=True,
        random_state=args.seed,
        shuffle_rows=bool(args.patch_limit),
        cache_dir=args.cache_dir,
    )
    val_ds = AgriPotentialVisionDataset(
        args.data_dir,
        "val",
        args.temporal_mode,
        label_name=args.label_name,
        patch_limit=args.val_patch_limit,
        augment=False,
        random_state=args.seed + 1,
        shuffle_rows=bool(args.val_patch_limit),
        cache_dir=args.cache_dir,
    )
    if args.precache:
        warm_train_ds = AgriPotentialVisionDataset(
            args.data_dir,
            "train",
            args.temporal_mode,
            label_name=args.label_name,
            patch_limit=args.patch_limit,
            augment=False,
            random_state=args.seed,
            shuffle_rows=bool(args.patch_limit),
            cache_dir=args.cache_dir,
        )
        warm_feature_cache(warm_train_ds, args.batch_size, args.num_workers, "train")
        warm_feature_cache(val_ds, args.batch_size, args.num_workers, "val")
    train_loader = make_loader(train_ds, args.batch_size, args.num_workers, shuffle=True)
    val_loader = make_loader(val_ds, args.batch_size, args.num_workers, shuffle=False)

    model = build_model(args.model, train_ds.input_channels, base_channels=args.base_channels).to(args.device)
    model._class_weights = parse_class_weights(args.class_weights, args.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    best_score = -1.0
    stale_epochs = 0
    history = []
    started = time.monotonic()

    config = jsonable_args(args)
    config.update({"run_id": run_id, "input_channels": train_ds.input_channels})
    save_json(paths["run_dir"] / "config.json", config)
    train_log = paths["run_dir"] / "train.log"
    train_log.write_text("$ " + " ".join(sys.argv) + "\n\n")
    export_visuals(train_ds, None, paths["visual_dir"], "train_sample", min(args.visual_limit, 8))

    for epoch in range(1, args.epochs + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, args.device, args.loss)
        val_metrics, val_payload = evaluate(model, val_loader, args.device, args.decode, args.median_size)
        epoch_record = {"epoch": epoch, "train_loss": train_loss, **val_metrics}
        history.append(epoch_record)
        save_json(paths["run_dir"] / "metrics_history.json", {"history": history})
        epoch_line = json.dumps(epoch_record, sort_keys=True)
        print(epoch_line)
        with train_log.open("a") as log:
            log.write(epoch_line + "\n")

        score = float(val_metrics["accuracy_pm1"])
        if score > best_score:
            best_score = score
            stale_epochs = 0
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "model": args.model,
                    "temporal_mode": args.temporal_mode,
                    "input_channels": train_ds.input_channels,
                    "base_channels": args.base_channels,
                    "decode": args.decode,
                    "median_size": args.median_size,
                    "config": config,
                },
                paths["run_dir"] / "best.pt",
            )
            np.savez_compressed(paths["val_pred_dir"] / f"{run_id}_val_probs.npz", **val_payload)
            export_visuals(val_ds, val_payload, paths["visual_dir"], "val_pred", args.visual_limit)
            save_json(
                paths["run_dir"] / "metrics.json",
                {
                    "run_id": run_id,
                    "best_epoch": epoch,
                    "elapsed_seconds": round(time.monotonic() - started, 3),
                    **val_metrics,
                },
            )
        else:
            stale_epochs += 1
            if stale_epochs >= args.patience:
                print(f"early stopping after {epoch} epochs")
                break

    if args.write_test_visuals:
        infer_visuals(args, paths["run_dir"] / "best.pt", run_id, limit=args.test_visual_limit)

    print(f"Wrote run artifacts under {paths['run_dir']}")
    print(f"Wrote visual review panels under {paths['visual_dir']}")


@torch.no_grad()
def predict_dataset(model, loader, device: str, decode: str, median_size: int):
    model.eval()
    for batch in tqdm(loader, desc="infer"):
        x = batch["x"].to(device, non_blocking=True)
        logits = model(x)
        pred = decode_logits(logits, mode=decode).cpu().numpy().astype("uint8")
        if median_size > 1:
            pred = np.stack([median_smooth(item, median_size) for item in pred], axis=0)
        for patch_id, mask in zip(batch["patch_id"], pred):
            yield patch_id, mask


def load_checkpoint_model(args: argparse.Namespace, checkpoint_path: Path):
    checkpoint = torch.load(checkpoint_path, map_location=args.device)
    input_channels = int(checkpoint.get("input_channels") or AgriPotentialVisionDataset(args.data_dir, args.split, args.temporal_mode).input_channels)
    model_name = checkpoint.get("model", args.model)
    base_channels = int(checkpoint.get("base_channels", args.base_channels))
    model = build_model(model_name, input_channels, base_channels=base_channels).to(args.device)
    model.load_state_dict(checkpoint["model_state"])
    decode = args.decode if args.decode is not None else checkpoint.get("decode", "argmax")
    median_size = args.median_size if args.median_size is not None else int(checkpoint.get("median_size", 1))
    return model, decode, median_size


def infer_command(args: argparse.Namespace) -> None:
    run_id = make_run_id(args)
    paths = run_paths(args.out_root, run_id)
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)

    dataset = AgriPotentialVisionDataset(
        args.data_dir,
        args.split,
        args.temporal_mode,
        label_name=args.label_name,
        patch_limit=args.limit,
        augment=False,
        random_state=args.seed,
    )
    loader = make_loader(dataset, 1, args.num_workers, shuffle=False)
    model, decode, median_size = load_checkpoint_model(args, args.checkpoint)
    out_path = args.out or (paths["submission_dir"] / f"{run_id}.zip")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for patch_id, mask in predict_dataset(model, loader, args.device, decode, median_size):
            submission_mask = np.clip(mask.astype("int16") + args.submission_label_offset, 0, 255).astype("uint8")
            zf.writestr(f"{patch_id}.png", grayscale_png(mask.shape[1], mask.shape[0], submission_mask))

    infer_visuals(args, args.checkpoint, run_id, limit=args.visual_limit)
    print(f"Wrote {out_path}")


def infer_visuals(args: argparse.Namespace, checkpoint_path: Path, run_id: str, limit: int) -> None:
    from ai4agri.subtask1.visualize import save_sample_panel

    paths = run_paths(args.out_root, run_id)
    dataset = AgriPotentialVisionDataset(
        args.data_dir,
        "test",
        args.temporal_mode,
        label_name=args.label_name,
        patch_limit=limit,
        augment=False,
        random_state=args.seed,
    )
    loader = make_loader(dataset, 1, getattr(args, "num_workers", 0), shuffle=False)
    model, decode, median_size = load_checkpoint_model(argparse.Namespace(**{**vars(args), "split": "test"}), checkpoint_path)
    predictions = list(predict_dataset(model, loader, args.device, decode, median_size))
    pred_by_id = {patch_id: mask for patch_id, mask in predictions}
    for index in range(min(limit, len(dataset))):
        item = dataset[index]
        save_sample_panel(
            paths["visual_dir"] / f"test_pred_{index:03d}_{item['patch_id']}.png",
            item["x"].numpy(),
            y_pred=pred_by_id[str(item["patch_id"])],
            title=str(item["patch_id"]),
        )


def self_test_command(args: argparse.Namespace) -> None:
    model = build_model(args.model, args.channels)
    x = torch.rand(2, args.channels, 128, 128)
    y = torch.randint(0, 5, (2, 128, 128))
    logits = model(x)
    if tuple(logits.shape) != (2, 5, 128, 128):
        raise SystemExit(f"bad output shape: {tuple(logits.shape)}")
    loss = pm1_multihot_binary_cross_entropy(logits, y)
    pred = decode_logits(logits, mode="neighbor_sum_sigmoid")
    metrics = segmentation_metrics(y.numpy(), pred.numpy())
    print(json.dumps({"output_shape": list(logits.shape), "loss": float(loss.detach()), "metrics": metrics}, indent=2))


def main() -> None:
    args = parse_args()
    if args.command == "train":
        train_command(args)
    elif args.command == "infer":
        infer_command(args)
    elif args.command == "self-test":
        self_test_command(args)
    else:
        raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
