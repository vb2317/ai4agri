# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Notebook 10 — Final Stack, TTA, and Submission
#
# **Goal:** Combine all available model predictions into the best possible submission.
#
# **Pipeline:**
# ```
# Val predictions (soft probs, shape N×H×W×K) from:
#   ├── NB2: pixel baseline (LightGBM / HistGB)
#   ├── NB3: U-Net with ordinal soft labels
#   ├── NB7: CORN ordinal U-Net
#   └── NB9: pseudo-retrained pixel model (optional)
#         ↓
# Grid search on val Acc±1 over ensemble weights
#         ↓
# Expected-value decoding (optimal for Acc±1)
#         ↓
# D4 TTA (U-Net models only, 8-fold: 4 rots × 2 flips)
#         ↓
# 5×5 median filter (spatial smoothing)
#         ↓
# Test inference → 800 PNGs → ZIP → validate_submission_zip.py
# ```
#
# **HITL gate:** VB spot-checks 10 random test predictions, reviews metrics table,
# and approves before CodaBench submission.
#
# **Outputs:**
# - `results/subtask1/submissions/submit_<date>.zip` — final submission ZIP
# - `results/subtask1/submissions/final_metrics_table.csv` — val Acc±1 comparison
# - `results/subtask1/submissions/best_config.json` — winning ensemble config

# %%
import os, json, subprocess, zipfile, pickle
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

_cwd = Path(os.getcwd())
REPO_ROOT = _cwd if (_cwd / 'scripts').exists() else _cwd.parent

DATA_DIR   = REPO_ROOT / 'data' / 'subtask1'
CKPT_DIR   = REPO_ROOT / 'results' / 'subtask1' / 'checkpoints'
PRED_DIR   = REPO_ROOT / 'results' / 'subtask1' / 'val_preds'
SUB_DIR    = REPO_ROOT / 'results' / 'subtask1' / 'submissions'
VIS_DIR    = REPO_ROOT / 'results' / 'subtask1' / 'val_vis_final'

for d in [SUB_DIR, VIS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

print('REPO_ROOT:', REPO_ROOT)

# %%
# ── Config (review before running) ──────────────────────────────────────────
NUM_CLASSES    = 5
PATCH_SIZE     = 128

# Which models to include in the ensemble.
# SCRIPT_VISION_RUN_IDS should contain run IDs created by scripts/run_subtask1_vision.py.
USE_PIXEL_BASE = False
SCRIPT_VISION_RUN_IDS = []  # e.g. ['20260505T120000Z_unet_summary', '20260505T123000Z_resnet_fpn_summary']

# Post-processing options (tune based on val results)
USE_EV_DECODE  = True   # expected-value decoding (True = Acc±1-optimal; False = argmax)
USE_TTA        = True   # D4 TTA on U-Net models (8 augmentations)
MEDIAN_KSIZE   = 5      # 0 to disable median filter; try 3 or 5

# Temporal mode — must match the U-Net checkpoints
TEMPORAL_MODE  = 'summary'   # same as NB3/NB7 training
BASE_CH        = 32

import torch
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
print('Device:', DEVICE)


# %% [markdown]
# ## 1. Load Val Predictions
#
# Each model's val predictions are stored as `.npz` files in `results/subtask1/val_preds/`.
# Script-generated neural runs use `probs` shaped **(N_patches, K, H, W)** plus `y_true`.
# This notebook normalizes everything to **(N_patches, H, W, K)** for comparison.

# %%
def load_val_probs(npz_path):
    """Load soft probabilities and ground truth from legacy or script-generated .npz files."""
    data = np.load(npz_path, allow_pickle=True)
    probs = data['probs']
    gt = data['y_true'] if 'y_true' in data.files else data['gt']
    if probs.ndim == 4 and probs.shape[1] == NUM_CLASSES:
        probs = np.moveaxis(probs, 1, -1)  # N,K,H,W -> N,H,W,K
    return probs.astype('float32'), gt.astype('uint8')


def acc_pm1(pred, gt):
    return float((np.abs(pred.astype(int) - gt.astype(int)) <= 1).mean())

def exact_acc(pred, gt):
    return float((pred == gt).mean())

def ev_decode(probs):
    """probs: (..., K) → (...,) rounded expected value"""
    K      = probs.shape[-1]
    ev     = (probs * np.arange(K)).sum(axis=-1)
    return np.round(ev).astype(int).clip(0, K - 1)


models_loaded = {}

candidate_files = []
if USE_PIXEL_BASE:
    candidate_files.append(('pixel_base', PRED_DIR / 'pixel_base_val_probs.npz'))
for run_id in SCRIPT_VISION_RUN_IDS:
    candidate_files.append((run_id, PRED_DIR / f'{run_id}_val_probs.npz'))
if not SCRIPT_VISION_RUN_IDS:
    candidate_files.extend((path.stem.replace('_val_probs', ''), path) for path in sorted(PRED_DIR.glob('*_val_probs.npz')))

for label, path in candidate_files:
    if path.exists():
        probs, gt = load_val_probs(path)
        pred_argmax = probs.argmax(axis=-1)
        pred_ev     = ev_decode(probs)
        apm1_argmax = acc_pm1(pred_argmax.ravel(), gt.ravel())
        apm1_ev     = acc_pm1(pred_ev.ravel(),     gt.ravel())
        print(f'  {label:12s}  probs={probs.shape}  '
              f'Acc±1(argmax)={apm1_argmax:.4f}  Acc±1(EV)={apm1_ev:.4f}')
        models_loaded[label] = {'probs': probs, 'gt': gt}
    else:
        print(f'  {label:12s}  NOT FOUND: {path}')

print(f'\nLoaded {len(models_loaded)} model prediction(s).')

# %% [markdown]
# ## 2. Grid Search Over Ensemble Weights

# %%
if len(models_loaded) == 0:
    raise RuntimeError('No model predictions loaded. Run NB2/NB3/NB7 first.')

model_names = list(models_loaded.keys())
prob_arrays  = [models_loaded[k]['probs'] for k in model_names]

# Make sure all probs are (N, H*W, K) for consistent indexing
# Pixel-model probs may be (N_pix, K) — reshape if ground truth shape is known
gt_ref = models_loaded[model_names[0]]['gt']  # (N, H, W)

def reshape_probs(probs, ref_shape):
    """If probs is flat (N_pix, K), reshape to (N, H, W, K)"""
    N, H, W = ref_shape
    K = probs.shape[-1]
    if probs.ndim == 2:
        return probs.reshape(N, H, W, K)
    return probs  # already (N, H, W, K)

reshaped = [reshape_probs(p, gt_ref.shape) for p in prob_arrays]
gt_flat  = gt_ref.ravel()

# Grid search over weights
# With up to 4 models, do a coarse-to-fine search
best_score  = 0.0
best_weights = None
best_ensemble = None

weight_values = np.arange(0.0, 1.05, 0.1)  # 0.0 to 1.0 in steps of 0.1

from itertools import product as iproduct

n_models = len(reshaped)

if n_models == 1:
    best_weights = [1.0]
    best_ensemble = reshaped[0]
    pred = ev_decode(best_ensemble) if USE_EV_DECODE else best_ensemble.argmax(-1)
    best_score = acc_pm1(pred.ravel(), gt_flat)
    print(f'Single model Acc±1: {best_score:.4f}')
else:
    print(f'Grid searching weights for {n_models} models...')
    # Generate weight combinations that sum to 1 (coarse grid)
    count = 0
    for w in iproduct(weight_values, repeat=n_models):
        w = np.array(w)
        if w.sum() == 0:
            continue
        w = w / w.sum()
        # Weighted average of probs
        ensemble = sum(wi * pi for wi, pi in zip(w, reshaped))
        pred = ev_decode(ensemble) if USE_EV_DECODE else ensemble.argmax(-1)
        score = acc_pm1(pred.ravel(), gt_flat)
        if score > best_score:
            best_score   = score
            best_weights = w.tolist()
            best_ensemble = ensemble
        count += 1

    print(f'Searched {count} weight combinations.')
    print(f'Best val Acc±1: {best_score:.4f}')
    print('Best weights:')
    for name, w in zip(model_names, best_weights):
        print(f'  {name}: {w:.3f}')

# %%
# Compare all configurations in a table
rows = []
for name, mdata in models_loaded.items():
    probs = reshape_probs(mdata['probs'], gt_ref.shape)
    pred_argmax = probs.argmax(-1)
    pred_ev     = ev_decode(probs)
    rows.append({'Config': name,
                 'Acc±1 (argmax)': acc_pm1(pred_argmax.ravel(), gt_flat),
                 'Acc±1 (EV dec)': acc_pm1(pred_ev.ravel(), gt_flat)})

if best_ensemble is not None and len(models_loaded) > 1:
    pred_ens = ev_decode(best_ensemble) if USE_EV_DECODE else best_ensemble.argmax(-1)
    rows.append({'Config': 'Ensemble (best weights)',
                 'Acc±1 (argmax)': acc_pm1(best_ensemble.argmax(-1).ravel(), gt_flat),
                 'Acc±1 (EV dec)': acc_pm1(pred_ens.ravel(), gt_flat)})

metrics_df = pd.DataFrame(rows)
print('\n=== Val Acc±1 Comparison ===')
print(metrics_df.to_string(index=False, float_format=lambda x: f'{x:.4f}'))

metrics_df.to_csv(SUB_DIR / 'final_metrics_table.csv', index=False)

# %% [markdown]
# ## 3. Apply Median Filter (Spatial Smoothing)

# %%
from scipy.ndimage import median_filter

def apply_median_filter(pred_patches, ksize=5):
    """pred_patches: (N, H, W) int array → smoothed (N, H, W) int array"""
    if ksize == 0:
        return pred_patches
    out = np.zeros_like(pred_patches)
    for i in range(len(pred_patches)):
        out[i] = median_filter(pred_patches[i], size=ksize, mode='reflect').astype(int)
    return out


if best_ensemble is not None:
    pred_val = ev_decode(best_ensemble) if USE_EV_DECODE else best_ensemble.argmax(-1)
    pred_val_smooth = apply_median_filter(pred_val, ksize=MEDIAN_KSIZE)

    before = acc_pm1(pred_val.ravel(), gt_flat)
    after  = acc_pm1(pred_val_smooth.ravel(), gt_flat)
    print(f'Median filter (k={MEDIAN_KSIZE}): Acc±1 {before:.4f} → {after:.4f} (Δ={after-before:+.4f})')

    if after < before:
        print('Median filter hurt performance — consider setting MEDIAN_KSIZE=3 or 0.')

# %% [markdown]
# ## 4. D4 TTA on U-Net Models (8-fold Augmentation)
#
# For each test patch: run the U-Net(s) on 8 augmented versions (4 rotations × 2 flips),
# average the logits/probs before decoding. Only meaningful on spatial models (U-Net / CORN).
#
# **Note:** TTA is applied during test inference (below), not on val cached predictions.
# The val metrics above use single-pass predictions.

# %%
import torch
import torch.nn as nn

def tta_probs_unet(model, x_tensor, is_corn=False, device='cpu'):
    """
    Run D4 TTA on a single patch tensor.
    x_tensor: (F, H, W) float32
    Returns: (H, W, K) averaged probabilities
    """
    model.eval()
    total_probs = None
    x = x_tensor.unsqueeze(0).to(device)   # (1, F, H, W)

    augments = []
    for k in range(4):                     # 4 rotations
        xr = torch.rot90(x, k, dims=[2, 3])
        augments.append((xr, k, False))
        xf = torch.flip(xr, dims=[3])       # horizontal flip
        augments.append((xf, k, True))

    with torch.no_grad():
        for xa, rot_k, flipped in augments:
            logits = model(xa)              # (1, K or K-1, H, W)

            if is_corn:
                probs = _corn_probs_torch(logits.permute(0,2,3,1))  # (1, H, W, K)
            else:
                probs = torch.softmax(logits.permute(0,2,3,1), dim=-1)  # (1, H, W, K)

            probs_np = probs[0].cpu().numpy()   # (H, W, K)

            # Reverse augmentation
            if flipped:
                probs_np = probs_np[:, ::-1, :]   # un-flip
            probs_np = np.rot90(probs_np, -rot_k, axes=(0, 1))  # un-rotate

            if total_probs is None:
                total_probs = probs_np.copy()
            else:
                total_probs += probs_np

    return (total_probs / len(augments)).clip(0, 1)


def _corn_probs_torch(logits):
    """logits: (B, H, W, K-1) → (B, H, W, K)"""
    cond = torch.sigmoid(logits)
    cum  = torch.cumprod(cond, dim=-1)
    ones  = torch.ones(*logits.shape[:-1], 1, device=logits.device)
    zeros = torch.zeros(*logits.shape[:-1], 1, device=logits.device)
    ext   = torch.cat([ones, cum, zeros], dim=-1)
    return (ext[..., :-1] - ext[..., 1:]).clamp(min=0)


print('TTA functions defined.')


# %%
# ── Load U-Net checkpoints for inference ─────────────────────────────────────

class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=False), nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1, bias=False), nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True),
        )
    def forward(self, x): return self.block(x)


def build_unet(in_ch, num_classes, base_ch, head_type='soft'):
    """head_type: 'soft' (K outputs) or 'corn' (K-1 outputs)"""

    class UNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.enc1 = DoubleConv(in_ch, base_ch)
            self.enc2 = DoubleConv(base_ch, base_ch*2)
            self.enc3 = DoubleConv(base_ch*2, base_ch*4)
            self.enc4 = DoubleConv(base_ch*4, base_ch*8)
            self.pool = nn.MaxPool2d(2)
            self.bottleneck = DoubleConv(base_ch*8, base_ch*16)
            self.up4, self.dec4 = nn.ConvTranspose2d(base_ch*16, base_ch*8, 2, 2), DoubleConv(base_ch*16, base_ch*8)
            self.up3, self.dec3 = nn.ConvTranspose2d(base_ch*8,  base_ch*4, 2, 2), DoubleConv(base_ch*8,  base_ch*4)
            self.up2, self.dec2 = nn.ConvTranspose2d(base_ch*4,  base_ch*2, 2, 2), DoubleConv(base_ch*4,  base_ch*2)
            self.up1, self.dec1 = nn.ConvTranspose2d(base_ch*2,  base_ch,   2, 2), DoubleConv(base_ch*2,  base_ch)
            out_ch = num_classes - 1 if head_type == 'corn' else num_classes
            self.head = nn.Conv2d(base_ch, out_ch, 1)
        def forward(self, x):
            e1 = self.enc1(x); e2 = self.enc2(self.pool(e1))
            e3 = self.enc3(self.pool(e2)); e4 = self.enc4(self.pool(e3))
            b  = self.bottleneck(self.pool(e4))
            d4 = self.dec4(torch.cat([self.up4(b), e4], 1))
            d3 = self.dec3(torch.cat([self.up3(d4), e3], 1))
            d2 = self.dec2(torch.cat([self.up2(d3), e2], 1))
            d1 = self.dec1(torch.cat([self.up1(d2), e1], 1))
            return self.head(d1)

    return UNet()


# Infer IN_CHANNELS from temporal mode and band count
mode_to_ch = {'concat': 340, 'summary': 20, 'seasonal': 40}
IN_CHANNELS = mode_to_ch.get(TEMPORAL_MODE, 20)

unet_models = {}
for label, ckpt_name, head_type in [
    ('unet_soft', 'unet_best.pt',      'soft'),
    ('corn',      'corn_unet_best.pt', 'corn'),
]:
    ckpt_path = CKPT_DIR / ckpt_name
    if ckpt_path.exists() and (label in models_loaded or USE_TTA):
        ckpt = torch.load(ckpt_path, map_location=DEVICE)
        in_ch = ckpt.get('in_channels', IN_CHANNELS)
        bc    = ckpt.get('base_ch', BASE_CH)
        m = build_unet(in_ch, NUM_CLASSES, bc, head_type).to(DEVICE)
        m.load_state_dict(ckpt['model_state'])
        m.eval()
        unet_models[label] = (m, head_type == 'corn', in_ch)
        print(f'Loaded {label}: in_ch={in_ch}, base_ch={bc}')

print(f'\nU-Net models ready for inference: {list(unet_models.keys())}')

# %% [markdown]
# ## 5. Save Best Config

# %%
best_config = {
    'model_weights': dict(zip(model_names, best_weights)) if best_weights else {},
    'use_ev_decode': USE_EV_DECODE,
    'use_tta':       USE_TTA,
    'median_ksize':  MEDIAN_KSIZE,
    'temporal_mode': TEMPORAL_MODE,
    'base_ch':       BASE_CH,
    'val_acc_pm1':   best_score,
    'date':          datetime.now().strftime('%Y-%m-%d'),
}
(SUB_DIR / 'best_config.json').write_text(json.dumps(best_config, indent=2))
print('Best config saved:')
print(json.dumps(best_config, indent=2))

# %% [markdown]
# ## 6. Test Inference → 800 PNGs

# %%
import rasterio
from rasterio.windows import Window
from PIL import Image

TEST_CSV  = DATA_DIR / 'test.csv'
NORM_FILE = REPO_ROOT / 'results' / 'subtask1' / 'norm_stats.npz'
norm_stats = dict(np.load(NORM_FILE)) if NORM_FILE.exists() else None

PNG_DIR = SUB_DIR / 'pngs'
PNG_DIR.mkdir(parents=True, exist_ok=True)

test_df = pd.read_csv(TEST_CSV)
print(f'Test patches: {len(test_df)}')


def list_sentinel_tifs(data_dir):
    tifs = sorted(Path(data_dir).glob('S2*.tif'))
    if not tifs: tifs = sorted(Path(data_dir).glob('**/*.tif'))
    return tifs

sentinel_files = list_sentinel_tifs(DATA_DIR)
print(f'Sentinel TIF files: {len(sentinel_files)}')


def load_stack(row_idx, col_idx, patch_size):
    win = Window(col_idx, row_idx, patch_size, patch_size)
    frames = []
    for f in sentinel_files:
        with rasterio.open(f) as src:
            frames.append(src.read(window=win).astype(np.float32))
    return np.stack(frames, 0) / 10000.0   # (T, C, H, W)


def reduce_temporal(stack, mode):
    if mode == 'concat':
        T, C, H, W = stack.shape; return stack.reshape(T*C, H, W)
    elif mode == 'summary':
        return np.concatenate([stack.mean(0), stack.std(0)], axis=0)
    elif mode == 'seasonal':
        T = stack.shape[0]; q = T // 4
        return np.concatenate([stack[:q].mean(0), stack[q:2*q].mean(0),
                                stack[2*q:3*q].mean(0), stack[3*q:].mean(0)], axis=0)
    raise ValueError(mode)


def normalise(feat, norm_stats):
    if norm_stats is None: return feat
    m = norm_stats['mean'][:, None, None].astype(np.float32)
    s = norm_stats['std'][:, None, None].astype(np.float32)
    return (feat - m) / np.where(s == 0, 1.0, s)


# %%
# Also load pixel model for test inference
pixel_clf = None
if USE_PIXEL_BASE:
    # Try pseudo-retrained first, then original NB2 model
    for pkl_name in ['pseudo_lgbm_r2.pkl', 'pseudo_lgbm_r1.pkl', 'pixel_baseline.pkl']:
        pkl_path = CKPT_DIR / pkl_name
        if pkl_path.exists():
            with open(pkl_path, 'rb') as f:
                pixel_clf = pickle.load(f)
            print(f'Loaded pixel model: {pkl_name}')
            break

    if pixel_clf is None:
        print('No pixel model checkpoint found. Pixel baseline excluded from test inference.')
        USE_PIXEL_BASE = False

# %%
all_test_preds = []
t0 = __import__('time').time()

print(f'Running inference on {len(test_df)} test patches...')
print(f'  TTA: {USE_TTA}, Median filter k={MEDIAN_KSIZE}')

for i, row in test_df.iterrows():
    patch_id = row['patch_id']
    r, c, ps = int(row['row']), int(row['col']), int(row['patch_size'])

    stack = load_stack(r, c, ps)               # (T, C, H, W)
    feat  = reduce_temporal(stack, TEMPORAL_MODE)  # (F, H, W)
    feat  = normalise(feat, norm_stats)
    x_t   = torch.from_numpy(feat)             # (F, H, W)

    ensemble_probs = None

    # ── U-Net / CORN predictions ────────────────────────────────────────────
    for label, (model, is_corn, in_ch) in unet_models.items():
        w = best_config['model_weights'].get(label, 1.0 / max(len(unet_models), 1))
        if w == 0:
            continue
        if USE_TTA:
            p = tta_probs_unet(model, x_t[:in_ch], is_corn=is_corn, device=DEVICE)
        else:
            with torch.no_grad():
                logits = model(x_t[:in_ch].unsqueeze(0).to(DEVICE))
                if is_corn:
                    p = _corn_probs_torch(logits.permute(0,2,3,1))[0].cpu().numpy()
                else:
                    p = torch.softmax(logits.permute(0,2,3,1), dim=-1)[0].cpu().numpy()
        ensemble_probs = p * w if ensemble_probs is None else ensemble_probs + p * w

    # ── Pixel model prediction ──────────────────────────────────────────────
    if pixel_clf is not None:
        w = best_config['model_weights'].get('pixel_base', 0.0)
        if w > 0:
            f_flat = feat.reshape(feat.shape[0], -1).T     # (H*W, F)
            # Match feature count expected by pixel model
            n_feat = getattr(pixel_clf, 'n_features_in_', f_flat.shape[1])
            f_flat = f_flat[:, :n_feat]
            pix_prob = pixel_clf.predict_proba(f_flat)     # (H*W, K)
            pix_prob = pix_prob.reshape(ps, ps, NUM_CLASSES)  # (H, W, K)
            ensemble_probs = (pix_prob * w if ensemble_probs is None
                              else ensemble_probs + pix_prob * w)

    # ── Fallback: argmax if no model ran ───────────────────────────────────
    if ensemble_probs is None:
        pred = np.zeros((ps, ps), dtype=np.uint8)
    else:
        if USE_EV_DECODE:
            pred = ev_decode(ensemble_probs).astype(np.uint8)
        else:
            pred = ensemble_probs.argmax(-1).astype(np.uint8)

    # ── Median filter ──────────────────────────────────────────────────────
    if MEDIAN_KSIZE > 0:
        from scipy.ndimage import median_filter
        pred = median_filter(pred, size=MEDIAN_KSIZE, mode='reflect').astype(np.uint8)

    # ── Save PNG ────────────────────────────────────────────────────────────
    Image.fromarray(pred).save(PNG_DIR / f'{patch_id}.png')
    all_test_preds.append(pred)

    if (i + 1) % 100 == 0:
        elapsed = __import__('time').time() - t0
        print(f'  {i+1}/{len(test_df)} patches done  ({elapsed:.0f}s elapsed)')

print(f'\nInference complete: {len(test_df)} patches in {__import__("time").time()-t0:.1f}s')
png_files = list(PNG_DIR.glob('*.png'))
print(f'PNG files written: {len(png_files)}')

# %% [markdown]
# ## 7. Sanity Checks

# %%
import matplotlib.pyplot as plt

all_preds_arr = np.stack(all_test_preds)   # (800, H, W)

# Class histogram over all 800 test patches
unique, counts = np.unique(all_preds_arr, return_counts=True)
total = counts.sum()
print('Test prediction class distribution:')
for u, cnt in zip(unique, counts):
    print(f'  Class {u}: {cnt:,} pixels ({100*cnt/total:.1f}%)')

# Flag missing classes
present = set(unique)
missing = set(range(NUM_CLASSES)) - present
if missing:
    print(f'\nWARNING: Classes {missing} are completely absent from test predictions!')
    print('This may indicate a degenerate model. Review ensemble weights.')
else:
    print('\nAll 5 classes present in test predictions — OK.')

# Bar chart
fig, ax = plt.subplots(figsize=(7, 4))
colors = ['#1a1a1a', '#4d8c57', '#a3c86a', '#f5e642', '#e07b1a']
for cls in range(NUM_CLASSES):
    cnt = counts[list(unique).index(cls)] if cls in unique else 0
    ax.bar(cls, cnt, color=colors[cls], edgecolor='white')
ax.set(xlabel='Predicted class', ylabel='Pixel count',
       title='Test prediction class distribution (800 patches)')
ax.set_xticks(range(NUM_CLASSES))
plt.tight_layout()
plt.savefig(SUB_DIR / 'test_class_dist.png', dpi=100)
plt.show()

# %%
# Visual spot-check: 10 random test patches (no ground truth)
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

CLASS_CMAP = ListedColormap(['#1a1a1a', '#4d8c57', '#a3c86a', '#f5e642', '#e07b1a'])
N_VIS = 10

indices = np.random.choice(len(all_test_preds), N_VIS, replace=False)
patch_ids = test_df['patch_id'].values

fig, axes = plt.subplots(2, 5, figsize=(18, 7))
for j, idx in enumerate(indices):
    ax = axes[j // 5, j % 5]
    ax.imshow(all_test_preds[idx], cmap=CLASS_CMAP, vmin=0, vmax=4, interpolation='nearest')
    ax.set_title(f'{patch_ids[idx]}', fontsize=8)
    ax.axis('off')

plt.suptitle('Test Predictions — HITL Spot-Check (no ground truth)', fontsize=13)
plt.tight_layout()
plt.savefig(SUB_DIR / 'test_spotcheck.png', dpi=100)
plt.show()
print('\nHITL: Review these predictions visually before submitting.')
print('Look for: spatial coherence, expected class distribution, no all-one-class patches.')

# %% [markdown]
# ## 8. Package ZIP and Validate

# %%
date_str = datetime.now().strftime('%Y%m%d_%H%M')
zip_path = SUB_DIR / f'submit_{date_str}.zip'

print(f'Packaging {len(png_files)} PNGs into {zip_path.name}...')
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for png_f in sorted(PNG_DIR.glob('*.png')):
        zf.write(png_f, png_f.name)   # root-level, no subdirectory

print(f'ZIP size: {zip_path.stat().st_size / 1e6:.1f} MB')

# %%
# Run the project validator
validator_script = REPO_ROOT / 'scripts' / 'validate_submission_zip.py'

if validator_script.exists():
    result = subprocess.run(
        ['python3', str(validator_script),
         '--zip', str(zip_path),
         '--subtask1-codabench',
         '--check-class-values',
         '--test-csv', str(DATA_DIR / 'test.csv')],
        capture_output=True, text=True
    )
    print('=== Validator Output ===')
    print(result.stdout)
    if result.returncode == 0:
        print('✓ Validation PASSED — ZIP is ready for submission.')
    else:
        print('✗ Validation FAILED:')
        print(result.stderr)
else:
    print(f'Validator script not found at {validator_script}')
    print('Run: python scripts/validate_submission_zip.py --help')

# %% [markdown]
# ## Final Summary Table

# %%
print('=' * 60)
print('FINAL SUBMISSION SUMMARY')
print('=' * 60)
print()
print(metrics_df.to_string(index=False, float_format=lambda x: f'{x:.4f}'))
print()
print(f'Best config val Acc±1:  {best_score:.4f}')
print(f'Temporal mode:          {TEMPORAL_MODE}')
print(f'EV decode:              {USE_EV_DECODE}')
print(f'TTA (D4):               {USE_TTA}')
print(f'Median filter size:     {MEDIAN_KSIZE}')
print()
print(f'ZIP path:  {zip_path}')
print()
print('HITL final gate:')
print('  [ ] Spot-check images look spatially coherent')
print('  [ ] All 5 classes present in predictions')
print('  [ ] Validator exited with code 0')
print('  [ ] Val Acc±1 meets or exceeds target (0.90)')
print('  [ ] VB submits ZIP to CodaBench')
