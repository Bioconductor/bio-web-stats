-- Athena SQL to expose www.biconductor.org web logs as a SQL table
-- TODO: Add dynamic partition projection on year and month

CREATE EXTERNAL TABLE `bioc_web_logs`(
  `date` date COMMENT '', 
  `time` string COMMENT '', 
  `x-edge-location` string COMMENT '', 
  `sc-bytes` bigint COMMENT '', 
  `c-ip` string COMMENT '', 
  `cs-method` string COMMENT '', 
  `cs(host)` string COMMENT '', 
  `cs-uri-stem` string COMMENT '', 
  `sc-status` bigint COMMENT '', 
  `cs(referer)` string COMMENT '', 
  `cs(user-agent)` string COMMENT '', 
  `cs-uri-query` string COMMENT '', 
  `cs(cookie)` string COMMENT '', 
  `x-edge-result-type` string COMMENT '', 
  `x-edge-request-id` string COMMENT '', 
  `x-host-header` string COMMENT '', 
  `cs-protocol` string COMMENT '', 
  `cs-bytes` bigint COMMENT '', 
  `time-taken` double COMMENT '', 
  `x-forwarded-for` string COMMENT '', 
  `ssl-protocol` string COMMENT '', 
  `ssl-cipher` string COMMENT '', 
  `x-edge-response-result-type` string COMMENT '', 
  `cs-protocol-version` string COMMENT '', 
  `fle-status` bigint COMMENT '', 
  `fle-encrypted-fields` bigint COMMENT '', 
  `c-port` bigint COMMENT '', 
  `time-to-first-byte` double COMMENT '', 
  `x-edge-detailed-result-type` string COMMENT '', 
  `sc-content-type` string COMMENT '', 
  `sc-content-len` bigint COMMENT '', 
  `sc-range-start` bigint COMMENT '', 
  `sc-range-end` bigint COMMENT '')
ROW FORMAT DELIMITED 
  FIELDS TERMINATED BY '\t' 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://bioc-cloudfront-logs/'
TBLPROPERTIES (
  'areColumnsQuoted'='false', 
  'classification'='csv', 
  'columnsOrdered'='true', 
  'commentCharacter'='#', 
  'compressionType'='gzip', 
  'delimiter'='\t', 
  'typeOfData'='file')