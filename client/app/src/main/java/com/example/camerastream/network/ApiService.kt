interface ApiService {
    @Multipart
    @POST("upload_frame")
    fun sendFrame(@Part frame: MultipartBody.Part): Call<ResponseBody>

    @GET("get_mp3")
    fun getMp3(): Call<ResponseBody>
}
