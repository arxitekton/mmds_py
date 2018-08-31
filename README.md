### Ranking articles in ukwiki by volatility
#### Goal
Create a ranking of relevant articles that exists in the Ukranian Wikipedia (ukwiki) but are missing in the English Wikipedia (enwiki) with ranking by volatility.
Volatility. this is important both - for people writing content (lifetime value) and maybe for Wikimedia Foundation (planning some resources, development, distribution,  organazing datacenter etc.
#### Problem statement 
Create a ranking considering the less volatile (by views) articles in ukwiki that are missing in enwiki.
#### ML tasks
Clustering received pages by volatile and average pageviews
#### Data
The following data were used for the project:
* ukwiki-20180701-langlinks.sql.gz
* ukwiki-20180701-page.sql.gz

pageviews (Totalling 274.8 GB):
* pageviews-20180601-000000.gz
* ...
* pageviews-20180731-230000.gz

source: 
* https://dumps.wikimedia.org/ukwiki/20180701/
* https://dumps.wikimedia.org/other/pageviews/2018/2018-06/
* https://dumps.wikimedia.org/other/pageviews/2018/2018-07/


To download files:
```bash
wget https://dumps.wikimedia.org/ukwiki/20180701/ukwiki-20180701-langlinks.sql.gz
wget https://dumps.wikimedia.org/ukwiki/20180701/ukwiki-20180701-page.sql.gz
wget https://dumps.wikimedia.org/other/pageviews/2018/2018-06/pageviews-201806{01..30}-{00..23}0000.gz
wget https://dumps.wikimedia.org/other/pageviews/2018/2018-07/pageviews-201807{01..30}-{00..23}0000.gz
```
#### Preprocessing
[langlinks_sql2csv.py](https://github.com/arxitekton/mmds_py/blob/master/langlinks_sql2csv.py) - python script to convert langlinks.sql.gz file to csv
[page_sql2csv.py](https://github.com/arxitekton/mmds_py/blob/master/page_sql2csv.py) - python script to convert langlinks.sql.gz file to csv


#### ETL: 
[pageviewRequest.ipynb](https://github.com/arxitekton/mmds_py/blob/master/pageviewRequest.ipynb), [pageviewRequest_jule.ipynb](https://github.com/arxitekton/mmds_py/blob/master/pageviewRequest_jule.ipynb) - jupyter notebooks with pyspark for processing uk article, missing in the enwiki, and collecting daily pageviews in the period {june, jule 2018} (61 days) to pageviews.parquet
[variance_ts_final.ipynb](https://github.com/arxitekton/mmds_py/blob/master/variance_ts_final.ipynb) - jupyter notebooks with pyspark  for group requests by page_id and compute variance and avg pageviews; and pandas for clustering and visualization

#### Results: 
[ranking.csv](https://github.com/arxitekton/mmds_py/blob/master/ranking.csv/part-00000-0ce4d713-8433-4b99-8fe9-96250aae356b-c000.csv) – csv file with uk article, missing in the enwiki, which have daily views and average pageview > 100 plus theirs variance (order by variance)

page_id | title | variance
------- | ----- | --------
 348286|              Пропан|15.339344262294935|
2560908|  Кіновсесвіт_Marvel|368.74590163934425|
2615953|Список_померлих_2...| 619.4448087431697|
2204198|Список_українськи...| 645.3043715846995|
 535221|Список_українськи...| 645.3043715846995|
 334485|             Ukr.net|  775.563387978142|
2673689|             Ukr.net| 775.5633879781421|
 268344|Вікіпедія:Патрулю...| 862.5989071038254|
 250851|            Чернівці| 891.0830601092896|
  36061|     Українська_мова| 917.7486338797814|
 845354|     Українська_мова| 917.7486338797816|
  25716|     Українська_мова| 917.7486338797818|
  23021|              Харків| 972.7043715846991|
1048374|              Харків| 972.7043715846993|
 526117|              Харків| 972.7043715846995|
1734695|             Вінниця|1002.2967213114752|
 776413|             Вінниця|1002.2967213114753|
2383741|             Вінниця|1002.2967213114755|
  39405|             Вінниця|1002.2967213114756|
  36825|Бандера_Степан_Ан...| 1101.649726775956|


#### Clustering: 
For clustering I used kmeans (see [variance_ts_final.ipynb](https://github.com/arxitekton/mmds_py/blob/master/variance_ts_final.ipynb)).
To identify the optimal number of clusters I used “Elbow Curve” approach (see [variance_ts_final.ipynb](https://github.com/arxitekton/mmds_py/blob/master/variance_ts_final.ipynb)):


algorithm:
* getting 'langlinks' data and filter $"lang" ==="en"
* getting 'page' data
* from 20180601 to 20180731:
    * getting hourly "pageviews" for this date and filter $"project" === "uk"
    * left join "pageviews" with 'page' on 'title' because we need $"page_id"
    * leftanti with 'langlinks' (exclude corresponding row) - because we need just article missing in the enwiki
    * groupBy "page_id" and aggregate sum of "requests"
    * append to parquet
