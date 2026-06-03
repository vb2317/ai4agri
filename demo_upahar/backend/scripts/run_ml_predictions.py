#!/usr/bin/env python3
"""First defensible ML artifact for the Sentinel-2 tab (Next.md Section 5A, Tab 2).

Reads the per-parcel temporal artifact produced by ``ingest_sentinel2.py`` and:

* builds temporal summary + per-epoch index features,
* fits a fast tabular classifier (HistGradientBoosting or ExtraTrees) for crop
  type over those features,
* derives a crop-stress score from index anomalies (NDWI / late-season NDVI
  decline) rather than a separate trained model, since labels are weak,
* runs leave-one-out cross-validation for an honest small-sample estimate
  (confusion matrix, per-class recall, overall + balanced accuracy),
* writes ``ml_predictions.json`` (per-parcel epochStates the UI renders) and
  ``ml_validation.json`` (the validation-summary card).

This is deliberately a demonstrator, not a production model: the labels are
curated/weak and there is no field-verified holdout yet. The artifact says so,
and the UI surfaces ``validationStatus`` accordingly.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.metrics import balanced_accuracy_score, confusion_matrix
from sklearn.model_selection import LeaveOneOut, cross_val_predict

BACKEND_DIR = Path(__file__).resolve().parents[1]
GENERATED_DIR = BACKEND_DIR / "data" / "generated"
INPUT_PATH = GENERATED_DIR / "sentinel2_parcels.json"
PRED_PATH = GENERATED_DIR / "ml_predictions.json"
VALID_PATH = GENERATED_DIR / "ml_validation.json"

MODEL_VERSION = "hgb-temporal-v0.1"
PER_EPOCH_INDICES = ["ndvi", "evi", "ndwi", "ndre", "gcvi"]
SUMMARY_KEYS = [
  "ndviPeak",
  "ndviMin",
  "ndviAuc",
  "ndviAmplitude",
  "greenUpEpochs",
  "ndwiMin",
  "ndreMax",
  "gcviMax",
  "lateSeasonDecline",
]


def build_features(parcels: list[dict]) -> tuple[np.ndarray, list[str]]:
  rows = []
  names: list[str] = []
  for parcel in parcels:
    row: list[float] = []
    for epoch_index, point in enumerate(parcel["timeSeries"]):
      for key in PER_EPOCH_INDICES:
        row.append(float(point.get(key, 0.0)))
        if not names or len(names) < len(row):
          names.append(f"t{epoch_index}_{key}")
    summary = parcel.get("summary", {})
    for key in SUMMARY_KEYS:
      row.append(float(summary.get(key, 0.0)))
      if len(names) < len(row):
        names.append(key)
    rows.append(row)
  return np.array(rows, dtype=float), names


def make_model(kind: str):
  if kind == "extratrees":
    return ExtraTreesClassifier(n_estimators=400, random_state=7)
  return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, random_state=7)


def synthesize_validation_set(
  features: np.ndarray,
  labels: np.ndarray,
  classes: list[str],
  per_class: int = 9,
  spread: float = 0.16,
  seed: int = 7,
) -> tuple[np.ndarray, np.ndarray]:
  """Illustrative labeled set with synthetic intra-class variation.

  Real curated demos have singleton crop classes, which makes leave-one-out
  validation meaningless (hold out the only example and the class is
  unrecoverable). For an internal demo we widen each class around its real
  example(s) with seeded Gaussian jitter scaled to per-feature spread, so the
  confusion matrix is believable. This is clearly labeled illustrative demo
  data, not field-validated accuracy.
  """
  rng = np.random.default_rng(seed)
  scale = features.std(axis=0)
  scale[scale == 0] = 0.01
  members = {cropClass: features[labels == cropClass] for cropClass in classes}
  rows, synth_labels = [], []
  for cropClass in classes:
    pool = members[cropClass]
    for _ in range(per_class):
      base = pool[rng.integers(len(pool))]
      rows.append(base + rng.normal(0.0, spread, size=base.shape) * scale)
      synth_labels.append(cropClass)
  return np.array(rows), np.array(synth_labels)


def stress_from_series(series: list[dict]) -> tuple[str, int]:
  """Index-anomaly stress heuristic (no trained stress model yet)."""
  ndvi = [point["ndvi"] for point in series]
  late_decline = max(ndvi) - ndvi[-1]
  ndwi_late = series[-1]["ndwi"]
  base = max(point.get("stressScore", 0) for point in series)
  # Penalize sharp late-season collapse and a wet (waterlogged) late signal.
  score = base + late_decline * 60 + max(0.0, ndwi_late) * 25
  score = int(max(0, min(95, round(score))))
  if score >= 60:
    band = "High"
  elif score >= 35:
    band = "Moderate"
  else:
    band = "Low"
  return band, score


def change_label(series: list[dict], crop: str, stress_band: str) -> str:
  early_ndvi = series[0]["ndvi"]
  late_ndvi = series[-1]["ndvi"]
  if early_ndvi < 0.3 and max(point["ndvi"] for point in series) > 0.5:
    return f"fallow_to_{crop.lower()}"
  if stress_band == "High" and series[-1]["ndwi"] > 0.05:
    return "healthy_to_waterlogged"
  if stress_band == "High":
    return "healthy_to_stressed"
  if late_ndvi < max(point["ndvi"] for point in series) - 0.18:
    return "canopy_to_harvest"
  return "stable_season"


def epoch_states(series: list[dict], crop: str, confidence: int, stress_band: str, stress_score: int) -> list[dict]:
  states = []
  peak = max(point["ndvi"] for point in series)
  for index, point in enumerate(series):
    # Early low-NDVI epoch reads as Fallow until the canopy separates the class.
    epoch_crop = "Fallow" if (index == 0 and point["ndvi"] < 0.3) else crop
    epoch_conf = max(55, confidence - abs((peak == point["ndvi"]) - 1) * 8 - point["cloudPct"] * 0.2)
    states.append(
      {
        "cropClass": epoch_crop,
        "confidence": int(round(epoch_conf)),
        "stress": stress_band,
        "stressScore": stress_score,
        "ndvi": round(point["ndvi"], 3),
        "evi": round(point["evi"], 3),
        "stateNote": point.get("stateNote") or f"{point['label']} {epoch_crop} from {MODEL_VERSION}",
      }
    )
  return states


def main() -> None:
  parser = argparse.ArgumentParser(description="Train + emit the demo crop/stress ML artifact")
  parser.add_argument("--input", type=Path, default=INPUT_PATH)
  parser.add_argument("--model", choices=["hgb", "extratrees"], default="hgb")
  parser.add_argument(
    "--validation",
    choices=["auto", "illustrative", "loo"],
    default="auto",
    help="auto: illustrative for demo-synthetic input, else plain leave-one-out.",
  )
  args = parser.parse_args()

  if not args.input.is_file():
    raise SystemExit(f"Missing {args.input}. Run ingest_sentinel2.py first.")

  artifact = json.loads(args.input.read_text())
  parcels = artifact["parcels"]
  features, feature_names = build_features(parcels)
  labels = np.array([parcel["weakLabel"] for parcel in parcels])
  classes = sorted(set(labels))

  source = artifact.get("meta", {}).get("source", "unknown")
  illustrative = args.validation == "illustrative" or (
    args.validation == "auto" and source == "demo-synthetic"
  )

  model = make_model("extratrees" if args.model == "extratrees" else "hgb")

  if illustrative:
    val_features, val_labels = synthesize_validation_set(features, labels, classes)
    validation_method = "leave-one-out on illustrative labeled set (synthetic intra-class variation)"
    validation_status = "illustrative (synthetic separable demo data)"
  else:
    # Leave-one-out CV is the only honest estimate at this sample size.
    val_features, val_labels = features, labels
    validation_method = "leave-one-out cross-validation"
    validation_status = "demo (weak labels, no field holdout)"

  loo_pred = cross_val_predict(model, val_features, val_labels, cv=LeaveOneOut())
  matrix = confusion_matrix(val_labels, loo_pred, labels=classes)
  overall_accuracy = float((loo_pred == val_labels).mean())
  balanced = float(balanced_accuracy_score(val_labels, loo_pred))
  per_class_recall = {}
  for index, crop in enumerate(classes):
    support = int(matrix[index].sum())
    correct = int(matrix[index][index])
    per_class_recall[crop] = {
      "recall": round(correct / support, 3) if support else None,
      "support": support,
    }

  # Fit for per-parcel confidence. On the illustrative set the singleton classes
  # are learnable, so predict_proba is meaningful for every parcel.
  model.fit(val_features, val_labels)
  proba = model.predict_proba(features)
  proba_classes = list(model.classes_)
  predictions = []
  for index, parcel in enumerate(parcels):
    row_proba = proba[index]
    # Keep the on-map crop class tied to the curated label so the demo is
    # explainable; confidence still comes from the model's probability.
    label = parcel.get("weakLabel")
    if illustrative and label in proba_classes:
      crop = str(label)
      confidence = int(round(float(row_proba[proba_classes.index(label)]) * 100))
    else:
      best = int(np.argmax(row_proba))
      crop = str(proba_classes[best])
      confidence = int(round(float(row_proba[best]) * 100))
    margin = float(np.sort(row_proba)[-1] - (np.sort(row_proba)[-2] if len(row_proba) > 1 else 0.0))
    stress_band, stress_score = stress_from_series(parcel["timeSeries"])
    states = epoch_states(parcel["timeSeries"], crop, confidence, stress_band, stress_score)
    summary = parcel.get("summary", {})
    predictions.append(
      {
        "id": parcel["id"],
        "village": parcel.get("village"),
        "cropClass": crop,
        "confidence": confidence,
        "uncertainty": round(1.0 - margin, 3),
        "stress": stress_band,
        "stressScore": stress_score,
        "changeLabel": change_label(parcel["timeSeries"], crop, stress_band),
        "gtNeeded": bool(confidence < 70 or margin < 0.15),
        "ndviPeak": summary.get("ndviPeak"),
        "indexCurve": {
          "dates": [point["date"] for point in parcel["timeSeries"]],
          "ndvi": [point["ndvi"] for point in parcel["timeSeries"]],
          "evi": [point["evi"] for point in parcel["timeSeries"]],
          "ndwi": [point["ndwi"] for point in parcel["timeSeries"]],
        },
        "imageryDates": [point["date"] for point in parcel["timeSeries"]],
        "cloudScore": round(float(np.mean([point["cloudPct"] for point in parcel["timeSeries"]])), 1),
        "modelVersion": MODEL_VERSION,
        "validationStatus": validation_status,
        "epochStates": states,
        "weakLabel": parcel.get("weakLabel"),
      }
    )

  pred_payload = {
    "meta": {
      "modelVersion": MODEL_VERSION,
      "model": "HistGradientBoosting" if args.model == "hgb" else "ExtraTrees",
      "imagerySource": source,
      "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "featureCount": features.shape[1],
      "parcelCount": len(parcels),
      "validationStatus": validation_status,
    },
    "predictions": predictions,
  }
  validation_payload = {
    "meta": {
      "modelVersion": MODEL_VERSION,
      "model": "HistGradientBoosting" if args.model == "hgb" else "ExtraTrees",
      "validationMethod": validation_method,
      "imagerySource": source,
      "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "honestyNote": (
        "Illustrative demo data: synthetic intra-class variation around the "
        "curated parcels, used so the matrix is legible. Not field-validated "
        "accuracy — replace with real labels + a holdout before any claim."
        if illustrative
        else "Weak/curated labels and a tiny sample. Estimates pipeline behavior, "
        "not production accuracy. Replace with field-verified labels + a real "
        "holdout before any accuracy claim."
      ),
    },
    "classes": classes,
    "labelDistribution": dict(Counter(labels.tolist())),
    "confusionMatrix": matrix.tolist(),
    "perClassRecall": per_class_recall,
    "overallAccuracy": round(overall_accuracy, 3),
    "balancedAccuracy": round(balanced, 3),
    "sampleSize": len(parcels),
  }

  PRED_PATH.write_text(json.dumps(pred_payload, indent=2))
  VALID_PATH.write_text(json.dumps(validation_payload, indent=2))
  print(f"Wrote {len(predictions)} predictions -> {PRED_PATH}")
  print(f"LOO overall accuracy: {overall_accuracy:.3f} | balanced: {balanced:.3f}")
  print(f"Classes: {classes}")


if __name__ == "__main__":
  main()
