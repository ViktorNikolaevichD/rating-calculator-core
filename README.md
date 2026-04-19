# rating-calculator-core

Общая Python-библиотека с бизнес-логикой расчёта рейтингов и связанных значений.
Используется в двух проектах:
- `backend`
- `admin`

## Возможности
Сейчас библиотека содержит логику для:
- расчёта среднего рейтинга организации
- определения характера отзывов организации

## Структура
```text
src/rating_calculator_core/
````

## Установка для локальной разработки
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Сборка пакета
```bash
python -m build
```
После сборки артефакты будут находиться в папке `dist/`.
