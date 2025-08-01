package com.example.myclientapp

import com.example.myclientapp.R
import android.os.Bundle
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.view.PreviewView

class MainActivity : AppCompatActivity() {
    private lateinit var previewView: PreviewView
    private lateinit var subtitleText: TextView
    private lateinit var cameraStreamer: CameraStreamer
    private lateinit var tcpClient: TCPSocketClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        previewView = findViewById(R.id.previewView)
        subtitleText = findViewById(R.id.subtitleText)

        cameraStreamer = CameraStreamer(this, previewView, "10.198.139.201", 9999) // 서버 IP
        cameraStreamer.startCamera()

        tcpClient = TCPSocketClient("10.198.139.201", 8888) { text, audioFile ->
            runOnUiThread {
                subtitleText.text = text
                tcpClient.playAudio(audioFile)
            }
        }
        tcpClient.start()
    }
}
