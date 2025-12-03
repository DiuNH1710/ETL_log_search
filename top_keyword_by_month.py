import glob
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count, row_number, to_date, month, first
from pyspark.sql.window import Window

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

def get_top_keyword_by_month(df: DataFrame) -> DataFrame:
    """
     Get top 1 keyword per user_id and per month, then pivot into separate columns.
    """
       # Convert datetime to date and extract month
    df_with_month = df.withColumn("date", to_date("datetime")) \
                      .withColumn("month", month("date"))

   
      # Count keyword searches per user per month
    keyword_count = (
        df_with_month.groupBy("user_id", "month", "keyword")
                     .agg(count("*").alias("search_count"))
    )

   # Window specification per user + month
    windowSpec = Window.partitionBy("user_id", "month").orderBy(col("search_count").desc())

    # Rank and filter top keyword
    top_keywords = (
        keyword_count.withColumn("rank", row_number().over(windowSpec))
                     .filter(col("rank") == 1)
                     .select("user_id", "month", "keyword", "search_count")
    )

    # Pivot to get columns most_search_t6, most_search_t7
    pivot_df = top_keywords.groupBy("user_id").pivot("month", [6, 7]) \
                           .agg(first("keyword").alias("most_search"))
    
     # Rename columns for clarity
    pivot_df = pivot_df.withColumnRenamed("6", "most_search_t6") \
                       .withColumnRenamed("7", "most_search_t7")

    return pivot_df

if __name__ == "__main__":
    base_path = r"D:\study_de\Homework\log_search_etl\log_search"
    output_dir = r"D:\study_de\Homework\log_search_etl\outputs\top_keyword_by_month"

      # Initialize SparkSession
    spark = SparkSession.builder.appName("TopKeywordByMonth").getOrCreate()

    print("Reading parquet data...")
    df = read_all_parquet(base_path, spark)

    print("Schema of the dataset:")
    df.printSchema()

    print("Calculating top keyword per user_id and month...")
    top_month_df = get_top_keyword_by_month(df)

    print("Top keyword results by month:")
    top_month_df.show(50, truncate=False)

    print(f"Saving results to: {output_dir}")
    top_month_df.coalesce(1).write.mode("overwrite").option("header", True).csv(output_dir)

    print("Successfully saved CSV file for top keywords by month!")

    spark.stop()
