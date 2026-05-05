"""Dataset loading for AgriPotential Subtask 1 segmentation models."""

from __future__ import annotations

import csv
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import torch
from torch.utils.data import Dataset


SPLIT_COLUMNS = ("patch_id", "row", "col", "patch_size", "n_annotated")
BANDS_PER_SCENE = 10


@dataclass(frozen=True)
class Scene:
    path: Path
    month: int | None = None


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def require_split_columns(rows: list[dict[str, str]], path: Path) -> None:
    if not rows:
        raise ValueError(f"empty split CSV: {path}")
    missing = [column for column in SPLIT_COLUMNS if column not in rows[0]]
    if missing:
        raise ValueError(f"{path} is missing required columns: {', '.join(missing)}")


def read_scenes(data_dir: Path) -> list[Scene]:
    metadata_path = data_dir / "metadata.csv"
    rows = read_csv_rows(metadata_path)
    if not rows or "filename" not in rows[0]:
        raise ValueError(f"{metadata_path} must contain a filename column")
    scenes: list[Scene] = []
    for row in rows:
        filename = row.get("filename", "").strip()
        if not filename:
            continue
        path = data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"missing Sentinel-2 raster file: {path}")
        month = int(row["month"]) if row.get("month", "").strip() else None
        scenes.append(Scene(path=path, month=month))
    if not scenes:
        raise ValueError(f"no Sentinel-2 scenes found in {metadata_path}")
    return scenes


def read_window(source, row: int, col: int, patch_size: int) -> np.ndarray:
    from rasterio.windows import Window

    return source.read(window=Window(col, row, patch_size, patch_size))


def normalize_reflectance(stack: np.ndarray) -> np.ndarray:
    """Scrub invalid Sentinel-2 reflectance and scale to roughly 0..1."""

    stack = stack.astype("float32", copy=False)
    invalid = (~np.isfinite(stack)) | (stack < 0) | (stack > 10000)
    stack = stack / 10000.0
    stack[invalid] = np.nan
    return np.nan_to_num(stack, nan=0.0, posinf=0.0, neginf=0.0)


def seasonal_index(month: int | None) -> int:
    if month in (12, 1, 2):
        return 0
    if month in (3, 4, 5):
        return 1
    if month in (6, 7, 8):
        return 2
    return 3


def temporal_features(stack: np.ndarray, scenes: Sequence[Scene], mode: str) -> np.ndarray:
    """Return C,H,W features from a T,B,H,W reflectance stack."""

    if mode == "concat":
        return stack.reshape(stack.shape[0] * stack.shape[1], stack.shape[2], stack.shape[3])
    if mode == "summary":
        reducers = (np.nanmean, np.nanstd, np.nanmin, np.nanmax)
        return np.concatenate([fn(stack, axis=0) for fn in reducers], axis=0).astype("float32", copy=False)
    if mode == "seasonal":
        blocks = []
        for season in range(4):
            indices = [index for index, scene in enumerate(scenes) if seasonal_index(scene.month) == season]
            season_stack = stack[indices] if indices else np.zeros((1, *stack.shape[1:]), dtype="float32")
            blocks.extend([np.nanmean(season_stack, axis=0), np.nanstd(season_stack, axis=0)])
        return np.concatenate(blocks, axis=0).astype("float32", copy=False)
    raise ValueError(f"unknown temporal mode: {mode}")


def channels_for_mode(scene_count: int, mode: str) -> int:
    if mode == "concat":
        return scene_count * BANDS_PER_SCENE
    if mode == "summary":
        return 4 * BANDS_PER_SCENE
    if mode == "seasonal":
        return 8 * BANDS_PER_SCENE
    raise ValueError(f"unknown temporal mode: {mode}")


class AgriPotentialVisionDataset(Dataset):
    """Reads Sentinel-2 patch tensors and optional viticulture labels on demand."""

    def __init__(
        self,
        data_dir: Path,
        split: str,
        temporal_mode: str,
        label_name: str = "viticulture",
        patch_limit: int = 0,
        augment: bool = False,
        random_state: int = 42,
    ) -> None:
        self.data_dir = data_dir
        self.split = split
        self.temporal_mode = temporal_mode
        self.label_name = label_name
        self.augment = augment
        self.rng = np.random.default_rng(random_state)

        self.scenes = read_scenes(data_dir)
        split_path = data_dir / f"{split}.csv"
        self.rows = read_csv_rows(split_path)
        require_split_columns(self.rows, split_path)
        if patch_limit:
            self.rows = self.rows[:patch_limit]

        label_path = data_dir / f"{label_name}.tif"
        self.label_path = label_path if label_path.exists() and split != "test" else None

    @property
    def input_channels(self) -> int:
        return channels_for_mode(len(self.scenes), self.temporal_mode)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, object]:
        import rasterio

        patch = self.rows[index]
        row = int(patch["row"])
        col = int(patch["col"])
        patch_size = int(patch["patch_size"])
        with ExitStack() as stack:
            sources = [stack.enter_context(rasterio.open(scene.path)) for scene in self.scenes]
            arrays = [read_window(source, row, col, patch_size) for source in sources]
            raw = normalize_reflectance(np.stack(arrays, axis=0))
            x = temporal_features(raw, self.scenes, self.temporal_mode)

            y = None
            if self.label_path is not None:
                label_source = stack.enter_context(rasterio.open(self.label_path))
                y = read_window(label_source, row, col, patch_size)[0].astype("int64")
                y[(y < 0) | (y > 4)] = 255

        if self.augment:
            x, y = self.apply_augmentation(x, y)

        item: dict[str, object] = {
            "patch_id": patch["patch_id"],
            "x": torch.from_numpy(np.ascontiguousarray(x)).float(),
        }
        if y is not None:
            item["y"] = torch.from_numpy(np.ascontiguousarray(y)).long()
        return item

    def apply_augmentation(self, x: np.ndarray, y: np.ndarray | None) -> tuple[np.ndarray, np.ndarray | None]:
        if self.rng.random() < 0.5:
            x = x[:, :, ::-1]
            y = y[:, ::-1] if y is not None else None
        if self.rng.random() < 0.5:
            x = x[:, ::-1, :]
            y = y[::-1, :] if y is not None else None
        rotations = int(self.rng.integers(0, 4))
        if rotations:
            x = np.rot90(x, rotations, axes=(1, 2))
            y = np.rot90(y, rotations, axes=(0, 1)) if y is not None else None
        return x.copy(), y.copy() if y is not None else None


def collate_patches(batch: list[dict[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {
        "patch_id": [str(item["patch_id"]) for item in batch],
        "x": torch.stack([item["x"] for item in batch]),  # type: ignore[index]
    }
    if "y" in batch[0]:
        result["y"] = torch.stack([item["y"] for item in batch])  # type: ignore[index]
    return result
