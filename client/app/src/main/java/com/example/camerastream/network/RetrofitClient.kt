object RetrofitClient {
    private val retrofit = Retrofit.Builder()
        .baseUrl("http://<서버IP>:5000/")  // 로컬 서버 주소
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val api: ApiService = retrofit.create(ApiService::class.java)
}
