package com.example.myclientapp

import android.media.MediaPlayer
import java.io.DataInputStream
import java.io.File
import java.io.FileOutputStream
import java.net.Socket

class TCPSocketClient(
    private val serverIP: String,
    private val serverPort: Int,
    private val onDataReceived: (String, File) -> Unit
) {
    fun start() {
        Thread {
            val socket = Socket(serverIP, serverPort)
            val input = DataInputStream(socket.getInputStream())

            while (true) {
                val textLength = input.readInt()
                val textBytes = ByteArray(textLength)
                input.readFully(textBytes)
                val text = String(textBytes)

                val audioLength = input.readInt()
                val audioBytes = ByteArray(audioLength)
                input.readFully(audioBytes)

                val audioFile = File.createTempFile("audio", ".mp3")
                FileOutputStream(audioFile).use {
                    it.write(audioBytes)
                }

                onDataReceived(text, audioFile)
            }
        }.start()
    }

    fun playAudio(file: File) {
        val mediaPlayer = MediaPlayer().apply {
            setDataSource(file.absolutePath)
            prepare()
            start()
        }
    }
}
