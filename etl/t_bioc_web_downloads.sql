CREATE EXTERNAL TABLE `bioc_web_downloads`(
  `date` date, 
  `c-ip` string, 
  `sc-status` int, 
  `category` string, 
  `package` string)
PARTITIONED BY ( 
  `year` string, 
  `month` string, 
  `day` string)
  ROW FORMAT SERDE 
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
LOCATION
  's3://web-stats-dev/parquet'
TBLPROPERTIES (
  'parquet.compression'='SNAPPY')