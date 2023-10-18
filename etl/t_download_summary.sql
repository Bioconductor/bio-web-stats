CREATE EXTERNAL TABLE `download_summary`(
  `category` string, 
  `package` string,
  `date` date, 
  `ip_count` bigint, 
  `download_count` bigint
  )
ROW FORMAT SERDE 
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
LOCATION
  's3://web-stats-dev/parquet/ds'
TBLPROPERTIES (
  'parquet.compression'='SNAPPY')