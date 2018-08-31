from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, avg, count, variance

sess = SparkSession.builder.master("local[*]").appName("mmds_variance").getOrCreate()

df = sess.read.parquet("./pageviews.parquet")
df.show()

ds = df.groupBy("page_id", "date").agg(sum("sum_requests").alias("requests"))
ds.show()

vari = ds.groupBy("page_id").agg(variance("requests").alias("variance"), count("date").alias("count"),  avg("requests").alias("avg"))
vari.show()

result = vari.filter("count == 30").filter("avg >= 100").orderBy(vari.variance.asc())
result.show()

df_page = sess.read.format("csv").option("header", "true").load("./data/page/ukwiki-20180701-page.csv")
df_page.printSchema()
df_page.show()

result_with_title = result.join(df_page, "page_id")

fnl = result_with_title.select("page_id", "title", "variance").orderBy(result_with_title.variance.asc())
fnl.show()

fnl.coalesce(1).write.mode("overwrite").format("com.databricks.spark.csv").option("header", "true").csv("./ranking.csv")