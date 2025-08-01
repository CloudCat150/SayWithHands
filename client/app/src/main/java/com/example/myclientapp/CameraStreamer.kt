package com.example.myclientapp

import android.graphics.*
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import java.io.ByteArrayOutputStream
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.util.concurrent.Executors
import android.util.Log
import android.widget.Toast

class CameraStreamer(
    private val activity: AppCompatActivity,
    private val previewView: PreviewView,
    private val serverIP: String,
    private val serverPort: Int
) {
    fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(activity)
        cameraProviderFuture.addListener({
            try {
                val cameraProvider = cameraProviderFuture.get()

                val preview = Preview.Builder().build().also {
                    it.setSurfaceProvider(previewView.surfaceProvider)
                }

                val imageAnalyzer = ImageAnalysis.Builder()
                    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                    .build()
                    .also {
                        it.setAnalyzer(Executors.newSingleThreadExecutor()) { imageProxy ->
                            try {
                                val bitmap = imageProxyToBitmap(imageProxy)
                                if (bitmap != null) {
                                    sendFrame(bitmap)
                                }
                            } catch (e: Exception) {
                                Log.e("CameraStreamer", "이미지 처리 오류: ${e.message}")
                                activity.runOnUiThread {
                                    Toast.makeText(activity, "이미지 처리 오류: ${e.message}", Toast.LENGTH_SHORT).show()
                                }
                            } finally {
                                imageProxy.close()
                            }
                        }
                    }

                val cameraSelector = CameraSelector.DEFAULT_FRONT_CAMERA
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(activity, cameraSelector, preview, imageAnalyzer)
            } catch (e: Exception) {
                Log.e("CameraStreamer", "카메라 시작 오류: ${e.message}")
                activity.runOnUiThread {
                    Toast.makeText(activity, "카메라 시작 오류: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }, ContextCompat.getMainExecutor(activity))
    }

    private fun imageProxyToBitmap(image: ImageProxy): Bitmap? {
        return try {
            val yBuffer = image.planes[0].buffer
            val uBuffer = image.planes[1].buffer
            val vBuffer = image.planes[2].buffer

            val ySize = yBuffer.remaining()
            val uSize = uBuffer.remaining()
            val vSize = vBuffer.remaining()

            val nv21 = ByteArray(ySize + uSize + vSize)
            yBuffer.get(nv21, 0, ySize)
            vBuffer.get(nv21, ySize, vSize)
            uBuffer.get(nv21, ySize + vSize, uSize)

            val yuvImage = YuvImage(nv21, ImageFormat.NV21, image.width, image.height, null)
            val out = ByteArrayOutputStream()
            yuvImage.compressToJpeg(Rect(0, 0, image.width, image.height), 60, out)
            val jpegBytes = out.toByteArray()
            BitmapFactory.decodeByteArray(jpegBytes, 0, jpegBytes.size)
        } catch (e: Exception) {
            Log.e("CameraStreamer", "Bitmap 변환 실패: ${e.message}")
            activity.runOnUiThread {
                    Toast.makeText(activity, "Bitmap 변환 실패: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            null
        }
    }

    private fun sendFrame(bitmap: Bitmap) {
        Thread {
            try {
                val stream = ByteArrayOutputStream()
                bitmap.compress(Bitmap.CompressFormat.JPEG, 15, stream)
                val data = stream.toByteArray()

                val socket = DatagramSocket()
                val packet =
                    DatagramPacket(data, data.size, InetAddress.getByName(serverIP), serverPort)
                socket.send(packet)
                socket.close()
            } catch (e: Exception) {
                Log.e("CameraStreamer", "프레임 전송 오류: ${e.message}")

                activity.runOnUiThread {
                    Toast.makeText(activity, "프레임 전송 실패: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }.start()
    }
}
