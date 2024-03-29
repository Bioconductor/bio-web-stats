CREATE EXTERNAL TABLE `stats`(
  `category` string, 
  `package` string,
  `date` date, 
  `is_monthly` boolean,
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