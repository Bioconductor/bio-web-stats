CREATE EXTERNAL TABLE `old_stats`(
  `date` date COMMENT '', 
  `c-ip` string COMMENT '', 
  `sc-status` bigint COMMENT '', 
  `cs-uri-stem` string COMMENT '')
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY '\t' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://web-stats-dev/sqlite/'
TBLPROPERTIES (
  'areColumnsQuoted'='false', 
  'classification'='csv', 
  'compressionType'='gzip', 
  'delimiter'='\t', 
  'typeOfData'='file')