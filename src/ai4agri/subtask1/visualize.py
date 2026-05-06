"""Notebook-ready visual artifact helpers for Subtask 1."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


CLASS_COLORS = ["#d73027", "#fc8d59", "#fee08b", "#91cf60", "#1a9850", "#7f7f7f"]
TOLERANCE_COLORS = ["#1a9850", "#fee08b", "#d73027", "#4d4d4d"]


def rgb_composite(x: np.ndarray) -> np.ndarray:
    """Build a stable pseudo-RGB from the first available 10-band block."""

    if x.shape[0] >= 8:
        bands = [3, 2, 1]
    elif x.shape[0] >= 3:
        bands = [2, 1, 0]
    else:
        return np.repeat(x[:1], 3, axis=0).transpose(1, 2, 0)
    rgb = x[bands].transpose(1, 2, 0)
    low, high = np.nanpercentile(rgb, [2, 98])
    return np.clip((rgb - low) / max(high - low, 1e-6), 0, 1)


def mask_cmap():
    from matplotlib.colors import ListedColormap

    return ListedColormap(CLASS_COLORS)


def tolerance_cmap():
    from matplotlib.colors import ListedColormap

    return ListedColormap(TOLERANCE_COLORS)


def display_mask(mask: np.ndarray) -> np.ndarray:
    """Map nodata/boundary pixels to the explicit 5th display color."""

    display = np.asarray(mask, dtype="int16", order="C").copy()
    display[(display == 255)] = 5
    return display


def accuracy_pm1_display(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Encode exact, within-one, miss, and ignored pixels for visual review."""

    true = np.asarray(y_true, dtype="int16")
    pred = np.asarray(y_pred, dtype="int16")
    valid = (true >= 0) & (true <= 4) & (pred >= 0) & (pred <= 4)
    diff = np.abs(true - pred)
    display = np.full(true.shape, 3, dtype="uint8")
    display[valid & (diff > 1)] = 2
    display[valid & (diff == 1)] = 1
    display[valid & (diff == 0)] = 0
    return display


def add_tolerance_legend(ax) -> None:
    labels = ["Exact", "Within +/-1", "Miss >1", "Ignored"]
    handles = [
        mpatches.Patch(facecolor=color, edgecolor="black", linewidth=0.3, label=label)
        for color, label in zip(TOLERANCE_COLORS, labels)
    ]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False, fontsize=7)


def save_sample_panel(
    path: Path,
    x: np.ndarray,
    y_true: np.ndarray | None = None,
    y_pred: np.ndarray | None = None,
    title: str = "",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    panels = 1 + int(y_true is not None) + int(y_pred is not None) + 2 * int(y_true is not None and y_pred is not None)
    fig, axes = plt.subplots(1, panels, figsize=(4 * panels, 4))
    if panels == 1:
        axes = [axes]
    axis_index = 0
    axes[axis_index].imshow(rgb_composite(x))
    axes[axis_index].set_title("Sentinel composite")
    axes[axis_index].axis("off")
    axis_index += 1
    if y_true is not None:
        axes[axis_index].imshow(display_mask(y_true), cmap=mask_cmap(), vmin=0, vmax=5, interpolation="nearest")
        axes[axis_index].set_title("Ground truth")
        axes[axis_index].axis("off")
        axis_index += 1
    if y_pred is not None:
        axes[axis_index].imshow(display_mask(y_pred), cmap=mask_cmap(), vmin=0, vmax=5, interpolation="nearest")
        axes[axis_index].set_title("Prediction")
        axes[axis_index].axis("off")
        axis_index += 1
    if y_true is not None and y_pred is not None:
        valid = (y_true >= 0) & (y_true <= 4) & (y_pred >= 0) & (y_pred <= 4)
        error = np.abs(y_true.astype("int16") - y_pred.astype("int16")).astype("float32", copy=False)
        error[~valid] = np.nan
        error_cmap = plt.cm.magma.copy()
        error_cmap.set_bad("black")
        axes[axis_index].imshow(error, cmap=error_cmap, vmin=0, vmax=4)
        axes[axis_index].set_title("Absolute error")
        axes[axis_index].axis("off")
        axis_index += 1

        axes[axis_index].imshow(
            accuracy_pm1_display(y_true, y_pred),
            cmap=tolerance_cmap(),
            vmin=0,
            vmax=3,
            interpolation="nearest",
        )
        axes[axis_index].set_title("Accuracy +/-1 map")
        axes[axis_index].axis("off")
        add_tolerance_legend(axes[axis_index])
    if title:
        fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
