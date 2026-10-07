package com.example.styletransferapp

import android.content.ContentValues
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.drawable.ColorDrawable
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.view.View
import android.widget.Button
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.FileProvider
import org.tensorflow.lite.DataType
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.Tensor
import java.io.File
import java.io.FileInputStream
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.MappedByteBuffer
import java.nio.channels.FileChannel
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.Executors
import kotlin.math.roundToInt

class MainActivity : AppCompatActivity() {

    companion object {
        private const val STYLE_IMAGE_SIZE = 256
        private const val CONTENT_IMAGE_SIZE = 384
    }

    private var contentUri: Uri? = null
    private var styleUri: Uri? = null
    private var cameraPhotoUri: Uri? = null
    private var selectedBuiltInStyle: String? = null
    private var resultBitmap: Bitmap? = null

    private lateinit var contentImageView: ImageView
    private lateinit var styleImageView: ImageView
    private lateinit var resultImageView: ImageView
    private lateinit var styleGalleryLayout: LinearLayout
    private lateinit var applyStyleButton: Button
    private lateinit var saveResultButton: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var statusTextView: TextView

    private val executor = Executors.newSingleThreadExecutor()

    private val pickContentImage =
        registerForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri ->
            uri?.let {
                contentUri = it
                cameraPhotoUri = null
                contentImageView.setImageURI(it)

                clearPreviousResult()
                statusTextView.text = "Исходная фотография выбрана"
                updateApplyButton()
            }
        }

    private val pickStyleImage =
        registerForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri ->
            uri?.let {
                styleUri = it
                selectedBuiltInStyle = null
                styleImageView.setImageURI(it)

                clearPreviousResult()
                statusTextView.text = "Изображение-стиль выбрано"
                updateApplyButton()
            }
        }

    private val takePhoto =
        registerForActivityResult(ActivityResultContracts.TakePicture()) { wasTaken ->
            val photoUri = cameraPhotoUri

            if (wasTaken && photoUri != null) {
                contentUri = photoUri
                contentImageView.setImageURI(photoUri)

                clearPreviousResult()
                statusTextView.text = "Фотография с камеры добавлена"
                updateApplyButton()
            } else {
                Toast.makeText(
                    this,
                    "Съёмка отменена",
                    Toast.LENGTH_SHORT
                ).show()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        contentImageView = findViewById(R.id.contentImageView)
        styleImageView = findViewById(R.id.styleImageView)
        resultImageView = findViewById(R.id.resultImageView)
        styleGalleryLayout = findViewById(R.id.styleGalleryLayout)
        applyStyleButton = findViewById(R.id.applyStyleButton)
        saveResultButton = findViewById(R.id.saveResultButton)
        progressBar = findViewById(R.id.progressBar)
        statusTextView = findViewById(R.id.statusTextView)

        findViewById<Button>(R.id.selectContentButton).setOnClickListener {
            pickContentImage.launch(
                PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)
            )
        }

        findViewById<Button>(R.id.takePhotoButton).setOnClickListener {
            try {
                val photoUri = createCameraPhotoUri()
                cameraPhotoUri = photoUri
                takePhoto.launch(photoUri)
            } catch (error: IOException) {
                Toast.makeText(
                    this,
                    "Не удалось открыть камеру: ${error.message}",
                    Toast.LENGTH_LONG
                ).show()
            }
        }

        findViewById<Button>(R.id.selectStyleButton).setOnClickListener {
            pickStyleImage.launch(
                PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)
            )
        }

        applyStyleButton.setOnClickListener {
            runStyleTransfer()
        }

        saveResultButton.setOnClickListener {
            saveResultToGallery()
        }

        loadBuiltInStyles()
    }

    override fun onDestroy() {
        executor.shutdown()
        super.onDestroy()
    }

    private fun clearPreviousResult() {
        resultBitmap = null
        saveResultButton.isEnabled = false
    }

    private fun updateApplyButton() {
        val hasStyle = styleUri != null || selectedBuiltInStyle != null
        val isReady = contentUri != null && hasStyle

        applyStyleButton.isEnabled = isReady

        if (isReady) {
            statusTextView.text = "Всё готово к переносу стиля"
        }
    }

    private fun loadBuiltInStyles() {
        val styleFiles = try {
            assets.list("styles")
                ?.filter { fileName ->
                    fileName.endsWith(".jpg", ignoreCase = true) ||
                            fileName.endsWith(".jpeg", ignoreCase = true) ||
                            fileName.endsWith(".png", ignoreCase = true)
                }
                ?.sorted()
                ?: emptyList()
        } catch (_: IOException) {
            emptyList()
        }

        if (styleFiles.isEmpty()) {
            return
        }

        val itemSize = dpToPx(96)
        val margin = dpToPx(6)

        styleFiles.forEach { fileName ->
            val preview = ImageView(this).apply {
                layoutParams = LinearLayout.LayoutParams(itemSize, itemSize).apply {
                    setMargins(margin, 0, margin, 0)
                }

                scaleType = ImageView.ScaleType.CENTER_CROP
                background = ColorDrawable(0xFF2A2A2A.toInt())
                contentDescription = "Встроенный стиль $fileName"
                setPadding(dpToPx(2), dpToPx(2), dpToPx(2), dpToPx(2))
            }

            try {
                assets.open("styles/$fileName").use { inputStream ->
                    preview.setImageBitmap(BitmapFactory.decodeStream(inputStream))
                }
            } catch (_: IOException) {
                return@forEach
            }

            preview.setOnClickListener {
                try {
                    val selectedStyle = assets.open("styles/$fileName").use { inputStream ->
                        BitmapFactory.decodeStream(inputStream)
                            ?: throw IOException("Не удалось открыть $fileName")
                    }

                    styleUri = null
                    selectedBuiltInStyle = "styles/$fileName"
                    styleImageView.setImageBitmap(selectedStyle)

                    clearPreviousResult()
                    statusTextView.text = "Выбран встроенный стиль: $fileName"
                    updateApplyButton()
                } catch (error: IOException) {
                    Toast.makeText(
                        this,
                        "Не удалось открыть встроенный стиль: ${error.message}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }

            styleGalleryLayout.addView(preview)
        }
    }

    private fun dpToPx(valueInDp: Int): Int {
        return (valueInDp * resources.displayMetrics.density).roundToInt()
    }

    private fun createCameraPhotoUri(): Uri {
        val cameraDirectory = File(cacheDir, "camera")

        if (!cameraDirectory.exists() && !cameraDirectory.mkdirs()) {
            throw IOException("Не удалось создать папку для фото")
        }

        val photoFile = File.createTempFile(
            "content_",
            ".jpg",
            cameraDirectory
        )

        return FileProvider.getUriForFile(
            this,
            "com.example.styletransferapp.fileprovider",
            photoFile
        )
    }

    private fun runStyleTransfer() {
        val selectedContentUri = contentUri ?: return

        setProcessingState(true, "Загрузка изображений…")

        executor.execute {
            try {
                val contentBitmap = loadBitmap(selectedContentUri)
                val styleBitmap = loadSelectedStyleBitmap()

                runOnUiThread {
                    statusTextView.text = "Определяется художественный стиль…"
                }

                val stylizedBitmap = runInference(contentBitmap, styleBitmap)

                runOnUiThread {
                    resultBitmap = stylizedBitmap
                    resultImageView.setImageBitmap(stylizedBitmap)
                    setProcessingState(false, "Готово. Стиль применён.")
                    saveResultButton.isEnabled = true
                }
            } catch (error: Exception) {
                runOnUiThread {
                    setProcessingState(
                        false,
                        "Ошибка: ${error.message ?: "неизвестная ошибка"}"
                    )

                    Toast.makeText(
                        this,
                        "Перенос стиля не выполнен: ${error.message}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        }
    }

    private fun loadSelectedStyleBitmap(): Bitmap {
        val selectedUri = styleUri

        if (selectedUri != null) {
            return loadBitmap(selectedUri)
        }

        val assetPath = selectedBuiltInStyle
            ?: throw IOException("Сначала выберите изображение-стиль")

        return assets.open(assetPath).use { inputStream ->
            BitmapFactory.decodeStream(inputStream)
                ?: throw IOException("Не удалось прочитать встроенный стиль")
        }
    }

    private fun runInference(contentBitmap: Bitmap, styleBitmap: Bitmap): Bitmap {
        val styleInterpreter = Interpreter(loadModelFile("style_predict.tflite"))
        val transformInterpreter = Interpreter(loadModelFile("style_transform.tflite"))

        try {
            val styleInputTensor = styleInterpreter.getInputTensor(0)
            val styleOutputTensor = styleInterpreter.getOutputTensor(0)

            val styleInput = bitmapToModelInput(
                bitmap = styleBitmap,
                width = STYLE_IMAGE_SIZE,
                height = STYLE_IMAGE_SIZE,
                tensor = styleInputTensor
            )

            val styleEmbedding = ByteBuffer
                .allocateDirect(styleOutputTensor.numBytes())
                .order(ByteOrder.nativeOrder())

            styleInterpreter.run(styleInput, styleEmbedding)
            styleEmbedding.rewind()

            val contentInputTensor = transformInterpreter.getInputTensor(0)
            val styleEmbeddingInputTensor = transformInterpreter.getInputTensor(1)
            val transformOutputTensor = transformInterpreter.getOutputTensor(0)

            val contentInput = bitmapToModelInput(
                bitmap = contentBitmap,
                width = CONTENT_IMAGE_SIZE,
                height = CONTENT_IMAGE_SIZE,
                tensor = contentInputTensor
            )

            if (styleEmbedding.capacity() != styleEmbeddingInputTensor.numBytes()) {
                throw IllegalStateException(
                    "Несовместимые модели: style_predict создаёт embedding " +
                            "размером ${styleEmbedding.capacity()} байт, а style_transform " +
                            "ожидает ${styleEmbeddingInputTensor.numBytes()} байт."
                )
            }

            val outputBuffer = ByteBuffer
                .allocateDirect(transformOutputTensor.numBytes())
                .order(ByteOrder.nativeOrder())

            transformInterpreter.runForMultipleInputsOutputs(
                arrayOf(contentInput, styleEmbedding),
                mapOf(0 to outputBuffer)
            )

            outputBuffer.rewind()

            return outputBufferToBitmap(
                buffer = outputBuffer,
                width = CONTENT_IMAGE_SIZE,
                height = CONTENT_IMAGE_SIZE,
                tensor = transformOutputTensor
            )
        } finally {
            styleInterpreter.close()
            transformInterpreter.close()
        }
    }

    private fun bitmapToModelInput(
        bitmap: Bitmap,
        width: Int,
        height: Int,
        tensor: Tensor
    ): ByteBuffer {
        val resized = centerCropAndResize(bitmap, width, height)
        val pixels = IntArray(width * height)

        resized.getPixels(
            pixels,
            0,
            width,
            0,
            0,
            width,
            height
        )

        val buffer = ByteBuffer
            .allocateDirect(tensor.numBytes())
            .order(ByteOrder.nativeOrder())

        val quantization = tensor.quantizationParams()
        val scale = quantization.scale
        val zeroPoint = quantization.zeroPoint

        for (pixel in pixels) {
            val red = ((pixel shr 16) and 0xFF) / 255f
            val green = ((pixel shr 8) and 0xFF) / 255f
            val blue = (pixel and 0xFF) / 255f

            putTensorValue(buffer, red, tensor.dataType(), scale, zeroPoint)
            putTensorValue(buffer, green, tensor.dataType(), scale, zeroPoint)
            putTensorValue(buffer, blue, tensor.dataType(), scale, zeroPoint)
        }

        buffer.rewind()
        return buffer
    }

    private fun putTensorValue(
        buffer: ByteBuffer,
        realValue: Float,
        dataType: DataType,
        scale: Float,
        zeroPoint: Int
    ) {
        when (dataType) {
            DataType.FLOAT32 -> {
                buffer.putFloat(realValue)
            }

            DataType.INT8 -> {
                val quantized = (realValue / scale + zeroPoint)
                    .roundToInt()
                    .coerceIn(-128, 127)

                buffer.put(quantized.toByte())
            }

            DataType.UINT8 -> {
                val quantized = (realValue / scale + zeroPoint)
                    .roundToInt()
                    .coerceIn(0, 255)

                buffer.put(quantized.toByte())
            }

            else -> {
                throw IllegalArgumentException(
                    "Неподдерживаемый тип входного тензора: $dataType"
                )
            }
        }
    }

    private fun outputBufferToBitmap(
        buffer: ByteBuffer,
        width: Int,
        height: Int,
        tensor: Tensor
    ): Bitmap {
        val pixels = IntArray(width * height)
        val quantization = tensor.quantizationParams()
        val scale = quantization.scale
        val zeroPoint = quantization.zeroPoint

        for (index in pixels.indices) {
            val red = readTensorValue(
                buffer,
                tensor.dataType(),
                scale,
                zeroPoint
            )

            val green = readTensorValue(
                buffer,
                tensor.dataType(),
                scale,
                zeroPoint
            )

            val blue = readTensorValue(
                buffer,
                tensor.dataType(),
                scale,
                zeroPoint
            )

            val r = (red.coerceIn(0f, 1f) * 255f).roundToInt()
            val g = (green.coerceIn(0f, 1f) * 255f).roundToInt()
            val b = (blue.coerceIn(0f, 1f) * 255f).roundToInt()

            pixels[index] = (0xFF shl 24) or
                    (r shl 16) or
                    (g shl 8) or
                    b
        }

        return Bitmap.createBitmap(
            pixels,
            width,
            height,
            Bitmap.Config.ARGB_8888
        )
    }

    private fun readTensorValue(
        buffer: ByteBuffer,
        dataType: DataType,
        scale: Float,
        zeroPoint: Int
    ): Float {
        return when (dataType) {
            DataType.FLOAT32 -> {
                buffer.float
            }

            DataType.INT8 -> {
                val quantized = buffer.get().toInt()
                (quantized - zeroPoint) * scale
            }

            DataType.UINT8 -> {
                val quantized = buffer.get().toInt() and 0xFF
                (quantized - zeroPoint) * scale
            }

            else -> {
                throw IllegalArgumentException(
                    "Неподдерживаемый тип выходного тензора: $dataType"
                )
            }
        }
    }

    private fun centerCropAndResize(
        source: Bitmap,
        targetWidth: Int,
        targetHeight: Int
    ): Bitmap {
        val sourceWidth = source.width
        val sourceHeight = source.height

        val sourceRatio = sourceWidth.toFloat() / sourceHeight
        val targetRatio = targetWidth.toFloat() / targetHeight

        val cropWidth: Int
        val cropHeight: Int
        val left: Int
        val top: Int

        if (sourceRatio > targetRatio) {
            cropHeight = sourceHeight
            cropWidth = (sourceHeight * targetRatio).roundToInt()
            left = (sourceWidth - cropWidth) / 2
            top = 0
        } else {
            cropWidth = sourceWidth
            cropHeight = (sourceWidth / targetRatio).roundToInt()
            left = 0
            top = (sourceHeight - cropHeight) / 2
        }

        val cropped = Bitmap.createBitmap(
            source,
            left,
            top,
            cropWidth,
            cropHeight
        )

        return Bitmap.createScaledBitmap(
            cropped,
            targetWidth,
            targetHeight,
            true
        )
    }

    private fun loadBitmap(uri: Uri): Bitmap {
        contentResolver.openInputStream(uri).use { inputStream ->
            return BitmapFactory.decodeStream(inputStream)
                ?: throw IOException("Не удалось прочитать выбранное изображение")
        }
    }

    private fun loadModelFile(modelName: String): MappedByteBuffer {
        assets.openFd(modelName).use { descriptor ->
            FileInputStream(descriptor.fileDescriptor).channel.use { channel ->
                return channel.map(
                    FileChannel.MapMode.READ_ONLY,
                    descriptor.startOffset,
                    descriptor.declaredLength
                )
            }
        }
    }

    private fun setProcessingState(processing: Boolean, message: String) {
        progressBar.visibility = if (processing) View.VISIBLE else View.GONE

        val hasStyle = styleUri != null || selectedBuiltInStyle != null

        applyStyleButton.isEnabled = !processing &&
                contentUri != null &&
                hasStyle

        statusTextView.text = message
    }

    private fun saveResultToGallery() {
        val bitmap = resultBitmap ?: return

        executor.execute {
            try {
                val timestamp = SimpleDateFormat(
                    "yyyyMMdd_HHmmss",
                    Locale.US
                ).format(Date())

                val fileName = "style_transfer_$timestamp.jpg"

                val values = ContentValues().apply {
                    put(MediaStore.Images.Media.DISPLAY_NAME, fileName)
                    put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
                    put(
                        MediaStore.Images.Media.RELATIVE_PATH,
                        "${Environment.DIRECTORY_PICTURES}/StyleTransferApp"
                    )
                    put(MediaStore.Images.Media.IS_PENDING, 1)
                }

                val outputUri = contentResolver.insert(
                    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
                    values
                ) ?: throw IOException("Не удалось создать файл результата")

                contentResolver.openOutputStream(outputUri).use { outputStream ->
                    if (outputStream == null) {
                        throw IOException("Не удалось открыть файл для записи")
                    }

                    val wasSaved = bitmap.compress(
                        Bitmap.CompressFormat.JPEG,
                        95,
                        outputStream
                    )

                    if (!wasSaved) {
                        throw IOException("Не удалось сохранить JPEG")
                    }
                }

                values.clear()
                values.put(MediaStore.Images.Media.IS_PENDING, 0)

                contentResolver.update(outputUri, values, null, null)

                runOnUiThread {
                    Toast.makeText(
                        this,
                        "Результат сохранён в Галерею",
                        Toast.LENGTH_LONG
                    ).show()
                }
            } catch (error: Exception) {
                runOnUiThread {
                    Toast.makeText(
                        this,
                        "Ошибка сохранения: ${error.message}",
                        Toast.LENGTH_LONG
                    ).show()
                }
            }
        }
    }
}