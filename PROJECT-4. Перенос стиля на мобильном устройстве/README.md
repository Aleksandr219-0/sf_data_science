# Перенос стиля на мобильном устройстве

## Описание проекта

Проект демонстрирует перенос художественного стиля с изображения картины
на контентное изображение с использованием модели
Magenta Arbitrary Image Stylization.

Для примеров стиля используются изображения из WikiArt.
Инференс выполняется в ноутбуке Python с TensorFlow и TensorFlow Hub.

## Возможности

- Выбор контентного изображения.
- Выбор стилевого изображения из WikiArt.
- Перенос художественного стиля на контентное изображение.
- Визуализация контента, стиля и результата в одной строке.
- Сохранение результатов инференса.

## Структура репозитория

```text
├── app/                         # Исходный код Android-приложения
├── data/                        # Контентные и стилевые изображения
├── models/                      # Локальные модели и кэш моделей
├── reports/                     # Отчёты и дополнительные материалы
├── results/                     # Результаты инференса
├── training/
│   └── style_transfer_wikiart.ipynb  # Ноутбук инференса модели Magenta
├── video/                       # Видео работы мобильного прототипа
├── requirements.txt             # Python-зависимости
└── README.md
```

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Запуск инференса

1. Откройте ноутбук:

   ```text
   training/style_transfer_wikiart.ipynb
   ```

2. Установите зависимости из `requirements.txt`.

3. Запустите ячейки ноутбука по порядку.

4. Ноутбук случайно выбирает:
   - контентное изображение;
   - изображение стиля WikiArt.

5. На экране появляются три изображения:
   - контент;
   - стиль WikiArt;
   - результат переноса стиля.

## Используемая модель

Используется предобученная модель:

```text
Magenta Arbitrary Image Stylization
```

TensorFlow Hub:

```text
[https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2](https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2)
```

Источник и пример мобильного инференса:

```text
[https://github.com/magenta/magenta/tree/main/magenta/models/arbitrary_image_stylization](https://github.com/magenta/magenta/tree/main/magenta/models/arbitrary_image_stylization)
```

## Результаты

Готовые изображения после переноса стиля сохраняются в папке:

```text
results/
```

## Мобильное приложение

Исходный код мобильного прототипа будет размещён в папке:

```text
app/
```

## Видео

Видео, демонстрирующее работу прототипа и применение стиля, размещается в папке:

```text
video/
```