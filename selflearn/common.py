# -*- coding: utf-8 -*-
"""Общие утилиты: логи, IO, метрики."""
import json
import logging
import os
from pathlib import Path
import numpy as np
import yaml


def load_yaml(p):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure(p):
    Path(p).mkdir(parents=True, exist_ok=True)
    return Path(p)


def jdump(obj, p):
    p = Path(p)
    ensure(p.parent)
    tmp = str(p) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def jload(p, default=None):
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def get_logger(name, logfile=None):
    lg = logging.getLogger(name)
    if lg.handlers:
        return lg
    lg.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(name)-8s | %(levelname)-7s | %(message)s", "%H:%M:%S")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    lg.addHandler(sh)
    if logfile:
        ensure(Path(logfile).parent)
        fh = logging.FileHandler(logfile, encoding="utf-8")
        fh.setFormatter(fmt)
        lg.addHandler(fh)
    return lg


def iou(a, b):
    """IoU для двух боксов [x0, y0, x1, y1]."""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    iw = max(0, min(ax1, bx1) - max(ax0, bx0))
    ih = max(0, min(ay1, by1) - max(ay0, by0))
    inter = iw * ih
    union = max(0, ax1 - ax0) * max(0, ay1 - ay0) + max(0, bx1 - bx0) * max(0, by1 - by0) - inter
    return inter / union if union > 0 else 0.0


def match_boxes(pred, gt, thr=0.5):
    """Жадное сопоставление боксов -> (precision, recall, mean_iou)."""
    pairs = sorted(((iou(p, g), pi, gi) for pi, p in enumerate(pred) for gi, g in enumerate(gt)),
                   key=lambda t: -t[0])
    used_p, used_g, ious = set(), set(), []
    for v, pi, gi in pairs:
        if v < thr:
            break
        if pi in used_p or gi in used_g:
            continue
        used_p.add(pi)
        used_g.add(gi)
        ious.append(v)
    tp = len(ious)
    prec = tp / len(pred) if pred else (1.0 if not gt else 0.0)
    rec = tp / len(gt) if gt else 1.0
    return prec, rec, (float(np.mean(ious)) if ious else 0.0)


def token_f1(a, b):
    """Token-level F1 для текстовых описаний."""
    ta = set(str(a).lower().split())
    tb = set(str(b).lower().split())
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    p = inter / len(ta) if ta else 0.0
    r = inter / len(tb) if tb else 0.0
    return 2 * p * r / (p + r) if p + r > 0 else 0.0


def mask_iou(pred_mask, gt_mask):
    """IoU для бинарных масок (numpy arrays)."""
    pred_b = pred_mask > 0.5
    gt_b = gt_mask > 0.5
    inter = np.logical_and(pred_b, gt_b).sum()
    union = np.logical_or(pred_b, gt_b).sum()
    return float(inter / union) if union > 0 else 0.0
