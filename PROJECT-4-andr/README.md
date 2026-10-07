# Перенос художественного стиля на мобильном устройстве

## Цель проекта

Цель работы — реализовать приложение Android для произвольного переноса художественного стиля на фотографию пользователя.

Приложение позволяет:

- сделать исходную фотографию камерой смартфона;
- выбрать фотографию из Галереи;
- выбрать картину-стиль из Галереи или из встроенного набора WikiArt;
- применить нейросетевой перенос стиля локально на мобильном устройстве;
- сохранить готовый результат в Галерею.

В основе решения лежит архитектура **Magenta Arbitrary Image Stylization**. Для мобильного inference используются TensorFlow Lite-модели, получаемые после обучения и конвертации мобильной версии модели.

## Архитектура решения

```text
                    Этап обучения / подготовки модели

Изображения WikiArt
        ↓
Создание style_images.tfrecord
        ↓
arbitrary_image_stylization_train_mobile
        ↓
Checkpoint обученной mobile-модели
        ↓
arbitrary_image_stylization_convert_tflite
        ↓
style_predict.tflite + style_transform.tflite
        ↓
Добавление моделей в Android assets


                    Этап мобильного inference

Камера / Галерея
        ↓
Контентное изображение
        +
Стиль из Галереи / встроенный стиль WikiArt
        ↓
style_predict.tflite
        ↓
Style embedding
        +
Контентное изображение
        ↓
style_transform.tflite
        ↓
Стилизованное изображение
        ↓
Сохранение в Галерею Android-устройства
```

## Реализованный мобильный прототип

Приложение разработано на Kotlin в Android Studio и протестировано на физическом Android-устройстве Samsung.

### Функциональность

- Получение контентного изображения из системной камеры.
- Выбор контентного изображения из Галереи.
- Выбор изображения-стиля из Галереи.
- Выбор встроенного набора художественных стилей WikiArt.
- Отображение миниатюр встроенных стилей в горизонтальной ленте.
- Предпросмотр выбранного контентного изображения и изображения-стиля.
- Локальный TensorFlow Lite inference.
- Индикатор процесса стилизации.
- Отображение созданного изображения.
- Сохранение результата как JPEG в медиатеку телефона.
- Работа без передачи пользовательских изображений на внешний сервер.

### Использование приложения

1. Нажать **«Сделать фото камерой»** или **«Выбрать фотографию из галереи»**.
2. Получить исходное контентное изображение.
3. Выбрать стиль:
   - через кнопку **«Выбрать стиль из галереи»**;
   - либо нажать на одну из встроенных миниатюр WikiArt.
4. Нажать **«Применить стиль»**.
5. Дождаться завершения локального inference.
6. Просмотреть результат.
7. Нажать **«Сохранить результат»**.

Готовые изображения сохраняются в:

```text
Pictures/StyleTransferApp
```

## Обучение модели

### Подход

Для обучения используется официальный pipeline Magenta `arbitrary_image_stylization`.

Модель состоит из двух основных компонентов:

| Компонент | Назначение |
|---|---|
| Style Prediction Network | Получает изображение картины и строит style embedding |
| Style Transform Network | Получает контентное изображение и embedding, формирует стилизованный результат |

Для мобильной версии применяется MobileNetV2 как облегчённая сеть предсказания стиля. Это позволяет экспортировать модель в TensorFlow Lite и запускать inference на Android-устройстве. [Magenta README](https://github.com/magenta/magenta/tree/main/magenta/models/arbitrary_image_stylization)

### Требуемые данные и checkpoints

Официальный pipeline Magenta требует:

1. Каталог изображений-стилей.
2. ImageNet, предварительно подготовленный в формате TFRecord.
3. Checkpoint VGG для perceptual loss.
4. Checkpoint Inception-v3.
5. Checkpoint MobileNetV2 для обучения мобильной модели.
6. Репозиторий Magenta и библиотеку TF-Slim.

В проекте в качестве стилевых изображений используется набор WikiArt:

```text
data/style_images/
```

Подготовленные встроенные изображения для Android-приложения находятся в:

```text
app/src/main/assets/styles/
```

### Подготовка style TFRecord

Перед обучением изображения-стили необходимо преобразовать в TFRecord.

Пример команды из pipeline Magenta:

```bash
arbitrary_image_stylization_create_dataset \
  --style_files="/path/to/style_images/*.jpg" \
  --output_file="/path/to/style_images.tfrecord"
```

Пример путей для проекта:

```bash
arbitrary_image_stylization_create_dataset \
  --style_files="data/style_images/*.jpg" \
  --output_file="training/data/style_images.tfrecord"
```

> Конкретные параметры подготовки данных должны соответствовать установленной версии Magenta. Полученный файл `style_images.tfrecord` используется на этапе обучения.

### Обучение mobile-модели

Для обучения модели, пригодной для TensorFlow Lite и Android, используется команда:

```bash
arbitrary_image_stylization_train_mobile \
  --batch_size=8 \
  --imagenet_data_dir=/path/to/imagenet-2012-tfrecord \
  --vgg_checkpoint=/path/to/vgg-checkpoint \
  --mobilenet_checkpoint=/path/to/mobilenet_v2_1.0_224/checkpoint/mobilenet_v2_1.0_224.ckpt \
  --style_dataset_file=/path/to/style_images.tfrecord \
  --train_dir=/path/to/logdir/train_dir \
  --random_style_image_size=True \
  --augment_style_images=True \
  --center_crop=False \
  --logtostderr
```

Параметры:

| Параметр | Назначение |
|---|---|
| `--batch_size` | Размер mini-batch |
| `--imagenet_data_dir` | Каталог ImageNet в TFRecord-формате |
| `--vgg_checkpoint` | VGG checkpoint для perceptual loss |
| `--mobilenet_checkpoint` | Предобученный MobileNetV2 checkpoint |
| `--style_dataset_file` | TFRecord с изображениями WikiArt |
| `--train_dir` | Каталог логов и checkpoints |
| `--random_style_image_size=True` | Случайный размер стилевого изображения |
| `--augment_style_images=True` | Аугментации стилевых изображений |
| `--center_crop=False` | Отключение фиксированного central crop |

В репозитории команды запуска можно хранить в файле:

```text
training/train_mobile.sh
```

Пример структуры артефактов обучения:

```text
training/
├── data/
│   └── style_images.tfrecord
├── checkpoints/
│   ├── checkpoint
│   ├── model.ckpt-XXXX.index
│   └── model.ckpt-XXXX.data-00000-of-00001
├── logs/
│   └── training_log.txt
├── train_mobile.sh
└── style_transfer_wikiart.ipynb
```

### Экспорт в TensorFlow Lite

После завершения обучения checkpoint mobile-модели конвертируется в TensorFlow Lite:

```bash
arbitrary_image_stylization_convert_tflite \
  --checkpoint=/path/to/logdir/train_dir \
  --output_dir=/path/to/logdir/tflite
```

После конвертации создаются модели для мобильного inference:

```text
style_predict.tflite
style_transform.tflite
```

Они добавляются в Android-приложение:

```text
app/src/main/assets/
├── style_predict.tflite
└── style_transform.tflite
```

## TensorFlow Lite inference на Android

В приложении используются две модели:

| Файл | Вход | Выход |
|---|---|---|
| `style_predict.tflite` | Изображение-стиль | Style embedding |
| `style_transform.tflite` | Контентное изображение + style embedding | Стилизованное изображение |

Подготовка изображений в приложении:

- изображение-стиль приводится к размеру 256 × 256;
- контентное изображение приводится к размеру 384 × 384;
- изображения преобразуются в RGB-тензоры;
- приложение получает параметры квантизации непосредственно из TFLite-тензоров;
- поддерживаются `FLOAT32`, `INT8` и `UINT8` значения TensorFlow Lite.

## Структура репозитория

```text
StyleTransferApp/
├── app/                                      # Android-приложение
│   └── src/main/
│       ├── assets/
│       │   ├── style_predict.tflite          # Style Prediction Network
│       │   ├── style_transform.tflite        # Style Transform Network
│       │   └── styles/                       # Встроенные стили WikiArt
│       │       ├── style_000.jpg
│       │       ├── style_001.jpg
│       │       └── ...
│       ├── java/com/example/styletransferapp/
│       │   └── MainActivity.kt               # Камера, UI, TFLite inference
│       ├── res/
│       │   ├── layout/activity_main.xml
│       │   └── xml/file_paths.xml            # FileProvider для камеры
│       └── AndroidManifest.xml
├── data/
│   └── style_images/                         # Исходные стилевые изображения WikiArt
├── training/
│   ├── style_transfer_wikiart.ipynb          # Ноутбук экспериментов
│   ├── train_mobile.sh                       # Команда обучения mobile-модели
│   ├── data/
│   │   └── style_images.tfrecord             # Генерируется локально
│   ├── checkpoints/                          # Необязательно хранить в Git
│   └── logs/
├── results/                                  # Примеры: content + style + result
├── video/                                    # Видео демонстрации на смартфоне
├── .gitignore
├── README.md
├── build.gradle.kts
└── settings.gradle.kts
```

## Запуск приложения

### Требования

- Android Studio;
- Android SDK;
- физическое Android-устройство с USB Debugging или Android Emulator;
- интернет-соединение для первой Gradle-синхронизации.

### Инструкция

1. Открыть корневую папку проекта в Android Studio.
2. Дождаться завершения Gradle Sync.
3. Подключить смартфон через USB.
4. Подтвердить USB debugging на устройстве.
5. Выбрать подключённое устройство в Android Studio.
6. Нажать кнопку **Run** ▶.

## Демонстрация

Видео работы размещается в папке:

```text
video/
```

В видео показан полный сценарий:

1. Запуск приложения на физическом Android-устройстве.
2. Создание фотографии через системную камеру.
3. Возврат фотографии в приложение.
4. Выбор встроенного стиля WikiArt.
5. Запуск TensorFlow Lite inference.
6. Отображение стилизованного результата.
7. Сохранение результата в Галерею.
8. Открытие сохранённого JPEG.

## Источники

- [Magenta Arbitrary Image Stylization](https://github.com/magenta/magenta/tree/main/magenta/models/arbitrary_image_stylization)
- [Train a model on a large dataset with data augmentation to run on mobile](https://github.com/magenta/magenta/tree/main/magenta/models/arbitrary_image_stylization#train-a-model-on-a-large-dataset-with-data-augmentation-to-run-on-mobile)
- [TensorFlow Hub: Fast Style Transfer for Arbitrary Styles](https://www.tensorflow.org/hub/tutorials/tf2_arbitrary_image_stylization)
- [TensorFlow Lite Style Transfer Android Example](https://github.com/tensorflow/examples/tree/master/lite/examples/style_transfer/android)