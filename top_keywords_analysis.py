import glob
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count, row_number
from pyspark.sql.window import Window

def get_top3_keywords_per_user(df: DataFrame) -> DataFrame:
    """
    Return the top 3 most searched keywords for each user_id.
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
    Read all parquet files recursively under base_path.
    """
    files = glob.glob(f"{base_path}/**/*.parquet", recursive=True)
    
    if not files:
        raise FileNotFoundError(f"No parquet files found in: {base_path}")
    
    print(f"Found  {len(files)} file parquet.")
    df = spark.read.parquet(*files)
    return df


if __name__ == "__main__":
    base_path = r"D:\study_de\Homework\log_search_etl\log_search"

    # Initialize SparkSession
    spark = SparkSession.builder.appName("TopKeywordsAnalysis").getOrCreate()

    print("Reading parquet data...")
    df = read_all_parquet(base_path, spark)

    print("Schema of the dataset:")
    df.printSchema()

    print("Calculating top 3 keywords per user_id...")
    top3_df = get_top3_keywords_per_user(df)

    print("Top 3 keywords result:")
    top3_df.show(50, truncate=False)

     # Get top 1 keyword per user (rank == 1)
    print("Extracting top 1 keyword per user_id...")
    top1_df = top3_df.filter(col("rank") == 1)

    # Output directories
    output_dir_top3 = r"D:\study_de\Homework\log_search_etl\outputs\top3_keywords"
    output_dir_top1 = r"D:\study_de\Homework\log_search_etl\outputs\top1_keywords"

    print(f"Saving results to: {output_dir_top3} và {output_dir_top1}")

    # Write CSV (single file)
    top3_df.coalesce(1).write.mode("overwrite").option("header", True).csv(output_dir_top3)
    top1_df.coalesce(1).write.mode("overwrite").option("header", True).csv(output_dir_top1)

    print("CSV files successfully saved!")

    spark.stop()
