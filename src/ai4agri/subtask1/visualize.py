"""Notebook-ready visual artifact helpers for Subtask 1."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


CLASS_COLORS = ["#d73027", "#fc8d59", "#fee08b", "#91cf60", "#1a9850"]


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


def save_sample_panel(
    path: Path,
    x: np.ndarray,
    y_true: np.ndarray | None = None,
    y_pred: np.ndarray | None = None,
    title: str = "",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    panels = 1 + int(y_true is not None) + int(y_pred is not None) + int(y_true is not None and y_pred is not None)
    fig, axes = plt.subplots(1, panels, figsize=(4 * panels, 4))
    if panels == 1:
        axes = [axes]
    axis_index = 0
    axes[axis_index].imshow(rgb_composite(x))
    axes[axis_index].set_title("Sentinel composite")
    axes[axis_index].axis("off")
    axis_index += 1
    if y_true is not None:
        axes[axis_index].imshow(y_true, cmap=mask_cmap(), vmin=0, vmax=4, interpolation="nearest")
        axes[axis_index].set_title("Ground truth")
        axes[axis_index].axis("off")
        axis_index += 1
    if y_pred is not None:
        axes[axis_index].imshow(y_pred, cmap=mask_cmap(), vmin=0, vmax=4, interpolation="nearest")
        axes[axis_index].set_title("Prediction")
        axes[axis_index].axis("off")
        axis_index += 1
    if y_true is not None and y_pred is not None:
        axes[axis_index].imshow(np.abs(y_true.astype("int16") - y_pred.astype("int16")), cmap="magma", vmin=0, vmax=4)
        axes[axis_index].set_title("Absolute error")
        axes[axis_index].axis("off")
    if title:
        fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)

