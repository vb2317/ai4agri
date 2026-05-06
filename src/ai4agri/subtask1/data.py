"""Dataset loading for AgriPotential Subtask 1 segmentation models."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import torch
from torch.utils.data import Dataset


SPLIT_COLUMNS = ("patch_id", "row", "col", "patch_size", "n_annotated")
BANDS_PER_SCENE = 10
RAW_LABEL_MIN = 1
RAW_LABEL_MAX = 5
IGNORE_INDEX = 255


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


def remap_raw_labels(labels: np.ndarray) -> np.ndarray:
    """Map raw AgriPotential labels 1..5 to model classes 0..4; raw 0 is ignored."""

    raw = labels.astype("int64", copy=False)
    mapped = np.full(raw.shape, IGNORE_INDEX, dtype="int64")
    valid = (raw >= RAW_LABEL_MIN) & (raw <= RAW_LABEL_MAX)
    mapped[valid] = raw[valid] - RAW_LABEL_MIN
    return mapped


class AgriPotentialVisionDataset(Dataset):
    """Reads Sentinel-2 patch tensors and optional viticulture labels on demand."""

    def __init__(
        self,
        data_dir: Path | str,
        split: str,
        temporal_mode: str,
        label_name: str = "viticulture",
        patch_limit: int = 0,
        augment: bool = False,
        random_state: int = 42,
        shuffle_rows: bool = False,
        cache_dir: Path | str | None = None,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.split = split
        self.temporal_mode = temporal_mode
        self.label_name = label_name
        self.augment = augment
        self.rng = np.random.default_rng(random_state)

        self.scenes = read_scenes(self.data_dir)
        split_path = self.data_dir / f"{split}.csv"
        self.rows = read_csv_rows(split_path)
        require_split_columns(self.rows, split_path)
        if shuffle_rows:
            indices = self.rng.permutation(len(self.rows))
            self.rows = [self.rows[int(index)] for index in indices]
        if patch_limit:
            self.rows = self.rows[:patch_limit]

        label_path = self.data_dir / f"{label_name}.tif"
        self.label_path = label_path if label_path.exists() and split != "test" else None
        self.cache_dir = Path(cache_dir) / split if cache_dir else None
        if self.cache_dir is not None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._sources: list[Any] | None = None
        self._label_source: Any | None = None

    @property
    def input_channels(self) -> int:
        return channels_for_mode(len(self.scenes), self.temporal_mode)

    def __len__(self) -> int:
        return len(self.rows)

    def __getstate__(self) -> dict[str, object]:
        state = self.__dict__.copy()
        state["_sources"] = None
        state["_label_source"] = None
        return state

    def close(self) -> None:
        for source in getattr(self, "_sources", None) or []:
            source.close()
        label_source = getattr(self, "_label_source", None)
        if label_source is not None:
            label_source.close()
        self._sources = None
        self._label_source = None

    def __del__(self) -> None:
        self.close()

    def sources(self) -> list[Any]:
        import rasterio

        if self._sources is None:
            self._sources = [rasterio.open(scene.path) for scene in self.scenes]
        return self._sources

    def label_source(self) -> Any | None:
        import rasterio

        if self.label_path is None:
            return None
        if self._label_source is None:
            self._label_source = rasterio.open(self.label_path)
        return self._label_source

    def __getitem__(self, index: int) -> dict[str, object]:
        patch = self.rows[index]
        cached = self.read_cached_arrays(index, patch)
        if cached is not None:
            x, y = cached
            if self.augment:
                x, y = self.apply_augmentation(x, y)
            return self.make_item(patch["patch_id"], x, y)

        row = int(patch["row"])
        col = int(patch["col"])
        patch_size = int(patch["patch_size"])
        try:
            arrays = [read_window(source, row, col, patch_size) for source in self.sources()]
        except Exception:
            self.close()
            arrays = [read_window(source, row, col, patch_size) for source in self.sources()]
        raw = normalize_reflectance(np.stack(arrays, axis=0))
        x = temporal_features(raw, self.scenes, self.temporal_mode)

        y = None
        label_source = self.label_source()
        if label_source is not None:
            try:
                y = read_window(label_source, row, col, patch_size)[0].astype("int64")
            except Exception:
                self._label_source = None
                label_source.close()
                reopened_label_source = self.label_source()
                if reopened_label_source is None:
                    raise
                y = read_window(reopened_label_source, row, col, patch_size)[0].astype("int64")
            y = remap_raw_labels(y)

        self.write_cached_item(index, patch, x, y)

        if self.augment:
            x, y = self.apply_augmentation(x, y)

        return self.make_item(patch["patch_id"], x, y)

    def make_item(self, patch_id: str, x: np.ndarray, y: np.ndarray | None) -> dict[str, object]:
        item: dict[str, object] = {
            "patch_id": patch_id,
            "x": torch.from_numpy(np.ascontiguousarray(x)).float(),
        }
        if y is not None:
            item["y"] = torch.from_numpy(np.ascontiguousarray(y)).long()
        return item

    def cache_path(self, index: int, patch: dict[str, str]) -> Path | None:
        if self.cache_dir is None:
            return None
        patch_id = patch["patch_id"].replace("/", "_")
        return self.cache_dir / f"{index:06d}_{patch_id}_{self.temporal_mode}.npz"

    def read_cached_arrays(self, index: int, patch: dict[str, str]) -> tuple[np.ndarray, np.ndarray | None] | None:
        path = self.cache_path(index, patch)
        if path is None or not path.exists():
            return None
        try:
            with np.load(path) as payload:
                x = payload["x"].astype("float32", copy=False)
                y = payload["y"].astype("int64", copy=False) if "y" in payload.files else None
                return x, y
        except Exception:
            path.unlink(missing_ok=True)
            return None

    def write_cached_item(self, index: int, patch: dict[str, str], x: np.ndarray, y: np.ndarray | None) -> None:
        path = self.cache_path(index, patch)
        if path is None:
            return
        temp_path = path.with_suffix(path.suffix + ".tmp")
        try:
            payload: dict[str, np.ndarray] = {"x": x.astype("float16", copy=False)}
            if y is not None:
                payload["y"] = y.astype("uint8", copy=False)
            with temp_path.open("wb") as file:
                np.savez(file, **payload)
            temp_path.replace(path)
        except Exception:
            temp_path.unlink(missing_ok=True)

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
