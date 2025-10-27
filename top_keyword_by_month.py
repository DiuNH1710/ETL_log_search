import glob
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count, row_number, to_date, month, first
from pyspark.sql.window import Window

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

def get_top_keyword_by_month(df: DataFrame) -> DataFrame:
    """
    Lấy top 1 keyword theo từng user_id và từng tháng, pivot sang cột riêng.
    """
    # Chuyển datetime sang date và lấy tháng
    df_with_month = df.withColumn("date", to_date("datetime")) \
                      .withColumn("month", month("date"))

    # Đếm số lần tìm kiếm keyword cho từng user theo tháng
    keyword_count = (
        df_with_month.groupBy("user_id", "month", "keyword")
                     .agg(count("*").alias("search_count"))
    )

    # Window theo user + month
    windowSpec = Window.partitionBy("user_id", "month").orderBy(col("search_count").desc())

    top_keywords = (
        keyword_count.withColumn("rank", row_number().over(windowSpec))
                     .filter(col("rank") == 1)
                     .select("user_id", "month", "keyword", "search_count")
    )

    # Pivot để có các cột most_search_t6, most_search_t7
    pivot_df = top_keywords.groupBy("user_id").pivot("month", [6, 7]) \
                           .agg(first("keyword").alias("most_search"))
    
    # Đổi tên cột cho rõ ràng
    pivot_df = pivot_df.withColumnRenamed("6", "most_search_t6") \
                       .withColumnRenamed("7", "most_search_t7")

    return pivot_df

if __name__ == "__main__":
    base_path = r"D:\study_de\Homework\log_search_etl\log_search"
    output_dir = r"D:\study_de\Homework\log_search_etl\outputs\top_keyword_by_month"

    # Khởi tạo SparkSession
    spark = SparkSession.builder.appName("TopKeywordByMonth").getOrCreate()

    print("Đang đọc dữ liệu parquet...")
    df = read_all_parquet(base_path, spark)

    print("Schema của dữ liệu:")
    df.printSchema()

    print("Đang tính top keyword theo từng user_id và tháng...")
    top_month_df = get_top_keyword_by_month(df)

    print("Kết quả top keyword theo tháng:")
    top_month_df.show(50, truncate=False)

    print(f"Đang lưu kết quả vào: {output_dir}")
    top_month_df.coalesce(1).write.mode("overwrite").option("header", True).csv(output_dir)

    print("Đã lưu thành công file CSV top keyword theo tháng!")

    spark.stop()
