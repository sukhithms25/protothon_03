from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

def get_repo_files():

    df = spark.read.format("delta").load("repo_index")

    return [row.file_path for row in df.collect()]