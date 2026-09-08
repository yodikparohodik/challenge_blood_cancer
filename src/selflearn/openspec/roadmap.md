# OpenSpec: SelfLearn Development Roadmap

## 📋 Обзор проекта

**Название**: SelfLearn  
**Версия спецификации**: 1.0.0  
**Статус**: Active Development  
**Тип**: Автономная система самообучения с архитектурой Teacher-Student-Referee

---

## 🎯 Цели проекта

### Основная цель
Создать полностью автономную систему, которая:
1. Генерирует собственные обучающие данные
2. Обучает модели без участия человека
3. Адаптирует сложность данных на основе результатов
4. Сохраняет и восстанавливает состояние после прерываний

### Ключевые метрики успеха
- ✅ Полная автономность (no human intervention)
- ✅ Адаптивная сложность данных
- ✅ Сохранение состояния после каждого раунда
- ✅ Веб-интерфейс для мониторинга
- ✅ Модульная архитектура

---

## 🏗️ Архитектура системы

### Компоненты

```
┌─────────────────────────────────────────────────────────────┐
│                        Referee                              │
│                    (Оркестратор)                            │
│  - Управление циклом обучения                               │
│  - Оценка результатов                                       │
│  - Адаптация стратегии                                      │
└───────────────┬─────────────────────────────────┬───────────┘
                │                                 │
                ▼                                 ▼
┌───────────────────────────┐       ┌─────────────────────────┐
│         Teacher           │       │         Student         │
│      (Генератор)          │       │       (Модели)          │
│  - Синтез данных          │       │  - Классификаторы       │
│  - Применение искажений   │       │  - Обучение             │
│  - Метки истинности       │       │  - Инференс             │
└───────────────────────────┘       └─────────────────────────┘
                │                                 │
                └──────────┬──────────────────────┘
                           ▼
                  ┌─────────────────┐
                  │   Degrade API   │
                  │  (9 искажений)  │
                  └─────────────────┘
```

### Модули

| Модуль | Файл | Описание | Статус |
|--------|------|----------|--------|
| Common | `common.py` | Утилиты, метрики, константы | ✅ Done |
| Degrade | `degrade.py` | 9 типов искажений изображений | ✅ Done |
| Synthesize | `synthesize.py` | Генерация базовых изображений | ✅ Done |
| Teacher | `teacher.py` | Логика учителя (композиция) | ✅ Done |
| Student | `student.py` | Модели ученика + обучение | ✅ Done |
| Referee | `referee.py` | Оркестрация всего процесса | ✅ Done |
| API | `api.py` | FastAPI веб-сервер | ✅ Done |
| Runner | `run.py` | CLI точка входа | ✅ Done |

---

## 📦 Спецификация модулей

### 1. Common (`common.py`)

**Ответственность**: Общие утилиты и функции

**Функции**:
- `calculate_metrics(predictions, labels)` → dict
  - accuracy, precision, recall, f1_score, confusion_matrix
- `set_seed(seed)` → None
  - Установка seed для воспроизводимости
- `setup_logging(level, file)` → Logger
- `ensure_dir(path)` → None

**Константы**:
- `DEGRADATION_TYPES`: список из 9 типов искажений
- `DEFAULT_CONFIG`: значения по умолчанию

---

### 2. Degrade (`degrade.py`)

**Ответственность**: Применение искажений к изображениям

**Класс**: `DegradeAPI`

**Методы**:
- `apply(image, degradation_type, severity)` → PIL.Image
  - `degradation_type`: один из 9 типов
  - `severity`: float [0.0, 1.0]

**Типы искажений**:
1. `gaussian_noise` — Гауссов шум
2. `salt_pepper` — Соль-перец шум
3. `blur` — Размытие (Gaussian blur)
4. `brightness` — Изменение яркости
5. `contrast` — Изменение контраста
6. `rotation` — Поворот изображения
7. `occlusion` — Частичное закрытие (окклюзия)
8. `compression` — JPEG компрессия
9. `distortion` — Геометрические искажения

---

### 3. Synthesize (`synthesize.py`)

**Ответственность**: Генерация базовых изображений

**Класс**: `Synthesizer`

**Методы**:
- `generate_digit(digit, size=(64,64))` → PIL.Image
- `generate_shape(shape_type, size=(64,64))` → PIL.Image
- `generate_text(text, font_size=20)` → PIL.Image

**Параметры**:
- `size`: кортеж (width, height)
- `background_color`: RGB или 'white'/'black'
- `foreground_color`: RGB или 'random'

---

### 4. Teacher (`teacher.py`)

**Ответственность**: Генерация задач с искажениями

**Класс**: `Teacher`

**Методы**:
- `generate_task(degradation_probs)` → Task
  - Возвращает объект Task с полями:
    - `image`: PIL.Image
    - `label`: int/string
    - `metadata`: dict (тип искажения, severity, etc.)
- `adapt_strategy(error_analysis)` → None
  - Обновляет вероятности искажений на основе ошибок

**Логика адаптации**:
```python
if error_rate[degradation_type] > threshold:
    probability[degradation_type] *= 1.2  # увеличить фокус
else:
    probability[degradation_type] *= 0.9  # уменьшить фокус
```

---

### 5. Student (`student.py`)

**Ответственность**: Модели и обучение

**Классы**:
- `StudentBase` (абстрактный)
- `SimpleCNN` (наследует StudentBase)
- `ResNetStudent` (наследует StudentBase, опционально)

**Методы**:
- `train(dataset, epochs, batch_size)` → TrainingHistory
- `predict(images)` → predictions
- `save(path)` → None
- `load(path)` → StudentBase

**Архитектура SimpleCNN**:
```
Input (64x64x3)
  ↓
Conv2D(32, 3x3) + ReLU + MaxPool
  ↓
Conv2D(64, 3x3) + ReLU + MaxPool
  ↓
Flatten
  ↓
Dense(128) + ReLU + Dropout(0.5)
  ↓
Dense(num_classes) + Softmax
```

---

### 6. Referee (`referee.py`)

**Ответственность**: Оркестрация цикла обучения

**Класс**: `Referee`

**Методы**:
- `run_competition(rounds, tasks_per_round)` → CompetitionResult
- `evaluate_round(tasks, predictions)` → RoundMetrics
- `save_state()` → None
- `load_state()` → State
- `stop()` → None

**Цикл работы**:
```
FOR each competition:
  FOR each round:
    1. Teacher генерирует N задач
    2. Student решает задачи
    3. Referee оценивает результаты
    4. Teacher адаптирует стратегию
    5. Сохранить состояние
    IF stop_requested: BREAK
  END FOR
END FOR
```

---

### 7. API (`api.py`)

**Ответственность**: Веб-интерфейс

**Framework**: FastAPI

**Endpoints**:

| Method | Path | Описание |
|--------|------|----------|
| GET | `/status` | Текущее состояние системы |
| GET | `/results` | История соревнований |
| GET | `/models` | Доступные модели |
| GET | `/metrics/{competition_id}` | Детальные метрики |
| POST | `/train` | Запустить обучение |
| POST | `/admin/reset` | Сброс состояния |
| POST | `/admin/stop` | Остановить обучение |

**Request/Response примеры**:

```json
// POST /train
{
  "competitions": 5,
  "rounds": 10,
  "tasks_per_round": 50
}

// Response 200 OK
{
  "status": "started",
  "job_id": "uuid-here",
  "message": "Training started"
}
```

---

### 8. Runner (`run.py`)

**Ответственность**: CLI интерфейс

**Аргументы командной строки**:
- `--action`: {test, run, api}
- `--competitions`: int (default: 3)
- `--rounds`: int (default: 5)
- `--tasks`: int (default: 20)
- `--config`: path to YAML (default: config/default.yaml)
- `--log-level`: {DEBUG, INFO, WARNING, ERROR}
- `--log-file`: path (optional)
- `--port`: int (для API, default: 8000)

---

## 📊 Структура данных

### State (`data/state.json`)

```json
{
  "current_competition": 2,
  "current_round": 3,
  "total_competitions": 5,
  "degradation_probs": {
    "gaussian_noise": 0.15,
    "blur": 0.20,
    ...
  },
  "model_weights_path": "data/models/best.pth",
  "last_updated": "2024-01-15T10:30:00Z",
  "is_running": true
}
```

### Results (`data/results.json`)

```json
{
  "competitions": [
    {
      "id": 1,
      "started_at": "...",
      "completed_at": "...",
      "rounds": [
        {
          "round_number": 1,
          "tasks_count": 50,
          "metrics": {
            "accuracy": 0.85,
            "f1_score": 0.83,
            "confusion_matrix": [[...]]
          },
          "error_by_degradation": {
            "gaussian_noise": 0.12,
            "blur": 0.08,
            ...
          }
        }
      ]
    }
  ]
}
```

---

## 🔧 Конфигурация

### default.yaml

```yaml
system:
  seed: 42
  log_level: INFO
  data_dir: data
  save_every_round: true

training:
  batch_size: 32
  learning_rate: 0.001
  epochs: 10
  optimizer: adam
  patience: 5  # early stopping

teacher:
  initial_degradation_probs:
    gaussian_noise: 0.11
    salt_pepper: 0.11
    blur: 0.11
    brightness: 0.11
    contrast: 0.11
    rotation: 0.11
    occlusion: 0.11
    compression: 0.11
    distortion: 0.12
  adaptation_rate: 0.1
  max_probability: 0.4
  min_probability: 0.05

student:
  model_type: SimpleCNN
  num_classes: 10
  input_size: [64, 64, 3]
```

### degradations.yaml

```yaml
degradations:
  gaussian_noise:
    severity_range: [0.0, 0.5]
    params:
      mean: 0
      std_multiplier: [0.01, 0.5]
  
  blur:
    severity_range: [0.0, 1.0]
    params:
      kernel_size: [3, 15]
  
  # ... остальные типы
```

---

## 🧪 Тестирование

### Unit тесты (планируется)

```python
# tests/test_degrade.py
def test_gaussian_noise():
    img = Image.new('RGB', (64, 64))
    degraded = DegradeAPI.apply(img, 'gaussian_noise', 0.5)
    assert degraded.size == (64, 64)

# tests/test_teacher.py
def test_generate_task():
    teacher = Teacher()
    task = teacher.generate_task()
    assert task.image is not None
    assert task.label is not None

# tests/test_referee.py
def test_run_competition():
    referee = Referee()
    result = referee.run_competition(rounds=2, tasks_per_round=10)
    assert len(result.rounds) == 2
```

### Integration тесты

- Проверка полного цикла обучения
- Проверка сохранения/восстановления состояния
- Проверка API endpoints

---

## 🚀 План развития (Roadmap)

### Фаза 1: MVP (✅ Завершено)
- [x] Базовая архитектура Teacher-Student-Referee
- [x] 9 типов искажений
- [x] Простая CNN модель
- [x] Сохранение состояния
- [x] CLI интерфейс
- [x] Базовый API

### Фаза 2: Улучшения (В работе)
- [ ] Добавить больше архитектур моделей (ResNet, EfficientNet)
- [ ] Поддержка GPU через CUDA
- [ ] Визуализация прогресса обучения (графики)
- [ ] Расширенные метрики (ROC-AUC, PR-curve)

### Фаза 3: Production (План)
- [ ] Docker контейнеризация
- [ ] Kubernetes deployment manifests
- [ ] Monitoring (Prometheus metrics)
- [ ] Distributed training support
- [ ] REST API authentication

### Фаза 4: Advanced Features (Будущее)
- [ ] Multi-modal данные (текст + изображения)
- [ ] Reinforcement Learning для адаптации
- [ ] AutoML для подбора архитектуры
- [ ] Federated Learning поддержка

---

## 📝 Changelog

### v1.0.0 (2024-01-15)
- Initial release
- Full autonomous learning loop
- 9 degradation types
- Web API with FastAPI
- State persistence

---

## 🔗 Ссылки

- Исходный репозиторий: https://github.com/yodikparohodik/challenge_page_elements
- Документация: `/workspace/src/selflearn/README.md`
- Конфигурации: `/workspace/src/selflearn/config/`
