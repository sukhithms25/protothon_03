from pyspark.sql import SparkSession
import os

spark = SparkSession.builder.appName("repo-analysis").getOrCreate()

def index_repository(path):

    files = []

    for root, dirs, fs in os.walk(path):
        for f in fs:
            if f.endswith(".py") or f.endswith(".js"):
                files.append((os.path.join(root,f),))

    df = spark.createDataFrame(files, ["file_path"])

    df.write.format("delta").mode("overwrite").save("repo_index")