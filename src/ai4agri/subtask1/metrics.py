"""Metrics for ordinal Subtask 1 masks."""

from __future__ import annotations

import numpy as np
import torch


def soft_ordinal_cross_entropy(logits: torch.Tensor, target: torch.Tensor, sigma: float = 0.85) -> torch.Tensor:
    classes = torch.arange(logits.shape[1], device=logits.device, dtype=torch.float32)
    valid = (target >= 0) & (target <= 4)
    safe_target = target.clamp(0, 4).float()
    distances = (classes.view(1, -1, 1, 1) - safe_target.unsqueeze(1)).abs()
    soft = torch.exp(-(distances**2) / (2.0 * sigma**2))
    soft = soft / soft.sum(dim=1, keepdim=True).clamp_min(1e-6)
    log_prob = torch.log_softmax(logits, dim=1)
    loss = -(soft * log_prob).sum(dim=1)
    return loss[valid].mean()


def pm1_multihot_binary_cross_entropy(logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """BCE loss where true class and its +/-1 neighbors are positive targets."""

    classes = torch.arange(logits.shape[1], device=logits.device, dtype=torch.float32)
    valid = (target >= 0) & (target <= 4)
    safe_target = target.clamp(0, 4).float()
    distances = (classes.view(1, -1, 1, 1) - safe_target.unsqueeze(1)).abs()
    multi_hot = (distances <= 1).to(dtype=logits.dtype)
    loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, multi_hot, reduction="none").mean(dim=1)
    return loss[valid].mean()


def _neighbor_sum(prob: torch.Tensor) -> torch.Tensor:
    padded = torch.nn.functional.pad(prob, (0, 0, 0, 0, 1, 1))
    return padded[:, :-2] + padded[:, 1:-1] + padded[:, 2:]


def decode_logits(logits: torch.Tensor, mode: str = "argmax") -> torch.Tensor:
    if mode == "expected":
        prob = torch.softmax(logits, dim=1)
        values = torch.arange(logits.shape[1], device=logits.device, dtype=prob.dtype)
        return (prob * values.view(1, -1, 1, 1)).sum(dim=1).round().clamp(0, 4).long()
    if mode == "neighbor_sum":
        prob = torch.softmax(logits, dim=1)
        return _neighbor_sum(prob).argmax(dim=1).long()
    if mode == "neighbor_sum_sigmoid":
        prob = torch.sigmoid(logits)
        return _neighbor_sum(prob).argmax(dim=1).long()
    if mode == "argmax":
        return logits.argmax(dim=1).long()
    raise ValueError(f"unknown decode mode: {mode}")


def median_smooth(mask: np.ndarray, size: int) -> np.ndarray:
    if size <= 1:
        return mask
    try:
        from scipy.ndimage import median_filter

        return median_filter(mask, size=size).astype(mask.dtype, copy=False)
    except Exception:
        pad = size // 2
        padded = np.pad(mask, pad_width=pad, mode="edge")
        out = np.empty_like(mask)
        for row in range(mask.shape[0]):
            for col in range(mask.shape[1]):
                out[row, col] = np.median(padded[row : row + size, col : col + size])
        return out


def segmentation_metrics(y_true: np.ndarray, y_pred: np.ndarray, num_classes: int = 5) -> dict[str, object]:
    true = y_true.reshape(-1).astype("int64")
    pred = y_pred.reshape(-1).astype("int64")
    valid = np.isfinite(true) & (true >= 0) & (true < num_classes)
    true = true[valid]
    pred = np.clip(pred[valid], 0, num_classes - 1)
    if true.size == 0:
        return {
            "exact_accuracy": 0.0,
            "accuracy_pm1": 0.0,
            "mean_absolute_error": 0.0,
            "per_class_recall": {str(i): 0.0 for i in range(num_classes)},
            "confusion_matrix": np.zeros((num_classes, num_classes), dtype=int).tolist(),
            "pixels": 0,
        }

    confusion = np.zeros((num_classes, num_classes), dtype=np.int64)
    for t_value, p_value in zip(true, pred):
        confusion[int(t_value), int(p_value)] += 1
    recall = {}
    for cls in range(num_classes):
        denom = confusion[cls].sum()
        recall[str(cls)] = float(confusion[cls, cls] / denom) if denom else 0.0
    return {
        "exact_accuracy": float(np.mean(true == pred)),
        "accuracy_pm1": float(np.mean(np.abs(true - pred) <= 1)),
        "mean_absolute_error": float(np.mean(np.abs(true - pred))),
        "per_class_recall": recall,
        "confusion_matrix": confusion.astype(int).tolist(),
        "pixels": int(true.size),
    }
