# 🚀 SelfLearn

**Autonomous Self-Learning AI System** | Version 1.0.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-stable-green.svg)]()

## 📖 О проекте

SelfLearn — это полностью автономная система самообучения искусственного интеллекта, которая не требует участия человека в процессе обучения. Система самостоятельно:

- ✅ Генерирует обучающие данные с адаптивной сложностью
- ✅ Обучает нейронные сети без вмешательства человека
- ✅ Оценивает результаты и адаптируется к слабым местам модели
- ✅ Сохраняет прогресс и может возобновить обучение после прерывания
- ✅ Предоставляет веб-интерфейс для мониторинга

## ⚡ Быстрый старт

### 1. Установка зависимостей

```bash
cd /workspace/project
pip install -r requirements.txt
```

### 2. Запуск теста

```bash
python src/selflearn/run.py --action test
```

### 3. Запуск обучения

```bash
python src/selflearn/run.py --action run --competitions 5 --rounds 10 --tasks 50
```

### 4. Запуск веб-интерфейса

```bash
python src/selflearn/run.py --action api --port 8000
```

Откройте в браузере: http://localhost:8000/docs

## 🏗️ Архитектура

Система использует архитектуру **Teacher-Student-Referee**:

```
┌─────────────────────────────────────────┐
│           Referee (Оркестратор)         │
│    Управляет циклом обучения            │
└───────────────┬─────────────────────────┘
                │
        ┌───────┴───────┐
        ▼               ▼
┌──────────────┐  ┌──────────────┐
│   Teacher    │  │   Student    │
│ (Генератор)  │  │  (Модели)    │
│ Создаёт задачи│  │  Обучается   │
│ с искажениями │  │  Решает      │
└──────────────┘  └──────────────┘
```

### 9 типов искажений

1. **Gaussian Noise** — Гауссов шум
2. **Salt & Pepper** — Импульсный шум
3. **Blur** — Размытие
4. **Brightness** — Яркость
5. **Contrast** — Контраст
6. **Rotation** — Поворот
7. **Occlusion** — Частичное закрытие
8. **Compression** — JPEG компрессия
9. **Distortion** — Геометрические искажения

## 📁 Структура проекта

```
/workspace/project/
├── src/selflearn/       # Исходный код системы
├── static/              # Веб-интерфейс (HTML, JS)
├── config/              # YAML конфигурации
├── data/                # Данные и модели
├── docs/                # Документация
├── specs/               # Спецификации OpenSpec
└── tests/               # Тесты
```

Подробная структура: [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)

## 📚 Документация

| Документ | Описание |
|----------|----------|
| [USER_GUIDE.md](docs/USER_GUIDE.md) | Полное руководство пользователя |
| [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Структура проекта |
| [specs/template.md](specs/template.md) | Шаблон спецификаций |

## 🔧 Конфигурация

Основные параметры в `config/default.yaml`:

```yaml
system:
  seed: 42
  log_level: INFO

training:
  batch_size: 32
  epochs: 10
  learning_rate: 0.001

teacher:
  adaptation_rate: 0.1
```

## 🎯 Режимы работы

### Test mode
```bash
python src/selflearn/run.py --action test
```
Быстрая проверка (1 competition, 1 round, 5 tasks)

### Run mode
```bash
python src/selflearn/run.py --action run \
  --competitions 10 \
  --rounds 20 \
  --tasks 100
```
Полноценное обучение

### API mode
```bash
python src/selflearn/run.py --action api --port 8000
```
Веб-сервер для мониторинга и управления

## 🌐 API Endpoints

| Method | Endpoint | Описание |
|--------|----------|----------|
| GET | `/status` | Статус системы |
| GET | `/results` | Результаты обучения |
| GET | `/models` | Доступные модели |
| POST | `/train` | Запустить обучение |
| POST | `/admin/stop` | Остановить обучение |
| POST | `/admin/reset` | Сбросить состояние |

Интерактивная документация: http://localhost:8000/docs

## 🧪 Тестирование

```bash
# Запустить все тесты
pytest tests/

# Запустить конкретный тест
pytest tests/test_degrade.py -v
```

## 📊 Метрики

Система отслеживает:
- **Accuracy** — Точность распознавания
- **Precision** — Точность положительных предсказаний
- **Recall** — Полнота обнаружения
- **F1-Score** — Гармоническое среднее

## 🛠️ Требования

- Python 3.8+
- PyTorch
- FastAPI
- Pillow
- NumPy
- PyYAML

Полный список: [requirements.txt](requirements.txt)

## 📈 Пример использования

```python
from src.selflearn.referee import Referee
from src.selflearn.common import DEFAULT_CONFIG

# Инициализация
referee = Referee(data_dir='data', config=DEFAULT_CONFIG)

# Запуск обучения
result = referee.run_competition(
    competitions=5,
    rounds_per_competition=10,
    tasks_per_round=50,
    epochs=10,
    batch_size=32
)

# Получение результатов
print(f"Final accuracy: {result['competitions'][-1]['rounds'][-1]['metrics']['accuracy']}")
```

## 🤝 Вклад в проект

Все новые задачи должны оформляться через спецификации OpenSpec:

1. Создать файл в `specs/SPC-XXX-description.md`
2. Заполнить разделы Plan → Implement → Verify → Document → Archive
3. Следовать процессу PIVDA

Подробнее: [specs/OPENSPEC-RULE-001.md](specs/OPENSPEC-RULE-001.md)

## 📄 Лицензия

MIT License — см. [LICENSE](LICENSE) файл для деталей.

## 🔗 Ссылки

- Исходный репозиторий: https://github.com/yodikparohodik/challenge_page_elements
- Документация: `/workspace/project/docs/`
- API: http://localhost:8000/docs

---

**Версия**: 1.0.0  
**Дата обновления**: 2024-01-15  
**Статус**: Stable
