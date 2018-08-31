from pyspark.sql import SparkSession
import pyspark.sql.functions as sf
from pyspark.sql.functions import sum
import datetime

sess = SparkSession.builder.master("local[*]").appName("mmds2").getOrCreate()

df_lang = sess.read.format("csv").option("header", "true").load("./data/langlinks/ukwiki-20180701-langlinks.csv")

#test = df_lang.filter(df_lang.id == 1273710)
#test.show()

dl = df_lang.filter(df_lang.lang == "en")
dl.printSchema()
dl.show()

df_page = sess.read.format("csv").option("header", "true").load("./data/page/ukwiki-20180701-page.csv")
df_page.printSchema()
df_page.show()

# dl_set = set(dl.collect())

startDate = '20180601'
endDate = '20180630'

format = '%Y%m%d'

start = datetime.datetime.strptime(startDate, format)
end = datetime.datetime.strptime(endDate, format)

step = datetime.timedelta(days=1)

while start <= end:

    date_Str = start.strftime(format)

    print("Date: " + date_Str)

    rawData = sess.read.option("delimiter", " ").option("inferSchema", "true").csv("./data/pageviews/pageviews-" + date_Str + "*")

    cols = ["project", "title", "requests", "hour_vise"]

    rawDF = rawData.toDF(*cols)

    rawDF_uk = rawDF.filter(rawDF.project == "uk")

    rawDF_uk_with_id = rawDF_uk.join(df_page, "title")
    rawDF_uk_with_id.printSchema()
    rawDF_uk_with_id.show()

    rawDF_uk_notEn = rawDF_uk_with_id.join(dl, rawDF_uk_with_id.page_id == dl.id, 'left_anti')

    ds = rawDF_uk_notEn.groupBy("page_id").agg(sum("requests").alias("sum_requests"))

    ds.printSchema()
    ds.show()

    enDS = ds.select("page_id", "sum_requests").withColumn("date", sf.lit(date_Str))
    enDS.write.format("parquet").mode('append').save("./pageviews.parquet")

    start += step
