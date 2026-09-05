Нужны ссылка на датасеты размеченных сканов крови с раковыми клетками с фотографиями и метаданными (сегментированное выделение раковых образований, текстовое описание раковых образований, объем, классы, ссылки на репозитории)

Определи, какую llm модель лучше использовать для написания приложения, которое автономно подобрать модели для предобработки изображений и собрать несколько нейросетевых моделей на первично на скаченных медицинских данных (классифицирует фото, разметит сегменты области с раковыми объектами, даст текстовое описание выделенных сегментов), затем сможет сгенерировать правдоподобные данные (сформировать фото с и без раковых объектов, классифицирует фото, разметит сегменты области с раковыми объектами, даст текстовое описание выделенных сегментов), в том числе с деградированными изображениями для дополнительного обучения. По результату обучения предложит самую лучшую модель для работы.

# 1. Оценка моделей: топ-3 по связке «качество + скорость»

Для полного цикла «сегментация → выделение участков (детекция) → классификация → описание» в 2024–2026 наиболее перспективны:

| Модель | Качество | Скорость | Сегментация | Выделение участков | Классификация | Описание текстом |
|---|---|---|---|---|---|---|
| **Grounded SAM 2** (Grounding DINO 1.5 + SAM 2) | 9/10 (zero-shot) | 6/10 | ✅ по текстовому промпту («опухолевые клетки») | ✅ боксы | ⚠️ через внешний классификатор | ⚠️ через VLM |
| **MedSAM / EfficientViT-SAM** | 8–9/10 (мед. домен) | 6–8/10 | ✅ лучший мед.-сегмент | ⚠️ по промптам/боксам | — | — |
| **YOLO11/YOLOv8-seg** | 7–8/10 (после дообучения) | 10/10 (реалтайм) | ✅ маски | ✅ боксы | ✅ встроенная | — |

**Выводы:**
- **Максимальное качество «из коробки»** (без обучения): Grounded SAM 2 — находит и вырезает раковые структуры по текстовому запросу; описание добавляется через VLM (LLaVA-Med, Qwen2.5-VL, PathChat для гистологии).
- **Максимальное качество медицинской сегментации с дообучением**: MedSAM (и его быстрые варианты EfficientViT-SAM/MobileSAM); классическая альтернатива — U-Net/Unet++ из `segmentation_models_pytorch`, который обучается быстрее и проще — он и взят в приложение 2.
- **Лучшее соотношение скорость/качество для продакшена**: YOLO-seg — одна модель вместо трёх, обучение за минуты/часы, инференс реалтайм.
- Для **классификации** гистологии отдельно сильны foundation-модели патологии (UNI, CONCH, H-Optimus-0) + MIL; для **описаний** — связка сегментатора с VLM.

Приложение 2 обучает именно «обучаемую тройку»: классификаторы (любые архитектуры, включая эффективные), U-Net-семейство для сегментации и YOLO для детекции+сегментации.

# 2. Структура проекта

```
cancer_cv/
├── requirements.txt
├── configs/
│   ├── download.yaml     # конфиг приложения 1
│   └── train.yaml        # конфиг приложения 2
├── app1_downloader.py
├── app2_autotrain.py
└── tools/
    └── npz2folders.py    # конвертер датасетов MedMNIST в папки
```

**requirements.txt**

```
requests>=2.31
PyYAML>=6.0
tqdm>=4.66
numpy>=1.24
Pillow>=10.0
torch>=2.1
torchvision>=0.16
scikit-learn>=1.3
timm>=0.9
segmentation-models-pytorch>=0.3.3
ultralytics>=8.2
```

# 3. Приложение 1 — загрузчик данных

**configs/download.yaml**

```yaml
settings:
  base_dir: ./data          # все пути ниже — относительно этой папки
  timeout: 120
  retries: 3
  verify_ssl: true
  headers:
    User-Agent: research-downloader/1.0

downloads:
  # --- файл (без распаковки) ---
  - name: bloodmnist            # контроль: нормальные клетки крови (8 классов)
    url: https://zenodo.org/records/10519652/files/bloodmnist.npz
    dest: bloodmnist/bloodmnist.npz   # путь к итоговому файлу
    kind: file
    overwrite: false
    # sha256: <хэш>             # необязательная проверка целостности

  # --- архив (скачать и распаковать) ---
  - name: tn3k_repo             # УЗИ щитовидной железы, маски узлов
    url: https://github.com/haifangong/TRFE-Net-for-thyroid-nodule-segmentation/archive/refs/heads/main.zip
    dest: tn3k
    kind: archive
    keep_archive: false

  # --- шаблон для своих ссылок ---
  # - name: my_dataset
  #   url: https://example.org/data.zip
  #   dest: my_dataset
  #   kind: archive            # archive | file
  #   sha256: null
  #   overwrite: false
```

> Для датасетов с Kaggle/HuggingFace прямые ссылки часто требуют авторизации: качайте их вручную (`kaggle datasets download ...`, `huggingface-cli download --repo-type dataset ...`) и кладите в `data/...` — приложение 2 работает уже с локальными папками. Загрузчик поддерживает любые прямые ссылки, включая токены через `headers`.

**app1_downloader.py**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приложение 1: загрузка датасетов по конфигу (скачивание, контроль сумм, распаковка)."""
from __future__ import annotations

import argparse
import hashlib
import logging
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
import yaml

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

log = logging.getLogger("downloader")


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO,
                        format="%(asctime)s | %(levelname)-7s | %(message)s",
                        datefmt="%H:%M:%S")


def human(n: float) -> str:
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"


def sha256_of(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def url_filename(url: str) -> str:
    name = Path(unquote(urlparse(url).path)).name
    return name or "download.bin"


def download_one(url: str, target: Path, session: requests.Session,
                 timeout: int, retries: int, resume: bool = True) -> None:
    """Скачивание с докачкой и ретраями."""
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".part")
    pos = tmp.stat().st_size if (resume and tmp.exists()) else 0

    attempt = 0
    while True:
        attempt += 1
        headers = {"Range": f"bytes={pos}-"} if pos else {}
        try:
            with session.get(url, headers=headers, stream=True, timeout=timeout) as r:
                if pos and r.status_code == 206:
                    mode = "ab"                      # сервер поддержит докачку
                else:
                    r.raise_for_status()
                    mode, pos = "wb", 0              # начинаем заново
                total = int(r.headers.get("Content-Length") or 0) + pos
                bar = tqdm(total=total or None, initial=pos, unit="B",
                           unit_scale=True, desc=target.name[:40], ncols=90) if tqdm else None
                with open(tmp, mode) as f:
                    for chunk in r.iter_content(1 << 20):
                        if not chunk:
                            continue
                        f.write(chunk)
                        if bar:
                            bar.update(len(chunk))
                if bar:
                    bar.close()
            tmp.rename(target)
            log.info("OK: %s (%s)", target, human(target.stat().st_size))
            return
        except Exception as e:  # noqa: BLE001
            if attempt > retries:
                raise RuntimeError(f"Не удалось скачать {url}: {e}") from e
            wait = 2 ** attempt
            log.warning("Ошибка (%s). Повтор %d/%d через %d с...", e, attempt, retries, wait)
            time.sleep(wait)


def safe_extract(archive: Path, dest_dir: Path) -> None:
    dest_dir = dest_dir.resolve()
    suf = "".join(archive.suffixes).lower()
    if suf.endswith(".zip"):
        import zipfile
        with zipfile.ZipFile(archive) as z:
            for m in z.infolist():                 # защита от zip-slip
                if not str((dest_dir / m.filename).resolve()).startswith(str(dest_dir)):
                    raise RuntimeError(f"Небезопасный путь в архиве: {m.filename}")
            z.extractall(dest_dir)
    elif suf.endswith((".tar.gz", ".tgz", ".tar")):
        import tarfile
        mode = "r:gz" if suf.endswith((".tar.gz", ".tgz")) else "r:"
        with tarfile.open(archive, mode) as t:
            for m in t.getmembers():
                if not str((dest_dir / m.name).resolve()).startswith(str(dest_dir)):
                    raise RuntimeError(f"Небезопасный путь в архиве: {m.name}")
            t.extractall(dest_dir)
    else:
        raise ValueError(f"Неподдерживаемый формат архива: {archive.name}")


def process_item(item: dict, settings: dict, session: requests.Session, force: bool) -> None:
    base = Path(settings.get("base_dir", "."))
    dest = (base / item["dest"]).resolve()
    kind = item.get("kind", "archive")
    url = item["url"]
    overwrite = bool(item.get("overwrite", False)) or force
    timeout = int(settings.get("timeout", 120))
    retries = int(settings.get("retries", 3))

    if kind == "file":
        if dest.exists() and not overwrite:
            log.info("SKIP %s: файл уже существует", item.get("name", url))
            return
        download_one(url, dest, session, timeout, retries)
        if item.get("sha256"):
            real = sha256_of(dest)
            if real.lower() != str(item["sha256"]).lower():
                raise RuntimeError(f"Контрольная сумма не совпала для {dest}")
        return

    # archive
    if dest.exists() and any(dest.iterdir()) and not overwrite:
        log.info("SKIP %s: папка уже существует (%s)", item.get("name", url), dest)
        return
    dest.mkdir(parents=True, exist_ok=True)
    archive = dest / url_filename(url)
    download_one(url, archive, session, timeout, retries)
    if item.get("sha256"):
        real = sha256_of(archive)
        if real.lower() != str(item["sha256"]).lower():
            raise RuntimeError(f"Контрольная сумма не совпала для {archive}")
    safe_extract(archive, dest)
    log.info("Распаковано в %s", dest)
    if not item.get("keep_archive", False):
        archive.unlink()


def main() -> None:
    ap = argparse.ArgumentParser(description="Загрузчик датасетов по конфигу")
    ap.add_argument("--config", required=True)
    ap.add_argument("--only", nargs="*", default=None, help="только эти имена")
    ap.add_argument("--force", action="store_true", help="перезакачать существующее")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    setup_logging(args.verbose)

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    settings = cfg.get("settings", {})
    session = requests.Session()
    session.headers.update(settings.get("headers") or {"User-Agent": "app1-downloader/1.0"})
    session.verify = bool(settings.get("verify_ssl", True))

    items = cfg.get("downloads", [])
    if args.only:
        items = [i for i in items if i.get("name") in args.only]

    ok, failed = [], []
    for item in items:
        name = item.get("name", item["url"])
        try:
            process_item(item, settings, session, args.force)
            ok.append(name)
        except Exception as e:  # noqa: BLE001
            log.error("FAILED %s: %s", name, e)
            failed.append((name, str(e)))

    log.info("Итог: %d успешно, %d с ошибками", len(ok), len(failed))
    for n, err in failed:
        log.error("  - %s: %s", n, err)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

# 4. Конвертер (для примера с BloodMNIST)

**tools/npz2folders.py**

```python
#!/usr/bin/env python3
"""MedMNIST npz -> папки train/val/test для приложения 2."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    data = np.load(args.npz)
    out = Path(args.out)
    for split in ("train", "val", "test"):
        x, y = data[f"{split}_images"], data[f"{split}_labels"]
        for i, (img, lab) in enumerate(zip(x, y)):
            cls = int(lab) if np.ndim(lab) == 0 else int(lab[0])
            d = out / split / f"class_{cls}"
            d.mkdir(parents=True, exist_ok=True)
            Image.fromarray(img).save(d / f"{i:06d}.png")
    print(f"Готово: {out}")


if __name__ == "__main__":
    main()
```

# 5. Приложение 2 — автообучение и отчёт

**configs/train.yaml**

```yaml
run:
  work_dir: runs/blood_exp1
  seed: 42
  device: auto            # auto | cuda | cpu

data:
  task: classification    # тип по умолчанию (у каждой модели свой)
  root: data/bloodmnist   # куда скачали/положили данные
  train_dir: train        # <root>/train/<класс>/*.png
  val_dir: val
  test_dir: test
  img_size: 64
  # для сегментации (тип модели: segmentation):
  images_subdir: images   # <root>/<train_dir>/images
  masks_subdir: masks     # <root>/<train_dir>/masks

models:
  # 1) быстрый бейзлайн классификации
  - name: resnet18_baseline
    type: classification
    arch: resnet18
    enabled: true
    params: {epochs: 8, batch_size: 64, lr: 3e-4, optimizer: adamw, scheduler: cosine, patience: 4, pretrained: true}

  # 2) более ёмкая архитектура
  - name: efficientnet_b0
    type: classification
    arch: efficientnet_b0
    enabled: true
    params: {epochs: 12, batch_size: 64, lr: 2e-4, weight_decay: 1e-4, patience: 5, pretrained: true}

  # 3) сегментация (нужны пары images+маски; по умолчанию выключено)
  - name: unet_r34_seg
    type: segmentation
    arch: unet
    enabled: false
    params: {encoder: resnet34, img_size: 256, epochs: 20, batch_size: 16, lr: 1e-3, patience: 5, pretrained: true}

  # 4) YOLO: детекция + сегментация (нужен data.yaml в формате COCO/YOLO)
  - name: yolo_seg
    type: yolo_seg
    arch: yolov8n-seg.pt
    enabled: false
    params: {data: data/my_coco/data.yaml, epochs: 30, imgsz: 640, batch: 16}
```

**app2_autotrain.py**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приложение 2: автономное обучение моделей из конфига, сравнение и отчёт."""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import yaml
from PIL import Image
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                             f1_score, roc_auc_score)
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms

log = logging.getLogger("autotrain")
IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
MEAN, STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)


# ----------------------------- утилиты ---------------------------------------
def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)-7s | %(message)s",
                        datefmt="%H:%M:%S")


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def pick_device(pref: str) -> torch.device:
    if pref == "cpu":
        return torch.device("cpu")
    if pref == "cuda" or (pref == "auto" and torch.cuda.is_available()):
        return torch.device("cuda")
    if pref == "auto" and getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def make_scaler(device: torch.device):
    if device.type != "cuda":
        return None
    try:
        return torch.amp.GradScaler("cuda")
    except Exception:  # старые версии torch
        try:
            return torch.cuda.amp.GradScaler()
        except Exception:
            return None


def safe_load(path: Path, device: torch.device):
    try:
        return torch.load(path, map_location=device, weights_only=True)
    except TypeError:
        return torch.load(path, map_location=device)


# --------------------------- классификация -----------------------------------
def cls_transforms(img_size: int, train: bool = True):
    if train:
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(0.2, 0.2, 0.2, 0.05),
            transforms.RandomAffine(degrees=10, translate=(0.05, 0.05)),
            transforms.ToTensor(),
            transforms.Normalize(MEAN, STD)])
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD)])


def patch_classifier_head(model: nn.Module, num_classes: int) -> None:
    for attr in ("fc", "classifier", "head"):
        if hasattr(model, attr):
            head = getattr(model, attr)
            if isinstance(head, nn.Linear):
                setattr(model, attr, nn.Linear(head.in_features, num_classes))
                return
            if isinstance(head, nn.Sequential):          # efficientnet и похожие
                for i, m in enumerate(head):
                    if isinstance(m, nn.Linear):
                        head[i] = nn.Linear(m.in_features, num_classes)
                        return
    raise RuntimeError(f"Не удалось заменить последний слой модели на {num_classes} классов")


def build_classifier(arch: str, num_classes: int, pretrained: bool = True) -> nn
# 1. Оценка моделей: топ-3 по связке «качество + скорость»

Для полного цикла «сегментация → выделение участков (детекция) → классификация → описание» в 2024–2026 наиболее перспективны:

| Модель | Качество | Скорость | Сегментация | Выделение участков | Классификация | Описание текстом |
|---|---|---|---|---|---|---|
| **Grounded SAM 2** (Grounding DINO 1.5 + SAM 2) | 9/10 (zero-shot) | 6/10 | ✅ по текстовому промпту («опухолевые клетки») | ✅ боксы | ⚠️ через внешний классификатор | ⚠️ через VLM |
| **MedSAM / EfficientViT-SAM** | 8–9/10 (мед. домен) | 6–8/10 | ✅ лучший мед.-сегмент | ⚠️ по промптам/боксам | — | — |
| **YOLO11/YOLOv8-seg** | 7–8/10 (после дообучения) | 10/10 (реалтайм) | ✅ маски | ✅ боксы | ✅ встроенная | — |

**Выводы:**
- **Максимальное качество «из коробки»** (без обучения): Grounded SAM 2 — находит и вырезает раковые структуры по текстовому запросу; описание добавляется через VLM (LLaVA-Med, Qwen2.5-VL, PathChat для гистологии).
- **Максимальное качество медицинской сегментации с дообучением**: MedSAM (и его быстрые варианты EfficientViT-SAM/MobileSAM); классическая альтернатива — U-Net/Unet++ из `segmentation_models_pytorch`, который обучается быстрее и проще — он и взят в приложение 2.
- **Лучшее соотношение скорость/качество для продакшена**: YOLO-seg — одна модель вместо трёх, обучение за минуты/часы, инференс реалтайм.
- Для **классификации** гистологии отдельно сильны foundation-модели патологии (UNI, CONCH, H-Optimus-0) + MIL; для **описаний** — связка сегментатора с VLM.

Приложение 2 обучает именно «обучаемую тройку»: классификаторы (любые архитектуры, включая эффективные), U-Net-семейство для сегментации и YOLO для детекции+сегментации.

# 2. Структура проекта

```
cancer_cv/
├── requirements.txt
├── configs/
│   ├── download.yaml     # конфиг приложения 1
│   └── train.yaml        # конфиг приложения 2
├── app1_downloader.py
├── app2_autotrain.py
└── tools/
    └── npz2folders.py    # конвертер датасетов MedMNIST в папки
```

**requirements.txt**

```
requests>=2.31
PyYAML>=6.0
tqdm>=4.66
numpy>=1.24
Pillow>=10.0
torch>=2.1
torchvision>=0.16
scikit-learn>=1.3
timm>=0.9
segmentation-models-pytorch>=0.3.3
ultralytics>=8.2
```

# 3. Приложение 1 — загрузчик данных

**configs/download.yaml**

```yaml
settings:
  base_dir: ./data          # все пути ниже — относительно этой папки
  timeout: 120
  retries: 3
  verify_ssl: true
  headers:
    User-Agent: research-downloader/1.0

downloads:
  # --- файл (без распаковки) ---
  - name: bloodmnist            # контроль: нормальные клетки крови (8 классов)
    url: https://zenodo.org/records/10519652/files/bloodmnist.npz
    dest: bloodmnist/bloodmnist.npz   # путь к итоговому файлу
    kind: file
    overwrite: false
    # sha256: <хэш>             # необязательная проверка целостности

  # --- архив (скачать и распаковать) ---
  - name: tn3k_repo             # УЗИ щитовидной железы, маски узлов
    url: https://github.com/haifangong/TRFE-Net-for-thyroid-nodule-segmentation/archive/refs/heads/main.zip
    dest: tn3k
    kind: archive
    keep_archive: false

  # --- шаблон для своих ссылок ---
  # - name: my_dataset
  #   url: https://example.org/data.zip
  #   dest: my_dataset
  #   kind: archive            # archive | file
  #   sha256: null
  #   overwrite: false
```

> Для датасетов с Kaggle/HuggingFace прямые ссылки часто требуют авторизации: качайте их вручную (`kaggle datasets download ...`, `huggingface-cli download --repo-type dataset ...`) и кладите в `data/...` — приложение 2 работает уже с локальными папками. Загрузчик поддерживает любые прямые ссылки, включая токены через `headers`.

**app1_downloader.py**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приложение 1: загрузка датасетов по конфигу (скачивание, контроль сумм, распаковка)."""
from __future__ import annotations

import argparse
import hashlib
import logging
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
import yaml

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

log = logging.getLogger("downloader")


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO,
                        format="%(asctime)s | %(levelname)-7s | %(message)s",
                        datefmt="%H:%M:%S")


def human(n: float) -> str:
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"


def sha256_of(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def url_filename(url: str) -> str:
    name = Path(unquote(urlparse(url).path)).name
    return name or "download.bin"


def download_one(url: str, target: Path, session: requests.Session,
                 timeout: int, retries: int, resume: bool = True) -> None:
    """Скачивание с докачкой и ретраями."""
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".part")
    pos = tmp.stat().st_size if (resume and tmp.exists()) else 0

    attempt = 0
    while True:
        attempt += 1
        headers = {"Range": f"bytes={pos}-"} if pos else {}
        try:
            with session.get(url, headers=headers, stream=True, timeout=timeout) as r:
                if pos and r.status_code == 206:
                    mode = "ab"                      # сервер поддержит докачку
                else:
                    r.raise_for_status()
                    mode, pos = "wb", 0              # начинаем заново
                total = int(r.headers.get("Content-Length") or 0) + pos
                bar = tqdm(total=total or None, initial=pos, unit="B",
                           unit_scale=True, desc=target.name[:40], ncols=90) if tqdm else None
                with open(tmp, mode) as f:
                    for chunk in r.iter_content(1 << 20):
                        if not chunk:
                            continue
                        f.write(chunk)
                        if bar:
                            bar.update(len(chunk))
                if bar:
                    bar.close()
            tmp.rename(target)
            log.info("OK: %s (%s)", target, human(target.stat().st_size))
            return
        except Exception as e:  # noqa: BLE001
            if attempt > retries:
                raise RuntimeError(f"Не удалось скачать {url}: {e}") from e
            wait = 2 ** attempt
            log.warning("Ошибка (%s). Повтор %d/%d через %d с...", e, attempt, retries, wait)
            time.sleep(wait)


def safe_extract(archive: Path, dest_dir: Path) -> None:
    dest_dir = dest_dir.resolve()
    suf = "".join(archive.suffixes).lower()
    if suf.endswith(".zip"):
        import zipfile
        with zipfile.ZipFile(archive) as z:
            for m in z.infolist():                 # защита от zip-slip
                if not str((dest_dir / m.filename).resolve()).startswith(str(dest_dir)):
                    raise RuntimeError(f"Небезопасный путь в архиве: {m.filename}")
            z.extractall(dest_dir)
    elif suf.endswith((".tar.gz", ".tgz", ".tar")):
        import tarfile
        mode = "r:gz" if suf.endswith((".tar.gz", ".tgz")) else "r:"
        with tarfile.open(archive, mode) as t:
            for m in t.getmembers():
                if not str((dest_dir / m.name).resolve()).startswith(str(dest_dir)):
                    raise RuntimeError(f"Небезопасный путь в архиве: {m.name}")
            t.extractall(dest_dir)
    else:
        raise ValueError(f"Неподдерживаемый формат архива: {archive.name}")


def process_item(item: dict, settings: dict, session: requests.Session, force: bool) -> None:
    base = Path(settings.get("base_dir", "."))
    dest = (base / item["dest"]).resolve()
    kind = item.get("kind", "archive")
    url = item["url"]
    overwrite = bool(item.get("overwrite", False)) or force
    timeout = int(settings.get("timeout", 120))
    retries = int(settings.get("retries", 3))

    if kind == "file":
        if dest.exists() and not overwrite:
            log.info("SKIP %s: файл уже существует", item.get("name", url))
            return
        download_one(url, dest, session, timeout, retries)
        if item.get("sha256"):
            real = sha256_of(dest)
            if real.lower() != str(item["sha256"]).lower():
                raise RuntimeError(f"Контрольная сумма не совпала для {dest}")
        return

    # archive
    if dest.exists() and any(dest.iterdir()) and not overwrite:
        log.info("SKIP %s: папка уже существует (%s)", item.get("name", url), dest)
        return
    dest.mkdir(parents=True, exist_ok=True)
    archive = dest / url_filename(url)
    download_one(url, archive, session, timeout, retries)
    if item.get("sha256"):
        real = sha256_of(archive)
        if real.lower() != str(item["sha256"]).lower():
            raise RuntimeError(f"Контрольная сумма не совпала для {archive}")
    safe_extract(archive, dest)
    log.info("Распаковано в %s", dest)
    if not item.get("keep_archive", False):
        archive.unlink()


def main() -> None:
    ap = argparse.ArgumentParser(description="Загрузчик датасетов по конфигу")
    ap.add_argument("--config", required=True)
    ap.add_argument("--only", nargs="*", default=None, help="только эти имена")
    ap.add_argument("--force", action="store_true", help="перезакачать существующее")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    setup_logging(args.verbose)

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    settings = cfg.get("settings", {})
    session = requests.Session()
    session.headers.update(settings.get("headers") or {"User-Agent": "app1-downloader/1.0"})
    session.verify = bool(settings.get("verify_ssl", True))

    items = cfg.get("downloads", [])
    if args.only:
        items = [i for i in items if i.get("name") in args.only]

    ok, failed = [], []
    for item in items:
        name = item.get("name", item["url"])
        try:
            process_item(item, settings, session, args.force)
            ok.append(name)
        except Exception as e:  # noqa: BLE001
            log.error("FAILED %s: %s", name, e)
            failed.append((name, str(e)))

    log.info("Итог: %d успешно, %d с ошибками", len(ok), len(failed))
    for n, err in failed:
        log.error("  - %s: %s", n, err)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

# 4. Конвертер (для примера с BloodMNIST)

**tools/npz2folders.py**

```python
#!/usr/bin/env python3
"""MedMNIST npz -> папки train/val/test для приложения 2."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    data = np.load(args.npz)
    out = Path(args.out)
    for split in ("train", "val", "test"):
        x, y = data[f"{split}_images"], data[f"{split}_labels"]
        for i, (img, lab) in enumerate(zip(x, y)):
            cls = int(lab) if np.ndim(lab) == 0 else int(lab[0])
            d = out / split / f"class_{cls}"
            d.mkdir(parents=True, exist_ok=True)
            Image.fromarray(img).save(d / f"{i:06d}.png")
    print(f"Готово: {out}")


if __name__ == "__main__":
    main()
```

# 5. Приложение 2 — автообучение и отчёт

**configs/train.yaml**

```yaml
run:
  work_dir: runs/blood_exp1
  seed: 42
  device: auto            # auto | cuda | cpu

data:
  task: classification    # тип по умолчанию (у каждой модели свой)
  root: data/bloodmnist   # куда скачали/положили данные
  train_dir: train        # <root>/train/<класс>/*.png
  val_dir: val
  test_dir: test
  img_size: 64
  # для сегментации (тип модели: segmentation):
  images_subdir: images   # <root>/<train_dir>/images
  masks_subdir: masks     # <root>/<train_dir>/masks

models:
  # 1) быстрый бейзлайн классификации
  - name: resnet18_baseline
    type: classification
    arch: resnet18
    enabled: true
    params: {epochs: 8, batch_size: 64, lr: 3e-4, optimizer: adamw, scheduler: cosine, patience: 4, pretrained: true}

  # 2) более ёмкая архитектура
  - name: efficientnet_b0
    type: classification
    arch: efficientnet_b0
    enabled: true
    params: {epochs: 12, batch_size: 64, lr: 2e-4, weight_decay: 1e-4, patience: 5, pretrained: true}

  # 3) сегментация (нужны пары images+маски; по умолчанию выключено)
  - name: unet_r34_seg
    type: segmentation
    arch: unet
    enabled: false
    params: {encoder: resnet34, img_size: 256, epochs: 20, batch_size: 16, lr: 1e-3, patience: 5, pretrained: true}

  # 4) YOLO: детекция + сегментация (нужен data.yaml в формате COCO/YOLO)
  - name: yolo_seg
    type: yolo_seg
    arch: yolov8n-seg.pt
    enabled: false
    params: {data: data/my_coco/data.yaml, epochs: 30, imgsz: 640, batch: 16}
```

**app2_autotrain.py**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приложение 2: автономное обучение моделей из конфига, сравнение и отчёт."""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import yaml
from PIL import Image
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                             f1_score, roc_auc_score)
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms

log = logging.getLogger("autotrain")
IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
MEAN, STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)


# ----------------------------- утилиты ---------------------------------------
def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)-7s | %(message)s",
                        datefmt="%H:%M:%S")


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def pick_device(pref: str) -> torch.device:
    if pref == "cpu":
        return torch.device("cpu")
    if pref == "cuda" or (pref == "auto" and torch.cuda.is_available()):
        return torch.device("cuda")
    if pref == "auto" and getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def make_scaler(device: torch.device):
    if device.type != "cuda":
        return None
    try:
        return torch.amp.GradScaler("cuda")
    except Exception:  # старые версии torch
        try:
            return torch.cuda.amp.GradScaler()
        except Exception:
            return None


def safe_load(path: Path, device: torch.device):
    try:
        return torch.load(path, map_location=device, weights_only=True)
    except TypeError:
        return torch.load(path, map_location=device)


# --------------------------- классификация -----------------------------------
def cls_transforms(img_size: int, train: bool = True):
    if train:
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(0.2, 0.2, 0.2, 0.05),
            transforms.RandomAffine(degrees=10, translate=(0.05, 0.05)),
            transforms.ToTensor(),
            transforms.Normalize(MEAN, STD)])
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD)])


def patch_classifier_head(model: nn.Module, num_classes: int) -> None:
    for attr in ("fc", "classifier", "head"):
        if hasattr(model, attr):
            head = getattr(model, attr)
            if isinstance(head, nn.Linear):
                setattr(model, attr, nn.Linear(head.in_features, num_classes))
                return
            if isinstance(head, nn.Sequential):          # efficientnet и похожие
                for i, m in enumerate(head):
                    if isinstance(m, nn.Linear):
                        head[i] = nn.Linear(m.in_features, num_classes)
                        return
    raise RuntimeError(f"Не удалось заменить последний слой модели на {num_classes} классов")


def build_classifier(arch: str, num_classes: int, pretrained: bool = True) -> nn.Module:
    try:
        import timm
        model = timm.create_model(arch, pretrained=pretrained, num_classes=num_classes)
        log.info("Архитектура %s загружена через timm", arch)
        return model
    except Exception as e:  # noqa: BLE001
        log.warning("timm недоступен/модели %s нет (%s) — пробую torchvision", arch, e)
    import torchvision.models as tvm
    try:
        model = tvm.get_model(arch, weights="DEFAULT" if pretrained else None)
    except Exception as e2:  # noqa: BLE001
        raise RuntimeError(f"Не удалось создать архитектуру {arch}: {e2}") from e2
    patch_classifier_head(model, num_classes)
    return model


@torch.no_grad()
def eval_classification(model, loader, device, num_classes: int) -> dict:
    model.eval()
    ys, ps, probs = [], [], []
    for x, y in loader:
        logits = model(x.to(device))
        probs.append(torch.softmax(logits, 1).cpu().numpy())
        ps.append(logits.argmax(1).cpu().numpy())
        ys.append(y.numpy())
    y_true, y_pred, prob = np.concatenate(ys), np.concatenate(ps), np.concatenate(probs)
    m = {"accuracy": float(accuracy_score(y_true, y_pred)),
         "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
         "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0))}
    try:
        if num_classes == 2:
            m["roc_auc"] = float(roc_auc_score(y_true, prob[:, 1]))
        else:
            m["roc_auc"] = float(roc_auc_score(y_true, prob, multi_class="ovr"))
    except Exception:  # noqa: BLE001
        m["roc_auc"] = None
    return m


def cls_score(m: dict) -> float:
    parts = [m["balanced_accuracy"], m["f1_macro"]]
    if m.get("roc_auc") is not None:
        parts.append(m["roc_auc"])
    return float(np.mean(parts))


def train_classification(mcfg: dict, data_cfg: dict, run_cfg: dict, device) -> dict:
    p = mcfg.get("params", {})
    img_size = int(p.get("img_size", data_cfg.get("img_size", 224)))
    epochs = int(p.get("epochs", 10))
    bs = int(p.get("batch_size", 32))
    lr = float(p.get("lr", 1e-4))
    wd = float(p.get("weight_decay", 1e-4))
    patience = int(p.get("patience", max(3, epochs // 4)))
    opt_name = str(p.get("optimizer", "adamw")).lower()
    sched_name = str(p.get("scheduler", "cosine")).lower()

    root = Path(data_cfg["root"])
    tr_dir, va_dir = root / data_cfg.get("train_dir", "train"), root / data_cfg.get("val_dir", "val")
    if not tr_dir.exists():
        raise FileNotFoundError(f"Нет папки {tr_dir}. Ожидается: <root>/<train_dir>/<класс>/изображения")
    tr = datasets.ImageFolder(tr_dir, transform=cls_transforms(img_size, True))
    va = datasets.ImageFolder(va_dir, transform=cls_transforms(img_size, False))
    classes, num_classes = tr.classes, len(tr.classes)
    te_dir = root / data_cfg.get("test_dir", "test")
    te = datasets.ImageFolder(te_dir, transform=cls_transforms(img_size, False)) if te_dir.exists() else None

    model = build_classifier(mcfg["arch"], num_classes, bool(p.get("pretrained", True))).to(device)
    crit = nn.CrossEntropyLoss()
    opt = (torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=wd)
           if opt_name == "sgd"
           else torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd))
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1)) if sched_name == "cosine" else None
    scaler = make_scaler(device)
    trl, val = DataLoader(tr, batch_size=bs, shuffle=True), DataLoader(va, batch_size=bs)

    out_dir = Path(run_cfg["work_dir"]) / mcfg["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    best, history, bad = {"epoch": 0, "score": -1.0, "metrics": {}}, [], 0
    t0 = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        tot, n = 0.0, 0
        for x, y in trl:
            x, y = x.to(device), y.to(device)
            opt.zero_grad(set_to_none=True)
            ctx = torch.autocast(device_type="cuda") if scaler else nullcontext()
            with ctx:
                loss = crit(model(x), y)
            if scaler:
                scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
            else:
                loss.backward(); opt.step()
            tot += loss.item() * x.size(0); n += x.size(0)
        if sched:
            sched.step()
        m = eval_classification(model, val, device, num_classes)
        s = cls_score(m)
        history.append({"epoch": epoch, "train_loss": tot / max(n, 1),
                        **{f"val_{k}": v for k, v in m.items()}})
        log.info("[%s] ep %d/%d loss=%.4f acc=%.3f balacc=%.3f f1=%.3f auc=%s",
                 mcfg["name"], epoch, epochs, tot / max(n, 1), m["accuracy"],
                 m["balanced_accuracy"], m["f1_macro"],
                 f"{m['roc_auc']:.3f}" if m.get("roc_auc") is not None else "-")
        if s > best["score"] + 1e-4:
            best = {"epoch": epoch, "score": s, "metrics": m}
            torch.save(model.state_dict(), out_dir / "best.pt")
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                log.info("[%s] early stop", mcfg["name"])
                break
    if te is not None:
        model.load_state_dict(safe_load(out_dir / "best.pt", device))
        best["test_metrics"] = eval_classification(model, DataLoader(te, batch_size=bs), device, num_classes)
    (out_dir / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    return {"task": "classification", "arch": mcfg["arch"], "classes": classes, "best": best,
            "params_M": count_params(model) / 1e6, "train_time_s": time.time() - t0,
            "checkpoint": str(out_dir / "best.pt"), "history": str(out_dir / "history.json")}


# ----------------------------- сегментация -----------------------------------
class SegDataset(Dataset):
    def __init__(self, img_dir, mask_dir, img_size: int, train: bool = True):
        self.img_dir, self.mask_dir = Path(img_dir), Path(mask_dir)
        self.img_size, self.train = img_size, train
        self.mask_index = {}
        if self.mask_dir.exists():
            self.mask_index = {Path(f).stem: f for f in os.listdir(self.mask_dir)}
        self.files = [f for f in sorted(os.listdir(self.img_dir))
                      if f.lower().endswith(tuple(IMG_EXT)) and Path(f).stem in self.mask_index] if self.img_dir.exists() else []

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, idx: int):
        name = self.files[idx]
        img = Image.open(self.img_dir / name).convert("RGB")
        mask = Image.open(self.mask_dir / self.mask_index[Path(name).stem]).convert("L")
        img = img.resize((self.img_size, self.img_size))
        mask = mask.resize((self.img_size, self.img_size), Image.NEAREST)
        if self.train and random.random() < 0.5:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            mask = mask.transpose(Image.FLIP_LEFT_RIGHT)
        x = transforms.Normalize(MEAN, STD)(transforms.ToTensor()(img))
        y = (transforms.ToTensor()(mask) > 0.5).float()
        return x, y


@torch.no_grad()
def eval_segmentation(model, loader, device, thresh: float = 0.5) -> dict:
    model.eval()
    dice_sum, iou_sum, n = 0.0, 0.0, 0
    eps = 1e-7
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        pred = (torch.sigmoid(model(x)) > thresh).float()
        inter = (pred * y).sum(dim=(1, 2, 3))
        area = pred.sum(dim=(1, 2, 3)) + y.sum(dim=(1, 2, 3))
        dice_sum += ((2 * inter + eps) / (area + eps)).sum().item()
        iou_sum += ((inter + eps) / (area - inter + eps)).sum().item()
        n += x.size(0)
    return {"dice": dice_sum / max(n, 1), "iou": iou_sum / max(n, 1)}


def train_segmentation(mcfg: dict, data_cfg: dict, run_cfg: dict, device) -> dict:
    try:
        import segmentation_models_pytorch as smp
    except ImportError as e:  # noqa: BLE001
        raise RuntimeError("pip install segmentation-models-pytorch") from e
    p = mcfg.get("params", {})
    img_size = int(p.get("img_size", data_cfg.get("img_size", 256)))
    epochs, bs = int(p.get("epochs", 20)), int(p.get("batch_size", 16))
    lr, patience = float(p.get("lr", 1e-3)), int(p.get("patience", 5))

    root = Path(data_cfg["root"])
    im_sub, mk_sub = data_cfg.get("images_subdir", "images"), data_cfg.get("masks_subdir", "masks")
    tr_dir, va_dir = root / data_cfg.get("train_dir", "train"), root / data_cfg.get("val_dir", "val")
    tr = SegDataset(tr_dir / im_sub, tr_dir / mk_sub, img_size, True)
    va = SegDataset(va_dir / im_sub, va_dir / mk_sub, img_size, False)
    if len(tr) == 0:
        raise FileNotFoundError(f"Не найдено пар изображение+маска в {tr_dir} ({im_sub}/, {mk_sub}/)")

    model = smp.create_model(mcfg.get("arch", "unet"), encoder_name=p.get("encoder", "resnet34"),
                             in_channels=3, classes=1,
                             encoder_weights="imagenet" if p.get("pretrained", True) else None).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=float(p.get("weight_decay", 1e-4)))
    dice_loss, bce_loss = smp.losses.DiceLoss(mode="binary"), nn.BCEWithLogitsLoss()
    trl, val = DataLoader(tr, batch_size=bs, shuffle=True), DataLoader(va, batch_size=bs)

    out_dir = Path(run_cfg["work_dir"]) / mcfg["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    best, history, bad = {"epoch": 0, "score": -1.0, "metrics": {}}, [], 0
    t0 = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        tot, n = 0.0, 0
        for x, y in trl:
            x, y = x.to(device), y.to(device)
            opt.zero_grad(set_to_none=True)
            logits = model(x)
            loss = dice_loss(logits, y) + bce_loss(logits, y)
            loss.backward(); opt.step()
            tot += loss.item() * x.size(0); n += x.size(0)
        m = eval_segmentation(model, val, device)
        s = 0.6 * m["dice"] + 0.4 * m["iou"]
        history.append({"epoch": epoch, "train_loss": tot / max(n, 1),
                        **{f"val_{k}": v for k, v in m.items()}})
        log.info("[%s] ep %d/%d loss=%.4f dice=%.3f iou=%.3f",
                 mcfg["name"], epoch, epochs, tot / max(n, 1), m["dice"], m["iou"])
        if s > best["score"] + 1e-4:
            best = {"epoch": epoch, "score": s, "metrics": m}
            torch.save(model.state_dict(), out_dir / "best.pt")
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                log.info("[%s] early stop", mcfg["name"])
                break
    (out_dir / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    return {"task": "segmentation", "arch": mcfg.get("arch", "unet"), "best": best,
            "params_M": count_params(model) / 1e6, "train_time_s": time.time() - t0,
            "checkpoint": str(out_dir / "best.pt")}


# --------------------------- YOLO (det+seg) ----------------------------------
def train_yolo(mcfg: dict, data_cfg: dict, run_cfg: dict, device) -> dict:
    try:
        from ultralytics import YOLO
    except ImportError as e:  # noqa: BLE001
        raise RuntimeError("pip install ultralytics") from e
    p = mcfg.get("params", {})
    data_yaml = p.get("data") or data_cfg.get("yolo_data_yaml")
    if not data_yaml:
        raise ValueError("Укажите params.data или data.yolo_data_yaml (путь к data.yaml COCO/YOLO)")
    t0 = time.time()
    model = YOLO(mcfg.get("arch", "yolov8n-seg.pt"))
    results = model.train(data=data_yaml,
                          epochs=int(p.get("epochs", 30)),
                          imgsz=int(p.get("imgsz", 640)),
                          batch=int(p.get("batch", 16)),
                          device=0 if device.type == "cuda" else "cpu",
                          project=str(Path(run_cfg["work_dir"]) / mcfg["name"]),
                          name="train", exist_ok=True, verbose=False)
    metrics = {}
    try:
        rd = results.results_dict or {}
        for k in ("metrics/mAP50(B)", "metrics/mAP50-95(B)", "metrics/mAP50(M)",
                  "metrics/precision(B)", "metrics/recall(B)"):
            if k in rd:
                metrics[k.replace("metrics/", "")] = float(rd[k])
    except Exception as e:  # noqa: BLE001
        log.warning("Не удалось прочитать метрики YOLO: %s", e)
    map_b = metrics.get("mAP50(B)", 0.0)
    map_m = metrics.get("mAP50(M)", map_b)
    ckpt = Path(run_cfg["work_dir"]) / mcfg["name"] / "train" / "weights" / "best.pt"
    return {"task": mcfg.get("type", "yolo_seg"), "arch": mcfg.get("arch"), "metrics": metrics,
            "score": 0.5 * map_b + 0.5 * map_m, "train_time_s": time.time() - t0,
            "checkpoint": str(ckpt)}


# ------------------------------- отчёт ---------------------------------------
def score_of(res: dict) -> float:
    if res.get("error"):
        return 0.0
    t = res.get("task")
    if t == "classification":
        return float(res.get("best", {}).get("score", 0.0))
    if t == "segmentation":
        m = res.get("best", {}).get("metrics", {})
        return 0.6 * m.get("dice", 0.0) + 0.4 * m.get("iou", 0.0)
    return float(res.get("score", 0.0))


def fmt_metrics(res: dict) -> str:
    if res.get("error"):
        return f"ERROR: {res['error'][:60]}"
    t = res.get("task")
    if t == "classification":
        m = res["best"]["metrics"]
        out = (f"acc={m['accuracy']:.3f} balacc={m['balanced_accuracy']:.3f} f1={m['f1_macro']:.3f}")
        if m.get("roc_auc") is not None:
            out += f" auc={m['roc_auc']:.3f}"
        return out
    if t == "segmentation":
        m = res["best"]["metrics"]
        return f"Dice={m['dice']:.3f} IoU={m['iou']:.3f}"
    if str(t).startswith("yolo"):
        m = res.get("metrics", {})
        return f"mAP50(B)={m.get('mAP50(B)', 0):.3f} mAP50(M)={m.get('mAP50(M)', 0):.3f}"
    return "-"


def make_report(results: list, cfg: dict, work_dir: str) -> Path:
    wd = Path(work_dir)
    wd.mkdir(parents=True, exist_ok=True)
    ok = [r for r in results if not r.get("error")]
    ranked = sorted(ok, key=lambda r: (-score_of(r), r.get("train_time_s", 1e18)))

    L = ["# Отчёт автообучения",
         f"\nСформирован: {datetime.now():%Y-%m-%d %H:%M:%S}",
         f"\nДанные: `{cfg['data'].get('root')}` · моделей обучено: {len(results)}\n",
         "## Сводная таблица",
         "",
         "| № | Модель | Задача | Архитектура | Ключевые метрики | Score | Время, с | Парам., М | Статус |",
         "|---|--------|--------|-------------|------------------|-------|----------|-----------|--------|"]
    for i, r in enumerate(results, 1):
        pm = f"{r['params_M']:.1f}" if r.get("params_M") else "-"
        L.append(f"| {i} | {r['name']} | {r.get('task', '-')} | {r.get('arch', '-')} | {fmt_metrics(r)} | "
                 f"{score_of(r):.3f} | {r.get('train_time_s', 0):.0f} | {pm} | {'OK' if not r.get('error') else 'ERROR'} |")

    L.append("\n## Рекомендация по выбору модели")
    if not ranked:
        L.append("\nНи одна модель не обучилась — проверьте пути к данным и параметры конфига.")
    else:
        best = ranked[0]
        L.append(f"\n**Лучшая по качеству: `{best['name']}`** (задача: {best['task']}, score = {score_of(best):.3f}).")
        L.append(f"Чекпоинт: `{best.get('checkpoint', '-')}`.")
        if len(ranked) > 1:
            alt = ranked[1]
            L.append(f"Вторая: `{alt['name']}` (score = {score_of(alt):.3f}, время {alt.get('train_time_s', 0):.0f} с).")
        fast = min(ranked, key=lambda r: r.get("train_time_s", 1e18))
        if fast is not best and score_of(best) - score_of(fast) <= 0.02:
            L.append(f"\nЕсли важна скорость: `{fast['name']}` — отставание по качеству всего "
                     f"{score_of(best) - score_of(fast):.3f}, а обучается/работает быстрее.")
        L.append("\n**Правила выбора:**")
        L.append("- продакшен/быстрый инференс — YOLO-модели (детекция+сегментация в одной сети);")
        L.append("- максимальное качество сегментации — smp U-Net/Unet++ (при необходимости + MedSAM);")
        L.append("- классификация — лучший классификатор из таблицы; возможен ансамбль с вице-лидером.")

    (wd / "report.md").write_text("\n".join(L), encoding="utf-8")
    payload = {"generated": datetime.now().isoformat(), "config": cfg, "results": results,
               "ranking": [r["name"] for r in ranked]}
    (wd / "report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    log.info("Отчёт: %s", wd / "report.md")
    return wd / "report.md"


# -------------------------------- main ---------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Автообучение моделей по конфигу")
    ap.add_argument("--config", required=True)
    ap.add_argument("--models", nargs="*", default=None, help="обучить только эти модели")
    ap.add_argument("--device", default=None, help="auto | cuda | cpu")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    setup_logging()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    run_cfg = cfg.get("run", {})
    run_cfg.setdefault("work_dir", "runs/exp")
    device = pick_device(args.device or run_cfg.get("device", "auto"))
    set_seed(int(run_cfg.get("seed", 42)))
    log.info("Устройство: %s", device)

    models = [m for m in cfg.get("models", []) if m.get("enabled", True)]
    if args.models:
        models = [m for m in models if m.get("name") in args.models]
    if args.dry_run:
        print(json.dumps({"device": str(device),
                          "models": [m["name"] for m in models]}, ensure_ascii=False, indent=2))
        return

    results = []
    for mcfg in models:
        name = mcfg.get("name", mcfg.get("arch", "model"))
        log.info("=== Обучение: %s (тип %s, арх. %s) ===", name, mcfg.get("type"), mcfg.get("arch"))
        t0 = time.time()
        try:
            t = str(mcfg.get("type", ""))
            if t == "classification":
                res = train_classification(mcfg, cfg["data"], run_cfg, device)
            elif t == "segmentation":
                res = train_segmentation(mcfg, cfg["data"], run_cfg, device)
            elif t.startswith("yolo"):
                res = train_yolo(mcfg, cfg["data"], run_cfg, device)
            else:
                raise ValueError(f"Неизвестный тип модели: {mcfg.get('type')}")
            res.update({"name": name, "config": mcfg})
            results.append(res)
        except Exception as e:  # noqa: BLE001
            log.exception("Ошибка обучения %s", name)
            results.append({"name": name, "arch": mcfg.get("arch"), "task": mcfg.get("type"),
                            "error": str(e), "train_time_s": time.time() - t0})
        if device.type == "cuda":
            torch.cuda.empty_cache()

    report_path = make_report(results, cfg, run_cfg["work_dir"])
    print(f"\nГотово. Отчёт: {report_path}")


if __name__ == "__main__":
    main()
```

# 6. Запуск (сквозной пример)

```bash
pip install -r requirements.txt

# 1) скачать данные
python app1_downloader.py --config configs/download.yaml

# 2) превратить BloodMNIST в папочную структуру
python tools/npz2folders.py --npz data/bloodmnist/bloodmnist.npz --out data/bloodmnist

# 3) автономное обучение + отчёт
python app2_autotrain.py --config configs/train.yaml
# или выборочно:
python app2_autotrain.py --config configs/train.yaml --models efficientnet_b0 --device cuda
```

**Что получится в `runs/blood_exp1/`:** `report.md` (сводная таблица + рекомендация лучшей модели с обоснованием), `report.json`, чекпоинты `best.pt` и `history.json` по каждой модели.

**Примечания:**
- Под новые данные достаточно править конфиг: в `download.yaml` добавить ссылки и пути, в `train.yaml` — модели/гиперпараметры. Ошибки одной модели не прерывают обучение остальных — они попадают в отчёт со статусом `ERROR`.
- Для сегментации структура данных должна быть `<root>/<train_dir>/images` и `<root>/<train_dir>/masks` (имена файлов совпадают); для YOLO — стандартный `data.yaml` (COCO/YOLO-формат).
- Если нужны готовые конфиги под конкретные датасеты из прошлых сообщений (C-NMC, TN3K, TCGA-THCA) — подготовлю их вместе со скриптами приведения к нужной структуре папок.

 Для такой сложной мультимодальной задачи (медицинская визуализация + CV + генерация данных + AutoML) одной LLM недостаточно — нужна **многоагентная система**. Но если выделять ключевые роли, вот оптимальная конфигурация:

## 🏆 Основная LLM: Claude 4 Sonnet (или Claude 3.5 Sonnet)

**Почему именно она:**
- **Лучший кодинг** среди всех LLM на сложных CV-проектах (бенчмарки SWE-Bench, HumanEval)
- **Отличное понимание медицинского контекста** — корректно работает с терминологией онкологии, гистологии, радиологии
- **Tool use** — может последовательно запускать код, анализировать метрики (Dice, IoU, AUC), корректировать пайплайны
- **Большой контекст** (200K токенов) — позволяет держать весь проект (код + конфиги + логи экспериментов) в одной сессии

**Альтернатива:** GPT-4o / o3 — если критичен reasoning при выборе архитектур нейросетей, но дороже и медленнее.

---

## 🧠 Архитектура приложения (что будет делать LLM)

LLM выступает **оркестратором**, который пишет и управляет кодом для:

| Компонент | Модели/фреймворки (выбирает LLM) |
|-----------|----------------------------------|
| **Предобработка** | OpenCV, Albumentations, CLAHE, нормализация стейнинга |
| **Классификация** | EfficientNet-B7, ConvNeXt, Vision Transformer (ViT) |
| **Сегментация** | nnU-Net (золотой стандарт медицины), SAM-Med2D, SegFormer |
| **Текстовое описание** | LLaVA-Med, RadFM, или fine-tuned CLIP + GPT-4 |
| **Генерация синтетики** | Stable Diffusion + ControlNet, DDPM, StyleGAN3 |
| **Деградация изображений** | Albumentations (шум, blur, JPEG-artifacts), domain randomization |
| **AutoML/выбор модели** | Optuna, Ray Tune, WandB Sweeps — LLM пишет конфиги и анализирует результаты |

---

## 🛠️ Рекомендуемый стек (что реально использовать)

```python
# CV + Medical Imaging
torchvision, timm, segmentation-models-pytorch, monai, albumentations

# Сегментация
nnunet, sam-med2d, transformers (SegFormer)

# Генерация
diffusers, controlnet-aux, accelerate

# AutoML + эксперименты
optuna, ray[tune], wandb, mlflow

# Агентский фреймворк (LLM оркеструет)
langgraph, autogen, или кастомный ReAct-агент
```

---

## ⚡ Практический совет: не одна модель, а система

Для вашей задачи лучше построить **3 агента**:

1. **Архитектор** (Claude 4 Sonnet) — проектирует пайплайн, выбирает модели
2. **Инженер** (Claude 3.5 Sonnet / DeepSeek-V3) — пишет код экспериментов
3. **Аналитик** (Claude 4 Sonnet) — сравнивает метрики, выбирает лучшую модель

**Open-source альтернатива** (если нужно локально): 
- **DeepSeek-V3** (671B MoE) — близок к Claude по кодингу
- **Qwen3-235B** — сильный в мультимодальных задачах
- **Llama 3.3 70B** — для локального развёртывания, но потребует больше prompt engineering

---

## 🎯 Итоговая рекомендация

| Бюджет | Рекомендация |
|--------|-------------|
| **Без ограничений** | Claude 4 Sonnet + GPT-4o (для сложного reasoning) |
| **Средний** | Claude 3.5 Sonnet — оптимальное соотношение цена/качество |
| **Локально / open-source** | DeepSeek-V3 + Qwen2.5-VL (для vision-задач) |

**Ключевой момент:** LLM не заменит специализированные медицинские модели (nnU-Net, SAM-Med2D), но идеально справится с **автоматизацией их подбора, интеграции и сравнения** — именно это вам и нужно.


Как реализовать пайплайны с высоким качеством классификации, сегментациии описания?
Высокое качество медицинской сегментации — результат не одной «волшебной» архитектуры, а системы приёмов на всех этапах: от данных до постобработки. Разберу по слоям.

## 1. Архитектурные решения

**U-Net как базовая индуктивная схема.** Почти вся медицинская сегментация строится на энкодер–декодерной структуре с *пропускными соединениями* (skip connections):
- энкодер сжимает изображение до семантических признаков («что это»);
- декодер восстанавливает пространственное разрешение («где именно»);
- пропуски передают мелкие детали ранних слоёв, которые иначе теряются при даунсэмплинге.

Именно сохранение деталей через пропуски критично для тонких структур (сосуды, мембраны клеток, границы опухолей).

**Развития идеи:**
- **U-Net++ / Dense U-Net** — плотные вложенные пропуски: лучшее слияние признаков разных уровней;
- **Attention U-Net** — механизмы внимания гасят шумные области в пропусках;
- **TransUNet, Swin-UNETR, UNETR** — гибриды свёрток и трансформеров: свёртки дают локальную точность, трансформеры — глобальный контекст (важно для крупных органов и отдалённых метастазов);
- **глубокое наблюдение (deep supervision)** — вспомогательные выходы на разных уровнях декодера стабилизируют обучение.

## 2. Функции потерь под специфику медицины

Главная проблема — **сильный дисбаланс**: опухоль может занимать <1% вокселей. Обычный кросс-энтропи «решает» задачу, предсказав фон везде. Поэтому используют:

| Потеря | Что решает |
|---|---|
| **Dice loss** | оптимизирует مباشرة меру перекрытия; устойчива к дисбалансу |
| **Focal loss** | усиливает вес трудных пикселей/вокселей |
| **Кросс-энтропия + Dice** | стандартная комбинация: стабильные градиенты + качество границ |
| **Tversky / Focal Tversky** | управление компромиссом ложных срабатываний/пропусков |
| **Boundary / Hausdorff loss** | штраф за неточные границы — критично для хирургического планирования |
| **Топологические потери** | сохранение связности структур (сосуды не должны «рваться») |

## 3. Работа с данными — часто главный источник качества

**Аугментации**, имитирующие реальную вариативность снимков:
- геометрические: повороты, отражения, эластичные деформации (особенно эффективны в гистологии и УЗИ);
- интенсивностные: шум, размытие, гамма-коррекция, имитация разных аппаратов и протоколов;
- доменные: для МРТ — имитация разных полей и катушек, для КТ — вариации окон.

**Стратегии выборки патчей** (объёмные снимки не влезают в память):
- обучение на патчах с *акцентом на информативные области* (например, 33–67% патчей принудительно содержат передний план);
- инференс скользящим окном с перекрытием и усреднением предсказаний.

**Качество разметки:** согласование нескольких экспертов (консенсусные маски), учёт межэкспертной вариабельности, модели, устойчивые к шумным меткам; при дефиците разметки — слабая и самообучение (см. ниже).

## 4. Предобработка, стандартизированное в медицинской области

Для КТ/МРТ это часто важнее архитектуры:
- приведение к единому физическому разрешению (ресемплинг в мм/воксель);
- нормализация интенсивностей (для КТ — клиппинг по HU-окну органа; для МРТ — z-скор по объёму, коррекция неоднородности поля, например, N4);
- единый размер/интервал патчей, батч-нормализация входов.

## 5. Инженерные «автопилоты»: почему выигрывает nnU-Net

Феномен последних лет — **nnU-Net** («no-new U-Net»), который регулярно побеждает в челленджах без новой архитектуры. Его суть: правила, автоматически настраивающие весь пайплайн под конкретный датасет:
1. анализ отпечатка данных (разрешение, модальность, число классов);
2. автоматический выбор предобработки, размера патча, батча, архитектуры (2D/3D/каскад);
3. стандартизированное обучение (аугментации, потери, ранняя остановка);
4. автоматический отбор постобработки и ансамблирование по кросс-валидации.

Вывод сообщества: **воспроизводимая инженерия и корректная вализация дают больше, чем новая модель**.

## 6. Перенос знаний и фундаментальные модели

- **Предобучение**: энкодеры, обученные на ImageNet или на больших медицинских корпусах, ускоряют сходимость и повышают качество на малых данных;
- **самодистилляция / самообучение** (MAE, DINO-подходы) на неразмеченных снимках;
- **фундаментальные модели сегментации**: **SAM/MedSAM/SAM 2** — предобучены на миллионах масок и сегментируют новые объекты «из коробки» по промпту (бокс/точка/маска); в медицине их дообучают на целевом органе. Это меняет парадигму: вместо обучения с нуля — интерактивная доводка;
- в гистологии: фундаментальные модели патологии (UNI, CONCH, H-Optimus-0) как экстракторы признаков + слабое обучение на уровне целых слайдов (MIL), когда пиксельных масок нет вообще.

## 7. Постобработка и ограничения

- удаление мелких ложных компонентов, заполнение дырок, принудительная связность;
- анатомические ограничения (правила соседства органов, атласы);
- **тест-аугментация (TTA)**: усреднение предсказаний по отражениям входа (+1–3% Dice).

## 8. Как это проверяют (чтобы качество было настоящим)

- метрики: **Dice/IoU** (перекрытие), **Hausdorff 95%** и **ASSD** (границы — именно они важны клиницистам);
- строгая кросс-валидация по *пациентам* (не по срезам — иначе утечка данных), внешний тестовый набор из другого центра/аппарата;
- сравнение с межэкспертной вариативностью: если модель стабильно попадает в «диапазон согласия» экспертов, это практический потолок качества.

## Итог

Качество складывается так: **архитектура с сохранением деталей (U-Net-семейство/гибриды) + потери против дисбаланса (Dice-комбинации) + агрессивные доменные аугментации + стандартизированное предобучение и валидация (подход nnU-Net) + предобучение/фундаментальные модели + постобработка**. Отдельные новинки архитектур обычно дают проценты; основной выигрыш дают данные, предобработка и корректный пайплайн обучения.

Если интересно, могу показать конкретный минимальный пайплайн на MONAI/`segmentation_models_pytorch` (предобработка → Dice+CE → обучение → метрики) на примере любого из датасетов, которые обсуждали раньше.


Нужны ссылка на датасеты размеченных сканов крови с раковыми клетками с фотографиями и метаданными (сегментированное выделение раковых образований, текстовое описание раковых образований, объем, классы, ссылки на репозитории)

Определи, какую llm модель лучше использовать для написания приложения, которое автономно подобрать модели для предобработки изображений и собрать несколько нейросетевых моделей на первично на скаченных медицинских данных (классифицирует фото, разметит сегменты области с раковыми объектами, даст текстовое описание выделенных сегментов), затем сможет сгенерировать правдоподобные данные (сформировать фото с и без раковых объектов, классифицирует фото, разметит сегменты области с раковыми объектами, даст текстовое описание выделенных сегментов), в том числе с деградированными изображениями для дополнительного обучения. По результату обучения предложит самую лучшую модель для работы.

# 1. Оценка моделей: топ-3 по связке «качество + скорость»

Для полного цикла «сегментация → выделение участков (детекция) → классификация → описание» в 2024–2026 наиболее перспективны:

| Модель | Качество | Скорость | Сегментация | Выделение участков | Классификация | Описание текстом |
|---|---|---|---|---|---|---|
| **Grounded SAM 2** (Grounding DINO 1.5 + SAM 2) | 9/10 (zero-shot) | 6/10 | ✅ по текстовому промпту («опухолевые клетки») | ✅ боксы | ⚠️ через внешний классификатор | ⚠️ через VLM |
| **MedSAM / EfficientViT-SAM** | 8–9/10 (мед. домен) | 6–8/10 | ✅ лучший мед.-сегмент | ⚠️ по промптам/боксам | — | — |
| **YOLO11/YOLOv8-seg** | 7–8/10 (после дообучения) | 10/10 (реалтайм) | ✅ маски | ✅ боксы | ✅ встроенная | — |

**Выводы:**
- **Максимальное качество «из коробки»** (без обучения): Grounded SAM 2 — находит и вырезает раковые структуры по текстовому запросу; описание добавляется через VLM (LLaVA-Med, Qwen2.5-VL, PathChat для гистологии).
- **Максимальное качество медицинской сегментации с дообучением**: MedSAM (и его быстрые варианты EfficientViT-SAM/MobileSAM); классическая альтернатива — U-Net/Unet++ из `segmentation_models_pytorch`, который обучается быстрее и проще — он и взят в приложение 2.
- **Лучшее соотношение скорость/качество для продакшена**: YOLO-seg — одна модель вместо трёх, обучение за минуты/часы, инференс реалтайм.
- Для **классификации** гистологии отдельно сильны foundation-модели патологии (UNI, CONCH, H-Optimus-0) + MIL; для **описаний** — связка сегментатора с VLM.

Приложение 2 обучает именно «обучаемую тройку»: классификаторы (любые архитектуры, включая эффективные), U-Net-семейство для сегментации и YOLO для детекции+сегментации.

# 2. Структура проекта

```
cancer_cv/
├── requirements.txt
├── configs/
│   ├── download.yaml     # конфиг приложения 1
│   └── train.yaml        # конфиг приложения 2
├── app1_downloader.py
├── app2_autotrain.py
└── tools/
    └── npz2folders.py    # конвертер датасетов MedMNIST в папки
```

**requirements.txt**

```
requests>=2.31
PyYAML>=6.0
tqdm>=4.66
numpy>=1.24
Pillow>=10.0
torch>=2.1
torchvision>=0.16
scikit-learn>=1.3
timm>=0.9
segmentation-models-pytorch>=0.3.3
ultralytics>=8.2
```

# 3. Приложение 1 — загрузчик данных

**configs/download.yaml**

```yaml
settings:
  base_dir: ./data          # все пути ниже — относительно этой папки
  timeout: 120
  retries: 3
  verify_ssl: true
  headers:
    User-Agent: research-downloader/1.0

downloads:
  # --- файл (без распаковки) ---
  - name: bloodmnist            # контроль: нормальные клетки крови (8 классов)
    url: https://zenodo.org/records/10519652/files/bloodmnist.npz
    dest: bloodmnist/bloodmnist.npz   # путь к итоговому файлу
    kind: file
    overwrite: false
    # sha256: <хэш>             # необязательная проверка целостности

  # --- архив (скачать и распаковать) ---
  - name: tn3k_repo             # УЗИ щитовидной железы, маски узлов
    url: https://github.com/haifangong/TRFE-Net-for-thyroid-nodule-segmentation/archive/refs/heads/main.zip
    dest: tn3k
    kind: archive
    keep_archive: false

  # --- шаблон для своих ссылок ---
  # - name: my_dataset
  #   url: https://example.org/data.zip
  #   dest: my_dataset
  #   kind: archive            # archive | file
  #   sha256: null
  #   overwrite: false
```

> Для датасетов с Kaggle/HuggingFace прямые ссылки часто требуют авторизации: качайте их вручную (`kaggle datasets download ...`, `huggingface-cli download --repo-type dataset ...`) и кладите в `data/...` — приложение 2 работает уже с локальными папками. Загрузчик поддерживает любые прямые ссылки, включая токены через `headers`.

**app1_downloader.py**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приложение 1: загрузка датасетов по конфигу (скачивание, контроль сумм, распаковка)."""
from __future__ import annotations

import argparse
import hashlib
import logging
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
import yaml

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

log = logging.getLogger("downloader")


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO,
                        format="%(asctime)s | %(levelname)-7s | %(message)s",
                        datefmt="%H:%M:%S")


def human(n: float) -> str:
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"


def sha256_of(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def url_filename(url: str) -> str:
    name = Path(unquote(urlparse(url).path)).name
    return name or "download.bin"


def download_one(url: str, target: Path, session: requests.Session,
                 timeout: int, retries: int, resume: bool = True) -> None:
    """Скачивание с докачкой и ретраями."""
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".part")
    pos = tmp.stat().st_size if (resume and tmp.exists()) else 0

    attempt = 0
    while True:
        attempt += 1
        headers = {"Range": f"bytes={pos}-"} if pos else {}
        try:
            with session.get(url, headers=headers, stream=True, timeout=timeout) as r:
                if pos and r.status_code == 206:
                    mode = "ab"                      # сервер поддержит докачку
                else:
                    r.raise_for_status()
                    mode, pos = "wb", 0              # начинаем заново
                total = int(r.headers.get("Content-Length") or 0) + pos
                bar = tqdm(total=total or None, initial=pos, unit="B",
                           unit_scale=True, desc=target.name[:40], ncols=90) if tqdm else None
                with open(tmp, mode) as f:
                    for chunk in r.iter_content(1 << 20):
                        if not chunk:
                            continue
                        f.write(chunk)
                        if bar:
                            bar.update(len(chunk))
                if bar:
                    bar.close()
            tmp.rename(target)
            log.info("OK: %s (%s)", target, human(target.stat().st_size))
            return
        except Exception as e:  # noqa: BLE001
            if attempt > retries:
                raise RuntimeError(f"Не удалось скачать {url}: {e}") from e
            wait = 2 ** attempt
            log.warning("Ошибка (%s). Повтор %d/%d через %d с...", e, attempt, retries, wait)
            time.sleep(wait)


def safe_extract(archive: Path, dest_dir: Path) -> None:
    dest_dir = dest_dir.resolve()
    suf = "".join(archive.suffixes).lower()
    if suf.endswith(".zip"):
        import zipfile
        with zipfile.ZipFile(archive) as z:
            for m in z.infolist():                 # защита от zip-slip
                if not str((dest_dir / m.filename).resolve()).startswith(str(dest_dir)):
                    raise RuntimeError(f"Небезопасный путь в архиве: {m.filename}")
            z.extractall(dest_dir)
    elif suf.endswith((".tar.gz", ".tgz", ".tar")):
        import tarfile
        mode = "r:gz" if suf.endswith((".tar.gz", ".tgz")) else "r:"
        with tarfile.open(archive, mode) as t:
            for m in t.getmembers():
                if not str((dest_dir / m.name).resolve()).startswith(str(dest_dir)):
                    raise RuntimeError(f"Небезопасный путь в архиве: {m.name}")
            t.extractall(dest_dir)
    else:
        raise ValueError(f"Неподдерживаемый формат архива: {archive.name}")


def process_item(item: dict, settings: dict, session: requests.Session, force: bool) -> None:
    base = Path(settings.get("base_dir", "."))
    dest = (base / item["dest"]).resolve()
    kind = item.get("kind", "archive")
    url = item["url"]
    overwrite = bool(item.get("overwrite", False)) or force
    timeout = int(settings.get("timeout", 120))
    retries = int(settings.get("retries", 3))

    if kind == "file":
        if dest.exists() and not overwrite:
            log.info("SKIP %s: файл уже существует", item.get("name", url))
            return
        download_one(url, dest, session, timeout, retries)
        if item.get("sha256"):
            real = sha256_of(dest)
            if real.lower() != str(item["sha256"]).lower():
                raise RuntimeError(f"Контрольная сумма не совпала для {dest}")
        return

    # archive
    if dest.exists() and any(dest.iterdir()) and not overwrite:
        log.info("SKIP %s: папка уже существует (%s)", item.get("name", url), dest)
        return
    dest.mkdir(parents=True, exist_ok=True)
    archive = dest / url_filename(url)
    download_one(url, archive, session, timeout, retries)
    if item.get("sha256"):
        real = sha256_of(archive)
        if real.lower() != str(item["sha256"]).lower():
            raise RuntimeError(f"Контрольная сумма не совпала для {archive}")
    safe_extract(archive, dest)
    log.info("Распаковано в %s", dest)
    if not item.get("keep_archive", False):
        archive.unlink()


def main() -> None:
    ap = argparse.ArgumentParser(description="Загрузчик датасетов по конфигу")
    ap.add_argument("--config", required=True)
    ap.add_argument("--only", nargs="*", default=None, help="только эти имена")
    ap.add_argument("--force", action="store_true", help="перезакачать существующее")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    setup_logging(args.verbose)

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    settings = cfg.get("settings", {})
    session = requests.Session()
    session.headers.update(settings.get("headers") or {"User-Agent": "app1-downloader/1.0"})
    session.verify = bool(settings.get("verify_ssl", True))

    items = cfg.get("downloads", [])
    if args.only:
        items = [i for i in items if i.get("name") in args.only]

    ok, failed = [], []
    for item in items:
        name = item.get("name", item["url"])
        try:
            process_item(item, settings, session, args.force)
            ok.append(name)
        except Exception as e:  # noqa: BLE001
            log.error("FAILED %s: %s", name, e)
            failed.append((name, str(e)))

    log.info("Итог: %d успешно, %d с ошибками", len(ok), len(failed))
    for n, err in failed:
        log.error("  - %s: %s", n, err)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

# 4. Конвертер (для примера с BloodMNIST)

**tools/npz2folders.py**

```python
#!/usr/bin/env python3
"""MedMNIST npz -> папки train/val/test для приложения 2."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    data = np.load(args.npz)
    out = Path(args.out)
    for split in ("train", "val", "test"):
        x, y = data[f"{split}_images"], data[f"{split}_labels"]
        for i, (img, lab) in enumerate(zip(x, y)):
            cls = int(lab) if np.ndim(lab) == 0 else int(lab[0])
            d = out / split / f"class_{cls}"
            d.mkdir(parents=True, exist_ok=True)
            Image.fromarray(img).save(d / f"{i:06d}.png")
    print(f"Готово: {out}")


if __name__ == "__main__":
    main()
```

# 5. Приложение 2 — автообучение и отчёт

**configs/train.yaml**

```yaml
run:
  work_dir: runs/blood_exp1
  seed: 42
  device: auto            # auto | cuda | cpu

data:
  task: classification    # тип по умолчанию (у каждой модели свой)
  root: data/bloodmnist   # куда скачали/положили данные
  train_dir: train        # <root>/train/<класс>/*.png
  val_dir: val
  test_dir: test
  img_size: 64
  # для сегментации (тип модели: segmentation):
  images_subdir: images   # <root>/<train_dir>/images
  masks_subdir: masks     # <root>/<train_dir>/masks

models:
  # 1) быстрый бейзлайн классификации
  - name: resnet18_baseline
    type: classification
    arch: resnet18
    enabled: true
    params: {epochs: 8, batch_size: 64, lr: 3e-4, optimizer: adamw, scheduler: cosine, patience: 4, pretrained: true}

  # 2) более ёмкая архитектура
  - name: efficientnet_b0
    type: classification
    arch: efficientnet_b0
    enabled: true
    params: {epochs: 12, batch_size: 64, lr: 2e-4, weight_decay: 1e-4, patience: 5, pretrained: true}

  # 3) сегментация (нужны пары images+маски; по умолчанию выключено)
  - name: unet_r34_seg
    type: segmentation
    arch: unet
    enabled: false
    params: {encoder: resnet34, img_size: 256, epochs: 20, batch_size: 16, lr: 1e-3, patience: 5, pretrained: true}

  # 4) YOLO: детекция + сегментация (нужен data.yaml в формате COCO/YOLO)
  - name: yolo_seg
    type: yolo_seg
    arch: yolov8n-seg.pt
    enabled: false
    params: {data: data/my_coco/data.yaml, epochs: 30, imgsz: 640, batch: 16}
```

**app2_autotrain.py**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приложение 2: автономное обучение моделей из конфига, сравнение и отчёт."""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import yaml
from PIL import Image
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                             f1_score, roc_auc_score)
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms

log = logging.getLogger("autotrain")
IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
MEAN, STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)


# ----------------------------- утилиты ---------------------------------------
def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)-7s | %(message)s",
                        datefmt="%H:%M:%S")


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def pick_device(pref: str) -> torch.device:
    if pref == "cpu":
        return torch.device("cpu")
    if pref == "cuda" or (pref == "auto" and torch.cuda.is_available()):
        return torch.device("cuda")
    if pref == "auto" and getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def make_scaler(device: torch.device):
    if device.type != "cuda":
        return None
    try:
        return torch.amp.GradScaler("cuda")
    except Exception:  # старые версии torch
        try:
            return torch.cuda.amp.GradScaler()
        except Exception:
            return None


def safe_load(path: Path, device: torch.device):
    try:
        return torch.load(path, map_location=device, weights_only=True)
    except TypeError:
        return torch.load(path, map_location=device)


# --------------------------- классификация -----------------------------------
def cls_transforms(img_size: int, train: bool = True):
    if train:
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(0.2, 0.2, 0.2, 0.05),
            transforms.RandomAffine(degrees=10, translate=(0.05, 0.05)),
            transforms.ToTensor(),
            transforms.Normalize(MEAN, STD)])
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD)])


def patch_classifier_head(model: nn.Module, num_classes: int) -> None:
    for attr in ("fc", "classifier", "head"):
        if hasattr(model, attr):
            head = getattr(model, attr)
            if isinstance(head, nn.Linear):
                setattr(model, attr, nn.Linear(head.in_features, num_classes))
                return
            if isinstance(head, nn.Sequential):          # efficientnet и похожие
                for i, m in enumerate(head):
                    if isinstance(m, nn.Linear):
                        head[i] = nn.Linear(m.in_features, num_classes)
                        return
    raise RuntimeError(f"Не удалось заменить последний слой модели на {num_classes} классов")


def build_classifier(arch: str, num_classes: int, pretrained: bool = True) -> nn
# 1. Оценка моделей: топ-3 по связке «качество + скорость»

Для полного цикла «сегментация → выделение участков (детекция) → классификация → описание» в 2024–2026 наиболее перспективны:

| Модель | Качество | Скорость | Сегментация | Выделение участков | Классификация | Описание текстом |
|---|---|---|---|---|---|---|
| **Grounded SAM 2** (Grounding DINO 1.5 + SAM 2) | 9/10 (zero-shot) | 6/10 | ✅ по текстовому промпту («опухолевые клетки») | ✅ боксы | ⚠️ через внешний классификатор | ⚠️ через VLM |
| **MedSAM / EfficientViT-SAM** | 8–9/10 (мед. домен) | 6–8/10 | ✅ лучший мед.-сегмент | ⚠️ по промптам/боксам | — | — |
| **YOLO11/YOLOv8-seg** | 7–8/10 (после дообучения) | 10/10 (реалтайм) | ✅ маски | ✅ боксы | ✅ встроенная | — |

**Выводы:**
- **Максимальное качество «из коробки»** (без обучения): Grounded SAM 2 — находит и вырезает раковые структуры по текстовому запросу; описание добавляется через VLM (LLaVA-Med, Qwen2.5-VL, PathChat для гистологии).
- **Максимальное качество медицинской сегментации с дообучением**: MedSAM (и его быстрые варианты EfficientViT-SAM/MobileSAM); классическая альтернатива — U-Net/Unet++ из `segmentation_models_pytorch`, который обучается быстрее и проще — он и взят в приложение 2.
- **Лучшее соотношение скорость/качество для продакшена**: YOLO-seg — одна модель вместо трёх, обучение за минуты/часы, инференс реалтайм.
- Для **классификации** гистологии отдельно сильны foundation-модели патологии (UNI, CONCH, H-Optimus-0) + MIL; для **описаний** — связка сегментатора с VLM.

Приложение 2 обучает именно «обучаемую тройку»: классификаторы (любые архитектуры, включая эффективные), U-Net-семейство для сегментации и YOLO для детекции+сегментации.

# 2. Структура проекта

```
cancer_cv/
├── requirements.txt
├── configs/
│   ├── download.yaml     # конфиг приложения 1
│   └── train.yaml        # конфиг приложения 2
├── app1_downloader.py
├── app2_autotrain.py
└── tools/
    └── npz2folders.py    # конвертер датасетов MedMNIST в папки
```

**requirements.txt**

```
requests>=2.31
PyYAML>=6.0
tqdm>=4.66
numpy>=1.24
Pillow>=10.0
torch>=2.1
torchvision>=0.16
scikit-learn>=1.3
timm>=0.9
segmentation-models-pytorch>=0.3.3
ultralytics>=8.2
```

# 3. Приложение 1 — загрузчик данных

**configs/download.yaml**

```yaml
settings:
  base_dir: ./data          # все пути ниже — относительно этой папки
  timeout: 120
  retries: 3
  verify_ssl: true
  headers:
    User-Agent: research-downloader/1.0

downloads:
  # --- файл (без распаковки) ---
  - name: bloodmnist            # контроль: нормальные клетки крови (8 классов)
    url: https://zenodo.org/records/10519652/files/bloodmnist.npz
    dest: bloodmnist/bloodmnist.npz   # путь к итоговому файлу
    kind: file
    overwrite: false
    # sha256: <хэш>             # необязательная проверка целостности

  # --- архив (скачать и распаковать) ---
  - name: tn3k_repo             # УЗИ щитовидной железы, маски узлов
    url: https://github.com/haifangong/TRFE-Net-for-thyroid-nodule-segmentation/archive/refs/heads/main.zip
    dest: tn3k
    kind: archive
    keep_archive: false

  # --- шаблон для своих ссылок ---
  # - name: my_dataset
  #   url: https://example.org/data.zip
  #   dest: my_dataset
  #   kind: archive            # archive | file
  #   sha256: null
  #   overwrite: false
```

> Для датасетов с Kaggle/HuggingFace прямые ссылки часто требуют авторизации: качайте их вручную (`kaggle datasets download ...`, `huggingface-cli download --repo-type dataset ...`) и кладите в `data/...` — приложение 2 работает уже с локальными папками. Загрузчик поддерживает любые прямые ссылки, включая токены через `headers`.

**app1_downloader.py**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приложение 1: загрузка датасетов по конфигу (скачивание, контроль сумм, распаковка)."""
from __future__ import annotations

import argparse
import hashlib
import logging
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
import yaml

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

log = logging.getLogger("downloader")


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO,
                        format="%(asctime)s | %(levelname)-7s | %(message)s",
                        datefmt="%H:%M:%S")


def human(n: float) -> str:
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"


def sha256_of(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def url_filename(url: str) -> str:
    name = Path(unquote(urlparse(url).path)).name
    return name or "download.bin"


def download_one(url: str, target: Path, session: requests.Session,
                 timeout: int, retries: int, resume: bool = True) -> None:
    """Скачивание с докачкой и ретраями."""
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".part")
    pos = tmp.stat().st_size if (resume and tmp.exists()) else 0

    attempt = 0
    while True:
        attempt += 1
        headers = {"Range": f"bytes={pos}-"} if pos else {}
        try:
            with session.get(url, headers=headers, stream=True, timeout=timeout) as r:
                if pos and r.status_code == 206:
                    mode = "ab"                      # сервер поддержит докачку
                else:
                    r.raise_for_status()
                    mode, pos = "wb", 0              # начинаем заново
                total = int(r.headers.get("Content-Length") or 0) + pos
                bar = tqdm(total=total or None, initial=pos, unit="B",
                           unit_scale=True, desc=target.name[:40], ncols=90) if tqdm else None
                with open(tmp, mode) as f:
                    for chunk in r.iter_content(1 << 20):
                        if not chunk:
                            continue
                        f.write(chunk)
                        if bar:
                            bar.update(len(chunk))
                if bar:
                    bar.close()
            tmp.rename(target)
            log.info("OK: %s (%s)", target, human(target.stat().st_size))
            return
        except Exception as e:  # noqa: BLE001
            if attempt > retries:
                raise RuntimeError(f"Не удалось скачать {url}: {e}") from e
            wait = 2 ** attempt
            log.warning("Ошибка (%s). Повтор %d/%d через %d с...", e, attempt, retries, wait)
            time.sleep(wait)


def safe_extract(archive: Path, dest_dir: Path) -> None:
    dest_dir = dest_dir.resolve()
    suf = "".join(archive.suffixes).lower()
    if suf.endswith(".zip"):
        import zipfile
        with zipfile.ZipFile(archive) as z:
            for m in z.infolist():                 # защита от zip-slip
                if not str((dest_dir / m.filename).resolve()).startswith(str(dest_dir)):
                    raise RuntimeError(f"Небезопасный путь в архиве: {m.filename}")
            z.extractall(dest_dir)
    elif suf.endswith((".tar.gz", ".tgz", ".tar")):
        import tarfile
        mode = "r:gz" if suf.endswith((".tar.gz", ".tgz")) else "r:"
        with tarfile.open(archive, mode) as t:
            for m in t.getmembers():
                if not str((dest_dir / m.name).resolve()).startswith(str(dest_dir)):
                    raise RuntimeError(f"Небезопасный путь в архиве: {m.name}")
            t.extractall(dest_dir)
    else:
        raise ValueError(f"Неподдерживаемый формат архива: {archive.name}")


def process_item(item: dict, settings: dict, session: requests.Session, force: bool) -> None:
    base = Path(settings.get("base_dir", "."))
    dest = (base / item["dest"]).resolve()
    kind = item.get("kind", "archive")
    url = item["url"]
    overwrite = bool(item.get("overwrite", False)) or force
    timeout = int(settings.get("timeout", 120))
    retries = int(settings.get("retries", 3))

    if kind == "file":
        if dest.exists() and not overwrite:
            log.info("SKIP %s: файл уже существует", item.get("name", url))
            return
        download_one(url, dest, session, timeout, retries)
        if item.get("sha256"):
            real = sha256_of(dest)
            if real.lower() != str(item["sha256"]).lower():
                raise RuntimeError(f"Контрольная сумма не совпала для {dest}")
        return

    # archive
    if dest.exists() and any(dest.iterdir()) and not overwrite:
        log.info("SKIP %s: папка уже существует (%s)", item.get("name", url), dest)
        return
    dest.mkdir(parents=True, exist_ok=True)
    archive = dest / url_filename(url)
    download_one(url, archive, session, timeout, retries)
    if item.get("sha256"):
        real = sha256_of(archive)
        if real.lower() != str(item["sha256"]).lower():
            raise RuntimeError(f"Контрольная сумма не совпала для {archive}")
    safe_extract(archive, dest)
    log.info("Распаковано в %s", dest)
    if not item.get("keep_archive", False):
        archive.unlink()


def main() -> None:
    ap = argparse.ArgumentParser(description="Загрузчик датасетов по конфигу")
    ap.add_argument("--config", required=True)
    ap.add_argument("--only", nargs="*", default=None, help="только эти имена")
    ap.add_argument("--force", action="store_true", help="перезакачать существующее")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    setup_logging(args.verbose)

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    settings = cfg.get("settings", {})
    session = requests.Session()
    session.headers.update(settings.get("headers") or {"User-Agent": "app1-downloader/1.0"})
    session.verify = bool(settings.get("verify_ssl", True))

    items = cfg.get("downloads", [])
    if args.only:
        items = [i for i in items if i.get("name") in args.only]

    ok, failed = [], []
    for item in items:
        name = item.get("name", item["url"])
        try:
            process_item(item, settings, session, args.force)
            ok.append(name)
        except Exception as e:  # noqa: BLE001
            log.error("FAILED %s: %s", name, e)
            failed.append((name, str(e)))

    log.info("Итог: %d успешно, %d с ошибками", len(ok), len(failed))
    for n, err in failed:
        log.error("  - %s: %s", n, err)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

# 4. Конвертер (для примера с BloodMNIST)

**tools/npz2folders.py**

```python
#!/usr/bin/env python3
"""MedMNIST npz -> папки train/val/test для приложения 2."""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    data = np.load(args.npz)
    out = Path(args.out)
    for split in ("train", "val", "test"):
        x, y = data[f"{split}_images"], data[f"{split}_labels"]
        for i, (img, lab) in enumerate(zip(x, y)):
            cls = int(lab) if np.ndim(lab) == 0 else int(lab[0])
            d = out / split / f"class_{cls}"
            d.mkdir(parents=True, exist_ok=True)
            Image.fromarray(img).save(d / f"{i:06d}.png")
    print(f"Готово: {out}")


if __name__ == "__main__":
    main()
```

# 5. Приложение 2 — автообучение и отчёт

**configs/train.yaml**

```yaml
run:
  work_dir: runs/blood_exp1
  seed: 42
  device: auto            # auto | cuda | cpu

data:
  task: classification    # тип по умолчанию (у каждой модели свой)
  root: data/bloodmnist   # куда скачали/положили данные
  train_dir: train        # <root>/train/<класс>/*.png
  val_dir: val
  test_dir: test
  img_size: 64
  # для сегментации (тип модели: segmentation):
  images_subdir: images   # <root>/<train_dir>/images
  masks_subdir: masks     # <root>/<train_dir>/masks

models:
  # 1) быстрый бейзлайн классификации
  - name: resnet18_baseline
    type: classification
    arch: resnet18
    enabled: true
    params: {epochs: 8, batch_size: 64, lr: 3e-4, optimizer: adamw, scheduler: cosine, patience: 4, pretrained: true}

  # 2) более ёмкая архитектура
  - name: efficientnet_b0
    type: classification
    arch: efficientnet_b0
    enabled: true
    params: {epochs: 12, batch_size: 64, lr: 2e-4, weight_decay: 1e-4, patience: 5, pretrained: true}

  # 3) сегментация (нужны пары images+маски; по умолчанию выключено)
  - name: unet_r34_seg
    type: segmentation
    arch: unet
    enabled: false
    params: {encoder: resnet34, img_size: 256, epochs: 20, batch_size: 16, lr: 1e-3, patience: 5, pretrained: true}

  # 4) YOLO: детекция + сегментация (нужен data.yaml в формате COCO/YOLO)
  - name: yolo_seg
    type: yolo_seg
    arch: yolov8n-seg.pt
    enabled: false
    params: {data: data/my_coco/data.yaml, epochs: 30, imgsz: 640, batch: 16}
```

**app2_autotrain.py**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Приложение 2: автономное обучение моделей из конфига, сравнение и отчёт."""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import yaml
from PIL import Image
from sklearn.metrics import (accuracy_score, balanced_accuracy_score,
                             f1_score, roc_auc_score)
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms

log = logging.getLogger("autotrain")
IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
MEAN, STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)


# ----------------------------- утилиты ---------------------------------------
def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)-7s | %(message)s",
                        datefmt="%H:%M:%S")


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def pick_device(pref: str) -> torch.device:
    if pref == "cpu":
        return torch.device("cpu")
    if pref == "cuda" or (pref == "auto" and torch.cuda.is_available()):
        return torch.device("cuda")
    if pref == "auto" and getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def make_scaler(device: torch.device):
    if device.type != "cuda":
        return None
    try:
        return torch.amp.GradScaler("cuda")
    except Exception:  # старые версии torch
        try:
            return torch.cuda.amp.GradScaler()
        except Exception:
            return None


def safe_load(path: Path, device: torch.device):
    try:
        return torch.load(path, map_location=device, weights_only=True)
    except TypeError:
        return torch.load(path, map_location=device)


# --------------------------- классификация -----------------------------------
def cls_transforms(img_size: int, train: bool = True):
    if train:
        return transforms.Compose([
            transforms.Resize((img_size, img_size)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(0.2, 0.2, 0.2, 0.05),
            transforms.RandomAffine(degrees=10, translate=(0.05, 0.05)),
            transforms.ToTensor(),
            transforms.Normalize(MEAN, STD)])
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD)])


def patch_classifier_head(model: nn.Module, num_classes: int) -> None:
    for attr in ("fc", "classifier", "head"):
        if hasattr(model, attr):
            head = getattr(model, attr)
            if isinstance(head, nn.Linear):
                setattr(model, attr, nn.Linear(head.in_features, num_classes))
                return
            if isinstance(head, nn.Sequential):          # efficientnet и похожие
                for i, m in enumerate(head):
                    if isinstance(m, nn.Linear):
                        head[i] = nn.Linear(m.in_features, num_classes)
                        return
    raise RuntimeError(f"Не удалось заменить последний слой модели на {num_classes} классов")


def build_classifier(arch: str, num_classes: int, pretrained: bool = True) -> nn.Module:
    try:
        import timm
        model = timm.create_model(arch, pretrained=pretrained, num_classes=num_classes)
        log.info("Архитектура %s загружена через timm", arch)
        return model
    except Exception as e:  # noqa: BLE001
        log.warning("timm недоступен/модели %s нет (%s) — пробую torchvision", arch, e)
    import torchvision.models as tvm
    try:
        model = tvm.get_model(arch, weights="DEFAULT" if pretrained else None)
    except Exception as e2:  # noqa: BLE001
        raise RuntimeError(f"Не удалось создать архитектуру {arch}: {e2}") from e2
    patch_classifier_head(model, num_classes)
    return model


@torch.no_grad()
def eval_classification(model, loader, device, num_classes: int) -> dict:
    model.eval()
    ys, ps, probs = [], [], []
    for x, y in loader:
        logits = model(x.to(device))
        probs.append(torch.softmax(logits, 1).cpu().numpy())
        ps.append(logits.argmax(1).cpu().numpy())
        ys.append(y.numpy())
    y_true, y_pred, prob = np.concatenate(ys), np.concatenate(ps), np.concatenate(probs)
    m = {"accuracy": float(accuracy_score(y_true, y_pred)),
         "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
         "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0))}
    try:
        if num_classes == 2:
            m["roc_auc"] = float(roc_auc_score(y_true, prob[:, 1]))
        else:
            m["roc_auc"] = float(roc_auc_score(y_true, prob, multi_class="ovr"))
    except Exception:  # noqa: BLE001
        m["roc_auc"] = None
    return m


def cls_score(m: dict) -> float:
    parts = [m["balanced_accuracy"], m["f1_macro"]]
    if m.get("roc_auc") is not None:
        parts.append(m["roc_auc"])
    return float(np.mean(parts))


def train_classification(mcfg: dict, data_cfg: dict, run_cfg: dict, device) -> dict:
    p = mcfg.get("params", {})
    img_size = int(p.get("img_size", data_cfg.get("img_size", 224)))
    epochs = int(p.get("epochs", 10))
    bs = int(p.get("batch_size", 32))
    lr = float(p.get("lr", 1e-4))
    wd = float(p.get("weight_decay", 1e-4))
    patience = int(p.get("patience", max(3, epochs // 4)))
    opt_name = str(p.get("optimizer", "adamw")).lower()
    sched_name = str(p.get("scheduler", "cosine")).lower()

    root = Path(data_cfg["root"])
    tr_dir, va_dir = root / data_cfg.get("train_dir", "train"), root / data_cfg.get("val_dir", "val")
    if not tr_dir.exists():
        raise FileNotFoundError(f"Нет папки {tr_dir}. Ожидается: <root>/<train_dir>/<класс>/изображения")
    tr = datasets.ImageFolder(tr_dir, transform=cls_transforms(img_size, True))
    va = datasets.ImageFolder(va_dir, transform=cls_transforms(img_size, False))
    classes, num_classes = tr.classes, len(tr.classes)
    te_dir = root / data_cfg.get("test_dir", "test")
    te = datasets.ImageFolder(te_dir, transform=cls_transforms(img_size, False)) if te_dir.exists() else None

    model = build_classifier(mcfg["arch"], num_classes, bool(p.get("pretrained", True))).to(device)
    crit = nn.CrossEntropyLoss()
    opt = (torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=wd)
           if opt_name == "sgd"
           else torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd))
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1)) if sched_name == "cosine" else None
    scaler = make_scaler(device)
    trl, val = DataLoader(tr, batch_size=bs, shuffle=True), DataLoader(va, batch_size=bs)

    out_dir = Path(run_cfg["work_dir"]) / mcfg["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    best, history, bad = {"epoch": 0, "score": -1.0, "metrics": {}}, [], 0
    t0 = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        tot, n = 0.0, 0
        for x, y in trl:
            x, y = x.to(device), y.to(device)
            opt.zero_grad(set_to_none=True)
            ctx = torch.autocast(device_type="cuda") if scaler else nullcontext()
            with ctx:
                loss = crit(model(x), y)
            if scaler:
                scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
            else:
                loss.backward(); opt.step()
            tot += loss.item() * x.size(0); n += x.size(0)
        if sched:
            sched.step()
        m = eval_classification(model, val, device, num_classes)
        s = cls_score(m)
        history.append({"epoch": epoch, "train_loss": tot / max(n, 1),
                        **{f"val_{k}": v for k, v in m.items()}})
        log.info("[%s] ep %d/%d loss=%.4f acc=%.3f balacc=%.3f f1=%.3f auc=%s",
                 mcfg["name"], epoch, epochs, tot / max(n, 1), m["accuracy"],
                 m["balanced_accuracy"], m["f1_macro"],
                 f"{m['roc_auc']:.3f}" if m.get("roc_auc") is not None else "-")
        if s > best["score"] + 1e-4:
            best = {"epoch": epoch, "score": s, "metrics": m}
            torch.save(model.state_dict(), out_dir / "best.pt")
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                log.info("[%s] early stop", mcfg["name"])
                break
    if te is not None:
        model.load_state_dict(safe_load(out_dir / "best.pt", device))
        best["test_metrics"] = eval_classification(model, DataLoader(te, batch_size=bs), device, num_classes)
    (out_dir / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    return {"task": "classification", "arch": mcfg["arch"], "classes": classes, "best": best,
            "params_M": count_params(model) / 1e6, "train_time_s": time.time() - t0,
            "checkpoint": str(out_dir / "best.pt"), "history": str(out_dir / "history.json")}


# ----------------------------- сегментация -----------------------------------
class SegDataset(Dataset):
    def __init__(self, img_dir, mask_dir, img_size: int, train: bool = True):
        self.img_dir, self.mask_dir = Path(img_dir), Path(mask_dir)
        self.img_size, self.train = img_size, train
        self.mask_index = {}
        if self.mask_dir.exists():
            self.mask_index = {Path(f).stem: f for f in os.listdir(self.mask_dir)}
        self.files = [f for f in sorted(os.listdir(self.img_dir))
                      if f.lower().endswith(tuple(IMG_EXT)) and Path(f).stem in self.mask_index] if self.img_dir.exists() else []

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, idx: int):
        name = self.files[idx]
        img = Image.open(self.img_dir / name).convert("RGB")
        mask = Image.open(self.mask_dir / self.mask_index[Path(name).stem]).convert("L")
        img = img.resize((self.img_size, self.img_size))
        mask = mask.resize((self.img_size, self.img_size), Image.NEAREST)
        if self.train and random.random() < 0.5:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            mask = mask.transpose(Image.FLIP_LEFT_RIGHT)
        x = transforms.Normalize(MEAN, STD)(transforms.ToTensor()(img))
        y = (transforms.ToTensor()(mask) > 0.5).float()
        return x, y


@torch.no_grad()
def eval_segmentation(model, loader, device, thresh: float = 0.5) -> dict:
    model.eval()
    dice_sum, iou_sum, n = 0.0, 0.0, 0
    eps = 1e-7
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        pred = (torch.sigmoid(model(x)) > thresh).float()
        inter = (pred * y).sum(dim=(1, 2, 3))
        area = pred.sum(dim=(1, 2, 3)) + y.sum(dim=(1, 2, 3))
        dice_sum += ((2 * inter + eps) / (area + eps)).sum().item()
        iou_sum += ((inter + eps) / (area - inter + eps)).sum().item()
        n += x.size(0)
    return {"dice": dice_sum / max(n, 1), "iou": iou_sum / max(n, 1)}


def train_segmentation(mcfg: dict, data_cfg: dict, run_cfg: dict, device) -> dict:
    try:
        import segmentation_models_pytorch as smp
    except ImportError as e:  # noqa: BLE001
        raise RuntimeError("pip install segmentation-models-pytorch") from e
    p = mcfg.get("params", {})
    img_size = int(p.get("img_size", data_cfg.get("img_size", 256)))
    epochs, bs = int(p.get("epochs", 20)), int(p.get("batch_size", 16))
    lr, patience = float(p.get("lr", 1e-3)), int(p.get("patience", 5))

    root = Path(data_cfg["root"])
    im_sub, mk_sub = data_cfg.get("images_subdir", "images"), data_cfg.get("masks_subdir", "masks")
    tr_dir, va_dir = root / data_cfg.get("train_dir", "train"), root / data_cfg.get("val_dir", "val")
    tr = SegDataset(tr_dir / im_sub, tr_dir / mk_sub, img_size, True)
    va = SegDataset(va_dir / im_sub, va_dir / mk_sub, img_size, False)
    if len(tr) == 0:
        raise FileNotFoundError(f"Не найдено пар изображение+маска в {tr_dir} ({im_sub}/, {mk_sub}/)")

    model = smp.create_model(mcfg.get("arch", "unet"), encoder_name=p.get("encoder", "resnet34"),
                             in_channels=3, classes=1,
                             encoder_weights="imagenet" if p.get("pretrained", True) else None).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=float(p.get("weight_decay", 1e-4)))
    dice_loss, bce_loss = smp.losses.DiceLoss(mode="binary"), nn.BCEWithLogitsLoss()
    trl, val = DataLoader(tr, batch_size=bs, shuffle=True), DataLoader(va, batch_size=bs)

    out_dir = Path(run_cfg["work_dir"]) / mcfg["name"]
    out_dir.mkdir(parents=True, exist_ok=True)
    best, history, bad = {"epoch": 0, "score": -1.0, "metrics": {}}, [], 0
    t0 = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        tot, n = 0.0, 0
        for x, y in trl:
            x, y = x.to(device), y.to(device)
            opt.zero_grad(set_to_none=True)
            logits = model(x)
            loss = dice_loss(logits, y) + bce_loss(logits, y)
            loss.backward(); opt.step()
            tot += loss.item() * x.size(0); n += x.size(0)
        m = eval_segmentation(model, val, device)
        s = 0.6 * m["dice"] + 0.4 * m["iou"]
        history.append({"epoch": epoch, "train_loss": tot / max(n, 1),
                        **{f"val_{k}": v for k, v in m.items()}})
        log.info("[%s] ep %d/%d loss=%.4f dice=%.3f iou=%.3f",
                 mcfg["name"], epoch, epochs, tot / max(n, 1), m["dice"], m["iou"])
        if s > best["score"] + 1e-4:
            best = {"epoch": epoch, "score": s, "metrics": m}
            torch.save(model.state_dict(), out_dir / "best.pt")
            bad = 0
        else:
            bad += 1
            if bad >= patience:
                log.info("[%s] early stop", mcfg["name"])
                break
    (out_dir / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    return {"task": "segmentation", "arch": mcfg.get("arch", "unet"), "best": best,
            "params_M": count_params(model) / 1e6, "train_time_s": time.time() - t0,
            "checkpoint": str(out_dir / "best.pt")}


# --------------------------- YOLO (det+seg) ----------------------------------
def train_yolo(mcfg: dict, data_cfg: dict, run_cfg: dict, device) -> dict:
    try:
        from ultralytics import YOLO
    except ImportError as e:  # noqa: BLE001
        raise RuntimeError("pip install ultralytics") from e
    p = mcfg.get("params", {})
    data_yaml = p.get("data") or data_cfg.get("yolo_data_yaml")
    if not data_yaml:
        raise ValueError("Укажите params.data или data.yolo_data_yaml (путь к data.yaml COCO/YOLO)")
    t0 = time.time()
    model = YOLO(mcfg.get("arch", "yolov8n-seg.pt"))
    results = model.train(data=data_yaml,
                          epochs=int(p.get("epochs", 30)),
                          imgsz=int(p.get("imgsz", 640)),
                          batch=int(p.get("batch", 16)),
                          device=0 if device.type == "cuda" else "cpu",
                          project=str(Path(run_cfg["work_dir"]) / mcfg["name"]),
                          name="train", exist_ok=True, verbose=False)
    metrics = {}
    try:
        rd = results.results_dict or {}
        for k in ("metrics/mAP50(B)", "metrics/mAP50-95(B)", "metrics/mAP50(M)",
                  "metrics/precision(B)", "metrics/recall(B)"):
            if k in rd:
                metrics[k.replace("metrics/", "")] = float(rd[k])
    except Exception as e:  # noqa: BLE001
        log.warning("Не удалось прочитать метрики YOLO: %s", e)
    map_b = metrics.get("mAP50(B)", 0.0)
    map_m = metrics.get("mAP50(M)", map_b)
    ckpt = Path(run_cfg["work_dir"]) / mcfg["name"] / "train" / "weights" / "best.pt"
    return {"task": mcfg.get("type", "yolo_seg"), "arch": mcfg.get("arch"), "metrics": metrics,
            "score": 0.5 * map_b + 0.5 * map_m, "train_time_s": time.time() - t0,
            "checkpoint": str(ckpt)}


# ------------------------------- отчёт ---------------------------------------
def score_of(res: dict) -> float:
    if res.get("error"):
        return 0.0
    t = res.get("task")
    if t == "classification":
        return float(res.get("best", {}).get("score", 0.0))
    if t == "segmentation":
        m = res.get("best", {}).get("metrics", {})
        return 0.6 * m.get("dice", 0.0) + 0.4 * m.get("iou", 0.0)
    return float(res.get("score", 0.0))


def fmt_metrics(res: dict) -> str:
    if res.get("error"):
        return f"ERROR: {res['error'][:60]}"
    t = res.get("task")
    if t == "classification":
        m = res["best"]["metrics"]
        out = (f"acc={m['accuracy']:.3f} balacc={m['balanced_accuracy']:.3f} f1={m['f1_macro']:.3f}")
        if m.get("roc_auc") is not None:
            out += f" auc={m['roc_auc']:.3f}"
        return out
    if t == "segmentation":
        m = res["best"]["metrics"]
        return f"Dice={m['dice']:.3f} IoU={m['iou']:.3f}"
    if str(t).startswith("yolo"):
        m = res.get("metrics", {})
        return f"mAP50(B)={m.get('mAP50(B)', 0):.3f} mAP50(M)={m.get('mAP50(M)', 0):.3f}"
    return "-"


def make_report(results: list, cfg: dict, work_dir: str) -> Path:
    wd = Path(work_dir)
    wd.mkdir(parents=True, exist_ok=True)
    ok = [r for r in results if not r.get("error")]
    ranked = sorted(ok, key=lambda r: (-score_of(r), r.get("train_time_s", 1e18)))

    L = ["# Отчёт автообучения",
         f"\nСформирован: {datetime.now():%Y-%m-%d %H:%M:%S}",
         f"\nДанные: `{cfg['data'].get('root')}` · моделей обучено: {len(results)}\n",
         "## Сводная таблица",
         "",
         "| № | Модель | Задача | Архитектура | Ключевые метрики | Score | Время, с | Парам., М | Статус |",
         "|---|--------|--------|-------------|------------------|-------|----------|-----------|--------|"]
    for i, r in enumerate(results, 1):
        pm = f"{r['params_M']:.1f}" if r.get("params_M") else "-"
        L.append(f"| {i} | {r['name']} | {r.get('task', '-')} | {r.get('arch', '-')} | {fmt_metrics(r)} | "
                 f"{score_of(r):.3f} | {r.get('train_time_s', 0):.0f} | {pm} | {'OK' if not r.get('error') else 'ERROR'} |")

    L.append("\n## Рекомендация по выбору модели")
    if not ranked:
        L.append("\nНи одна модель не обучилась — проверьте пути к данным и параметры конфига.")
    else:
        best = ranked[0]
        L.append(f"\n**Лучшая по качеству: `{best['name']}`** (задача: {best['task']}, score = {score_of(best):.3f}).")
        L.append(f"Чекпоинт: `{best.get('checkpoint', '-')}`.")
        if len(ranked) > 1:
            alt = ranked[1]
            L.append(f"Вторая: `{alt['name']}` (score = {score_of(alt):.3f}, время {alt.get('train_time_s', 0):.0f} с).")
        fast = min(ranked, key=lambda r: r.get("train_time_s", 1e18))
        if fast is not best and score_of(best) - score_of(fast) <= 0.02:
            L.append(f"\nЕсли важна скорость: `{fast['name']}` — отставание по качеству всего "
                     f"{score_of(best) - score_of(fast):.3f}, а обучается/работает быстрее.")
        L.append("\n**Правила выбора:**")
        L.append("- продакшен/быстрый инференс — YOLO-модели (детекция+сегментация в одной сети);")
        L.append("- максимальное качество сегментации — smp U-Net/Unet++ (при необходимости + MedSAM);")
        L.append("- классификация — лучший классификатор из таблицы; возможен ансамбль с вице-лидером.")

    (wd / "report.md").write_text("\n".join(L), encoding="utf-8")
    payload = {"generated": datetime.now().isoformat(), "config": cfg, "results": results,
               "ranking": [r["name"] for r in ranked]}
    (wd / "report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    log.info("Отчёт: %s", wd / "report.md")
    return wd / "report.md"


# -------------------------------- main ---------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Автообучение моделей по конфигу")
    ap.add_argument("--config", required=True)
    ap.add_argument("--models", nargs="*", default=None, help="обучить только эти модели")
    ap.add_argument("--device", default=None, help="auto | cuda | cpu")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    setup_logging()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    run_cfg = cfg.get("run", {})
    run_cfg.setdefault("work_dir", "runs/exp")
    device = pick_device(args.device or run_cfg.get("device", "auto"))
    set_seed(int(run_cfg.get("seed", 42)))
    log.info("Устройство: %s", device)

    models = [m for m in cfg.get("models", []) if m.get("enabled", True)]
    if args.models:
        models = [m for m in models if m.get("name") in args.models]
    if args.dry_run:
        print(json.dumps({"device": str(device),
                          "models": [m["name"] for m in models]}, ensure_ascii=False, indent=2))
        return

    results = []
    for mcfg in models:
        name = mcfg.get("name", mcfg.get("arch", "model"))
        log.info("=== Обучение: %s (тип %s, арх. %s) ===", name, mcfg.get("type"), mcfg.get("arch"))
        t0 = time.time()
        try:
            t = str(mcfg.get("type", ""))
            if t == "classification":
                res = train_classification(mcfg, cfg["data"], run_cfg, device)
            elif t == "segmentation":
                res = train_segmentation(mcfg, cfg["data"], run_cfg, device)
            elif t.startswith("yolo"):
                res = train_yolo(mcfg, cfg["data"], run_cfg, device)
            else:
                raise ValueError(f"Неизвестный тип модели: {mcfg.get('type')}")
            res.update({"name": name, "config": mcfg})
            results.append(res)
        except Exception as e:  # noqa: BLE001
            log.exception("Ошибка обучения %s", name)
            results.append({"name": name, "arch": mcfg.get("arch"), "task": mcfg.get("type"),
                            "error": str(e), "train_time_s": time.time() - t0})
        if device.type == "cuda":
            torch.cuda.empty_cache()

    report_path = make_report(results, cfg, run_cfg["work_dir"])
    print(f"\nГотово. Отчёт: {report_path}")


if __name__ == "__main__":
    main()
```

# 6. Запуск (сквозной пример)

```bash
pip install -r requirements.txt

# 1) скачать данные
python app1_downloader.py --config configs/download.yaml

# 2) превратить BloodMNIST в папочную структуру
python tools/npz2folders.py --npz data/bloodmnist/bloodmnist.npz --out data/bloodmnist

# 3) автономное обучение + отчёт
python app2_autotrain.py --config configs/train.yaml
# или выборочно:
python app2_autotrain.py --config configs/train.yaml --models efficientnet_b0 --device cuda
```

**Что получится в `runs/blood_exp1/`:** `report.md` (сводная таблица + рекомендация лучшей модели с обоснованием), `report.json`, чекпоинты `best.pt` и `history.json` по каждой модели.

**Примечания:**
- Под новые данные достаточно править конфиг: в `download.yaml` добавить ссылки и пути, в `train.yaml` — модели/гиперпараметры. Ошибки одной модели не прерывают обучение остальных — они попадают в отчёт со статусом `ERROR`.
- Для сегментации структура данных должна быть `<root>/<train_dir>/images` и `<root>/<train_dir>/masks` (имена файлов совпадают); для YOLO — стандартный `data.yaml` (COCO/YOLO-формат).
- Если нужны готовые конфиги под конкретные датасеты из прошлых сообщений (C-NMC, TN3K, TCGA-THCA) — подготовлю их вместе со скриптами приведения к нужной структуре папок.

 Для такой сложной мультимодальной задачи (медицинская визуализация + CV + генерация данных + AutoML) одной LLM недостаточно — нужна **многоагентная система**. Но если выделять ключевые роли, вот оптимальная конфигурация:

## 🏆 Основная LLM: Claude 4 Sonnet (или Claude 3.5 Sonnet)

**Почему именно она:**
- **Лучший кодинг** среди всех LLM на сложных CV-проектах (бенчмарки SWE-Bench, HumanEval)
- **Отличное понимание медицинского контекста** — корректно работает с терминологией онкологии, гистологии, радиологии
- **Tool use** — может последовательно запускать код, анализировать метрики (Dice, IoU, AUC), корректировать пайплайны
- **Большой контекст** (200K токенов) — позволяет держать весь проект (код + конфиги + логи экспериментов) в одной сессии

**Альтернатива:** GPT-4o / o3 — если критичен reasoning при выборе архитектур нейросетей, но дороже и медленнее.

---

## 🧠 Архитектура приложения (что будет делать LLM)

LLM выступает **оркестратором**, который пишет и управляет кодом для:

| Компонент | Модели/фреймворки (выбирает LLM) |
|-----------|----------------------------------|
| **Предобработка** | OpenCV, Albumentations, CLAHE, нормализация стейнинга |
| **Классификация** | EfficientNet-B7, ConvNeXt, Vision Transformer (ViT) |
| **Сегментация** | nnU-Net (золотой стандарт медицины), SAM-Med2D, SegFormer |
| **Текстовое описание** | LLaVA-Med, RadFM, или fine-tuned CLIP + GPT-4 |
| **Генерация синтетики** | Stable Diffusion + ControlNet, DDPM, StyleGAN3 |
| **Деградация изображений** | Albumentations (шум, blur, JPEG-artifacts), domain randomization |
| **AutoML/выбор модели** | Optuna, Ray Tune, WandB Sweeps — LLM пишет конфиги и анализирует результаты |

---

## 🛠️ Рекомендуемый стек (что реально использовать)

```python
# CV + Medical Imaging
torchvision, timm, segmentation-models-pytorch, monai, albumentations

# Сегментация
nnunet, sam-med2d, transformers (SegFormer)

# Генерация
diffusers, controlnet-aux, accelerate

# AutoML + эксперименты
optuna, ray[tune], wandb, mlflow

# Агентский фреймворк (LLM оркеструет)
langgraph, autogen, или кастомный ReAct-агент
```

---

## ⚡ Практический совет: не одна модель, а система

Для вашей задачи лучше построить **3 агента**:

1. **Архитектор** (Claude 4 Sonnet) — проектирует пайплайн, выбирает модели
2. **Инженер** (Claude 3.5 Sonnet / DeepSeek-V3) — пишет код экспериментов
3. **Аналитик** (Claude 4 Sonnet) — сравнивает метрики, выбирает лучшую модель

**Open-source альтернатива** (если нужно локально): 
- **DeepSeek-V3** (671B MoE) — близок к Claude по кодингу
- **Qwen3-235B** — сильный в мультимодальных задачах
- **Llama 3.3 70B** — для локального развёртывания, но потребует больше prompt engineering

---

## 🎯 Итоговая рекомендация

| Бюджет | Рекомендация |
|--------|-------------|
| **Без ограничений** | Claude 4 Sonnet + GPT-4o (для сложного reasoning) |
| **Средний** | Claude 3.5 Sonnet — оптимальное соотношение цена/качество |
| **Локально / open-source** | DeepSeek-V3 + Qwen2.5-VL (для vision-задач) |

**Ключевой момент:** LLM не заменит специализированные медицинские модели (nnU-Net, SAM-Med2D), но идеально справится с **автоматизацией их подбора, интеграции и сравнения** — именно это вам и нужно.

