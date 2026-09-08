# -*- coding: utf-8 -*-
"""Искажения: засветка, темнота, шум, размытие, непропечатанный текст, виньетка,
трапеция (разворот книги), рыбий глаз, JPEG-артефакты."""
import io
import numpy as np
from PIL import Image, ImageFilter


def overexpose(img, k):
    """Засветка изображения (k от 0 до 1)."""
    a = np.asarray(img, float) * (1 + 0.9 * k) + 60 * k
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def darken(img, k):
    """Затемнение изображения (k от 0 до 1)."""
    a = np.asarray(img, float) * (1 - 0.6 * k)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def gauss_noise(img, k):
    """Гауссов шум (k от 0 до 1)."""
    a = np.asarray(img, float) + np.random.normal(0, 6 + 20 * k, np.asarray(img).shape)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def blur(img, k):
    """Размытие (k от 0 до 1)."""
    return img.filter(ImageFilter.GaussianBlur(0.5 + 2.5 * k))


def fade_ink(img, k):
    """Непропечатанный текст (k от 0 до 1)."""
    a = np.asarray(img, float)
    bg = np.quantile(a, 0.9)
    a = a + (bg - a) * (0.55 * k)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def vignette(img, k):
    """Виньетка / тёмные края (k от 0 до 1)."""
    a = np.asarray(img, float)
    h, w = a.shape[:2]
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    m = 1 - np.clip(d - 0.6, 0, 1) * 0.8 * k
    return Image.fromarray(np.clip(a * m[..., None], 0, 255).astype(np.uint8))


def _coeffs(src, dst):
    """Вычисление коэффициентов перспективного преобразования."""
    A = []
    for (sx, sy), (dx, dy) in zip(src, dst):
        A.append([dx, dy, 1, 0, 0, 0, -sx * dx, -sx * dy])
        A.append([0, 0, 0, dx, dy, 1, -sy * dx, -sy * dy])
    A = np.asarray(A, dtype=float)
    B = np.array([sx, sy] for sx, sy in src).reshape(-1)
    coeffs = np.linalg.lstsq(A, B, rcond=None)[0]
    return coeffs.reshape(8)


def trapezoid(img, k):
    """Трапецеидальная деформация (разворот книги, k от 0 до 1)."""
    w, h = img.size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    shift_x = int(w * 0.15 * k)
    shift_y = int(h * 0.1 * k)
    dst = [
        (shift_x, shift_y),
        (w - shift_x, 0),
        (w, h),
        (0, h),
    ]
    c = _coeffs(src, dst)
    M = np.array([
        [c[0], c[1], c[2]],
        [c[3], c[4], c[5]],
        [c[6], c[7], 1.0]
    ])
    try:
        invM = np.linalg.inv(M)
        return img.transform((w, h), Image.PERSPECTIVE, list(invM[:2].flatten()), Image.BICUBIC)
    except Exception:
        return img


def fisheye(img, k):
    """Эффект рыбьего глаза (k от 0 до 1)."""
    if k < 0.01:
        return img
    arr = np.asarray(img).astype(float)
    h, w = arr.shape[:2]
    cx, cy = w / 2, h / 2
    
    # Нормализованные координаты
    y, x = np.mgrid[0:h, 0:w]
    x_norm = (x - cx) / max(cx, 1)
    y_norm = (y - cy) / max(cy, 1)
    
    r = np.sqrt(x_norm**2 + y_norm**2)
    mask = r < 1
    
    # Эффект рыбьего глаза
    theta = np.arctan(r[mask])
    r_new = np.tan(theta * (1 + 0.5 * k)) / np.tan(np.pi/4 * (1 + 0.5 * k))
    r_new = np.clip(r_new, 0, 0.99)
    
    angle = np.arctan2(y_norm[mask], x_norm[mask])
    
    xn = np.clip(cx + r_new * np.cos(angle) * max(cx, 1), 0, w - 1).astype(int)
    yn = np.clip(cy + r_new * np.sin(angle) * max(cy, 1), 0, h - 1).astype(int)
    
    out = np.zeros_like(arr)
    out_mask = np.zeros((h, w), dtype=bool)
    out_mask[y[mask], x[mask]] = True
    out[y[mask], x[mask]] = arr[yn, xn]
    
    # Заполняем края средним
    for c in range(arr.shape[2] if len(arr.shape) == 3 else 1):
        channel = arr[:, :, c] if len(arr.shape) == 3 else arr
        mean_val = channel.mean()
        if len(arr.shape) == 3:
            out[:, :, c][~out_mask[:, :, 0] if len(out_mask.shape) == 3 else ~out_mask] = mean_val
        else:
            out[~out_mask] = mean_val
    
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def jpeg_artifacts(img, k):
    """JPEG-артефакты (k от 0 до 1)."""
    buf = io.BytesIO()
    quality = max(5, int(95 * (1 - k)))
    img.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    return Image.open(buf)


DEGRADES = {
    "overexpose": overexpose,
    "darken": darken,
    "noise": gauss_noise,
    "blur": blur,
    "fade": fade_ink,
    "vignette": vignette,
    "trapezoid": trapezoid,
    "fisheye": fisheye,
    "jpeg": jpeg_artifacts,
}


def apply_degrade(img, name, k):
    """Применить искажение по имени с интенсивностью k."""
    fn = DEGRADES.get(name)
    if not fn:
        raise ValueError(f"Неизвестное искажение: {name}")
    return fn(img, k)
