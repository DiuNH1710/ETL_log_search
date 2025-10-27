import glob
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count, row_number
from pyspark.sql.window import Window

def get_top3_keywords_per_user(df: DataFrame) -> DataFrame:
    """
    Trả về top 3 keyword được tìm nhiều nhất cho mỗi user_id.
    """
    keyword_count = (
        df.groupBy("user_id", "keyword")
          .agg(count("*").alias("search_count"))
    )

    windowSpec = Window.partitionBy("user_id").orderBy(col("search_count").desc())

    top_keywords = (
        keyword_count
        .withColumn("rank", row_number().over(windowSpec))
        .filter(col("rank") <= 3)
        .select("user_id", "keyword", "search_count", "rank")
        .orderBy(col("search_count").desc())
    )

    return top_keywords


def read_all_parquet(base_path: str, spark: SparkSession) -> DataFrame:
    """
    Đọc toàn bộ file parquet trong tất cả thư mục con của base_path.
    """
    files = glob.glob(f"{base_path}/**/*.parquet", recursive=True)
    
    if not files:
        raise FileNotFoundError(f"Không tìm thấy file parquet trong: {base_path}")
    
    print(f"Tìm thấy {len(files)} file parquet.")
    df = spark.read.parquet(*files)
    return df


if __name__ == "__main__":
    base_path = r"D:\study_de\Homework\log_search_etl\log_search"

    # Khởi tạo SparkSession
    spark = SparkSession.builder.appName("TopKeywordsAnalysis").getOrCreate()

    print("Đang đọc dữ liệu parquet...")
    df = read_all_parquet(base_path, spark)

    print("Schema của dữ liệu:")
    df.printSchema()

    print("Đang phân tích top 3 keyword theo từng user_id...")
    top3_df = get_top3_keywords_per_user(df)

    print("Kết quả top 3 keyword:")
    top3_df.show(50, truncate=False)

    # Lấy top 1 keyword (rank == 1)
    print("Lấy top 1 keyword theo từng user_id...")
    top1_df = top3_df.filter(col("rank") == 1)

    # Ghi ra file CSV
    output_dir_top3 = r"D:\study_de\Homework\log_search_etl\outputs\top3_keywords"
    output_dir_top1 = r"D:\study_de\Homework\log_search_etl\outputs\top1_keywords"

    print(f"Đang lưu kết quả vào: {output_dir_top3} và {output_dir_top1}")

    # Ghi dạng CSV (1 file duy nhất)
    top3_df.coalesce(1).write.mode("overwrite").option("header", True).csv(output_dir_top3)
    top1_df.coalesce(1).write.mode("overwrite").option("header", True).csv(output_dir_top1)

    print("Đã lưu thành công các file CSV kết quả!")

    spark.stop()
