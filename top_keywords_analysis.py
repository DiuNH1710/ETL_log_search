import glob
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count, row_number
from pyspark.sql.window import Window

def get_top3_keywords_per_user(df: DataFrame) -> DataFrame:
    """
    Trả về top 3 keyword được tìm nhiều nhất cho mỗi user_id.
    """
    # Đếm số lần mỗi keyword được tìm bởi từng user
    keyword_count = (
        df.groupBy("user_id", "keyword")
          .agg(count("*").alias("search_count"))
    )

    # Xác định top 3 từ khóa phổ biến nhất cho từng user
    windowSpec = Window.partitionBy("user_id").orderBy(col("search_count").desc())

    top_keywords = (
        keyword_count
        .withColumn("rank", row_number().over(windowSpec))
        .filter(col("rank") <= 3)
        .select("user_id", "keyword", "search_count", "rank")
        .orderBy( col("search_count").desc())
    )

    return top_keywords


def read_all_parquet(base_path: str) -> DataFrame:
    """
    Đọc toàn bộ file parquet trong tất cả thư mục con của base_path.
    """
    # Tìm tất cả các file .parquet trong mọi folder con
    files = glob.glob(f"{base_path}/**/*.parquet", recursive=True)
    
    if not files:
        raise FileNotFoundError(f"Không tìm thấy file parquet trong đường dẫn: {base_path}")
    
    print(f"🔹 Tìm thấy {len(files)} file parquet.")

    # Khởi tạo SparkSession
    spark = SparkSession.builder.appName("TopKeywordsAnalysis").getOrCreate()

    # Đọc tất cả file parquet
    df = spark.read.parquet(*files)
    return df


if __name__ == "__main__":
    base_path = r"D:\study_de\Homework\log_search_etl\log_search"

    print("🚀 Đang đọc dữ liệu parquet...")
    df = read_all_parquet(base_path)

    print("📊 Schema của dữ liệu:")
    df.printSchema()

    print("🔥 Đang phân tích top 3 keyword theo từng user_id...")
    result_df = get_top3_keywords_per_user(df)

    print("✅ Kết quả top 3 keyword:")
    result_df.show(50, truncate=False)

    # Nếu muốn lưu kết quả lại (tuỳ chọn)
#     result_df.write.mode("overwrite").parquet(r"D:\study_de\Homework\output\top_keywords")
